#!/usr/bin/env python3
"""
Phase 2: Data Cleaning & Enrichment
Clean Yelp data and add Austin crime/permit data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import requests
import time

def clean_yelp_data(df):
    """Clean and prepare Yelp data"""
    print("🧹 Cleaning Yelp data...")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['id'], keep='first')
    print(f"  ✅ Removed {initial_count - len(df)} duplicate businesses")
    
    # Handle missing coordinates
    missing_coords = df[df['latitude'].isna() | df['longitude'].isna()]
    print(f"  ⚠️  {len(missing_coords)} businesses missing coordinates (will be removed)")
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Clean zip codes
    df['zip_code'] = df['zip_code'].astype(str).str[:5]
    
    # Add price level (convert $ to numeric)
    price_map = {'N/A': 0, '$': 1, '$$': 2, '$$$': 3, '$$$$': 4}
    df['price_level'] = df['price'].map(price_map).fillna(0)
    
    print(f"  ✅ Cleaned data: {len(df)} businesses ready")
    
    return df

def download_austin_crime_data():
    """Download Austin crime data from open data portal"""
    print("\n🚔 Downloading Austin crime data...")
    
    # Austin Open Data Portal - Crime Reports (last 12 months)
    # Using Socrata API
    url = "https://data.austintexas.gov/resource/fdj4-gpfu.json"
    
    # Get recent crime data (limit to 10,000 for now)
    params = {
        "$limit": 10000,
        "$order": "occ_date DESC",
        "$where": "occ_date > '2023-01-01T00:00:00.000'"
    }
    
    try:
        print("  📥 Fetching from Austin Open Data Portal...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)
        
        print(f"  ✅ Downloaded {len(df)} crime records")
        
        # Clean column names
        df = df.rename(columns={
            'latitude': 'crime_lat',
            'longitude': 'crime_lon',
            'occ_date': 'date',
            'clearance_status': 'status',
            'category_description': 'crime_type',
            'zip_code': 'zip_code'
        })
        
        # Select relevant columns
        columns_to_keep = ['date', 'crime_lat', 'crime_lon', 'crime_type', 'status', 'zip_code']
        available_cols = [col for col in columns_to_keep if col in df.columns]
        df = df[available_cols]
        
        # Convert coordinates to numeric
        if 'crime_lat' in df.columns and 'crime_lon' in df.columns:
            df['crime_lat'] = pd.to_numeric(df['crime_lat'], errors='coerce')
            df['crime_lon'] = pd.to_numeric(df['crime_lon'], errors='coerce')
            df = df.dropna(subset=['crime_lat', 'crime_lon'])
        
        print(f"  ✅ Processed {len(df)} crime records with valid coordinates")
        
        return df
        
    except Exception as e:
        print(f"  ⚠️  Error downloading crime data: {e}")
        print("  📝 Creating placeholder data...")
        return pd.DataFrame()

def download_austin_permits():
    """Download Austin building permit data"""
    print("\n🏗️  Downloading Austin building permits...")
    
    # Austin Open Data Portal - Issued Construction Permits
    url = "https://data.austintexas.gov/resource/3syk-w9eu.json"
    
    params = {
        "$limit": 5000,
        "$order": "issue_date DESC",
        "$where": "issue_date > '2023-01-01T00:00:00.000'"
    }
    
    try:
        print("  📥 Fetching from Austin Open Data Portal...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)
        
        print(f"  ✅ Downloaded {len(df)} building permits")
        
        # Clean columns
        df = df.rename(columns={
            'latitude': 'permit_lat',
            'longitude': 'permit_lon',
            'issue_date': 'date',
            'work_type': 'permit_type',
            'total_existing_bldg_sqft': 'building_sqft'
        })
        
        # Select relevant columns
        columns_to_keep = ['date', 'permit_lat', 'permit_lon', 'permit_type', 'building_sqft']
        available_cols = [col for col in columns_to_keep if col in df.columns]
        df = df[available_cols]
        
        # Convert coordinates to numeric
        if 'permit_lat' in df.columns and 'permit_lon' in df.columns:
            df['permit_lat'] = pd.to_numeric(df['permit_lat'], errors='coerce')
            df['permit_lon'] = pd.to_numeric(df['permit_lon'], errors='coerce')
            df = df.dropna(subset=['permit_lat', 'permit_lon'])
        
        print(f"  ✅ Processed {len(df)} permits with valid coordinates")
        
        return df
        
    except Exception as e:
        print(f"  ⚠️  Error downloading permit data: {e}")
        print("  📝 Creating placeholder data...")
        return pd.DataFrame()

def aggregate_by_zipcode(yelp_df, crime_df, permit_df):
    """Aggregate all data by zip code"""
    print("\n📊 Aggregating data by zip code...")
    
    # Yelp metrics by zip code
    yelp_by_zip = yelp_df.groupby('zip_code').agg({
        'id': 'count',
        'rating': 'mean',
        'review_count': 'sum',
        'price_level': 'mean'
    }).rename(columns={
        'id': 'business_count',
        'rating': 'avg_rating',
        'review_count': 'total_reviews',
        'price_level': 'avg_price_level'
    })
    
    # Count by category
    category_counts = yelp_df.groupby(['zip_code', 'category']).size().unstack(fill_value=0)
    
    # Combine
    result = yelp_by_zip.join(category_counts)
    
    # Add crime data if available
    if not crime_df.empty and 'zip_code' in crime_df.columns:
        crime_by_zip = crime_df.groupby('zip_code').size().rename('crime_count')
        result = result.join(crime_by_zip, how='left')
        result['crime_count'] = result['crime_count'].fillna(0)
        print(f"  ✅ Added crime data for {len(crime_by_zip)} zip codes")
    else:
        result['crime_count'] = 0
        print("  ⚠️  No crime data available")
    
    # Calculate "Hipster Index"
    result['hipster_index'] = (
        result.get('breweries', 0) * 0.5 + 
        result.get('coffee', 0) * 0.3 + 
        result['avg_rating'] * 0.2
    )
    
    print(f"  ✅ Aggregated data for {len(result)} zip codes")
    
    return result.reset_index()

def main():
    print("=" * 60)
    print("🏙️  PHASE 2: DATA CLEANING & ENRICHMENT")
    print("=" * 60)
    print()
    
    # Load Yelp data
    yelp_file = Path("data/raw/yelp_austin_20251213.csv")
    
    if not yelp_file.exists():
        print("❌ Error: Yelp data not found!")
        print(f"   Looking for: {yelp_file}")
        return
    
    print(f"📂 Loading: {yelp_file}")
    yelp_df = pd.read_csv(yelp_file)
    print(f"  ✅ Loaded {len(yelp_df)} Yelp businesses")
    
    # Clean Yelp data
    yelp_clean = clean_yelp_data(yelp_df)
    
    # Download Austin crime data
    crime_df = download_austin_crime_data()
    
    # Download Austin permit data
    permit_df = download_austin_permits()
    
    # Aggregate by zip code
    aggregated = aggregate_by_zipcode(yelp_clean, crime_df, permit_df)
    
    # Save processed data
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Save cleaned Yelp data
    yelp_clean_file = processed_dir / "yelp_cleaned.csv"
    yelp_clean.to_csv(yelp_clean_file, index=False)
    print(f"\n💾 Saved: {yelp_clean_file}")
    
    # Save crime data
    if not crime_df.empty:
        crime_file = processed_dir / "crime_data.csv"
        crime_df.to_csv(crime_file, index=False)
        print(f"💾 Saved: {crime_file}")
    
    # Save permit data
    if not permit_df.empty:
        permit_file = processed_dir / "permit_data.csv"
        permit_df.to_csv(permit_file, index=False)
        print(f"💾 Saved: {permit_file}")
    
    # Save aggregated data
    agg_file = processed_dir / "features_by_zipcode.csv"
    aggregated.to_csv(agg_file, index=False)
    print(f"💾 Saved: {agg_file}")
    
    print("\n" + "=" * 60)
    print("📊 PHASE 2 SUMMARY")
    print("=" * 60)
    print(f"Cleaned businesses: {len(yelp_clean)}")
    print(f"Crime records: {len(crime_df)}")
    print(f"Building permits: {len(permit_df)}")
    print(f"Zip codes analyzed: {len(aggregated)}")
    print()
    
    # Show top zip codes by Hipster Index
    print("🏆 TOP 5 ZIP CODES (Hipster Index):")
    top_zips = aggregated.nlargest(5, 'hipster_index')[['zip_code', 'business_count', 'avg_rating', 'hipster_index']]
    print(top_zips.to_string(index=False))
    print()
    
    print("✅ Phase 2 Complete!")
    print()
    print("Next: Phase 3 - Feature Engineering & Analysis")

if __name__ == "__main__":
    main()
