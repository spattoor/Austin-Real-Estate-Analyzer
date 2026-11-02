#!/usr/bin/env bash
# Run by the account owner in AWS CloudShell. Creates only named S3/IAM resources.
# No credentials are printed. Run after confirming the account's Free plan.
set -euo pipefail
umask 077
export AWS_PAGER=''
REGION="${1:-us-east-2}"
case "$REGION" in us-east-1|us-east-2) ;; *) echo 'Use us-east-1 or us-east-2 for this setup.'; exit 1;; esac
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
BUCKET="spattoor-austin-${ACCOUNT_ID}-${REGION}"
WRITER='spattoor-austin-github-refresh'
READER='spattoor-austin-streamlit-reader'
PROVIDER="arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
SETUP_DIR="$PWD/austin-cloud"
mkdir -p "$SETUP_DIR"
cd "$SETUP_DIR"

if ! aws s3api head-bucket --bucket "$BUCKET" --expected-bucket-owner "$ACCOUNT_ID" --region "$REGION" 2>/dev/null; then
  if [[ "$REGION" == 'us-east-1' ]]; then
    aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" >/dev/null
  else
    aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" --create-bucket-configuration "LocationConstraint=$REGION" >/dev/null
  fi
fi
aws s3api put-public-access-block --bucket "$BUCKET" --region "$REGION" --public-access-block-configuration 'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'
aws s3api put-bucket-encryption --bucket "$BUCKET" --region "$REGION" --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

if ! aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$PROVIDER" >/dev/null 2>&1; then
  aws iam create-open-id-connect-provider --url 'https://token.actions.githubusercontent.com' --client-id-list 'sts.amazonaws.com' >/dev/null
fi
cat > trust.json <<JSON
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Federated":"$PROVIDER"},"Action":"sts:AssumeRoleWithWebIdentity","Condition":{"StringEquals":{"token.actions.githubusercontent.com:aud":"sts.amazonaws.com","token.actions.githubusercontent.com:sub":"repo:spattoor/Austin-Real-Estate-Analyzer:ref:refs/heads/main"}}}]}
JSON
if ! aws iam get-role --role-name "$WRITER" >/dev/null 2>&1; then
  aws iam create-role --role-name "$WRITER" --assume-role-policy-document file://trust.json --tags Key=Project,Value=spattoor-austin-portfolio >/dev/null
else
  aws iam update-assume-role-policy --role-name "$WRITER" --policy-document file://trust.json
fi
cat > writer.json <<JSON
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:PutObject"],"Resource":["arn:aws:s3:::$BUCKET/raw/*","arn:aws:s3:::$BUCKET/snapshots/*","arn:aws:s3:::$BUCKET/latest.json"]}]}
JSON
aws iam put-role-policy --role-name "$WRITER" --policy-name AustinSnapshotWriter --policy-document file://writer.json

if ! aws iam get-user --user-name "$READER" >/dev/null 2>&1; then
  aws iam create-user --user-name "$READER" --tags Key=Project,Value=spattoor-austin-portfolio >/dev/null
fi
cat > reader.json <<JSON
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:GetObject"],"Resource":["arn:aws:s3:::$BUCKET/latest.json","arn:aws:s3:::$BUCKET/snapshots/*"]}]}
JSON
aws iam put-user-policy --user-name "$READER" --policy-name AustinSnapshotReader --policy-document file://reader.json

if [[ ! -s reader-key.json ]]; then
  KEY_COUNT="$(aws iam list-access-keys --user-name "$READER" --query 'length(AccessKeyMetadata)' --output text)"
  if [[ "$KEY_COUNT" != '0' ]]; then
    echo 'A reader key already exists, but its private file is not here. Stop and recover or rotate that key; no extra key was created.'
    exit 1
  fi
  aws iam create-access-key --user-name "$READER" --output json > reader-key.json
fi
export AUSTIN_SETUP_BUCKET="$BUCKET" AUSTIN_SETUP_REGION="$REGION"
python3 - <<'PY'
import json,os
from pathlib import Path
key=json.loads(Path('reader-key.json').read_text())['AccessKey']
values={'AUSTIN_S3_BUCKET':os.environ['AUSTIN_SETUP_BUCKET'],
        'AWS_DEFAULT_REGION':os.environ['AUSTIN_SETUP_REGION'],
        'AWS_ACCESS_KEY_ID':key['AccessKeyId'], 'AWS_SECRET_ACCESS_KEY':key['SecretAccessKey']}
Path('streamlit-aws-secrets.toml').write_text('\n'.join(k+' = '+json.dumps(v) for k,v in values.items())+'\n')
Path('streamlit-aws-secrets.toml').chmod(0o600)
PY
printf '\nSetup complete. Public identifiers only:\n'
printf 'AWS_ROLE_ARN=arn:aws:iam::%s:role/%s\n' "$ACCOUNT_ID" "$WRITER"
printf 'AWS_REGION=%s\nAUSTIN_S3_BUCKET=%s\n' "$REGION" "$BUCKET"
printf '\nPRIVATE reader credentials saved in: %s/streamlit-aws-secrets.toml\n' "$SETUP_DIR"
printf 'Download that file privately using CloudShell Actions > Download file. Append its contents to Streamlit Secrets. Never paste it into chat or GitHub.\n'
printf 'This setup does not establish snapshot publication, scheduled execution, or successful app restoration. Verify those next.\n'
