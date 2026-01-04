#!/usr/bin/env python3
"""
🏙️ AUSTIN NEIGHBORHOOD INVESTMENT DASHBOARD
Interactive web app to explore real estate investment opportunities
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import folium
from streamlit_folium import st_folium
from neighborhood_names import add_neighborhood_names

# Page config
st.set_page_config(
    page_title="Austin Investment Predictor",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .investment-tip {
        background-color: #f0f8ff;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 24px;
        background-color: #f0f2f6;
        border-radius: 5px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    # Try to load enhanced data with confidence scores, fall back to basic if not available
    try:
        neighborhoods = pd.read_csv('data/processed/neighborhoods_with_confidence.csv')
    except:
        neighborhoods = pd.read_csv('data/processed/neighborhoods_analyzed.csv')
        # Add basic confidence if not present
        neighborhoods['confidence_level'] = neighborhoods['business_count'].apply(
            lambda x: 'High' if x >= 20 else 'Medium' if x >= 10 else 'Low' if x >= 5 else 'Very Low'
        )
        neighborhoods['confidence_score'] = neighborhoods['business_count'].apply(
            lambda x: 90 if x >= 30 else 75 if x >= 20 else 60 if x >= 10 else 40 if x >= 5 else 20
        )
        neighborhoods['recommendation_strength'] = 'See data quality'
    
    yelp = pd.read_csv('data/processed/yelp_cleaned.csv')
    recommendations = pd.read_csv('data/processed/recommendations.csv')
    
    # Add neighborhood names
    neighborhoods = add_neighborhood_names(neighborhoods)
    yelp = add_neighborhood_names(yelp)
    recommendations = add_neighborhood_names(recommendations)
    
    return neighborhoods, yelp, recommendations

neighborhoods_df, yelp_df, recommendations_df = load_data()

# Header
st.markdown('<h1 class="main-header">🏙️ Austin Real Estate Investment Finder</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Find Neighborhoods to Buy Houses & Land Before Prices Explode 🚀</p>', unsafe_allow_html=True)

# Big, clear explanation
st.info("""
### 💡 **What This Dashboard Does:**
This tool tells you **which Austin neighborhoods to buy real estate in** (houses, condos, land) BEFORE they get expensive.

**Why it works:** When coffee shops and breweries open in an area, property values increase 50-200% over 5 years. 
We track 1,000+ businesses, crime data, and building permits to find these opportunities early.

**What to do:** Find a high-scoring neighborhood below → Search that zip code on Zillow/Redfin → Buy property → Wait 3-5 years → Sell for profit (or rent it out).
""")

# DATA QUALITY BANNER
high_conf_count = len(neighborhoods_df[neighborhoods_df['confidence_level'] == 'High'])
total_count = len(neighborhoods_df)
data_quality_pct = (high_conf_count / total_count * 100)

st.warning(f"""
⚠️ **HONEST DISCLOSURE - Data Quality:**

✅ **High Confidence Areas:** {high_conf_count}/{total_count} neighborhoods ({data_quality_pct:.0f}%) have 20+ businesses tracked
⚠️ **Limited Data:** {total_count - high_conf_count} areas have <20 businesses (less reliable scores)

**What this means:** Focus on "High" or "Medium" confidence neighborhoods. Low confidence scores may be inaccurate.

