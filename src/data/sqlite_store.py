"""Validated, repeatable CSV imports and SQL analysis using the Python standard library."""

import csv
import hashlib
import io
import json
import math
import re
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / 'data' / 'austin.db'
SQL_DIR = ROOT / 'sql'
REPORTS = {'rankings', 'cluster_summary', 'history', 'coverage'}
MISSING = {'', 'nan', 'none', 'null', 'n/a', 'na'}


@contextmanager
def connect(database=DEFAULT_DB, readonly=False):
    path = Path(database).resolve()
    if readonly:
        con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=10)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(path), timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    try:
        yield con
    finally:
        con.close()


def normalize_zip(value):
    value = str(value or '').strip()
    # Accept common CSV float artifacts and ZIP+4; preserve leading zeroes.
    if re.fullmatch(r'\d{5}\.0+', value):
        value = value.split('.')[0]
    if re.fullmatch(r'\d{5}-\d{4}', value):
        value = value[:5]
    if not re.fullmatch(r'\d{5}', value):
        raise ValueError('zip_code must be five digits, ZIP+4, or a whole five-digit CSV float')
    return value


def number(value, field, required=False, low=None, high=None, integer=False):
    text = '' if value is None else str(value).strip()
    if text.lower() in MISSING:
        if required:
            raise ValueError(field + ' is required')
        return None
    try:
        result = float(text)
    except (ValueError, TypeError):
        raise ValueError(field + ' must be numeric') from None
    if not math.isfinite(result):
        raise ValueError(field + ' must be finite')
    if low is not None and result < low or high is not None and result > high:
        raise ValueError(field + ' is outside its allowed range')
    if integer and not result.is_integer():
        raise ValueError(field + ' must be an integer')
    return int(result) if integer else result


def clean_row(raw):
    if None in raw:
        raise ValueError('row has more values than the CSV header')
    row = {k: (v.strip() if v is not None else '') for k, v in raw.items()}
    row['zip_code'] = normalize_zip(row['zip_code'])
    row['neighborhood_name'] = row.get('neighborhood_name') or 'ZIP ' + row['zip_code']
    row['investment_score'] = number(row.get('investment_score'), 'investment_score', True, 0, 100)
    row['median_home_value'] = number(row.get('median_home_value'), 'median_home_value')
    if row['median_home_value'] is not None and row['median_home_value'] <= 0:
        raise ValueError('median_home_value must be positive when provided')
    row['business_count'] = number(row.get('business_count'), 'business_count', low=0, integer=True)
    row['confidence_score'] = number(row.get('confidence_score'), 'confidence_score', low=0, high=100)
    row['cluster'] = row.get('cluster') or None
    return row


