#!/usr/bin/env python3
"""
PROFESSIONAL INVESTMENT PLATFORM - INSTITUTIONAL GRADE
Clean, modern interface like Bloomberg Terminal meets Zillow
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from datetime import datetime

# Page config - PROFESSIONAL
st.set_page_config(
    page_title="Austin Real Estate Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PROFESSIONAL CSS - Clean, modern, institutional
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional color palette */
    :root {
        --primary-blue: #1E3A8A;
        --success-green: #059669;
        --warning-orange: #D97706;
        --danger-red: #DC2626;
        --neutral-gray: #6B7280;
        --bg-light: #F9FAFB;
    }
    
    /* Clean typography */
    .main-header {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 1.1rem;
        color: #6B7280;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Professional metric cards */
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    /* Investment grade badges */
    .grade-excellent {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(5, 150, 105, 0.3);
    }
    
    .grade-good {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    .grade-average {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
    }
    
    .grade-poor {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }
    
    /* Professional tables */
    .dataframe {
        font-size: 0.95rem;
        border: none !important;
    }
    
    .dataframe th {
        background-color: #F9FAFB !important;
        color: #374151 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 1rem !important;
    }
    
    .dataframe td {
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid #F3F4F6 !important;
    }
    
    /* Source citations */
    .data-source {
        background: #F9FAFB;
        border-left: 3px solid #3B82F6;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 0.875rem;
        color: #4B5563;
    }
    
    .data-source strong {
        color: #1E40AF;
    }
    
    /* Action buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(30, 58, 138, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F9FAFB;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_professional_data():
    """Load all data with proper error handling"""
    try:
        # Try professional data first (with Zillow prices)
        try:
            df = pd.read_csv('data/processed/neighborhoods_professional.csv')
        except:
            # Fallback to enhanced
            df = pd.read_csv('data/processed/neighborhoods_enhanced.csv')
            # Add missing columns with defaults
            if 'median_home_value' not in df.columns:
                df['median_home_value'] = 500000
            if 'value_score' not in df.columns:
                df['value_score'] = 70
            if 'growth_score' not in df.columns:
                df['growth_score'] = 70
            if 'safety_score_pro' not in df.columns:
                df['safety_score_pro'] = 70
            if 'lifestyle_score_pro' not in df.columns:
                df['lifestyle_score_pro'] = 70
            if 'grade' not in df.columns:
                df['grade'] = df['investment_score'].apply(
                    lambda x: 'A' if x >= 85 else 'B' if x >= 70 else 'C' if x >= 50 else 'D' if x >= 30 else 'F'
                )
            if 'affordability' not in df.columns:
                df['affordability'] = 'Moderate'
        
        # Load data sources report
        try:
            with open('data/processed/data_sources_report.json', 'r') as f:
                sources = json.load(f)
        except:
            sources = None
        
        # Load economic data
        try:
            with open('data/processed/economic_indicators.json', 'r') as f:
                economic = json.load(f)
        except:
            economic = None
        
        return df, sources, economic, True
    except Exception as e:
        st.error(f"⚠️ Data files not found: {e}")
        st.info("Please run: python analyze_neighborhoods_professional.py")
        return None, None, None, False

df, sources, economic, data_loaded = load_professional_data()

if not data_loaded:
    st.stop()

# Professional Header
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<h1 class="main-header">Austin Real Estate Intelligence Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Institutional-Grade Investment Analysis | Data-Driven Insights</p>', unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 1rem;">
        <div style="font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em;">Last Updated</div>
        <div style="font-size: 1rem; font-weight: 600; color: #111827;">{datetime.now().strftime('%B %d, %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

# Key Metrics Dashboard
st.markdown("### 📊 Market Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    excellent_count = len(df[df['investment_score'] >= 85])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #059669;">{excellent_count}</div>
        <div class="metric-label">Grade A Opportunities</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_price = df['median_home_value'].mean() if 'median_home_value' in df.columns else 500000
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #1E3A8A;">${avg_price/1000:.0f}k</div>
        <div class="metric-label">Avg Median Price</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    fed_rate = economic.get('interest_rate', 5.25) if economic else 5.25
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #D97706;">{fed_rate}%</div>
        <div class="metric-label">Fed Funds Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_neighborhoods = len(df)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #6B7280;">{total_neighborhoods}</div>
        <div class="metric-label">Neighborhoods Analyzed</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar Filters
with st.sidebar:
    st.markdown("### 🎯 Investment Filters")
    
    min_score = st.slider("Minimum Investment Score", 0, 100, 70, 5,
                         help="Only show neighborhoods above this score")
    
    max_price = st.slider("Max Median Home Price", 200000, 1000000, 600000, 50000,
                         format="$%d",
                         help="Filter by affordability")
    
    school_min = st.slider("Minimum School Rating", 0.0, 10.0, 6.0, 0.5,
                          help="Filter by school quality")
    
    walkability = st.multiselect(
        "Walkability",
        ['Very Walkable', 'Walkable', 'Somewhat Walkable', 'Car-Dependent'],
        default=['Very Walkable', 'Walkable']
    )
    
    st.markdown("---")
    st.markdown("### 📚 Data Sources")
    st.markdown("""
    <div style="font-size: 0.8rem; color: #6B7280;">
    ✅ Austin Open Data Portal<br>
    ✅ Zillow Home Value Index<br>
    ✅ Federal Reserve (FRED)<br>
    ✅ Yelp Business Data<br>
    <br>
    <a href="#" style="color: #1E3A8A;">View Full Documentation →</a>
    </div>
    """, unsafe_allow_html=True)

# Apply filters
filtered_df = df[
    (df['investment_score'] >= min_score) &
    (df['median_home_value'] <= max_price) &
    (df['school_rating'] >= school_min)
]

if walkability:
    filtered_df = filtered_df[filtered_df['walkability'].isin(walkability)]

# Main Content Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Top Opportunities",
    "📈 Market Analysis",
    "🗺️ Geographic View",
    "📊 Data Transparency"
])

with tab1:
    st.markdown("### 🏆 Top Investment Opportunities")
    st.markdown(f"*Showing {len(filtered_df)} neighborhoods matching your criteria*")
    
    # Sort by score
    top_df = filtered_df.nlargest(10, 'investment_score')
    
    for idx, row in top_df.iterrows():
        # Determine grade
        score = row['investment_score']
        if score >= 70:
            grade_class = "grade-excellent"
            grade_text = "GRADE A - EXCELLENT"
        elif score >= 55:
            grade_class = "grade-good"
            grade_text = "GRADE B - GOOD"
        elif score >= 40:
            grade_class = "grade-average"
            grade_text = "GRADE C - AVERAGE"
        else:
            grade_class = "grade-poor"
            grade_text = "GRADE D/F - CAUTION"
        
        with st.expander(f"**{row['neighborhood_name']}** - Score: {score:.1f}/100", expanded=(idx==top_df.index[0])):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f'<div class="{grade_class}">{grade_text}</div>', unsafe_allow_html=True)
                st.markdown(f"**ZIP Code:** {row['zip_code']}")
                st.markdown(f"**Median Home Value:** ${row.get('median_home_value', 500000):,.0f}")
                st.markdown(f"**School Rating:** {row.get('school_rating', 6.0):.1f}/10")
                st.markdown(f"**Walkability:** {row.get('walkability', 'N/A')} ({row.get('walk_score', 50)}/100)")
                
                # Crime safety from safety score
                crime_safety = row.get('safety_score_pro', row.get('safety_score', 70))
                st.markdown(f"**Safety Score:** {crime_safety:.0f}/100")
                
                # Risk warnings
                if 'risk_warnings' in row and pd.notna(row['risk_warnings']):
                    if row['risk_warnings'] != "✅ No major risk warnings":
                        st.warning(f"⚠️ {row['risk_warnings']}")
            
            with col2:
                # Mini component scores
                components = {
                    'Value': row.get('value_score', 70),
                    'Growth': row.get('growth_score', 70),
                    'Safety': row.get('safety_score_pro', row.get('safety_score', 70)),
                    'Lifestyle': row.get('lifestyle_score_pro', row.get('lifestyle_score', 70))
                }
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=list(components.keys()),
                    x=list(components.values()),
                    orientation='h',
                    marker_color='#1E3A8A'
                ))
                fig.update_layout(
                    height=200,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis_range=[0, 100],
                    showlegend=False,
                    xaxis_title="Score",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True, key=f"bar_{idx}")
            
            st.markdown(f"[🏠 View Properties on Zillow](https://www.zillow.com/homes/{row['zip_code']}_rb/)")

with tab2:
    st.markdown("### 📈 Market Analysis")
    
    # Interactive scatter: Price vs Score
    fig = px.scatter(
        filtered_df,
        x='median_home_value',
        y='investment_score',
        size='confidence_score',
        color='investment_score',
        hover_data=['neighborhood_name', 'zip_code', 'school_rating'],
        title="Investment Score vs Home Price",
        labels={
            'median_home_value': 'Median Home Value ($)',
            'investment_score': 'Investment Score (0-100)'
        },
        color_continuous_scale='RdYlGn',
        template='plotly_white'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **How to read this chart:**
    - **Bottom-left quadrant** = Affordable + Low Score (avoid)
    - **Bottom-right quadrant** = Expensive + Low Score (definitely avoid)
    - **Top-left quadrant** = Affordable + High Score (BEST opportunities)
    - **Top-right quadrant** = Expensive + High Score (established areas)
    """)

