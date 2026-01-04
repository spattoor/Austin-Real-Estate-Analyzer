#!/usr/bin/env python3
"""
Phase 4: Interactive Visualization & Mapping
Create beautiful maps and charts for portfolio presentation
"""

import pandas as pd
import numpy as np
from pathlib import Path
import folium
from folium import plugins
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def create_investment_map(df):
    """Create interactive map with investment scores"""
    print("🗺️  Creating investment opportunity map...")
    
    # Austin center coordinates
    austin_center = [30.2672, -97.7431]
    
    # Create base map
    m = folium.Map(
        location=austin_center,
        zoom_start=11,
        tiles='CartoDB positron'
    )
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 500px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
        <h4 style="margin:0">🏙️ Austin Neighborhood Investment Analysis</h4>
        <p style="margin:5px 0"><b>Color Scale:</b> Green = High Investment Score | Red = Lower Score</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Color mapping based on investment score
    def get_color(score):
        if score > 65:
            return 'green'
        elif score > 55:
            return 'lightgreen'
        elif score > 50:
            return 'orange'
        else:
            return 'red'
    
    # Get business locations from cleaned Yelp data
    yelp_file = Path("data/processed/yelp_cleaned.csv")
    if yelp_file.exists():
        yelp_df = pd.read_csv(yelp_file)
        
        # Merge with analysis
        yelp_with_scores = yelp_df.merge(
            df[['zip_code', 'investment_score', 'neighborhood_type', 'hipster_index']], 
            on='zip_code', 
            how='left'
        )
        
        # Add markers for top businesses in top neighborhoods
        top_zips = df.nlargest(10, 'investment_score')['zip_code'].values
        top_businesses = yelp_with_scores[yelp_with_scores['zip_code'].isin(top_zips)]
        
        # Sample to avoid overcrowding
        if len(top_businesses) > 100:
            top_businesses = top_businesses.sample(100, random_state=42)
        
        # Create marker cluster
        marker_cluster = plugins.MarkerCluster(name="Businesses").add_to(m)
        
        for _, row in top_businesses.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                popup_html = f"""
                <div style="width:200px">
                    <b>{row['name']}</b><br>
                    ⭐ Rating: {row['rating']}<br>
                    📍 Zip: {row['zip_code']}<br>
                    🏆 Investment Score: {row['investment_score']:.1f}<br>
                    📊 Type: {row['neighborhood_type']}<br>
                    🎯 Category: {row['category']}
                </div>
                """
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=3,
                    popup=folium.Popup(popup_html, max_width=250),
                    color=get_color(row['investment_score']),
                    fill=True,
                    fillColor=get_color(row['investment_score']),
                    fillOpacity=0.6
                ).add_to(marker_cluster)
    
    # Add zip code centroids with scores
    for _, row in df.iterrows():
        # Calculate centroid (using business locations in that zip)
        if yelp_file.exists():
            zip_businesses = yelp_with_scores[yelp_with_scores['zip_code'] == row['zip_code']]
            if len(zip_businesses) > 0:
                lat = zip_businesses['latitude'].mean()
                lon = zip_businesses['longitude'].mean()
                
                if pd.notna(lat) and pd.notna(lon):
                    # Create popup
                    popup_html = f"""
                    <div style="width:250px; font-family: Arial">
                        <h4 style="margin:0; color:#333">Zip Code: {row['zip_code']}</h4>
                        <hr style="margin:5px 0">
                        <b>🏆 Investment Score:</b> {row['investment_score']:.1f}/100<br>
                        <b>📊 Type:</b> {row['neighborhood_type']}<br>
                        <b>🏪 Businesses:</b> {row['business_count']}<br>
                        <b>⭐ Avg Rating:</b> {row['avg_rating']:.2f}<br>
                        <b>🎯 Hipster Index:</b> {row['hipster_index']:.1f}<br>
                        <b>☕ Coffee Shops:</b> {row.get('coffee', 0):.0f}<br>
                        <b>🍺 Breweries:</b> {row.get('breweries', 0):.0f}<br>
                        <b>🛡️ Safety:</b> {row['safety_score']:.0f}/100<br>
                        {'<b style="color:green">💎 Undervalued!</b>' if row.get('is_undervalued', False) else ''}
                    </div>
                    """
                    
                    # Larger marker for zip centroids
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=8,
                        popup=folium.Popup(popup_html, max_width=300),
                        color=get_color(row['investment_score']),
                        fill=True,
                        fillColor=get_color(row['investment_score']),
                        fillOpacity=0.8,
                        weight=2
                    ).add_to(m)
                    
                    # Add label for top neighborhoods
                    if row['investment_score'] > 65:
                        folium.Marker(
                            location=[lat, lon],
                            icon=folium.DivIcon(html=f"""
                                <div style="font-size: 10pt; color: black; font-weight: bold; 
                                            background-color: white; padding: 2px 5px; 
                                            border-radius: 3px; border: 1px solid #333">
                                    {row['zip_code']}
                                </div>
                            """)
                        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    output_file = Path("outputs/maps/investment_map.html")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output_file))
    
    print(f"  ✅ Saved: {output_file}")
    return output_file

