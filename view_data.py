#!/usr/bin/env python3
"""
Data Viewer - Explore Phase 1 & 2 Results
"""

import pandas as pd
from pathlib import Path

def view_phase1_data():
    """View Phase 1: Raw Yelp Data"""
    print("=" * 70)
    print("📊 PHASE 1: RAW DATA COLLECTION")
    print("=" * 70)
    print()
    
    file = Path("data/raw/yelp_austin_20251213.csv")
    df = pd.read_csv(file)
    
    print(f"📂 File: {file}")
    print(f"📏 Size: {file.stat().st_size / 1024:.1f} KB")
    print(f"📊 Rows: {len(df):,} | Columns: {len(df.columns)}")
    print()
    
    print("📋 Column Names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2}. {col}")
    print()
    
    print("🔍 Sample Data (First 5 Businesses):")
    print(df[['name', 'rating', 'review_count', 'category', 'zip_code', 'address']].head().to_string(index=False))
    print()
    
    print("📊 Category Breakdown:")
    print(df['category'].value_counts().to_string())
    print()
    
    print("⭐ Rating Statistics:")
    print(df['rating'].describe().to_string())
    print()
    
    print("🗺️  Top 5 Zip Codes by Business Count:")
    print(df['zip_code'].value_counts().head().to_string())
    print()

def view_phase2_data():
    """View Phase 2: Cleaned & Enriched Data"""
    print("=" * 70)
    print("🧹 PHASE 2: CLEANED & ENRICHED DATA")
    print("=" * 70)
    print()
    
    # 1. Cleaned Yelp Data
    print("1️⃣  CLEANED YELP DATA")
    print("-" * 70)
    yelp_file = Path("data/processed/yelp_cleaned.csv")
    yelp_df = pd.read_csv(yelp_file)
    print(f"📂 File: {yelp_file}")
    print(f"📊 Rows: {len(yelp_df):,} | Columns: {len(yelp_df.columns)}")
    print(f"✅ Improvements: Removed duplicates, added price_level column")
    print()
    
    # 2. Crime Data
    print("2️⃣  CRIME DATA")
    print("-" * 70)
    crime_file = Path("data/processed/crime_data.csv")
    crime_df = pd.read_csv(crime_file)
    print(f"📂 File: {crime_file}")
    print(f"📊 Rows: {len(crime_df):,} crime incidents")
    print(f"📅 Time period: Recent 12 months")
    print()
    if 'crime_type' in crime_df.columns:
        print("🚔 Top 5 Crime Types:")
        print(crime_df['crime_type'].value_counts().head().to_string())
    print()
    
    # 3. Building Permits
    print("3️⃣  BUILDING PERMITS")
    print("-" * 70)
    permit_file = Path("data/processed/permit_data.csv")
    permit_df = pd.read_csv(permit_file)
    print(f"📂 File: {permit_file}")
    print(f"📊 Rows: {len(permit_df):,} building permits")
    print(f"🏗️  Development activity tracked")
    print()
    
    # 4. Aggregated Features by Zip Code
    print("4️⃣  FEATURES BY ZIP CODE (Master Dataset)")
    print("-" * 70)
    features_file = Path("data/processed/features_by_zipcode.csv")
    features_df = pd.read_csv(features_file)
    print(f"📂 File: {features_file}")
    print(f"📊 Rows: {len(features_df)} zip codes analyzed")
    print()
    
    print("📋 Available Features:")
    for i, col in enumerate(features_df.columns, 1):
        print(f"  {i:2}. {col}")
    print()
    
    print("🏆 TOP 10 NEIGHBORHOODS (by Hipster Index):")
    top10 = features_df.nlargest(10, 'hipster_index')[
        ['zip_code', 'business_count', 'coffee', 'breweries', 'avg_rating', 'hipster_index']
    ]
    print(top10.to_string(index=False))
    print()
    
    print("📊 Summary Statistics (All Zip Codes):")
    print(features_df[['business_count', 'avg_rating', 'hipster_index']].describe().to_string())
    print()

def view_file_locations():
    """Show where all files are located"""
    print("=" * 70)
    print("📁 FILE LOCATIONS")
    print("=" * 70)
    print()
    
    print("🗂️  Your Project Structure:")
    print()
    print("winter_project/")
    print("├── data/")
    print("│   ├── raw/                    ← Phase 1 Data")
    print("│   │   └── yelp_austin_20251213.csv")
    print("│   └── processed/              ← Phase 2 Data")
    print("│       ├── yelp_cleaned.csv")
    print("│       ├── crime_data.csv")
    print("│       ├── permit_data.csv")
    print("│       └── features_by_zipcode.csv  ← **Main Dataset**")
    print("├── collect_data.py             ← Phase 1 Script")
    print("├── clean_data.py               ← Phase 2 Script")
    print("└── view_data.py                ← This Script")
    print()
    
    print("💡 HOW TO OPEN THE DATA:")
    print()
    print("Option 1: In Terminal (Quick Preview)")
    print("  $ head -20 data/processed/features_by_zipcode.csv")
    print()
    print("Option 2: In Excel/Numbers/Google Sheets")
    print("  1. Open Finder")
    print("  2. Navigate to: /Users/saiabhinavpattoor/winter_project/data/processed/")
    print("  3. Double-click any .csv file")
    print()
    print("Option 3: In Python (for analysis)")
    print("  >>> import pandas as pd")
    print("  >>> df = pd.read_csv('data/processed/features_by_zipcode.csv')")
    print("  >>> df.head()")
    print()
    print("Option 4: Open folder in Finder")
    print("  $ open data/processed/")
    print()

def main():
    print("\n")
    print("🎯" * 35)
    print("   DATA VIEWER - AUSTIN NEIGHBORHOOD ANALYSIS")
    print("🎯" * 35)
    print()
    
    # Phase 1 Data
    view_phase1_data()
    
    # Phase 2 Data
    view_phase2_data()
    
    # File Locations
    view_file_locations()
    
    print("=" * 70)
    print("✅ DATA EXPLORATION COMPLETE")
    print("=" * 70)
    print()
    print("📌 KEY TAKEAWAY:")
    print("   The main dataset is: data/processed/features_by_zipcode.csv")
    print("   This contains all the aggregated metrics for analysis!")
    print()

if __name__ == "__main__":
    main()
