import csv
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.data.sqlite_store import audit, connect, import_csv, load_snapshot, load_snapshot_frame, report

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.db = self.directory / 'analysis.db'
        self.csv = self.directory / 'input.csv'

    def write(self, rows):
        fields = ['zip_code', 'neighborhood_name', 'investment_score', 'median_home_value',
                  'business_count', 'confidence_score', 'cluster', 'extra_metric']
        with self.csv.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def row(self, zip_code='78701', score='75', **extra):
        return dict(zip_code=zip_code, neighborhood_name='Area '+zip_code,
                    investment_score=score, **extra)

    def load(self, day='2026-10-01', **kwargs):
        return import_csv(self.csv, self.db, day, **kwargs)

    def test_repeat_and_correction_preserve_one_observation(self):
        self.write([self.row(median_home_value='500000')])
        self.assertEqual(self.load()['inserted_rows'], 1)
        self.assertEqual(self.load()['unchanged_rows'], 1)
        self.write([self.row(score='81', median_home_value='510000')])
        self.assertEqual(self.load()['updated_rows'], 1)
        self.assertEqual(len(load_snapshot(self.db)), 1)
        self.assertEqual(report('rankings', self.db)[0]['investment_score'], 81)
        self.assertEqual(len(audit(self.db)['runs']), 3)

    def test_history_window_and_coverage_keep_absent_area(self):
        self.write([self.row(median_home_value='500000'), self.row('78702', '65')])
        self.load()
        self.write([self.row(score='80', median_home_value='510000')])
        self.load('2026-10-02')
        history = report('history', self.db, zip_code='78701')
        self.assertIsNone(history[0]['score_change'])
        self.assertEqual(history[1]['score_change'], 5)
        self.assertEqual(history[1]['home_value_change'], 10000)
        coverage = report('coverage', self.db)
        self.assertEqual(coverage[1]['observations_on_date'], 0)
        self.assertEqual(coverage[1]['price_coverage'], 'Absent')
        self.assertEqual(len(load_snapshot(self.db)), 1)

    def test_strict_rejection_is_atomic_and_records_reasons(self):
        self.write([self.row()])
        self.load()
        self.write([self.row(score='90'), self.row('oops', '80')])
        result = self.load()
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['rejected_rows'], 1)
        self.assertEqual(report('rankings', self.db)[0]['investment_score'], 75)
        self.assertEqual(len(audit(self.db)['issues']), 1)

    def test_explicit_partial_import_and_exact_duplicates(self):
        row = self.row()
        self.write([row, row, self.row('78702', 'inf')])
        result = self.load(skip_invalid=True)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['duplicate_rows'], 1)
        self.assertEqual(result['rejected_rows'], 1)
        self.assertEqual(result['inserted_rows'], 1)

    def test_conflicting_duplicates_reject_batch(self):
        self.write([self.row(), self.row(score='80')])
        self.assertEqual(self.load()['status'], 'rejected')
        self.assertEqual(load_snapshot(self.db), [])

    def test_normalization_nulls_and_dataframe_extra_columns(self):
        self.write([self.row('78701.0', '0', business_count='0', extra_metric='1.25'),
                    self.row('02108-1234', '100')])
        self.load()
        frame = load_snapshot_frame(self.db)
        self.assertEqual(set(frame.zip_code), {'78701', '02108'})
        self.assertEqual(frame.loc[frame.zip_code == '78701', 'extra_metric'].iloc[0], 1.25)
        rows = report('rankings', self.db)
        self.assertIsNone(rows[0]['median_home_value'])
        self.assertEqual(rows[1]['business_count'], 0)

    def test_invalid_numbers_are_rejected(self):
        for extra in [dict(score='NaN'), dict(score='101'), dict(median_home_value='-1'),
                      dict(confidence_score='101'), dict(business_count='1.5')]:
            with self.subTest(extra=extra):
                self.write([self.row(**extra)])
                self.assertEqual(self.load()['status'], 'rejected')

    def test_foreign_keys_and_unique_key_are_enforced(self):
        self.write([self.row()])
        self.load()
        with connect(self.db) as con:
            self.assertEqual(con.execute('PRAGMA foreign_keys').fetchone()[0], 1)
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute('DELETE FROM neighborhoods')
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute('INSERT INTO observations SELECT * FROM observations')

    def test_grouped_averages_preserve_missing_price_and_filters(self):
        self.write([self.row(cluster='1', median_home_value='500000'),
                    self.row('78702', '65', cluster='1')])
        self.load()
        grouped = report('cluster_summary', self.db)[0]
        self.assertEqual(grouped['area_count'], 2)
        self.assertEqual(grouped['areas_with_price'], 1)
        self.assertEqual(grouped['average_score'], 70)
        self.assertEqual(grouped['average_home_value'], 500000)
        self.assertEqual(len(report('rankings', self.db, max_price=600000)), 1)
        self.assertEqual(report('rankings', self.db, min_score=90), [])
        self.assertEqual(report('history', self.db, zip_code="78701' OR 1=1 --"), [])

    def test_source_kind_collision_rolls_back_all_changes(self):
        self.write([self.row()])
        self.load(source_kind='synthetic')
        self.write([self.row('78702'), self.row(score='90')])
        with self.assertRaises(ValueError):
            self.load()
        self.assertEqual(len(load_snapshot(self.db)), 1)
        self.assertEqual(len(audit(self.db)['runs']), 1)

    def test_missing_files_headers_and_dates_do_not_mutate_database(self):
        self.csv.write_text('bad,headers\n1,2\n')
        with self.assertRaises(ValueError):
            self.load()
        self.assertFalse(self.db.exists())
        self.write([self.row()])
        with self.assertRaises(ValueError):
            self.load('not-a-date')
        with self.assertRaises(FileNotFoundError):
            import_csv(self.directory/'missing.csv', self.db, '2026-10-01')
        self.assertFalse(self.db.exists())

    def test_cli_import_report_and_rejection_exit_code(self):
        self.write([self.row()])
        base = [sys.executable, str(ROOT/'sql_pipeline.py'), '--db', str(self.db)]
        loaded = subprocess.run(base+['import', str(self.csv), '--observed-on', '2026-10-01'],
                                capture_output=True, text=True)
        self.assertEqual(loaded.returncode, 0, loaded.stderr)
        queried = subprocess.run(base+['report', 'rankings'], capture_output=True, text=True)
        self.assertEqual(queried.returncode, 0, queried.stderr)
        self.assertIn('78701', queried.stdout)
        self.write([self.row(score='bad')])
        rejected = subprocess.run(base+['import', str(self.csv), '--observed-on', '2026-10-01'],
                                  capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 2)


if __name__ == '__main__':
    unittest.main()