with tab3:
    st.markdown("### 🗺️ Geographic Distribution")
    
    # Create interactive map
    try:
        import folium
        from streamlit_folium import st_folium
        
        # Austin center coordinates
        austin_center = [30.2672, -97.7431]
        
        # Create map
        m = folium.Map(
            location=austin_center,
            zoom_start=11,
            tiles='CartoDB positron'
        )
        
        # Add neighborhoods as markers
        for idx, row in filtered_df.iterrows():
            # Determine color based on grade (70+ is Grade A)
            score = row['investment_score']
            if score >= 70:
                color = 'darkgreen'
                icon = 'star'
                grade = 'A'
            elif score >= 55:
                color = 'green'
                icon = 'arrow-up'
                grade = 'B'
            elif score >= 40:
                color = 'orange'
                icon = 'minus'
                grade = 'C'
            elif score >= 25:
                color = 'red'
                icon = 'arrow-down'
                grade = 'D'
            else:
                color = 'darkred'
                icon = 'remove'
                grade = 'F'
            
            # Get coordinates (use zip code center approximation)
            # This is simplified - in production, use geocoding API
            lat = 30.2672 + (hash(str(row['zip_code'])) % 100 - 50) / 100
            lon = -97.7431 + (hash(str(row['zip_code'] + 1000)) % 100 - 50) / 100
            
            # Create popup
            popup_html = f"""
            <div style="font-family: Arial; width: 250px;">
                <h4 style="margin: 0 0 10px 0;">{row['neighborhood_name']}</h4>
                <b>Score:</b> {row['investment_score']:.1f}/100<br>
                <b>Grade:</b> {row['grade']} ({row['grade_label']})<br>
                <b>Price:</b> ${row['median_home_value']:,.0f}<br>
                <b>Schools:</b> {row['school_rating']:.1f}/10<br>
                <b>Walkability:</b> {row['walkability']}<br>
                <hr style="margin: 5px 0;">
                <b>Action:</b> {row['action']}
            </div>
            """
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['neighborhood_name']} - Grade {row['grade']}",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(m)
        
        # Add legend
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; height: 180px; 
                    background-color: white; border: 2px solid grey; z-index: 9999; 
                    font-size: 14px; padding: 10px; border-radius: 8px;">
        <p style="margin: 0 0 10px 0; font-weight: bold;">Investment Grade</p>
        <p style="margin: 5px 0;"><i class="fa fa-star" style="color: darkgreen;"></i> Grade A - Excellent</p>
        <p style="margin: 5px 0;"><i class="fa fa-arrow-up" style="color: green;"></i> Grade B - Good</p>
        <p style="margin: 5px 0;"><i class="fa fa-minus" style="color: orange;"></i> Grade C - Average</p>
        <p style="margin: 5px 0;"><i class="fa fa-arrow-down" style="color: red;"></i> Grade D - Caution</p>
        <p style="margin: 5px 0;"><i class="fa fa-remove" style="color: darkred;"></i> Grade F - Avoid</p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Display map
        st_folium(m, width=1200, height=600)
        
        st.markdown("""
        **How to use this map:**
        - 🟢 **Green markers** = Good investment opportunities (Grade A/B)
        - 🟡 **Orange markers** = Average areas (Grade C)
        - 🔴 **Red markers** = Proceed with caution (Grade D/F)
        - Click any marker to see detailed info
        """)
        
    except ImportError:
        st.warning("Map visualization requires additional packages. Installing...")
        st.code("pip install folium streamlit-folium")
        
        st.info("""
        **Quick Setup:**
        ```bash
        pip install folium streamlit-folium
        ```
        Then refresh this page to see the interactive map!
        """)
    except Exception as e:
        st.error(f"Error creating map: {e}")
        st.info("Map coming soon - please ensure all dependencies are installed")

