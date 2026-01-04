#!/usr/bin/env python3
"""
Phase 3: Feature Engineering & Analysis
Calculate advanced metrics, clustering, and identify undervalued neighborhoods
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

def calculate_safety_score(df):
    """Calculate safety score based on crime data"""
    print("🛡️  Calculating safety scores...")
    
    # Normalize crime count (inverse - lower crime = higher score)
    if 'crime_count' in df.columns:
        max_crime = df['crime_count'].max()
        if max_crime > 0:
            df['safety_score'] = 100 * (1 - (df['crime_count'] / max_crime))
        else:
            df['safety_score'] = 100
    else:
        df['safety_score'] = 100
    
    # Ensure between 0-100
    df['safety_score'] = df['safety_score'].clip(0, 100)
    
    print(f"  ✅ Safety scores calculated (range: {df['safety_score'].min():.1f} - {df['safety_score'].max():.1f})")
    
    return df

def calculate_density_metrics(df):
    """Calculate amenity density metrics"""
    print("\n📊 Calculating density metrics...")
    
    # Amenities per business (diversity score)
    df['amenity_diversity'] = (
        (df['coffee'] > 0).astype(int) +
        (df['breweries'] > 0).astype(int) +
        (df['vegan'] > 0).astype(int) +
        (df['yoga'] > 0).astype(int) +
        (df['organic'] > 0).astype(int)
    )
    
    # Coffee & Brewery density
    df['cafe_density'] = df['coffee'] / df['business_count'].clip(lower=1)
    df['brewery_density'] = df['breweries'] / df['business_count'].clip(lower=1)
    
    # Overall lifestyle score
    df['lifestyle_score'] = (
        df['hipster_index'] * 0.4 +
        df['amenity_diversity'] * 10 * 0.3 +
        df['avg_rating'] * 10 * 0.3
    )
    
    print(f"  ✅ Amenity diversity calculated (max categories: {df['amenity_diversity'].max():.0f})")
    print(f"  ✅ Lifestyle scores calculated")
    
    return df

def calculate_investment_score(df):
    """Calculate investment potential score"""
    print("\n💰 Calculating investment potential...")
    
    # Normalize components to 0-100 scale
    scaler = StandardScaler()
    
    # Features for investment score
    features = ['hipster_index', 'lifestyle_score', 'safety_score', 'amenity_diversity']
    available_features = [f for f in features if f in df.columns]
    
    temp_df = df[available_features].copy()
    temp_df = temp_df.fillna(0)
    
    # Normalize
    normalized = pd.DataFrame(
        scaler.fit_transform(temp_df),
        columns=available_features,
        index=df.index
    )
    
    # Investment score = weighted combination
    df['investment_score'] = (
        normalized['hipster_index'] * 0.35 +
        normalized['lifestyle_score'] * 0.35 +
        normalized['safety_score'] * 0.20 +
        normalized['amenity_diversity'] * 0.10
    ) * 10 + 50  # Scale to roughly 0-100
    
    df['investment_score'] = df['investment_score'].clip(0, 100)
    
    print(f"  ✅ Investment scores calculated (range: {df['investment_score'].min():.1f} - {df['investment_score'].max():.1f})")
    
    return df

def perform_clustering(df):
    """Cluster neighborhoods into categories"""
    print("\n🎯 Performing K-Means clustering...")
    
    # Features for clustering
    cluster_features = [
        'business_count', 
        'hipster_index', 
        'lifestyle_score',
        'safety_score',
        'investment_score'
    ]
    
    # Prepare data
    X = df[cluster_features].fillna(0)
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # K-Means clustering (3 clusters)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Label clusters based on characteristics
    cluster_stats = df.groupby('cluster').agg({
        'hipster_index': 'mean',
        'business_count': 'mean',
        'investment_score': 'mean'
    })
    
    # Sort by investment score and assign labels
    cluster_stats = cluster_stats.sort_values('investment_score', ascending=False)
    
    cluster_labels = {
        cluster_stats.index[0]: 'Established Hot Spots',
        cluster_stats.index[1]: 'Up-and-Coming',
        cluster_stats.index[2]: 'Emerging Areas'
    }
    
    df['neighborhood_type'] = df['cluster'].map(cluster_labels)
    
    print(f"  ✅ Clustered into 3 categories:")
    for cluster_id, label in cluster_labels.items():
        count = (df['cluster'] == cluster_id).sum()
        avg_score = df[df['cluster'] == cluster_id]['investment_score'].mean()
        print(f"     • {label}: {count} zip codes (avg score: {avg_score:.1f})")
    
    return df

def identify_undervalued_areas(df):
    """Find undervalued neighborhoods (high potential, not yet expensive)"""
    print("\n💎 Identifying undervalued areas...")
    
    # Undervalued = High lifestyle score, moderate business count, high safety
    # (Not yet saturated but has good fundamentals)
    
    df['undervalued_score'] = (
        df['lifestyle_score'] * 0.4 +
        df['safety_score'] * 0.3 +
        df['amenity_diversity'] * 10 * 0.3
    )
    
    # Penalize oversaturation
    median_business_count = df['business_count'].median()
    df['saturation_penalty'] = (df['business_count'] / median_business_count).clip(upper=2) - 1
    df['undervalued_score'] = df['undervalued_score'] * (1 - df['saturation_penalty'] * 0.2)
    
    # Mark top undervalued areas
    threshold = df['undervalued_score'].quantile(0.75)
    df['is_undervalued'] = (
        (df['undervalued_score'] > threshold) & 
        (df['business_count'] < df['business_count'].quantile(0.75))
    )
    
    undervalued_count = df['is_undervalued'].sum()
    print(f"  ✅ Found {undervalued_count} undervalued neighborhoods")
    
    return df

def generate_recommendations(df):
    """Generate investment recommendations"""
    print("\n📝 Generating recommendations...")
    
    recommendations = []
    
    for _, row in df.iterrows():
        rec = {
            'zip_code': row['zip_code'],
            'neighborhood_type': row['neighborhood_type'],
            'investment_score': row['investment_score'],
            'recommendation': ''
        }
        
        # Generate recommendation based on characteristics
        if row['investment_score'] > 70:
            if row['business_count'] > df['business_count'].quantile(0.75):
                rec['recommendation'] = "Established - High competition, stable returns"
            else:
                rec['recommendation'] = "⭐ Strong Buy - High potential, room to grow"
        elif row['investment_score'] > 50:
            if row['is_undervalued']:
                rec['recommendation'] = "🔥 Hidden Gem - Undervalued opportunity"
            else:
                rec['recommendation'] = "Moderate - Watch for development activity"
        else:
            if row['safety_score'] < 50:
                rec['recommendation'] = "Caution - Safety concerns"
            else:
                rec['recommendation'] = "Emerging - Long-term potential"
        
        recommendations.append(rec)
    
    rec_df = pd.DataFrame(recommendations)
    
    print("  ✅ Recommendations generated")
    
    return rec_df

def main():
    print("=" * 70)
    print("🎯 PHASE 3: FEATURE ENGINEERING & ANALYSIS")
    print("=" * 70)
    print()
    
    # Load aggregated data
    features_file = Path("data/processed/features_by_zipcode.csv")
    
    if not features_file.exists():
        print("❌ Error: Features file not found!")
        print("   Run Phase 2 first (clean_data.py)")
        return
    
    print(f"📂 Loading: {features_file}")
    df = pd.read_csv(features_file)
    print(f"  ✅ Loaded {len(df)} zip codes")
    
    # Calculate all features
    df = calculate_safety_score(df)
    df = calculate_density_metrics(df)
    df = calculate_investment_score(df)
    df = perform_clustering(df)
    df = identify_undervalued_areas(df)
    
    # Generate recommendations
    recommendations = generate_recommendations(df)
    
    # Save enhanced dataset
    output_file = Path("data/processed/neighborhoods_analyzed.csv")
    df.to_csv(output_file, index=False)
    print(f"\n💾 Saved: {output_file}")
    
    # Save recommendations
    rec_file = Path("data/processed/recommendations.csv")
    recommendations.to_csv(rec_file, index=False)
    print(f"💾 Saved: {rec_file}")
    
    # Display results
    print("\n" + "=" * 70)
    print("📊 ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    print("🏆 TOP 10 INVESTMENT OPPORTUNITIES:")
    top10 = df.nlargest(10, 'investment_score')[
        ['zip_code', 'neighborhood_type', 'business_count', 'hipster_index', 
         'safety_score', 'investment_score', 'is_undervalued']
    ]
    print(top10.to_string(index=False))
    print()
    
    print("💎 UNDERVALUED GEMS (Hidden Opportunities):")
    undervalued = df[df['is_undervalued']].nlargest(5, 'undervalued_score')[
        ['zip_code', 'business_count', 'lifestyle_score', 'safety_score', 'amenity_diversity']
    ]
    if len(undervalued) > 0:
        print(undervalued.to_string(index=False))
    else:
        print("  No clear undervalued areas found (market is efficient)")
    print()
    
    print("📊 NEIGHBORHOOD DISTRIBUTION:")
    print(df['neighborhood_type'].value_counts().to_string())
    print()
    
    print("=" * 70)
    print("✅ PHASE 3 COMPLETE!")
    print("=" * 70)
    print()
    print("📌 Key Files Created:")
    print(f"   • {output_file} - Full analysis with all features")
    print(f"   • {rec_file} - Investment recommendations")
    print()
    print("🎯 Next: Phase 4 - Create Interactive Maps!")

if __name__ == "__main__":
    main()
