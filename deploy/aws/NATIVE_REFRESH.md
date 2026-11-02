# Austin refresh inside AWS

This path runs the existing five-stage **Prefect** pipeline in AWS CodeBuild and publishes private S3 snapshots. EventBridge starts the same project weekly. It does not use GitHub OIDC, long-lived access keys, privileged containers, or a paid-plan upgrade.

## Resources

- Existing private S3 bucket; public-access blocks and encryption remain enabled.
- CodeBuild project: `spattoor-austin-refresh`.
- EventBridge rule: `spattoor-austin-weekly`.
- CloudFormation stack: `spattoor-austin-refresh-native`.
- One CodeBuild role restricted to the Austin object prefixes and that project's logs.
- One EventBridge role restricted to starting that CodeBuild project.
- Small on-demand compute, ten-minute build and queue timeouts, one concurrent build, seven-day logs.

The template pins a reviewed source commit. A weekly refresh downloads current data using that reviewed code. Future code changes require updating the source revision after review.

## Deploy the reusable template

Set `AUSTIN_S3_BUCKET` to your existing private bucket and `AWS_DEFAULT_REGION` to its region. Neither variable is a credential.

```bash
aws cloudformation deploy \
  --template-file native-refresh.template.json \
  --stack-name spattoor-austin-refresh-native \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides DataBucket="$AUSTIN_S3_BUCKET" \
  --region "$AWS_DEFAULT_REGION"
```

The template creates a **disabled** schedule. Run and inspect a manual build before enabling it:

```bash
aws codebuild start-build \
  --project-name spattoor-austin-refresh \
  --region "$AWS_DEFAULT_REGION"
```

Require a successful build, passing tests, the `S3_RESTORE_VERIFIED` log marker, and a valid S3 `latest.json` pointer before enabling:

```bash
aws events enable-rule \
  --name spattoor-austin-weekly \
  --region "$AWS_DEFAULT_REGION"
```

The schedule is `cron(23 11 ? * MON *)`: Monday at 11:23 UTC. Scheduled jobs are asynchronous; configuration is not proof that a scheduled invocation has run. Enabling the rule directly creates intentional drift from the template's disabled-by-default state; redeploying the disabled template can turn it off again.

## What a successful job verifies

1. Installs pinned project dependencies.
2. Runs the repository's automated tests.
3. Runs ingest, clean, features, score, and load through Prefect.
4. Publishes content-addressed raw data and SQLite files, then replaces `latest.json` last.
5. Downloads a fresh copy from private S3 and compares its checksum with the generated database.
6. Checks SQLite integrity and prints restored counts and observation date.

## Cost and stopping

[CodeBuild pricing](https://aws.amazon.com/codebuild/pricing/) lists 100 free monthly minutes for the selected small compute class. All builds in the account share that allowance. S3, log storage, and applicable usage may consume credits. No paid-plan upgrade is part of this deployment.

To stop future refreshes:

```bash
aws events disable-rule \
  --name spattoor-austin-weekly \
  --region "$AWS_DEFAULT_REGION"
```

Stop an in-progress build separately with `aws codebuild stop-build --id BUILD_ID`. Deleting this named CloudFormation stack removes its job, rule, and roles, but leaves the existing S3 bucket and its data. Delete stored data only deliberately.

## Boundaries

- This is Prefect, not Airflow.
- S3 restoration in AWS does not establish private-S3 restoration inside Streamlit Community Cloud. That separate app identity is not configured here.
- The observed bundled dataset has 546 rows across 42 ZIP areas. Other project-wide metrics require their own evidence.
- Record exact build IDs and outcomes in the verification handoff; do not count a submitted build as a successful build.
