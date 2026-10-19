PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS import_runs (
    run_id INTEGER PRIMARY KEY,
    started_at TEXT NOT NULL,
    source_file TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    source_kind TEXT NOT NULL CHECK (source_kind IN ('user-provided', 'synthetic')),
    observed_on TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'rejected')),
    input_rows INTEGER NOT NULL DEFAULT 0,
    inserted_rows INTEGER NOT NULL DEFAULT 0,
    updated_rows INTEGER NOT NULL DEFAULT 0,
    unchanged_rows INTEGER NOT NULL DEFAULT 0,
    duplicate_rows INTEGER NOT NULL DEFAULT 0,
    rejected_rows INTEGER NOT NULL DEFAULT 0
);

-- ZIP areas are the existing project's unit of analysis, not exact neighborhood boundaries.
CREATE TABLE IF NOT EXISTS neighborhoods (
    zip_code TEXT PRIMARY KEY CHECK (length(zip_code) = 5 AND zip_code NOT GLOB '*[^0-9]*'),
    neighborhood_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS observations (
    zip_code TEXT NOT NULL REFERENCES neighborhoods(zip_code),
    observed_on TEXT NOT NULL,
    run_id INTEGER NOT NULL REFERENCES import_runs(run_id),
    investment_score REAL NOT NULL CHECK (investment_score BETWEEN 0 AND 100),
    median_home_value REAL CHECK (median_home_value > 0),
    business_count INTEGER CHECK (business_count >= 0),
    confidence_score REAL CHECK (confidence_score BETWEEN 0 AND 100),
    cluster TEXT,
    -- Preserve the existing dashboard's additional columns without inventing data.
    payload_json TEXT NOT NULL,
    PRIMARY KEY (zip_code, observed_on)
);

CREATE INDEX IF NOT EXISTS idx_observations_date_score
    ON observations(observed_on, investment_score DESC);
CREATE INDEX IF NOT EXISTS idx_observations_run ON observations(run_id);

CREATE TABLE IF NOT EXISTS validation_issues (
    issue_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES import_runs(run_id),
    csv_row INTEGER NOT NULL,
    reason TEXT NOT NULL
);
