"""Run the five stages locally or with Prefect; publish only when explicitly requested."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from portfolio import data

ingest = task(data.ingest, name='ingest', retries=2, retry_delay_seconds=10, cache_policy=NO_CACHE)
clean = task(data.clean, name='clean', cache_policy=NO_CACHE)
features = task(data.features, name='features', cache_policy=NO_CACHE)
score = task(data.score, name='score', cache_policy=NO_CACHE)
load = task(data.load, name='load', cache_policy=NO_CACHE)


@flow(name='austin-market-refresh', log_prints=True)
def refresh(output='deploy/data/austin.db', raw_dir='data/raw/portfolio', publish_s3=False):
    raw = ingest(raw_dir)
    frame, months = clean(raw)
    selected = months[max(36, len(months) - 13):]
    metadata = {'source_id': data.SOURCE_ID, 'source_url': data.SOURCE_URL,
                'raw_sha256': data.sha256(raw), 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'method_version': data.METHOD, 'source_kind': 'observed',
                'source_latest_month': months[-1],
                'scope': 'Austin city ZIP areas in Texas',
                'missing_data': 'Null inputs are not imputed; unscorable rows remain visible.',
                'limitations': 'Descriptive ZHVI comparison; no rental yields, forecasts, or return predictions.'}
    frames = [score(features(frame, months, month)) for month in selected]
    result = load(frames, output, metadata)
    if publish_s3:
        from portfolio.snapshot import publish
        result['s3_manifest'] = publish(Path(output), Path(raw))
    print(json.dumps(result, sort_keys=True))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', default='deploy/data/austin.db')
    p.add_argument('--raw-dir', default='data/raw/portfolio')
    p.add_argument('--publish-s3', action='store_true')
    a = p.parse_args()
    refresh(a.output, a.raw_dir, a.publish_s3)