def create_static_charts(df):
    """Create static charts for analysis"""
    print("\n📊 Creating static visualizations...")
    
    output_dir = Path("outputs/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Investment Score Distribution
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(data=df, x='investment_score', bins=20, kde=True, color='#2E86AB')
    plt.title('Investment Score Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Investment Score')
    plt.ylabel('Number of Zip Codes')
    
    plt.subplot(1, 2, 2)
    neighborhood_counts = df['neighborhood_type'].value_counts()
    colors = ['#A23B72', '#F18F01', '#C73E1D']
    plt.pie(neighborhood_counts.values, labels=neighborhood_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90)
    plt.title('Neighborhood Type Distribution', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'distribution_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ Saved: distribution_analysis.png")
    
    # 2. Top Neighborhoods Comparison
    plt.figure(figsize=(14, 8))
    top10 = df.nlargest(10, 'investment_score')
    
    x = np.arange(len(top10))
    width = 0.35
    
    plt.bar(x - width/2, top10['hipster_index'], width, label='Hipster Index', color='#06A77D')
    plt.bar(x + width/2, top10['investment_score'], width, label='Investment Score', color='#D4A017')
    
    plt.xlabel('Zip Code', fontsize=12, fontweight='bold')
    plt.ylabel('Score', fontsize=12, fontweight='bold')
    plt.title('Top 10 Neighborhoods: Hipster Index vs Investment Score', fontsize=14, fontweight='bold')
    plt.xticks(x, top10['zip_code'], rotation=45)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'top_neighborhoods.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ Saved: top_neighborhoods.png")
    
    # 3. Scatter: Business Count vs Investment Score
    plt.figure(figsize=(10, 8))
    
    for ntype in df['neighborhood_type'].unique():
        subset = df[df['neighborhood_type'] == ntype]
        plt.scatter(subset['business_count'], subset['investment_score'], 
                   label=ntype, s=100, alpha=0.6)
    
    plt.xlabel('Number of Businesses', fontsize=12, fontweight='bold')
    plt.ylabel('Investment Score', fontsize=12, fontweight='bold')
    plt.title('Business Density vs Investment Potential', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'density_vs_investment.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ Saved: density_vs_investment.png")
    
    # 4. Category Breakdown Heatmap
    plt.figure(figsize=(10, 8))
    
    top15 = df.nlargest(15, 'investment_score')
    categories = ['coffee', 'breweries', 'vegan', 'yoga', 'organic']
    heatmap_data = top15[categories].T
    
    sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', 
                xticklabels=top15['zip_code'], yticklabels=categories,
                cbar_kws={'label': 'Count'})
    plt.title('Top 15 Neighborhoods: Amenity Breakdown', fontsize=14, fontweight='bold')
    plt.xlabel('Zip Code', fontsize=12, fontweight='bold')
    plt.ylabel('Category', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'amenity_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ Saved: amenity_heatmap.png")

def create_interactive_plotly_charts(df):
    """Create interactive Plotly visualizations"""
    print("\n📈 Creating interactive charts...")
    
    output_dir = Path("outputs/figures")
    
    # 1. Interactive 3D Scatter
    fig = px.scatter_3d(
        df, 
        x='business_count', 
        y='hipster_index', 
        z='investment_score',
        color='neighborhood_type',
        size='business_count',
        hover_data=['zip_code', 'avg_rating', 'safety_score'],
        title='3D Analysis: Business Count vs Hipster Index vs Investment Score',
        labels={
            'business_count': 'Number of Businesses',
            'hipster_index': 'Hipster Index',
            'investment_score': 'Investment Score'
        }
    )
    
    fig.update_layout(height=700)
    fig.write_html(str(output_dir / '3d_scatter.html'))
    print(f"  ✅ Saved: 3d_scatter.html")
    
    # 2. Interactive Bar Chart
    top15 = df.nlargest(15, 'investment_score').sort_values('investment_score')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top15['zip_code'].astype(str),
        x=top15['investment_score'],
        orientation='h',
        marker=dict(
            color=top15['investment_score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Score")
        ),
        text=top15['investment_score'].round(1),
        textposition='outside',
        hovertemplate='<b>Zip: %{y}</b><br>Score: %{x:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Top 15 Investment Opportunities',
        xaxis_title='Investment Score',
        yaxis_title='Zip Code',
        height=600,
        showlegend=False
    )
    
    fig.write_html(str(output_dir / 'top_investments_interactive.html'))
    print(f"  ✅ Saved: top_investments_interactive.html")

def main():
    print("=" * 70)
    print("🎨 PHASE 4: VISUALIZATION & MAPPING")
    print("=" * 70)
    print()
    
    # Load analyzed data
    analysis_file = Path("data/processed/neighborhoods_analyzed.csv")
    
    if not analysis_file.exists():
        print("❌ Error: Analysis file not found!")
        print("   Run Phase 3 first (analyze_neighborhoods.py)")
        return
    
    print(f"📂 Loading: {analysis_file}")
    df = pd.read_csv(analysis_file)
    print(f"  ✅ Loaded {len(df)} neighborhoods")
    print()
    
    # Create visualizations
    map_file = create_investment_map(df)
    create_static_charts(df)
    create_interactive_plotly_charts(df)
    
    print("\n" + "=" * 70)
    print("✅ PHASE 4 COMPLETE - VISUALIZATIONS CREATED!")
    print("=" * 70)
    print()
    print("📁 Generated Files:")
    print("   Maps:")
    print("   • outputs/maps/investment_map.html")
    print()
    print("   Static Charts:")
    print("   • outputs/figures/distribution_analysis.png")
    print("   • outputs/figures/top_neighborhoods.png")
    print("   • outputs/figures/density_vs_investment.png")
    print("   • outputs/figures/amenity_heatmap.png")
    print()
    print("   Interactive Charts:")
    print("   • outputs/figures/3d_scatter.html")
    print("   • outputs/figures/top_investments_interactive.html")
    print()
    print("🌐 To view the interactive map, run:")
    print(f"   open {map_file}")
    print()
    print("🎯 Next: Phase 5 - Final Report & Documentation")

if __name__ == "__main__":
    main()
