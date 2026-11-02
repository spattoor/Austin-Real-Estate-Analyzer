"""Private S3 content-addressed files and an atomically replaced publication pointer."""
import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def client():
    import boto3
    from botocore.config import Config
    return boto3.client('s3', config=Config(connect_timeout=5, read_timeout=20,
                                         retries={'max_attempts': 2, 'mode': 'standard'}))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def publish(database, raw, s3=None, bucket=None):
    s3 = s3 or client()
    bucket = bucket or os.environ['AUSTIN_S3_BUCKET']
    db_sha, raw_sha = digest(database), digest(raw)
    db_key, raw_key = f'snapshots/{db_sha}.db', f'raw/{raw_sha}.csv'
    from botocore.exceptions import ClientError
    for key, path, kind in [(raw_key, raw, 'text/csv'), (db_key, database, 'application/vnd.sqlite3')]:
        with Path(path).open('rb') as body:
            try:
                s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType=kind,
                              ServerSideEncryption='AES256', IfNoneMatch='*')
            except ClientError as e:
                if e.response.get('ResponseMetadata', {}).get('HTTPStatusCode') != 412:
                    raise
    manifest = {'schema_version': 1, 'database_key': db_key, 'sha256': db_sha,
                'raw_key': raw_key, 'raw_sha256': raw_sha,
                'published_at': datetime.now(timezone.utc).isoformat()}
    # Write the pointer last, after both immutable files have uploaded successfully.
    s3.put_object(Bucket=bucket, Key='latest.json', Body=json.dumps(manifest).encode(),
                  ContentType='application/json', ServerSideEncryption='AES256')
    return f's3://{bucket}/latest.json'


def restore(directory, s3=None, bucket=None):
    s3 = s3 or client()
    bucket = bucket or os.environ['AUSTIN_S3_BUCKET']
    body = s3.get_object(Bucket=bucket, Key='latest.json')['Body']
    try:
        content = body.read(16385)
        if len(content) > 16384:
            raise ValueError('Snapshot manifest is too large')
        manifest = json.loads(content)
    finally:
        body.close()
    checksum = manifest.get('sha256', '')
    if (manifest.get('schema_version') != 1 or len(checksum) != 64 or
        any(c not in '0123456789abcdef' for c in checksum) or
        manifest.get('database_key') != f'snapshots/{checksum}.db'):
        raise ValueError('Invalid snapshot manifest')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (checksum + '.db')
    if target.exists() and digest(target) == checksum:
        return target
    obj = s3.get_object(Bucket=bucket, Key=manifest['database_key'])
    body = obj['Body']
    pending = None
    try:
        size = 0
        with tempfile.NamedTemporaryFile(dir=directory, suffix='.pending', delete=False) as f:
            pending = Path(f.name)
            while chunk := body.read(1024 * 1024):
                size += len(chunk)
                if size > 50 * 1024 * 1024:
                    raise ValueError('Snapshot is too large')
                f.write(chunk)
        if digest(pending) != checksum:
            raise ValueError('Snapshot checksum mismatch')
        with sqlite3.connect(pending.as_uri() + '?mode=ro', uri=True) as con:
            if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Snapshot is not a valid SQLite database')
            con.execute('SELECT zip_code, observed_on FROM market_observations LIMIT 1')
        pending.replace(target)
    finally:
        body.close()
        if pending is not None:
            pending.unlink(missing_ok=True)
    return target
