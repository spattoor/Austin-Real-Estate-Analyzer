"""Explore imported snapshots with named SQL queries. Run: streamlit run sql_dashboard.py"""
import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data.sqlite_store import DEFAULT_DB, SQL_DIR, audit, report

st.set_page_config(page_title='Austin SQL Explorer', layout='wide')
st.title('Austin SQL Explorer')
st.caption('Compare imported ZIP-area snapshots and inspect data coverage and import results.')
database = Path(os.environ.get('AUSTIN_DB_PATH', DEFAULT_DB))
st.sidebar.caption('Database: ' + str(database))
st.sidebar.button('Refresh results')
if not database.is_file():
    st.info('Import a CSV with sql_pipeline.py first. See SQL_GUIDE.md for the sample and your own data.')
    st.stop()

try:
    logs = audit(database)
    if not logs['runs']:
        st.info('No import runs yet.')
        st.stop()
    if any(r['source_kind'] == 'synthetic' for r in logs['runs']):
        st.warning('This database includes synthetic demonstration imports. These values are not market observations.')
    dates = sorted({r['observed_on'] for r in logs['runs'] if r['status'] == 'completed'}, reverse=True)
    if not dates:
        st.error('No completed import is available. Review rejected rows in Import history.')
        st.dataframe(pd.DataFrame(logs['issues']), width='stretch')
        st.stop()
    observed_on = st.sidebar.selectbox('Snapshot date', dates)
    min_score = st.sidebar.slider('Minimum score', 0, 100, 0)
    price_filter = st.sidebar.checkbox('Filter by maximum home value')
    max_price = st.sidebar.number_input('Maximum home value', min_value=1, value=600000) if price_filter else None
    table = pd.DataFrame(report('rankings', database, observed_on=observed_on,
                                min_score=min_score, max_price=max_price))
    rankings, clusters, history, coverage, imports = st.tabs(
        ['Comparisons', 'Clusters', 'History', 'Data coverage', 'Import history'])
    with rankings:
        st.caption('Scores come from the imported analysis. SQL does not establish predictive accuracy.')
        st.dataframe(table, width='stretch')
        st.download_button('Download comparison CSV', table.to_csv(index=False), 'sql_comparisons.csv', 'text/csv')
        with st.expander('View SQL'):
            st.code((SQL_DIR / 'rankings.sql').read_text(), language='sql')
    with clusters:
        st.dataframe(pd.DataFrame(report('cluster_summary', database, observed_on=observed_on)), width='stretch')
        with st.expander('View SQL'):
            st.code((SQL_DIR / 'cluster_summary.sql').read_text(), language='sql')
    with history:
        choices = report('coverage', database, observed_on=observed_on)
        selected_zip = st.selectbox('ZIP area', [r['zip_code'] for r in choices])
        timeline = pd.DataFrame(report('history', database, zip_code=selected_zip))
        st.dataframe(timeline, width='stretch')
        if not timeline.empty:
            st.line_chart(timeline.set_index('observed_on')['investment_score'])
        with st.expander('View SQL'):
            st.code((SQL_DIR / 'history.sql').read_text(), language='sql')
    with coverage:
        st.caption('Missing values remain missing. Areas absent from this date remain visible through a LEFT JOIN.')
        st.dataframe(pd.DataFrame(choices), width='stretch')
        with st.expander('View SQL'):
            st.code((SQL_DIR / 'coverage.sql').read_text(), language='sql')
    with imports:
        st.dataframe(pd.DataFrame(logs['runs']), width='stretch')
        st.write('Rejected rows')
        st.dataframe(pd.DataFrame(logs['issues']), width='stretch')
except (OSError, ValueError, sqlite3.Error) as exc:
    st.error('Could not read the SQLite analysis: ' + str(exc))