def import_csv(csv_path, database=DEFAULT_DB, observed_on=None,
               source_kind='user-provided', skip_invalid=False):
    """Upsert ZIP/date records. Strict validation rejects the entire batch by default.

    Repeat files create audit runs but do not duplicate observations. Corrected values
    replace the same ZIP/date; a different date preserves history. No API is called.
    """
    observed_on = observed_on or date.today().isoformat()
    if date.fromisoformat(observed_on).isoformat() != observed_on:
        raise ValueError('observed_on must be YYYY-MM-DD')
    if source_kind not in {'user-provided', 'synthetic'}:
        raise ValueError('unknown source_kind')
    path = Path(csv_path)
    contents = path.read_bytes()
    reader = csv.DictReader(io.StringIO(contents.decode('utf-8-sig')))
    fields = reader.fieldnames or []
    if not {'zip_code', 'investment_score'}.issubset(fields):
        raise ValueError('CSV requires zip_code and investment_score columns')
    if len(fields) != len(set(fields)):
        raise ValueError('CSV contains duplicate header names')
    rows, issues, duplicates, input_rows = {}, [], 0, 0
    for line, raw in enumerate(reader, 2):
        input_rows += 1
        try:
            row = clean_row(raw)
            key = row['zip_code']
            if key in rows:
                if rows[key] == row:
                    duplicates += 1
                    continue
                raise ValueError('conflicting duplicate ZIP in the same file: ' + key)
            rows[key] = row
        except ValueError as exc:
            issues.append((line, str(exc)))
    if input_rows == 0:
        raise ValueError('CSV has no data rows')
    result = dict(input_rows=input_rows, inserted_rows=0, updated_rows=0,
                  unchanged_rows=0, duplicate_rows=duplicates, rejected_rows=len(issues))
    status = 'rejected' if (issues and not skip_invalid) or not rows else 'completed'
    with connect(database) as con:
        con.executescript((SQL_DIR / 'schema.sql').read_text())
        with con:
            con.execute('BEGIN IMMEDIATE')
            run_id = con.execute(
                'INSERT INTO import_runs(started_at,source_file,source_sha256,source_kind,observed_on,status) '
                'VALUES (?,?,?,?,?,?)',
                (datetime.now(timezone.utc).isoformat(), path.name,
                 hashlib.sha256(contents).hexdigest(), source_kind, observed_on, 'running')
            ).lastrowid
            con.executemany('INSERT INTO validation_issues(run_id,csv_row,reason) VALUES (?,?,?)',
                            [(run_id, line, reason) for line, reason in issues])
            if status == 'completed':
                for zip_code, row in rows.items():
                    payload = json.dumps(row, sort_keys=True, allow_nan=False)
                    old = con.execute(
                        'SELECT o.payload_json, r.source_kind FROM observations o '
                        'JOIN import_runs r ON r.run_id=o.run_id '
                        'WHERE o.zip_code=? AND o.observed_on=?', (zip_code, observed_on)
                    ).fetchone()
                    if old and old['source_kind'] != source_kind:
                        raise ValueError('Cannot mix synthetic and user-provided records for the same ZIP/date')
                    if old and old['payload_json'] == payload:
                        result['unchanged_rows'] += 1
                        continue
                    con.execute('INSERT INTO neighborhoods VALUES (?,?) ON CONFLICT(zip_code) '
                                'DO UPDATE SET neighborhood_name=excluded.neighborhood_name',
                                (zip_code, row['neighborhood_name']))
                    con.execute(
                        'INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?) '
                        'ON CONFLICT(zip_code,observed_on) DO UPDATE SET '
                        'run_id=excluded.run_id, investment_score=excluded.investment_score, '
                        'median_home_value=excluded.median_home_value, business_count=excluded.business_count, '
                        'confidence_score=excluded.confidence_score, cluster=excluded.cluster, '
                        'payload_json=excluded.payload_json',
                        (zip_code, observed_on, run_id, row['investment_score'], row['median_home_value'],
                         row['business_count'], row['confidence_score'], row['cluster'], payload))
                    result['updated_rows' if old else 'inserted_rows'] += 1
            con.execute(
                'UPDATE import_runs SET status=?,input_rows=?,inserted_rows=?,updated_rows=?, '
                'unchanged_rows=?,duplicate_rows=?,rejected_rows=? WHERE run_id=?',
                (status, *result.values(), run_id))
    return dict(run_id=run_id, status=status, **result)


def report(name, database=DEFAULT_DB, **params):
    if name not in REPORTS:
        raise ValueError('Unknown report: ' + name)
    bindings = dict(observed_on=None, min_score=0, max_price=None, zip_code='')
    bindings.update(params)
    with connect(database, readonly=True) as con:
        return [dict(r) for r in con.execute((SQL_DIR / (name + '.sql')).read_text(), bindings)]


def audit(database=DEFAULT_DB):
    with connect(database, readonly=True) as con:
        runs = [dict(r) for r in con.execute('SELECT * FROM import_runs ORDER BY run_id DESC')]
        issues = [dict(r) for r in con.execute('SELECT * FROM validation_issues ORDER BY issue_id DESC')]
    return dict(runs=runs, issues=issues)


def load_snapshot(database=DEFAULT_DB, observed_on=None):
    """Return the existing dashboard's full records for one observation date."""
    with connect(database, readonly=True) as con:
        rows = con.execute('SELECT payload_json FROM observations WHERE observed_on = '
                           'COALESCE(?, (SELECT MAX(observed_on) FROM observations)) ORDER BY zip_code',
                           (observed_on,)).fetchall()
    return [json.loads(r[0]) for r in rows]


def load_snapshot_frame(database=DEFAULT_DB):
    # CSV inference restores types of extra columns exactly as in the original CSV loader.
    import pandas as pd
    rows = load_snapshot(database)
    if not rows:
        raise ValueError('SQLite database has no imported observations')
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(dict.fromkeys(k for row in rows for k in row)))
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)
    return pd.read_csv(buffer, dtype={'zip_code': str})
