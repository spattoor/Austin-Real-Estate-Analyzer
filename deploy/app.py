"""Streamlit entrypoint. Select this file in Community Cloud; requirements live beside it."""
import json
import os
import sqlite3
import sys
import tempfile
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from portfolio.ai import AIUnavailable, explain, facts_for

st.set_page_config(page_title='Austin | Market Explorer', page_icon='🏙️', layout='wide')


def setting(name, default=''):
    if os.environ.get(name):
        return os.environ[name]
    try:
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


@st.cache_data(ttl=300)
def cloud_snapshot(bucket):
    # boto3 reads AWS credentials from environment variables or its default credential chain.
    from portfolio.snapshot import restore
    return str(restore(Path(tempfile.gettempdir()) / 'austin-snapshots', bucket=bucket))


bucket = setting('AUSTIN_S3_BUCKET')
for name in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'AWS_DEFAULT_REGION']:
    value = setting(name)
    if value:
        os.environ[name] = value
try:
    database = Path(cloud_snapshot(bucket)) if bucket else Path(setting('AUSTIN_DB_PATH', str(ROOT/'deploy/data/austin.db')))
    with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as con:
        frame = pd.read_sql_query('SELECT * FROM market_observations', con)
        metadata = json.loads(con.execute('SELECT json FROM snapshot_metadata').fetchone()[0])
except Exception:
    st.error('A published snapshot could not be loaded. Run the refresh command or check the private S3 reader configuration.')
    st.stop()

st.caption('AUSTIN, TEXAS · HOUSING DATA PORTFOLIO')
st.title('A clearer view of Austin’s housing market')
st.write('Compare ZIP areas using historical home values, transparent scores, and machine learning clusters.')
st.info('Research demo: comparison scores summarize historical data. They do not predict returns or recommend a purchase.')
if metadata.get('source_kind') != 'observed':
    st.warning('Synthetic demonstration data. These values are not market observations.')

dates = sorted(frame.observed_on.unique(), reverse=True)
month = st.sidebar.selectbox('Snapshot month', dates)
latest = frame[frame.observed_on == month].copy()
max_price = st.sidebar.slider('Maximum typical home value', 100000, 3000000, 3000000, 50000, format='$%d')
min_score = st.sidebar.slider('Minimum comparison score', 0, 100, 0)
include_missing = st.sidebar.checkbox('Include areas without a complete score', value=True)
visible = latest[(latest.zhvi <= max_price) & ((latest.comparison_score >= min_score) |
                 (latest.comparison_score.isna() & include_missing))].sort_values('comparison_score', ascending=False)

a, b, c = st.columns(3)
a.metric('ZIP areas in snapshot', latest.zip_code.nunique())
b.metric('Median typical home value', f'${latest.zhvi.median():,.0f}')
c.metric('Median 1-year value change', f'{latest.change_1y_pct.median():+.2f}%')
st.caption(f'Source observation: {month} · Retrieved: {metadata.get("retrieved_at", "unknown")} · '
           + ('Private S3 snapshot' if bucket else 'Bundled snapshot'))
if (date.today() - date.fromisoformat(month)).days > 90:
    st.warning('This source observation is more than 90 days old. Check the refresh pipeline before using it as a current comparison.')

comparison, detail, method, provenance = st.tabs(['Compare areas', 'Explore & explain', 'Methodology', 'Sources & audit'])
with comparison:
    if visible.empty:
        st.info('No ZIP areas match these filters. Increase the price limit or lower the minimum score.')
    else:
        st.dataframe(visible[['zip_code', 'zhvi', 'change_1y_pct', 'change_3y_pct', 'comparison_score', 'cluster']],
                     hide_index=True, width='stretch', column_config={
                         'zhvi': st.column_config.NumberColumn('Typical home value (ZHVI)', format='$%.0f'),
                         'change_1y_pct': st.column_config.NumberColumn('1-year change %', format='%.2f'),
                         'change_3y_pct': st.column_config.NumberColumn('3-year change %', format='%.2f'),
                         'comparison_score': st.column_config.NumberColumn('Comparison /100', format='%.1f')})
        st.bar_chart(visible.head(15).set_index('zip_code')['comparison_score'])
        st.download_button('Download this comparison', visible.to_csv(index=False), 'austin-comparison.csv', 'text/csv')

with detail:
    selected = st.selectbox('Choose a ZIP area', sorted(latest.zip_code.unique()))
    row = latest[latest.zip_code == selected].iloc[0].to_dict()
    row = {k: None if pd.isna(v) else v for k, v in row.items()}
    st.line_chart(frame[frame.zip_code == selected].sort_values('observed_on').set_index('observed_on')['zhvi'])
    st.subheader('Verified facts')
    for fact in facts_for(row).values():
        st.write('• ' + fact)
    if row.get('comparison_score') is None:
        st.warning('A growth period is missing. This area has no comparison score or cluster.')
    st.subheader('AI-assisted explanation')
    st.caption('Gemini selects relevant evidence. Python displays the exact supplied values. No generated price forecasts.')
    question = st.text_input('Ask about these metrics', 'Explain the comparison score', max_chars=300)
    if st.button('Explain using verified data'):
        try:
            with st.spinner('Selecting relevant evidence…'):
                result = explain(row, question, api_key=setting('GEMINI_API_KEY'),
                                 model=setting('GEMINI_MODEL', 'gemini-3.5-flash-lite'))
            if result['supported']:
                st.success('AI response verified against the available metric IDs')
                for fact in result['facts']:
                    st.write('• ' + fact)
            else:
                st.info('This dataset cannot answer that question. Ask about historical home values or the comparison score.')
            st.caption(f'{result["provider"]} · {result["model_version"]} · Source: {result["source_id"]} · '
                       f'Date: {result["observed_on"]}' + (' · Cached' if result['cached'] else ''))
            st.download_button('Download AI verification record', json.dumps(result, indent=2), 'ai-verification.json')
        except AIUnavailable as exc:
            st.warning(str(exc))
            st.caption('No AI answer was generated. The verified facts above remain available.')

with method:
    st.subheader('A descriptive score you can inspect')
    st.write('Score = 40% lower-price percentile + 35% one-year change percentile + 25% three-year change percentile. '
             'Percentiles compare all available Austin ZIP areas within the selected month. The weights are a design choice, not a trained forecast.')
    st.write('Change = (current ZHVI / ZHVI at the exact earlier month − 1) × 100. Missing months remain missing. '
             'An area needs both growth periods for a score. ZHVI is a modeled typical home value, not a listing price or median transaction price.')
    st.write('K-Means groups standardized home values and historical changes into three clusters. Cluster IDs are local to each snapshot '
             'and have no quality order. This deployment path preserves the original Yelp analysis files and uses a separate Zillow-only methodology.')
    st.write('This dataset does not establish rental yield, crime, school quality, future appreciation, or investment-return accuracy.')

with provenance:
    st.markdown('Data: [Zillow Research — ZHVI](https://www.zillow.com/research/data/). Geographic scope: Zillow rows with City=Austin and State=TX.')
    st.json(metadata)
    st.write('Available source months:', ', '.join(dates))
    st.markdown('[View source code](https://github.com/spattoor/Austin-Real-Estate-Analyzer)')
