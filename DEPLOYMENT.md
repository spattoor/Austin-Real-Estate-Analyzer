# Deployment and verification

Updated November 1, 2026 (America/Chicago).

Public app: https://austin-real-estate-analyzer-d5mx2bhi5grprfmjggz83b.streamlit.app/

## Verified AWS execution

The deployed data path is:

```text
EventBridge weekly rule → CodeBuild → five Prefect stages → private S3
                                                        ↓
                                           read-only CloudFront → Streamlit
```

The private bucket contains the matching raw Zillow file, content-addressed SQLite snapshots, and an atomically replaced `latest.json` pointer. All four public-access blocks and SSE-S3/AES256 encryption remain enabled.

- A manual AWS build succeeded: `effb190c-1a4b-4044-af6f-2c9de36094a5`.
- Eight pipeline tests passed inside CodeBuild.
- A real EventBridge-triggered build succeeded: `e7c48c37-c967-4db1-b575-9df20e2b1581`, initiator `rule/spattoor-austin-weekly`.
- Both runs executed the five Prefect stages, published to S3, and verified a fresh restoration with matching SHA-256 and SQLite integrity.
- Restored data: 546 rows, 42 ZIP areas, latest observation September 30, 2026.
- Current restored SHA-256: `613a6a05089cd51ac06043c3c11554f8c504d749603adfd46edef7e75e3e74a4`.
- The permanent rule is enabled for Monday at 11:23 UTC. The scheduled-trigger smoke test used a temporary one-time expression on the same rule, then restored this weekly expression.

The account remained on its Free plan. No persistent AWS access keys were created. The earlier GitHub OIDC setup was denied by account policy and was not retried. The native AWS job uses scoped service roles and does not require GitHub federation.

## App snapshot delivery

`deploy/snapshot-source.json` contains the actual public CloudFront root. The manifest and published database objects are publicly readable through CloudFront; the S3 origin itself and raw source files stay private. The origin policy permits read-only access only from that specific CloudFront distribution.

The app retrieves a manifest at most every five minutes, checks its schema and path, limits the database to 50 MiB, verifies SHA-256, checks SQLite integrity, and atomically caches the restored file. A new app instance can restore the current snapshot without AWS credentials. A configured cloud-delivery failure is shown as an error rather than silently serving a bundled snapshot.

The HTTPS reader has tests for valid restoration/cache reuse, corrupt data, untrusted URLs/object paths, and redirects/errors. App checks cover bundled and CloudFront source selection. These tests complement the actual anonymous HTTPS restoration exercised against the deployed distribution.

Environment overrides:

- `AUSTIN_SNAPSHOT_BASE_URL`: an HTTPS CloudFront distribution root.
- `AUSTIN_SNAPSHOT_MODE=bundled`: explicit local bundled mode.
- `AUSTIN_S3_BUCKET`: optional alternative direct S3 reader, requiring its own AWS identity. That alternative is not configured for the deployed app.

The app uses branch `portfolio-cloud-upgrade`, entrypoint `deploy/app.py`, and Python 3.12. Existing Gemini secrets are separate from this storage deployment.

## Reproduce or stop

See `deploy/aws/NATIVE_REFRESH.md`, `native-refresh.template.json`, and `snapshot-delivery.template.json`. The refresh template creates a disabled rule by default. Enable it only after a verified build.

To stop refresh writes, disable `spattoor-austin-weekly` in EventBridge and stop any active CodeBuild run. To use the bundled app snapshot, set `AUSTIN_SNAPSHOT_MODE=bundled` or remove the delivery configuration. Deleting the refresh stack removes its job, rule, and roles; it does not delete the existing bucket. Disable/delete CloudFront deliberately if retiring public snapshot delivery.

Small CodeBuild compute has a published free allowance shared across the account. S3, logs, and other applicable usage may consume credits. Monitor the account's remaining credits and expiry. No paid-plan upgrade is required by this setup.

## Proof boundaries

This is **Prefect**, not Airflow. Docker container execution and the legacy GitHub OIDC publishing route are separate and were not verified by this deployment. The Zillow-only dataset in this deployment does not establish project-wide claims about seven sources or 50+ ZIP codes. AI provider verification is separate from the AWS pipeline work.