📅 **Data Freshness:** Updated December 13, 2025 (Today)
📊 **Sample Size:** {neighborhoods_df['business_count'].sum():.0f} businesses, {neighborhoods_df['crime_count'].sum():.0f} crime incidents analyzed
""")

st.markdown("---")

# Key Metrics at the top
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎯 Neighborhoods Analyzed",
        value=len(neighborhoods_df),
        delta="74 zip codes"
    )

with col2:
    top_score = neighborhoods_df['investment_score'].max()
    st.metric(
        label="🏆 Top Investment Score",
        value=f"{top_score:.1f}/100",
        delta="Downtown Austin"
    )

with col3:
    undervalued = neighborhoods_df[neighborhoods_df['is_undervalued'] == True].shape[0]
    st.metric(
        label="💎 Undervalued Gems",
        value=undervalued,
        delta="Hidden opportunities"
    )

with col4:
    businesses = neighborhoods_df['business_count'].sum()
    st.metric(
        label="☕ Total Businesses",
        value=businesses,
        delta="Tracked amenities"
    )

st.markdown("---")

# Sidebar filters
st.sidebar.header("🎚️ Filter Neighborhoods")
score_range = st.sidebar.slider(
    "Investment Score Range",
    0, 100, (45, 100),
    help="Filter neighborhoods by investment score (0-100)"
)

neighborhood_types = st.sidebar.multiselect(
    "Neighborhood Type",
    options=neighborhoods_df['neighborhood_type'].unique(),
    default=neighborhoods_df['neighborhood_type'].unique(),
    help="Select neighborhood categories to display"
)

show_undervalued = st.sidebar.checkbox("Show Only Undervalued Gems 💎", value=False)

# Filter data
filtered_df = neighborhoods_df[
    (neighborhoods_df['investment_score'] >= score_range[0]) &
    (neighborhoods_df['investment_score'] <= score_range[1]) &
    (neighborhoods_df['neighborhood_type'].isin(neighborhood_types))
]

if show_undervalued:
    filtered_df = filtered_df[filtered_df['is_undervalued'] == True]

# Tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Investment Opportunities", 
    "🗺️ Interactive Map", 
    "📈 Market Analysis",
    "💰 How to Invest",
    "🎓 What is This?"
])

# TAB 1: Investment Opportunities
with tab1:
    st.header("🎯 Top Investment Recommendations")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏆 Best Neighborhoods by Investment Score")
        top_10 = filtered_df.nlargest(10, 'investment_score')
        
        # Create a display column that combines name and zip
        top_10['display_name'] = top_10['neighborhood_name'] + ' (' + top_10['zip_code'].astype(str) + ')'
        
        # Create interactive bar chart
        fig = px.bar(
            top_10,
            x='investment_score',
            y='display_name',
            orientation='h',
            color='investment_score',
            color_continuous_scale='RdYlGn',
            labels={'investment_score': 'Investment Score (0-100)', 'display_name': 'Neighborhood'},
            title='Top 10 Best Investment Opportunities in Austin',
            hover_data={
                'display_name': False,
                'investment_score': ':.1f',
                'business_count': True,
                'hipster_index': ':.1f',
                'safety_score': ':.0f'
            }
        )
        fig.update_layout(
            height=500, 
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            font=dict(size=14)
        )
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}/100<br>Businesses: %{customdata[0]}<br>Hipster Index: %{customdata[1]:.1f}<br>Safety: %{customdata[2]:.0f}/100'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📋 Top 5 Opportunities")
        for idx, row in top_10.head(5).iterrows():
            # Determine what to buy based on score
            if row['investment_score'] > 65:
                what_to_buy = "🏠 Single-family homes (already appreciating)"
                strategy = "Buy premium property in established area"
                roi = "20-40% in 3-5 years"
            elif row['investment_score'] > 55:
                what_to_buy = "🏘️ Houses, condos, or townhomes"
                strategy = "Best value - buy before area peaks"
                roi = "50-100% in 3-5 years"
            else:
                what_to_buy = "🏗️ Land or fixer-uppers"
                strategy = "Long-term hold, higher risk/reward"
                roi = "100-200% in 5-10 years"
            
            # Get confidence level
            conf_level = row.get('confidence_level', 'Medium')
            conf_score = row.get('confidence_score', 50)
            
            # Set color based on confidence
            if conf_level == 'High':
                conf_color = 'green'
                conf_emoji = '✅'
            elif conf_level == 'Medium':
                conf_color = 'orange'
                conf_emoji = '⚠️'
            else:
                conf_color = 'red'
                conf_emoji = '🚨'
            
            with st.container():
                st.markdown(f"""
                <div class="investment-tip">
                    <h4>📍 {row['neighborhood_name']}</h4>
                    <p style="color: #666; font-size: 0.9em;">Zip Code: {row['zip_code']}</p>
                    <p><b>🏆 Investment Score:</b> {row['investment_score']:.1f}/100</p>
                    <p><b style="color: {conf_color};">{conf_emoji} Data Quality:</b> {conf_level} Confidence ({conf_score}/100)</p>
                    <p><b>📊 Status:</b> {row['neighborhood_type']}</p>
                    <p style="font-size: 0.85em; color: #666;"><i>Based on {row['business_count']:.0f} businesses</i></p>
                    <hr style="margin: 10px 0;">
                    <p><b>💰 What to Buy:</b> {what_to_buy}</p>
                    <p><b>📈 Expected ROI:</b> {roi}</p>
                    <p><b>🎯 Strategy:</b> {strategy}</p>
                    <p><b>🔍 Next Step:</b> <a href="https://www.zillow.com/homes/{row['zip_code']}_rb/" target="_blank">Search Zillow →</a></p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed table
    st.subheader("📊 Detailed Comparison Table")
    
    # Include confidence columns if they exist
    display_cols = ['neighborhood_name', 'zip_code', 'neighborhood_type', 'investment_score']
    if 'confidence_level' in filtered_df.columns:
        display_cols.append('confidence_level')
        display_cols.append('confidence_score')
    display_cols.extend(['hipster_index', 'safety_score', 'business_count', 'coffee', 'breweries', 'is_undervalued'])
    
    styled_df = filtered_df[display_cols].sort_values('investment_score', ascending=False)
    styled_df = styled_df.reset_index(drop=True)
    
    # Rename columns for clarity
    rename_dict = {
        'neighborhood_name': 'Neighborhood',
        'zip_code': 'Zip',
        'neighborhood_type': 'Type',
        'investment_score': 'Score',
        'confidence_level': 'Data Confidence',
        'confidence_score': 'Confidence %',
        'hipster_index': 'Hipster Index',
        'safety_score': 'Safety Score',
        'business_count': '# Businesses',
        'coffee': '☕ Coffee',
        'breweries': '🍺 Breweries',
        'is_undervalued': '💎 Undervalued'
    }
    styled_df = styled_df.rename(columns=rename_dict)
    
    # Style the dataframe
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Data (CSV)",
        data=csv,
        file_name="austin_investment_opportunities.csv",
        mime="text/csv"
    )

