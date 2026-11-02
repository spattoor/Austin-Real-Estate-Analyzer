# Deployment and verification

Prepared November 1, 2026 (America/Chicago). No live URL, real Gemini response, Docker build, or AWS resource has been verified yet.

## First deployment

1. Push the prepared `portfolio-cloud-upgrade` branch.
2. In Streamlit choose **Create app**, then deploy from GitHub.
3. Repository: `spattoor/Austin-Real-Estate-Analyzer`; branch: `portfolio-cloud-upgrade`; main file: `deploy/app.py`; Python: 3.12.
4. Deploy without secrets first. Verify tables, filters, ZIP history, source dates, methodology, and CSV download in a private browser window.
5. Add a fresh Gemini key in app settings → Secrets, following `deploy/secrets.example.toml`. Never paste it into GitHub or chat.
6. Ask a supported metric question and an unsupported prediction question. Download the AI verification record. Warnings do not prove actual AI inference.
7. Save a screenshot and update the README with the actual live URL.

## AWS, after the demo works

Use a Free account plan only if eligible. Inspect current service eligibility, credits and expiry. Do not upgrade to paid billing as part of these steps. S3 is not promised to be permanently free. No AWS provisioning has run.

1. Create a private general-purpose S3 bucket in your region, keeping **Block all public access** enabled. Use default SSE-S3 encryption. Record bucket name and region.
2. In IAM create an OIDC provider for `https://token.actions.githubusercontent.com` with audience `sts.amazonaws.com`, unless it already exists.
3. Create a role using `deploy/aws/github-trust.template.json`, replacing `ACCOUNT_ID`. It trusts only `main`: review and merge the deployment branch before enabling it. A temporary test must explicitly trust the actual test branch.
4. Attach `writer-policy.template.json` after replacing `BUCKET_NAME`. The role uploads raw files, snapshots and the pointer; it cannot delete objects or administer S3.
5. Set GitHub Actions repository variables `AWS_ROLE_ARN`, `AWS_REGION`, `AUSTIN_S3_BUCKET`. Run **Refresh Austin market snapshot** manually on the trusted branch.
6. Verify workflow logs, the raw object, hashed DB, and `latest.json`. Save the actual workflow run URL as evidence.
7. Create a separate app reader identity with only `reader-policy.template.json`. If it uses a static key, store it exclusively in Streamlit Secrets and rotate it. GitHub's OIDC role does not authenticate Streamlit automatically.
8. Add S3 settings to Streamlit. Verify **Private S3 snapshot**, reboot the app, and confirm restoration with the same source date and row counts. Local tests use simulated S3 and do not prove this cloud behavior.
9. Set `ENABLE_REFRESH=true`. Monday's schedule uses UTC, runs from the default branch, may be delayed, and may be disabled after repository inactivity. Verify an actual scheduled execution separately.

## Limits and shutdown

Weekly refresh is bounded to a 200 MiB download. Content-addressed files avoid duplicate uploads of identical content, but source revisions add storage. Inspect S3 storage, requests, egress, credits, and expiry. Billing alerts are notifications, not hard spending caps.

To stop cloud writes, set `ENABLE_REFRESH=false` and disable the workflow. Remove the reader key/writer role when no longer needed. Removing S3 settings restores bundled mode. Disabling automation does not remove stored objects; delete them deliberately if you want to stop storage costs.

Remove `GEMINI_API_KEY` from Streamlit to disable AI. Revoke the key at the provider to stop other callers too.

## Resume proof boundaries

Local source ingestion, five Prefect stages, clustering, SQLite generation and automated dashboard checks have been exercised. Tests also cover exact-month arithmetic, missing data, AI response validation, unsupported responses, provider failure, and simulated snapshot restoration/corruption.

Actual AI inference, hosting, S3/OIDC, a scheduled cloud run, Docker execution and restart restoration from real S3 remain unverified. The unsupported-response test is mocked; it does not establish live model behavior.
