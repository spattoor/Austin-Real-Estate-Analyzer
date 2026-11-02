import hashlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from portfolio.https_snapshot import CloudFrontSnapshotStore, restore_https


class Response:
    status_code = 200

    def __init__(self, content):
        self.raw = Mock()
        self.raw.read.side_effect = lambda size=-1, decode_content=True: self.body.read(size)
        self.body = io.BytesIO(content)
        self.closed = False

    def close(self):
        self.closed = True
        self.body.close()


class HTTPRestoreTests(unittest.TestCase):
    def test_restoration_validates_data_and_reuses_verified_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/'original.db'
            with sqlite3.connect(db) as con:
                con.execute('CREATE TABLE market_observations(zip_code TEXT, observed_on TEXT)')
                con.execute("INSERT INTO market_observations VALUES ('78701','2026-09-30')")
            content = db.read_bytes()
            checksum = hashlib.sha256(content).hexdigest()
            manifest = json.dumps({'schema_version':1, 'sha256':checksum,
                                   'database_key':f'snapshots/{checksum}.db'}).encode()
            responses = [Response(manifest), Response(content), Response(manifest)]
            session = Mock()
            session.get.side_effect = responses
            target = restore_https(Path(tmp)/'restored', 'https://example.cloudfront.net', session)
            self.assertEqual(target.read_bytes(), content)
            self.assertEqual(restore_https(Path(tmp)/'restored', 'https://example.cloudfront.net', session), target)
            self.assertEqual(session.get.call_count, 3)
            self.assertTrue(all(r.closed for r in responses))
            self.assertEqual(session.get.call_args.kwargs['allow_redirects'], False)

    def test_rejects_untrusted_urls_and_object_paths(self):
        for url in ['http://example.cloudfront.net', 'https://evil.example',
                    'https://example.cloudfront.net/extra',
                    'https://name@example.cloudfront.net',
                    'https://example.cloudfront.net?redirect=x']:
            with self.assertRaises(ValueError):
                CloudFrontSnapshotStore(url)
        store = CloudFrontSnapshotStore('https://example.cloudfront.net')
        for key in ['../secret', 'raw/source.csv', '/latest.json', 'snapshots/not-a-hash.db']:
            with self.assertRaises(ValueError):
                store.get_object(Bucket='unused', Key=key)

    def test_redirect_or_error_is_rejected_and_closed(self):
        response = Response(b'unused')
        response.status_code = 302
        session = Mock()
        session.get.return_value = response
        with self.assertRaises(ValueError):
            CloudFrontSnapshotStore('https://example.cloudfront.net', session).get_object(Bucket='unused', Key='latest.json')
        self.assertTrue(response.closed)

    def test_corruption_is_not_published_as_a_cache_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            checksum = 'a'*64
            manifest = json.dumps({'schema_version':1, 'sha256':checksum,
                                   'database_key':f'snapshots/{checksum}.db'}).encode()
            responses = [Response(manifest), Response(b'corrupt')]
            session = Mock()
            session.get.side_effect = responses
            target = Path(tmp)/'restored'
            with self.assertRaises(ValueError):
                restore_https(target, 'https://example.cloudfront.net', session)
            self.assertFalse(list(target.iterdir()))
            self.assertTrue(all(r.closed for r in responses))


if __name__ == '__main__':
    unittest.main()