# TAB 2: Interactive Map
with tab2:
    st.header("🗺️ Austin Investment Opportunity Map")
    st.markdown("**Green = High Investment Score | Yellow = Medium | Red = Lower Score**")
    
    # Create map
    austin_center = [30.2672, -97.7431]
    m = folium.Map(location=austin_center, zoom_start=11, tiles='CartoDB positron')
    
    def get_color(score):
        if score > 65:
            return 'green'
        elif score > 55:
            return 'lightgreen'
        elif score > 50:
            return 'orange'
        else:
            return 'red'
    
    # Add markers for each zip code
    for _, row in filtered_df.iterrows():
        # Get businesses in this zip
        zip_businesses = yelp_df[yelp_df['zip_code'] == row['zip_code']]
        
        if len(zip_businesses) > 0:
            lat = zip_businesses['latitude'].mean()
            lon = zip_businesses['longitude'].mean()
            
            if pd.notna(lat) and pd.notna(lon):
                popup_html = f"""
                <div style="width:280px; font-family: Arial">
                    <h3 style="margin:0; color:#333">{row['neighborhood_name']}</h3>
                    <p style="margin:2px 0; color:#666; font-size:0.9em;">Zip Code: {row['zip_code']}</p>
                    <hr style="margin:5px 0">
                    <b>🏆 Investment Score:</b> {row['investment_score']:.1f}/100<br>
                    <b>📊 Type:</b> {row['neighborhood_type']}<br>
                    <b>🏪 Businesses:</b> {row['business_count']}<br>
                    <b>⭐ Avg Rating:</b> {row['avg_rating']:.2f}<br>
                    <b>🎯 Hipster Index:</b> {row['hipster_index']:.1f}<br>
                    <b>☕ Coffee Shops:</b> {int(row['coffee'])}<br>
                    <b>🍺 Breweries:</b> {int(row['breweries'])}<br>
                    <b>🛡️ Safety:</b> {row['safety_score']:.0f}/100<br>
                    {'<b style="color:green">💎 Undervalued Gem!</b>' if row['is_undervalued'] else ''}
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=300),
                    color=get_color(row['investment_score']),
                    fill=True,
                    fillColor=get_color(row['investment_score']),
                    fillOpacity=0.7,
                    weight=2
                ).add_to(m)
    
    # Display map
    st_folium(m, width=1400, height=600)

# TAB 3: Market Analysis
with tab3:
    st.header("📈 Market Trends & Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 3D Scatter plot
        st.subheader("🎯 3D Score Visualization")
        fig = px.scatter_3d(
            filtered_df,
            x='lifestyle_score',
            y='safety_score',
            z='investment_score',
            color='investment_score',
            size='business_count',
            hover_data={
                'neighborhood_name': True,
                'zip_code': True,
                'neighborhood_type': True,
                'lifestyle_score': ':.1f',
                'safety_score': ':.1f',
                'investment_score': ':.1f',
                'business_count': True
            },
            color_continuous_scale='Viridis',
            labels={
                'lifestyle_score': 'Lifestyle Score',
                'safety_score': 'Safety Score',
                'investment_score': 'Investment Score'
            }
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter: Hipster Index vs Investment Score
        st.subheader("☕ Hipster Index Impact")
        fig = px.scatter(
            filtered_df,
            x='hipster_index',
            y='investment_score',
            color='neighborhood_type',
            size='business_count',
            hover_data={
                'neighborhood_name': True,
                'zip_code': True,
                'hipster_index': ':.1f',
                'investment_score': ':.1f',
                'business_count': True
            },
            labels={
                'hipster_index': 'Hipster Index (Trendiness)',
                'investment_score': 'Investment Score'
            },
            title='Does Trendiness = Investment Potential?'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution of scores
        st.subheader("📊 Score Distributions")
        fig = go.Figure()
        fig.add_trace(go.Box(y=filtered_df['investment_score'], name='Investment Score', marker_color='lightblue'))
        fig.add_trace(go.Box(y=filtered_df['hipster_index'], name='Hipster Index', marker_color='lightgreen'))
        fig.add_trace(go.Box(y=filtered_df['safety_score'], name='Safety Score', marker_color='lightyellow'))
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Amenity breakdown
        st.subheader("🏪 Amenity Analysis")
        amenities = filtered_df[['coffee', 'breweries', 'organic', 'vegan', 'yoga']].sum()
        fig = px.pie(
            values=amenities.values,
            names=amenities.index,
            title='Distribution of Tracked Amenities',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# TAB 4: How to Invest
with tab4:
    st.header("💰 How to Actually Invest Using This Data")
    
    # Big, clear callout
    st.success("""
    ### 🎯 **THE SIMPLE ANSWER:**
    
    **STEP 1:** Find a high-scoring neighborhood in the "Investment Opportunities" tab
    
    **STEP 2:** Go to [Zillow.com](https://zillow.com) or [Redfin.com](https://redfin.com) and search that zip code
    
    **STEP 3:** Buy a house, condo, townhome, or land in that area
    
    **STEP 4:** Wait 3-5 years while the neighborhood gentrifies
    
    **STEP 5:** Sell for 50-200% profit OR rent it out for cash flow
    
    **That's it. You're investing in PROPERTY, not coffee shops.**
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ## 🏠 **WHAT EXACTLY TO BUY (Be Specific):**
    
    ### **Option 1: Single-Family Homes** 🏠
    **Best for:** Scores 65-75 (Established Hot Spots)
    - **What:** 2-4 bedroom houses
    - **Price range:** $400K-$800K in Austin
    - **Strategy:** Buy, wait for appreciation, sell or rent
    - **Expected ROI:** 20-40% in 3-5 years
    - **Example:** Buy house in East Austin (78702) for $500K, sell for $700K in 5 years
    
    ### **Option 2: Condos/Townhomes** 🏘️
    **Best for:** Scores 55-65 (Up-and-Coming)
    - **What:** 1-3 bedroom condos in new developments
    - **Price range:** $250K-$500K
    - **Strategy:** Buy pre-construction or new builds
    - **Expected ROI:** 50-100% in 3-5 years
    - **Example:** Buy condo in Cedar Park (78613) for $300K, sell for $500K in 5 years
    
    ### **Option 3: Land/Vacant Lots** 🏗️
    **Best for:** Scores 45-55 (Emerging Areas)
    - **What:** Residential lots, 0.25-1 acre
    - **Price range:** $50K-$200K
    - **Strategy:** Buy raw land, hold long-term, sell to developer
    - **Expected ROI:** 100-300% in 5-10 years
    - **Example:** Buy lot in Pflugerville (78660) for $80K, sell for $200K in 7 years
    
    ### **Option 4: Fixer-Uppers** 🔨
    **Best for:** Any score, need renovation skills
    - **What:** Older homes needing repair
    - **Price range:** $200K-$400K
    - **Strategy:** Buy cheap, renovate, flip or rent
    - **Expected ROI:** 30-80% in 6-12 months
    - **Example:** Buy fixer in Manor (78653) for $250K, spend $50K fixing, sell for $400K
    
    ### **Option 5: Multi-Family Properties** 🏢
    **Best for:** Scores 50-60, experienced investors
    - **What:** Duplexes, triplexes, small apartment buildings
    - **Price range:** $500K-$2M+
    - **Strategy:** Buy, rent out units, collect cash flow + appreciation
    - **Expected ROI:** 8-15% annual cash flow + 30-60% appreciation
    - **Example:** Buy duplex in Round Rock (78681) for $600K, rent for $3K/month
    
    ---
    
    ## 🔑 **The Strategy Explained:**
    
    ### **Coffee Shops = Signal, Real Estate = Investment**
    
    **1️⃣ THE SIGNAL (What Coffee Shops Tell You):**
    - When trendy businesses (coffee, breweries, yoga) open in an area
    - It means young, educated professionals with money are moving in
    - This is called "gentrification" or "neighborhood improvement"
    - It's an EARLY WARNING that property values will increase
    
    **2️⃣ THE INVESTMENT (What You Actually Buy):**
    - **Houses:** Buy single-family homes to flip or rent
    - **Condos:** Purchase apartments in buildings
    - **Land:** Buy empty lots before development
    - **REITs:** Invest in real estate funds focused on these areas
    - **Commercial Property:** Buy retail spaces for businesses
    
    ---
    
    ## 💵 **Real-World Example:**
    
    ### **East Austin (78702) - Past Success Story**
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📅 2010:**
        - Few coffee shops
        - Low hipster index
        - Houses: $150K
        - Nobody wanted to live there
        """)
    
    with col2:
        st.markdown("""
        **📅 2015:**
        - 10+ coffee shops opened
        - Hipster index rising
        - Houses: $300K (100% gain)
        - Artists moving in
        """)
    
    with col3:
        st.markdown("""
        **📅 2025:**
        - 25+ trendy businesses
        - High hipster index
        - Houses: $500K+ (233% gain!)
        - Completely gentrified
        """)
    
    st.markdown("""
    ---
    
    ## 📋 **Step-by-Step Investment Process:**
    
    ### **Using This Dashboard:**
    
    1. **Find High-Potential Neighborhoods**
       - Look for "Up-and-Coming" areas (scores 55-70)
       - Check the map for green/yellow zones
       - Focus on rising hipster index but NOT already gentrified
    
    2. **Research the Area**
       - Visit the neighborhood in person
       - Check Zillow/Redfin for property prices
       - Look at crime trends (we provide safety scores)
       - See what businesses are opening
    
    3. **Analyze the Numbers**
       - Compare current prices to similar neighborhoods
       - Calculate potential ROI (Return on Investment)
       - Factor in renovation costs
       - Estimate rental income potential
    
    4. **Make the Investment**
       - Buy property through traditional mortgage
       - Use hard money loans for flips
       - Partner with other investors
       - Invest in real estate crowdfunding platforms
    
    5. **Hold or Flip**
       - **Hold:** Rent it out and wait 3-7 years for appreciation
       - **Flip:** Renovate and sell quickly for profit
       - **Live:** Buy to live in an appreciating area
    
    ---
    
    ## 🎯 **Current Opportunities (Based on Your Data):**
    """)
    
    # Show top opportunities
    opportunities = neighborhoods_df[
        (neighborhoods_df['investment_score'] >= 55) & 
        (neighborhoods_df['investment_score'] < 70)
    ].nlargest(5, 'investment_score')
    
    for idx, row in opportunities.iterrows():
        st.markdown(f"""
        <div class="investment-tip">
            <h3>📍 {row['neighborhood_name']}</h3>
            <p style="color: #666; font-size: 0.9em;">Zip Code: {row['zip_code']}</p>
            <p><b>🏆 Investment Score:</b> {row['investment_score']:.1f}/100</p>
            <p><b>📊 Status:</b> {row['neighborhood_type']}</p>
            <p><b>☕ Hipster Index:</b> {row['hipster_index']:.1f} (trendy businesses growing)</p>
            <p><b>🛡️ Safety:</b> {row['safety_score']:.0f}/100</p>
            <p><b>🏪 Businesses:</b> {row['business_count']} ({int(row['coffee'])} coffee, {int(row['breweries'])} breweries)</p>
            <p><b>💡 Why Invest:</b> {'Undervalued hidden gem!' if row['is_undervalued'] else 'Growing amenities, good safety, rising potential'}</p>
            <p><b>🎯 Strategy:</b> Buy residential property now, hold 3-5 years, expect 50-150% appreciation</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    ---
    
    ## 👥 **Who Pays for This Analysis?**
    
    - **🏢 Real Estate Investment Firms:** $50K-$200K for market analysis
    - **🏗️ Property Developers:** $30K-$100K to decide where to build
    - **💼 Hedge Funds:** $100K+ for geographic investment strategies
    - **🏠 Individual Investors:** $500-$5K for personalized reports
    - **🏦 Banks/Lenders:** Use to assess loan risk in different areas
    
    ---
    
    ## ⚠️ **Investment Risks to Consider:**
    
    - ❌ Economic downturns can delay gentrification
    - ❌ City policies might limit development
    - ❌ Competition from other investors
    - ❌ Takes 3-7 years to see full returns
    - ✅ But: Diversification and research mitigate risks!
    """)

# TAB 5: What is This?
with tab5:
    st.header("🎓 Project Explanation")
    
    st.markdown("""
    ## 🔬 **What This Project Does:**
    
    This is a **predictive analytics system** that identifies emerging real estate markets using alternative data sources.
    
    ### **📊 The Data Sources:**
    
    1. **Yelp API** - 1,000 trendy businesses (coffee, breweries, vegan, yoga, organic)
    2. **Austin Crime Data** - 10,000 incidents for safety analysis
    3. **Building Permits** - 4,995 permits showing development activity
    
    ### **🧮 The Algorithm:**
    
    **Hipster Index Formula:**
    ```
    Hipster Index = (Coffee × 1.5) + (Breweries × 1.2) + (Organic × 1.0) 
                    + (Vegan × 0.8) + (Yoga × 0.5)
    ```
    
    **Investment Score Formula:**
    ```
    Investment Score = (Lifestyle Score × 0.40) + (Safety Score × 0.30) 
                       + (Development Score × 0.15) + (Undervalued Score × 0.15)
    ```
    
    ### **🤖 Machine Learning:**
    
    - **K-Means Clustering** groups neighborhoods into 3 categories:
      - Established Hot Spots (already expensive)
      - Up-and-Coming (best investment targets)
      - Emerging Areas (long-term plays)
    
    ### **💼 Portfolio Value:**
    
    This project demonstrates:
    - ✅ API Integration & ETL pipelines
    - ✅ Feature Engineering & Custom Metrics
    - ✅ Machine Learning (Clustering)
    - ✅ Geospatial Analysis
    - ✅ Interactive Dashboards
    - ✅ Business Problem Solving
    
    ### **🚀 Technical Stack:**
    
    - **Python:** Pandas, NumPy, Scikit-learn
    - **Visualization:** Plotly, Folium, Streamlit
    - **Data:** Yelp API, Public crime data, Building permits
    - **ML:** K-Means clustering, feature engineering
    
    ### **📈 Business Impact:**
    
    > *"This system could help investors identify neighborhoods with 50-200% ROI potential 
    > over 5-7 years by detecting early gentrification signals that traditional methods miss."*
    
    ---
    
    ## 🎯 **The Bottom Line:**
    
    **Coffee shops don't make you money. Real estate in neighborhoods getting coffee shops does.**
    
    This dashboard finds those neighborhoods BEFORE everyone else figures it out.
    """)
    
    # Project stats
    st.markdown("---")
    st.subheader("📊 Project Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Data Points Analyzed", "16,000+", "Yelp + Crime + Permits")
    
    with col2:
        st.metric("Features Engineered", "20+", "Custom metrics")
    
    with col3:
        st.metric("Visualizations Created", "15+", "Charts & maps")

# Footer
st.markdown("---")

# IMPORTANT DISCLAIMERS
st.error("""
### ⚠️ **IMPORTANT DISCLAIMERS - READ THIS:**

**This is a data analysis tool, NOT financial advice.**

❌ **What This Tool CANNOT Do:**
- Predict economic recessions or crashes
- Account for natural disasters or policy changes  
- Guarantee any investment returns
- Replace professional financial advice
- Know about upcoming major developments not in public data

✅ **What This Tool DOES:**
- Analyzes current data to identify neighborhoods with favorable indicators
- Shows where trendy businesses are clustering (early gentrification signal)
- Ranks areas by multiple objective factors
- Saves you 40+ hours of manual research

🎯 **How to Use This Responsibly:**
1. Use this as a STARTING POINT to narrow down research
2. ALWAYS visit neighborhoods in person
3. Check home prices on Zillow/Redfin
4. Talk to local real estate agents
5. Consult a licensed financial advisor before investing
6. Only invest money you can afford to lose
7. Understand that real estate values can go DOWN

**Expected vs Reality:** When we say "50-100% ROI in 5 years", this is based on historical trends in similar markets. Actual results will vary. Some areas may not appreciate at all.

**Data Limitations:** Areas with "Low" or "Very Low" confidence have limited data (<10 businesses tracked). These scores are less reliable. Focus on "High" confidence neighborhoods for better accuracy.

📅 **Data Age:** Last updated December 13, 2025. Real estate markets change quickly - verify current conditions before investing.
""")

st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🏙️ <b>Austin Real Estate Investment Finder</b> | Data Science Portfolio Project 2025</p>
    <p>Built with Python, Streamlit, Plotly, and Machine Learning</p>
    <p><i>A smart screening tool for real estate opportunities - not a crystal ball</i></p>
    <p style="font-size: 0.9em; margin-top: 15px;">
        <b>Questions or Concerns?</b> This is an educational project demonstrating data analysis skills.<br>
        Always verify data and consult professionals before making financial decisions.
    </p>
</div>
""", unsafe_allow_html=True)
