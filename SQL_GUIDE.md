# SQLite data pipeline

This extension adds persistent storage and SQL analysis to the existing CSV workflow.
It does not fetch APIs, retrain the scoring model, or validate investment predictions.
Use it to explain relational modeling, repeatable imports, data quality checks,
SQL joins and aggregation, and historical comparisons in an interview.

## Run the offline example

From the repository root, use Python 3.10 or newer. The command-line importer and
reports use only Python's standard library. Install the smaller dashboard dependencies
if you want the interface:

```bash
python -m pip install -r requirements-sql.txt
python sql_pipeline.py --db data/austin_demo.db import examples/sql_demo/snapshot_day1.csv --observed-on 2026-10-01 --source-kind synthetic
python sql_pipeline.py --db data/austin_demo.db import examples/sql_demo/snapshot_day1.csv --observed-on 2026-10-01 --source-kind synthetic
python sql_pipeline.py --db data/austin_demo.db import examples/sql_demo/snapshot_day2.csv --observed-on 2026-10-02 --source-kind synthetic
python sql_pipeline.py --db data/austin_demo.db report rankings
python sql_pipeline.py --db data/austin_demo.db report history --zip-code 78701
python sql_pipeline.py --db data/austin_demo.db report coverage
python sql_pipeline.py --db data/austin_demo.db audit
```

Expected results: the first run inserts three observations; the repeated run inserts
zero and reports three unchanged rows. The second date adds two observations, for
five observations across three ZIP areas. ZIP 78701's score changes from 75 to 78;
ZIP 78703 is absent from the second date but still appears in the coverage report.
These CSV values are **synthetic test fixtures**, not Austin market measurements.
Use a separate demo database to keep them apart from your own observations.

Launch the SQL Explorer on macOS/Linux:

```bash
AUSTIN_DB_PATH=data/austin_demo.db streamlit run sql_dashboard.py
```

In PowerShell:

```powershell
$env:AUSTIN_DB_PATH="data/austin_demo.db"
python -m streamlit run sql_dashboard.py
```

The interface offers score/price filters, cluster summaries, dated history, coverage,
CSV export, readable SQL, and import/rejection logs. It displays a notice for synthetic
imports. It reads the database on each rerun, so the Refresh results button picks up changes.

## Import your existing analysis

Run the original collection and analysis workflow using your own local files and API
configuration. Its output is not checked into Git. Then import the processed CSV:

```bash
python sql_pipeline.py import data/processed/neighborhoods_professional.csv --observed-on 2026-10-18
python sql_pipeline.py report rankings --min-score 70 --max-price 600000
python sql_pipeline.py report cluster_summary
```

Replace the example date with the date represented by the input snapshot. It is not
automatically the date of the underlying API measurements: inputs can contain older
data and estimates. `user-provided` means an imported file, not independently verified data.

Required columns are `zip_code` and `investment_score` (a finite number from 0 to 100).
Optional typed columns are `neighborhood_name`, `median_home_value`, `business_count`,
`confidence_score`, and `cluster`. Additional original columns are preserved for the
existing dashboard. Numeric columns accept decimal values without currency formatting.
Missing prices remain NULL, zero businesses remains zero, and missing names use `ZIP #####`.
ZIP+4 and five-digit float artifacts such as `78701.0` are normalized. No neighborhood
name matching is used to guess ZIP codes. ZIP areas are not exact neighborhood boundaries.

To opt the existing professional dashboard into SQLite instead of CSV:

```bash
AUSTIN_DATA_BACKEND=sqlite streamlit run professional_dashboard.py
```

It expects a full processed professional CSV, with the same columns required by that
dashboard before this extension. The small demo fixture is for `sql_dashboard.py` only.
The original CSV backend remains the default; the SQL Explorer is an additional entry point.

## Import behavior and failure handling

- The observation key is `(zip_code, observed_on)`. Reimporting identical records does
  not add observations. Correcting the same ZIP/date updates that record; another date
  creates a historical observation. Import audit runs are intentionally retained.
- Each import stores its filename, SHA-256, source kind, date, and row counts.
- Exact repeated rows within a file are counted and skipped. Conflicting duplicate ZIPs
  are validation errors. With explicit partial import, the first valid occurrence wins.
- Invalid ZIPs, missing/nonfinite/out-of-range scores, nonpositive prices, invalid
  confidence scores, and negative/fractional business counts are rejected.
- By default, any invalid row rejects the whole batch and retains the validation issues
  in the audit tables. CLI exit status is 2. Existing observations remain unchanged.
- `--skip-invalid` explicitly allows valid rows to load while recording rejected rows.
  An all-invalid file is still rejected. Empty files, bad headers, missing files, and
  bad dates fail before a run is recorded.
- A write exception rolls back the entire transaction. Mixing synthetic and user-provided
  records for the same ZIP/date raises an error and rolls back that attempted run.
- Missing source files fail clearly; the importer does not substitute synthetic or live
  data. Recovery is to fix the source and rerun the same date, or import a different date.
- Imports upsert supplied areas; absence does not delete prior rows for that same date.
  Use a distinct date for each intended snapshot and the coverage report to inspect gaps.

## Relational structure and SQL

`neighborhoods` holds ZIP identities and their most recently imported display name.
`observations` holds dated scores/metrics and the original payload, linked to an
`import_runs` audit row. `validation_issues` records invalid source line numbers.
Foreign keys and CHECK constraints enforce integrity. A date/score index supports
snapshot filtering and ordering. Queries are parameterized.

| SQL file | Demonstrates |
| --- | --- |
| `sql/rankings.sql` | JOIN across three tables, filtering, subquery, deterministic ordering |
| `sql/cluster_summary.sql` | GROUP BY, AVG, COUNT(column), explicit missing-price coverage |
| `sql/history.sql` | LAG window function and changes between available dates |
| `sql/coverage.sql` | LEFT JOIN retaining areas with zero matches on the selected date |

Typed metrics support SQL comparisons. The extra JSON payload preserves the original
dashboard's changing feature columns; it is not a replacement for a fully normalized
model of every upstream API record. Ranking scores and any estimated prices retain
the limitations of the original pipeline.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests cover repeat imports, corrections, dated history, missing values, duplicate handling,
strict/partial rejection, transaction rollback, constraints, SQL filters and aggregation,
parameter binding, CLI exit codes, and preservation of extra dashboard columns.
Only the DataFrame compatibility test requires pandas; CLI/storage do not.

## Explain it in an interview

1. CSV outputs were difficult to compare across runs. SQLite now stores dated observations
   and import provenance with explicit keys and constraints.
2. Python validates records before writing. SQL UPSERT makes reruns safe, and a transaction
   prevents partially applied changes when a write fails.
3. SQL handles joins, grouped comparisons, coverage checks, and historical deltas.
4. The Streamlit page displays those query results, plus the SQL and import logs.
5. The offline example proves behavior, not real-world prediction accuracy or performance at scale.

Read the code and run the example before describing this extension in an interview.
Measure any performance claim against your own full dataset before adding it to a résumé.

References: [Python sqlite3](https://docs.python.org/3/library/sqlite3.html),
[SQLite UPSERT](https://www.sqlite.org/lang_upsert.html),
[SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).