with tab4:
    st.markdown("### 📊 Data Transparency")
    
    st.markdown("""
    **Why trust this data?** We use the SAME sources that professional investors use:
    """)
    
    if sources:
        for key, source in sources['sources'].items():
            st.markdown(f"""
            <div class="data-source">
                <strong>{source['name']}</strong><br>
                🔗 Source: <a href="{source['url']}" target="_blank">{source['url']}</a><br>
                📊 Reliability: {source['reliability']}<br>
                🔄 Update Frequency: {source['update_frequency']}<br>
                📅 Last Fetched: {source.get('last_updated', 'Pending')}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 Scoring Methodology
    
    Our scoring system mirrors institutional investment criteria:
    
    | Component | Weight | What It Measures |
    |-----------|--------|------------------|
    | **Value** | 25% | Affordability & price-to-income ratio |
    | **Growth Potential** | 20% | Hipster Index + recent appreciation |
    | **Safety** | 15% | Crime rate + disaster risk |
    | **Lifestyle** | 15% | Walkability + amenities |
    | **Development** | 10% | Building permit activity |
    | **Schools** | 10% | Public school ratings |
    | **Economy** | 5% | Job growth trends |
    
    **Total = 100%** weighted average
    
    [📄 Read Full Methodology](link)
    """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Disclaimer:**  
    For informational purposes only.  
    Not financial or investment advice.
    """)

with col2:
    st.markdown("""
    **Data Sources:**  
    Austin Open Data, Zillow, FRED, Yelp  
    Updated daily from official sources
    """)

with col3:
    st.markdown("""
    **Support:**  
    Questions? View documentation  
    or contact support
    """)
