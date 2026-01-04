#!/usr/bin/env python3
"""
Quick Data Collection Script for Austin, TX
Run this to collect Yelp data directly
"""

import pandas as pd
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search_yelp_businesses(api_key, term, location, limit=50):
    """Search Yelp API for businesses"""
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    all_businesses = []
    offset = 0
    max_offset = 1000
    
    while offset < max_offset:
        params = {
            "term": term,
            "location": location,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            businesses = data.get('businesses', [])
            if not businesses:
                break
                
            all_businesses.extend(businesses)
            print(f"  📥 Fetched {len(businesses)} businesses (Total: {len(all_businesses)})")
            
            if len(businesses) < limit:
                break
                
            offset += limit
            time.sleep(0.2)
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error: {e}")
            break
    
    return all_businesses

def extract_business_info(businesses):
    """Convert to DataFrame"""
    data = []
    
    for biz in businesses:
        data.append({
            'id': biz.get('id'),
            'name': biz.get('name'),
            'rating': biz.get('rating'),
            'review_count': biz.get('review_count'),
            'price': biz.get('price', 'N/A'),
            'latitude': biz.get('coordinates', {}).get('latitude'),
            'longitude': biz.get('coordinates', {}).get('longitude'),
            'address': biz.get('location', {}).get('address1'),
            'city': biz.get('location', {}).get('city'),
            'zip_code': biz.get('location', {}).get('zip_code'),
            'categories': ', '.join([cat['title'] for cat in biz.get('categories', [])]),
        })
    
    return pd.DataFrame(data)

def main():
    print("=" * 60)
    print("🏙️  NEXT HOT NEIGHBORHOOD PREDICTOR - DATA COLLECTION")
    print("=" * 60)
    print()
    
    # Configuration
    CITY_NAME = "Austin, TX"
    CITY_POPULATION = 978908
    
    print(f"🎯 Target City: {CITY_NAME}")
    print(f"👥 Population: {CITY_POPULATION:,}")
    print()
    
    # Load API key
    YELP_API_KEY = os.getenv('YELP_API_KEY')
    
    if not YELP_API_KEY:
        print("❌ ERROR: Yelp API key not found!")
        print("   Make sure your .env file exists with YELP_API_KEY")
        return
    
    print(f"✅ API key loaded (length: {len(YELP_API_KEY)})")
    print()
    
    # Categories to search
    categories = {
        'coffee': 'Coffee & Tea',
        'breweries': 'Breweries',
        'vegan': 'Vegan Restaurants',
        'yoga': 'Yoga Studios',
        'organic': 'Organic Stores'
    }
    
    # Collect data
    all_data = {}
    
    print("🔍 Starting data collection...")
    print()
    
    for term, description in categories.items():
        print(f"📍 Searching for: {description}")
        businesses = search_yelp_businesses(
            api_key=YELP_API_KEY,
            term=term,
            location=CITY_NAME,
            limit=50
        )
        
        df = extract_business_info(businesses)
        all_data[term] = df
        print(f"  ✅ Found {len(df)} locations")
        print()
    
    # Combine all data
    combined_df = pd.concat([
        df.assign(category=cat) for cat, df in all_data.items()
    ], ignore_index=True)
    
    print("=" * 60)
    print(f"📊 COLLECTION SUMMARY")
    print("=" * 60)
    print(f"Total businesses: {len(combined_df)}")
    print(f"Unique locations: {combined_df['id'].nunique()}")
    print()
    print("By category:")
    print(combined_df['category'].value_counts().to_string())
    print()
    
    # Save to CSV
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f"yelp_austin_{timestamp}.csv"
    filepath = data_dir / filename
    
    combined_df.to_csv(filepath, index=False)
    
    print("=" * 60)
    print("✅ DATA SAVED")
    print("=" * 60)
    print(f"File: {filepath}")
    print(f"Rows: {len(combined_df)}")
    print(f"Columns: {len(combined_df.columns)}")
    print(f"Size: {filepath.stat().st_size / 1024:.2f} KB")
    print()
    print("🎉 Data collection complete!")
    print()
    print("Next step: Run the data cleaning script")

if __name__ == "__main__":
    main()
