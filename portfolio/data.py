"""Keyless Zillow ZHVI ingestion, explicit features, heuristic scoring, and SQLite load."""
import hashlib
import json
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

SOURCE_ID = 'zillow-zhvi-zip-all-homes-sa'
SOURCE_URL = 'https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv'
METHOD = 'zhvi-descriptive-v1'


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def ingest(directory):
    """Download the fixed public source. Fail on HTTP errors; never invent observations."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / 'zillow_zhvi.csv'
    pending = target.with_suffix('.partial')
    started = time.monotonic()
    size = 0
    try:
        with requests.get(SOURCE_URL, stream=True, timeout=(10, 40)) as r:
            r.raise_for_status()
            with pending.open('wb') as f:
                for chunk in r.iter_content(1024 * 1024):
                    size += len(chunk)
                    if size > 200 * 1024 * 1024 or time.monotonic() - started > 180:
                        raise ValueError('Source download exceeded the size or duration limit')
                    f.write(chunk)
        pending.replace(target)
    finally:
        pending.unlink(missing_ok=True)
    return target


def clean(raw):
    """Keep Austin city ZIPs in Texas. Never substitute stale values for missing months."""
    pieces = []
    for frame in pd.read_csv(raw, dtype={'RegionName': 'str'}, chunksize=1500):
        required = {'RegionName', 'City', 'State'}
        if not required.issubset(frame.columns):
            raise ValueError('Zillow source schema changed')
        pieces.append(frame.loc[(frame['State'] == 'TX') & (frame['City'] == 'Austin')].copy())
    frame = pd.concat(pieces, ignore_index=True)
    if frame.empty or frame['RegionName'].duplicated().any():
        raise ValueError('No unique Austin ZIP observations were found')
    months = sorted(c for c in frame.columns if re.fullmatch(r'\d{4}-\d{2}-\d{2}', c))
    if len(months) < 37:
        raise ValueError('At least 37 monthly columns are required')
    if not frame['RegionName'].str.fullmatch(r'\d{5}').all():
        raise ValueError('Invalid ZIP codes in source')
    frame[months] = frame[months].apply(pd.to_numeric, errors='coerce')
    frame[months] = frame[months].where(frame[months] > 0)
    return frame, months


def features(frame, months, month):
    i = months.index(month)
    if i < 36:
        raise ValueError('36 months of history are required')
    records = []
    for _, row in frame.iterrows():
        value, year, three = (row[months[j]] for j in [i, i - 12, i - 36])
        if pd.isna(value):
            continue
        records.append({
            'zip_code': row['RegionName'], 'neighborhood_name': 'Austin ZIP ' + row['RegionName'],
            'observed_on': month, 'zhvi': float(value),
            'change_1y_pct': None if pd.isna(year) else float((value / year - 1) * 100),
            'change_3y_pct': None if pd.isna(three) else float((value / three - 1) * 100),
            'source_id': SOURCE_ID,
        })
    if not records:
        raise ValueError('No observations for ' + month)
    return pd.DataFrame(records)


def score(frame):
    """Descriptive comparison, NOT prediction. Missing inputs receive no score/cluster."""
    frame = frame.copy()
    frame['cost_percentile'] = (1 - frame['zhvi'].rank(method='average', pct=True)) * 100
    frame['momentum_1y_percentile'] = frame['change_1y_pct'].rank(method='average', pct=True) * 100
    frame['momentum_3y_percentile'] = frame['change_3y_pct'].rank(method='average', pct=True) * 100
    complete = frame[['zhvi', 'change_1y_pct', 'change_3y_pct']].notna().all(axis=1)
    frame['comparison_score'] = np.nan
    frame.loc[complete, 'comparison_score'] = (
        frame.loc[complete, 'cost_percentile'] * .40 +
        frame.loc[complete, 'momentum_1y_percentile'] * .35 +
        frame.loc[complete, 'momentum_3y_percentile'] * .25
    )
    frame['cluster'] = pd.Series([None] * len(frame), dtype='object')
    eligible = frame.loc[complete, ['zhvi', 'change_1y_pct', 'change_3y_pct']]
    if len(eligible) >= 3 and len(eligible.drop_duplicates()) >= 3:
        x = StandardScaler().fit_transform(eligible)
        labels = KMeans(n_clusters=3, random_state=42, n_init=10).fit_predict(x)
        # IDs describe this snapshot only; they do not imply investment quality.
        frame.loc[complete, 'cluster'] = [int(n) for n in labels]
    frame['method_version'] = METHOD
    return frame


def load(scored_frames, database, metadata):
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    pending = database.with_suffix('.pending.db')
    pending.unlink(missing_ok=True)
    frame = pd.concat(scored_frames, ignore_index=True)
    with sqlite3.connect(pending) as con:
        frame.to_sql('market_observations', con, index=False, if_exists='replace')
        con.execute('CREATE UNIQUE INDEX observation_zip_date ON market_observations(zip_code, observed_on)')
        con.execute('CREATE TABLE snapshot_metadata (json TEXT NOT NULL)')
        con.execute('INSERT INTO snapshot_metadata VALUES (?)', (json.dumps(metadata, allow_nan=False),))
        if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('SQLite integrity check failed')
    pending.replace(database)
    return {'rows': len(frame), 'zip_areas': int(frame.zip_code.nunique()),
            'snapshot_date': frame.observed_on.max(), 'database_sha256': sha256(database)}


def build(raw, database, history_months=13):
    frame, months = clean(raw)
    selected = months[max(36, len(months) - history_months):]
    metadata = {'source_id': SOURCE_ID, 'source_url': SOURCE_URL, 'raw_sha256': sha256(raw),
                'retrieved_at': datetime.now(timezone.utc).isoformat(), 'method_version': METHOD,
                'source_kind': 'observed', 'source_latest_month': months[-1],
                'scope': 'Zillow rows with State=TX and City=Austin; ZIP areas, not neighborhood boundaries',
                'missing_data': 'Unavailable values remain null. No score or cluster without both growth periods.',
                'limitations': 'ZHVI is a modeled typical home-value index. Scores are descriptive heuristics, not forecasts or investment returns.'}
    return load([score(features(frame, months, m)) for m in selected], database, metadata)
