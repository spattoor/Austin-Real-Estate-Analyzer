#!/usr/bin/env python3
"""
Integrate Real-Time Data with Analysis
Merges Zillow prices, crime, permits with neighborhood analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from professional_scoring import scorer

def main():
    print("="*60)
    print("🔗 INTEGRATING REAL-TIME DATA")
    print("="*60)
    
    data_dir = Path('data/processed')
    
    # Load base analysis
    print("\n📂 Loading base analysis...")
    df = pd.read_csv(data_dir / 'neighborhoods_enhanced.csv')
    print(f"   ✅ Loaded {len(df)} neighborhoods")
    
    # Load Zillow prices
    print("\n💰 Loading Zillow price data...")
    try:
        zillow_df = pd.read_csv(data_dir / 'zillow_prices_realtime.csv')
        zillow_df['zip_code'] = zillow_df['zip_code'].astype(int)
        
        # Merge prices
        df = df.merge(zillow_df[['zip_code', 'median_home_value']], on='zip_code', how='left')
        print(f"   ✅ Merged prices for {zillow_df['zip_code'].nunique()} zip codes")
        
        # Fill missing values with estimates
        df['median_home_value'] = df['median_home_value'].fillna(
            df.groupby('cluster')['median_home_value'].transform('median')
        )
        df['median_home_value'] = df['median_home_value'].fillna(500000)
        
    except Exception as e:
        print(f"   ⚠️ Error loading Zillow data: {e}")
        print("   Using estimated values...")
        df['median_home_value'] = 500000
    
    # Load real-time crime data
    print("\n🚨 Processing real-time crime data...")
    try:
        crime_df = pd.read_csv(data_dir / 'crime_data_realtime.csv')
        crime_df['zip_code'] = pd.to_numeric(crime_df['zip_code'], errors='coerce')
        crime_counts = crime_df.groupby('zip_code').size().reset_index(name='crime_incidents_90d')
        
        df = df.merge(crime_counts, on='zip_code', how='left')
        df['crime_incidents_90d'] = df['crime_incidents_90d'].fillna(0)
        
        # Update crime_incidents for scoring
        df['crime_incidents'] = df['crime_incidents_90d'] / 3  # Estimate yearly from 90 days
        
        print(f"   ✅ Updated crime data (last 90 days)")
        
    except Exception as e:
        print(f"   ⚠️ Error loading crime data: {e}")
    
    # Load permit data
    print("\n🏗️ Processing permit data...")
    try:
        permits_df = pd.read_csv(data_dir / 'permits_realtime.csv')
        # Count permits by zip
        if 'zip_code' in permits_df.columns:
            permit_counts = permits_df.groupby('zip_code').size().reset_index(name='permit_count_2024')
            df = df.merge(permit_counts, on='zip_code', how='left')
            df['permit_count_2024'] = df['permit_count_2024'].fillna(0)
            print(f"   ✅ Updated permit data (2024 YTD)")
    except Exception as e:
        print(f"   ⚠️ Error loading permit data: {e}")
    
    # Calculate professional scores
    print("\n📊 Calculating professional investment scores...")
    
    scores_list = []
    for idx, row in df.iterrows():
        score, components = scorer.calculate_professional_score(row)
        scores_list.append({
            'professional_score': score,
            'value_score': components.get('value', 50),
            'growth_score': components.get('growth_potential', 50),
            'safety_score_pro': components.get('safety', 50),
            'lifestyle_score_pro': components.get('lifestyle', 50),
            'development_score': components.get('development', 50),
            'schools_score': components.get('schools', 50),
            'economy_score': components.get('economy', 50)
        })
    
    scores_df = pd.DataFrame(scores_list)
    df = pd.concat([df, scores_df], axis=1)
    
    # Use professional score as main investment score
    df['investment_score_original'] = df['investment_score']
    df['investment_score'] = df['professional_score']
    
    # Add grade interpretations
    print("\n🎓 Adding grade interpretations...")
    df['grade'] = df['investment_score'].apply(
        lambda x: 'A' if x >= 85 else 'B' if x >= 70 else 'C' if x >= 50 else 'D' if x >= 30 else 'F'
    )
    
    df['grade_label'] = df['investment_score'].apply(
        lambda x: scorer.get_score_interpretation(x)['label']
    )
    
    df['action'] = df['investment_score'].apply(
        lambda x: scorer.get_score_interpretation(x)['action']
    )
    
    # Calculate price-to-income ratio
    df['price_to_income'] = df['median_home_value'] / df['estimated_median_income']
    df['price_to_income'] = df['price_to_income'].fillna(7.5)
    
    # Affordability category
    df['affordability'] = df['median_home_value'].apply(
        lambda x: 'Very Affordable' if x < 350000 
        else 'Affordable' if x < 500000 
        else 'Moderate' if x < 650000 
        else 'Expensive' if x < 800000 
        else 'Very Expensive'
    )
    
    # Sort by professional score
    df = df.sort_values('investment_score', ascending=False)
    
    # Save integrated data
    print("\n💾 Saving integrated data...")
    output_file = data_dir / 'neighborhoods_professional.csv'
    df.to_csv(output_file, index=False)
    print(f"   ✅ Saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 PROFESSIONAL ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nTotal neighborhoods: {len(df)}")
    print(f"\nGrade Distribution:")
    print(df['grade'].value_counts().sort_index())
    
    print(f"\nTop 5 Investment Opportunities:")
    for idx, row in df.head(5).iterrows():
        print(f"\n{row['neighborhood_name']} (ZIP {row['zip_code']})")
        print(f"  Score: {row['investment_score']:.1f}/100 - Grade {row['grade']} ({row['grade_label']})")
        print(f"  Action: {row['action']}")
        print(f"  Price: ${row['median_home_value']:,.0f}")
        print(f"  Schools: {row['school_rating']:.1f}/10")
        print(f"  Safety: {row['safety_score_pro']:.0f}/100")
    
    print(f"\n⚠️ High-Price Areas (>$700k):")
    expensive = df[df['median_home_value'] > 700000]
    print(f"  {len(expensive)} neighborhoods")
    if len(expensive) > 0:
        for _, row in expensive.head(3).iterrows():
            print(f"    • {row['neighborhood_name']}: ${row['median_home_value']:,.0f}")
    
    print(f"\n🌟 Affordable Grade A/B (<$500k):")
    affordable_good = df[(df['median_home_value'] < 500000) & (df['grade'].isin(['A', 'B']))]
    print(f"  {len(affordable_good)} neighborhoods - THESE ARE YOUR BEST BETS!")
    if len(affordable_good) > 0:
        for _, row in affordable_good.head(5).iterrows():
            print(f"    • {row['neighborhood_name']}: ${row['median_home_value']:,.0f} - Grade {row['grade']}")
    
    print("\n" + "="*60)
    print("✅ INTEGRATION COMPLETE!")
    print("="*60)
    print("\nNext step: Run 'streamlit run professional_dashboard.py'")


if __name__ == "__main__":
    main()
