import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
from portfolio import ai, data, snapshot


class AITests(unittest.TestCase):
    def setUp(self):
        ai._calls.clear()
        ai._cache.clear()
        self.row = {'zhvi': 400000., 'change_1y_pct': -2., 'change_3y_pct': None,
                    'comparison_score': None, 'observed_on': '2026-09-30', 'source_id': data.SOURCE_ID}

    def response(self, value):
        r = Mock(status_code=200, content=b'{}')
        r.json.return_value = {'modelVersion': 'test-model', 'candidates': [
            {'content': {'parts': [{'text': json.dumps(value)}]}}]}
        return r

    @patch('portfolio.ai.requests.post')
    def test_normal_evidence_and_cache(self, post):
        post.return_value = self.response({'supported': True, 'metric_ids': ['zhvi', 'change_1y_pct']})
        result = ai.explain(self.row, api_key='test-only')
        self.assertEqual(result['status'], 'ai')
        self.assertIn('$400,000', result['facts'][0])
        self.assertEqual(result['model_version'], 'test-model')
        self.assertTrue(ai.explain(self.row, api_key='test-only')['cached'])
        self.assertEqual(post.call_count, 1)

    @patch('portfolio.ai.requests.post')
    def test_unsupported_question(self, post):
        post.return_value = self.response({'supported': False, 'metric_ids': []})
        result = ai.explain(self.row, 'Will this double in value?', api_key='test-only')
        self.assertFalse(result['supported'])
        self.assertEqual(result['facts'], [])

    @patch('portfolio.ai.requests.post')
    def test_malformed_or_invented_evidence_is_rejected(self, post):
        for selection in [{'supported': True, 'metric_ids': ['change_3y_pct']},
                          {'supported': True, 'metric_ids': ['invented_roi']},
                          {'supported': True, 'metric_ids': ['zhvi'], 'claim': 'Buy now'},
                          {'supported': False, 'metric_ids': ['zhvi']}]:
            post.return_value = self.response(selection)
            with self.assertRaises(ai.AIUnavailable):
                ai.explain(self.row, api_key='test-only')
            ai._calls.clear()

    @patch('portfolio.ai.requests.post')
    def test_provider_failure_and_missing_key(self, post):
        post.return_value = Mock(status_code=429)
        with self.assertRaises(ai.AIUnavailable):
            ai.explain(self.row, api_key='test-only')
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ai.AIUnavailable):
                ai.explain(self.row)


class PipelineTests(unittest.TestCase):
    def test_missing_growth_is_not_imputed_or_scored(self):
        frame = pd.DataFrame({'zhvi': [400000, 500000, 600000, 700000],
                              'change_1y_pct': [1., 2., -1., None],
                              'change_3y_pct': [3., 4., 5., 6.]})
        scored = data.score(frame)
        self.assertTrue(pd.isna(scored.iloc[-1].comparison_score))
        self.assertTrue(pd.isna(scored.iloc[-1].cluster))
        self.assertEqual(scored.iloc[:3].cluster.nunique(), 3)
        self.assertTrue(scored.iloc[:3].comparison_score.between(0, 100).all())

    def test_exact_month_growth_and_null_history(self):
        months = pd.date_range('2023-01-31', periods=37, freq='ME').strftime('%Y-%m-%d').tolist()
        row = {'RegionName': '78701', **{m: 100. for m in months}}
        row[months[-1]] = 120.
        row[months[-13]] = None
        result = data.features(pd.DataFrame([row]), months, months[-1]).iloc[0]
        self.assertAlmostEqual(result.change_3y_pct, 20.)
        self.assertTrue(pd.isna(result.change_1y_pct))


class MemoryS3:
    def __init__(self):
        self.objects = {}
    def put_object(self, Bucket, Key, Body, **kwargs):
        self.objects[Key] = Body.read() if hasattr(Body, 'read') else Body
    def get_object(self, Bucket, Key):
        return {'Body': io.BytesIO(self.objects[Key])}


class SnapshotTests(unittest.TestCase):
    def test_restore_after_local_cache_deletion_and_reject_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            db, raw = base/'source.db', base/'raw.csv'
            raw.write_text('test fixture,not real market data\n')
            with sqlite3.connect(db) as con:
                con.execute('CREATE TABLE market_observations(zip_code TEXT, observed_on TEXT)')
                con.execute("INSERT INTO market_observations VALUES ('78701','2026-09-30')")
            s3 = MemoryS3()
            snapshot.publish(db, raw, s3=s3, bucket='fixture')
            restored = snapshot.restore(base/'cache', s3=s3, bucket='fixture')
            self.assertEqual(restored.read_bytes(), db.read_bytes())
            restored.unlink()
            self.assertTrue(snapshot.restore(base/'cache', s3=s3, bucket='fixture').exists())
            restored.unlink()
            key = json.loads(s3.objects['latest.json'])['database_key']
            s3.objects[key] = b'corrupt'
            with self.assertRaisesRegex(ValueError, 'checksum'):
                snapshot.restore(base/'cache', s3=s3, bucket='fixture')


class UITests(unittest.TestCase):
    def test_real_snapshot_dashboard_and_no_key_failure(self):
        from streamlit.testing.v1 import AppTest
        root = Path(__file__).resolve().parents[1]
        if not (root/'deploy/data/austin.db').exists():
            self.skipTest('Run refresh to build a source snapshot first')
        with patch.dict('os.environ', {'GEMINI_API_KEY': '', 'AUSTIN_S3_BUCKET': ''}):
            app = AppTest.from_file(str(root/'deploy/app.py')).run(timeout=30)
            self.assertFalse(app.exception)
            self.assertEqual(len(app.tabs), 4)
            self.assertGreater(app.dataframe[0].value.shape[0], 0)
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any('not configured' in w.value for w in app.warning))


if __name__ == '__main__':
    unittest.main()
