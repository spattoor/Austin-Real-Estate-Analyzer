"""Optional UI tests run when requirements-sql.txt is installed."""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.data.sqlite_store import import_csv

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('streamlit'), 'Install requirements-sql.txt for UI tests')
class DashboardTests(unittest.TestCase):
    def test_filters_and_synthetic_notice(self):
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/'demo.db'
            import_csv(ROOT/'examples/sql_demo/snapshot_day1.csv', db, '2026-10-01', 'synthetic')
            import_csv(ROOT/'examples/sql_demo/snapshot_day2.csv', db, '2026-10-02', 'synthetic')
            with patch.dict(os.environ, {'AUSTIN_DB_PATH': str(db)}):
                app = AppTest.from_file(str(ROOT/'sql_dashboard.py')).run(timeout=30)
                self.assertFalse(app.exception)
                self.assertEqual(len(app.tabs), 5)
                self.assertEqual(len(app.warning), 1)
                self.assertEqual(len(app.dataframe[0].value), 2)
                app.slider[0].set_value(80).run()
                self.assertEqual(len(app.dataframe[0].value), 1)
                app.checkbox[0].check().run()
                app.number_input[0].set_value(450000).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.dataframe[0].value), 0)

    def test_missing_database_is_explained(self):
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {'AUSTIN_DB_PATH': str(Path(tmp)/'missing.db')}):
                app = AppTest.from_file(str(ROOT/'sql_dashboard.py')).run(timeout=30)
                self.assertFalse(app.exception)
                self.assertEqual(len(app.info), 1)
