"""Checksum-verified public snapshots through CloudFront, without client AWS keys."""
import re
from urllib.parse import urlsplit

import requests

from portfolio.snapshot import restore


class _ResponseBody:
    def __init__(self, response):
        self.response = response

    def read(self, size=-1):
        return self.response.raw.read(size, decode_content=True)

    def close(self):
        self.response.close()


class CloudFrontSnapshotStore:
    def __init__(self, base_url, session=None):
        parsed = urlsplit(base_url)
        if (parsed.scheme != 'https' or
                not re.fullmatch(r'[a-z0-9-]+\.cloudfront\.net', parsed.netloc) or
                parsed.path not in ('', '/') or parsed.query or parsed.fragment):
            raise ValueError('Snapshot URL must be an HTTPS CloudFront distribution root')
        self.base_url = base_url.rstrip('/')
        self.session = session or requests

    def get_object(self, *, Bucket, Key):
        if Key != 'latest.json' and not re.fullmatch(r'snapshots/[a-f0-9]{64}\.db', Key):
            raise ValueError('Unexpected snapshot object path')
        response = self.session.get(self.base_url + '/' + Key, stream=True,
                                    timeout=(5, 20), allow_redirects=False)
        if response.status_code != 200:
            response.close()
            raise ValueError('Published snapshot request did not return HTTP 200')
        return {'Body': _ResponseBody(response)}


def restore_https(directory, base_url, session=None):
    # Reuse the manifest bounds, 50 MiB DB limit, SHA-256 verification, atomic
    # replacement, and SQLite validation of the existing S3 restoration path.
    return restore(directory, s3=CloudFrontSnapshotStore(base_url, session),
                   bucket='cloudfront-snapshot')
