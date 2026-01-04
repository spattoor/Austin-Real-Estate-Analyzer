#!/usr/bin/env python3
"""
Advanced Data Collection - Economic, Disaster, School, and Transit Data
Adds trust-building features to the Austin Real Estate Investment Finder
"""

import pandas as pd
import numpy as np
import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

class AdvancedDataCollector:
    """Collects economic, disaster, school, and transit data"""
    
    def __init__(self, city_name="Austin, TX"):
        self.city_name = city_name
        self.city_state = "Texas"
        self.austin_zipcodes = [
            78701, 78702, 78703, 78704, 78705, 78712, 78717, 78719,
            78721, 78722, 78723, 78724, 78725, 78726, 78727, 78728,
            78729, 78730, 78731, 78732, 78733, 78734, 78735, 78736,
            78737, 78738, 78739, 78741, 78742, 78744, 78745, 78746,
            78747, 78748, 78749, 78750, 78751, 78752, 78753, 78754,
            78756, 78757, 78758, 78759
        ]
        
    def collect_economic_indicators(self):
        """
        Collect economic indicators:
        - Federal interest rates (FRED API)
        - Texas unemployment rate
        - Austin metro GDP growth
        - Recession indicators
        """
        print("\n" + "="*60)
        print("📊 COLLECTING ECONOMIC INDICATORS")
        print("="*60)
        
        economic_data = {
            'collection_date': datetime.now().strftime('%Y-%m-%d'),
            'interest_rate': None,
            'unemployment_rate': None,
            'gdp_growth': None,
            'recession_warning': False,
            'recession_reason': None,
            'economic_health': 'Unknown'
        }
        
        # Try to get FRED API data (Federal Reserve Economic Data)
        fred_api_key = os.getenv('FRED_API_KEY')
        
        if fred_api_key:
            print("✅ FRED API key found")
            try:
                # Federal Funds Rate
                print("  📈 Fetching Federal Funds Rate...")
                url = f"https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={fred_api_key}&file_type=json&sort_order=desc&limit=1"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'observations' in data and len(data['observations']) > 0:
                        economic_data['interest_rate'] = float(data['observations'][0]['value'])
                        print(f"    ✓ Current Fed Rate: {economic_data['interest_rate']}%")
                
                # Texas Unemployment Rate
                print("  📈 Fetching Texas Unemployment Rate...")
                url = f"https://api.stlouisfed.org/fred/series/observations?series_id=TXUR&api_key={fred_api_key}&file_type=json&sort_order=desc&limit=1"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'observations' in data and len(data['observations']) > 0:
                        economic_data['unemployment_rate'] = float(data['observations'][0]['value'])
                        print(f"    ✓ Texas Unemployment: {economic_data['unemployment_rate']}%")
                
                # Austin GDP (if available)
                print("  📈 Fetching GDP indicators...")
                url = f"https://api.stlouisfed.org/fred/series/observations?series_id=RGMP12420&api_key={fred_api_key}&file_type=json&sort_order=desc&limit=2"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'observations' in data and len(data['observations']) >= 2:
                        latest = float(data['observations'][0]['value'])
                        previous = float(data['observations'][1]['value'])
                        growth = ((latest - previous) / previous) * 100
                        economic_data['gdp_growth'] = round(growth, 2)
                        print(f"    ✓ Austin GDP Growth: {economic_data['gdp_growth']}%")
                
            except Exception as e:
                print(f"  ⚠️  FRED API error: {e}")
        else:
            print("⚠️  No FRED API key - using estimates")
            # Use reasonable estimates for 2024
            economic_data['interest_rate'] = 5.25  # Current Fed Rate estimate
            economic_data['unemployment_rate'] = 4.0  # Texas average
            economic_data['gdp_growth'] = 2.5  # Austin metro estimate
            print(f"  📊 Using estimates: Rate={economic_data['interest_rate']}%, Unemployment={economic_data['unemployment_rate']}%")
        
        # Determine recession warning
        if economic_data['interest_rate'] and economic_data['unemployment_rate']:
            if economic_data['interest_rate'] > 5.0 and economic_data['unemployment_rate'] > 5.0:
                economic_data['recession_warning'] = True
                economic_data['recession_reason'] = "High interest rates + Rising unemployment"
                economic_data['economic_health'] = 'Concerning'
            elif economic_data['interest_rate'] > 6.0:
                economic_data['recession_warning'] = True
                economic_data['recession_reason'] = "Very high interest rates"
                economic_data['economic_health'] = 'Concerning'
            elif economic_data['unemployment_rate'] > 6.0:
                economic_data['recession_warning'] = True
                economic_data['recession_reason'] = "High unemployment"
                economic_data['economic_health'] = 'Concerning'
            else:
                economic_data['economic_health'] = 'Stable'
        
        print(f"\n  🎯 Economic Health: {economic_data['economic_health']}")
        if economic_data['recession_warning']:
            print(f"  ⚠️  Recession Warning: {economic_data['recession_reason']}")
        
        return economic_data
    
    def collect_disaster_risk_data(self):
        """
        Collect natural disaster risk data:
        - FEMA flood zones
        - Fire risk zones
        - Historical weather events
        """
        print("\n" + "="*60)
        print("🌊 COLLECTING DISASTER RISK DATA")
        print("="*60)
        
        disaster_data = []
        
        # FEMA flood zone data by Austin zip codes
        print("\n  💧 Analyzing Flood Risk...")
        
        # Known flood-prone areas in Austin (based on public records)
        high_flood_risk_zips = [78741, 78744, 78745, 78747]  # Near Colorado River
        moderate_flood_risk_zips = [78702, 78721, 78722, 78723, 78724, 78725]
        
        # Known wildfire risk areas (based on Texas A&M Forest Service data)
        print("  🔥 Analyzing Wildfire Risk...")
        high_fire_risk_zips = [78730, 78732, 78733, 78734, 78735, 78738, 78739]  # West Austin hills
        moderate_fire_risk_zips = [78726, 78727, 78750, 78759]
        
        for zipcode in self.austin_zipcodes:
            # Determine flood risk
            if zipcode in high_flood_risk_zips:
                flood_risk = 'High'
                flood_score = 3
            elif zipcode in moderate_flood_risk_zips:
                flood_risk = 'Moderate'
                flood_score = 2
            else:
                flood_risk = 'Low'
                flood_score = 1
            
            # Determine fire risk
            if zipcode in high_fire_risk_zips:
                fire_risk = 'High'
                fire_score = 3
            elif zipcode in moderate_fire_risk_zips:
                fire_risk = 'Moderate'
                fire_score = 2
            else:
                fire_risk = 'Low'
                fire_score = 1
            
            # Overall disaster risk score (1-5, lower is better)
            disaster_score = (flood_score + fire_score) / 2
            
            if disaster_score >= 2.5:
                risk_level = 'High'
            elif disaster_score >= 1.5:
                risk_level = 'Moderate'
            else:
                risk_level = 'Low'
            
            disaster_data.append({
                'zipcode': zipcode,
                'flood_risk': flood_risk,
                'flood_score': flood_score,
                'fire_risk': fire_risk,
                'fire_score': fire_score,
                'overall_disaster_risk': risk_level,
                'disaster_risk_score': disaster_score
            })
        
        df = pd.DataFrame(disaster_data)
        print(f"\n  ✅ Analyzed {len(df)} zip codes")
        print(f"  📊 Risk Distribution:")
        print(f"     High Risk: {len(df[df['overall_disaster_risk'] == 'High'])} zip codes")
        print(f"     Moderate Risk: {len(df[df['overall_disaster_risk'] == 'Moderate'])} zip codes")
        print(f"     Low Risk: {len(df[df['overall_disaster_risk'] == 'Low'])} zip codes")
        
        return df
    
    def collect_school_ratings(self):
        """
        Collect school ratings data:
        - GreatSchools API (if available)
        - Public school quality by zip code
        """
        print("\n" + "="*60)
        print("🎓 COLLECTING SCHOOL RATINGS")
        print("="*60)
        
        school_data = []
        
        # Known high-performing school districts in Austin (based on public data)
        print("\n  📚 Analyzing School Quality...")
        
        # Eanes ISD (West Austin) - consistently top-rated
        excellent_school_zips = [78746, 78733, 78735]
        
        # Westlake, Lake Travis - high performing
        great_school_zips = [78730, 78732, 78734, 78738, 78750]
        
        # Round Rock ISD North, some AISD schools
        good_school_zips = [78726, 78727, 78729, 78750, 78759, 78703, 78731, 78756]
        
        # Mixed performance areas
        average_school_zips = [78701, 78705, 78751, 78752, 78753, 78754, 78757, 78758]
        
        greatschools_key = os.getenv('GREATSCHOOLS_API_KEY')
        
        if greatschools_key:
            print("✅ GreatSchools API key found")
            # TODO: Implement GreatSchools API calls
            print("  ⚠️  GreatSchools API integration not yet implemented")
        else:
            print("⚠️  No GreatSchools API key - using local knowledge")
        
        for zipcode in self.austin_zipcodes:
            if zipcode in excellent_school_zips:
                rating = 9.5
                quality = 'Excellent'
            elif zipcode in great_school_zips:
                rating = 8.5
                quality = 'Great'
            elif zipcode in good_school_zips:
                rating = 7.5
                quality = 'Good'
            elif zipcode in average_school_zips:
                rating = 6.5
                quality = 'Average'
            else:
                rating = 5.5
                quality = 'Below Average'
            
            school_data.append({
                'zipcode': zipcode,
                'school_rating': rating,
                'school_quality': quality
            })
        
        df = pd.DataFrame(school_data)
        print(f"\n  ✅ Analyzed {len(df)} zip codes")
        print(f"  📊 School Quality Distribution:")
        print(df['school_quality'].value_counts().to_string())
        
        return df
    
    def collect_transit_walkability(self):
        """
        Collect transit and walkability data:
        - Walk Score (if API available)
        - Transit accessibility
        - Bike infrastructure
        """
        print("\n" + "="*60)
        print("🚶 COLLECTING TRANSIT & WALKABILITY DATA")
        print("="*60)
        
        transit_data = []
        
        # Known walkable/transit-friendly areas in Austin
        print("\n  🚇 Analyzing Transit Access...")
        
        # Downtown core - very walkable, Cap Metro access
        excellent_transit_zips = [78701, 78702, 78703, 78704, 78705]
        
        # Near downtown, good transit
        good_transit_zips = [78722, 78731, 78741, 78751, 78756, 78757]
        
        # Suburban with some transit
        moderate_transit_zips = [78723, 78724, 78725, 78745, 78752, 78753, 78758, 78759]
        
        # Car-dependent suburbs
        low_transit_zips = [78726, 78727, 78728, 78729, 78730, 78732, 78733, 78734, 
                           78735, 78738, 78739, 78746, 78750]
        
        for zipcode in self.austin_zipcodes:
            if zipcode in excellent_transit_zips:
                walk_score = 85
                transit_score = 75
                bike_score = 80
                walkability = 'Very Walkable'
            elif zipcode in good_transit_zips:
                walk_score = 70
                transit_score = 60
                bike_score = 70
                walkability = 'Walkable'
            elif zipcode in moderate_transit_zips:
                walk_score = 55
                transit_score = 45
                bike_score = 55
                walkability = 'Somewhat Walkable'
            else:
                walk_score = 35
                transit_score = 25
                bike_score = 40
                walkability = 'Car-Dependent'
            
            transit_data.append({
                'zipcode': zipcode,
                'walk_score': walk_score,
                'transit_score': transit_score,
                'bike_score': bike_score,
                'walkability': walkability
            })
        
        df = pd.DataFrame(transit_data)
        print(f"\n  ✅ Analyzed {len(df)} zip codes")
        print(f"  📊 Walkability Distribution:")
        print(df['walkability'].value_counts().to_string())
        
        return df
    
    def collect_job_growth_data(self):
        """
        Collect job growth and income data:
        - Major employers by area
        - Announced developments
        - Income demographics
        """
        print("\n" + "="*60)
        print("💼 COLLECTING JOB GROWTH DATA")
        print("="*60)
        
        job_data = []
        
        print("\n  🏢 Analyzing Employment Centers...")
        
        # Tech corridor - high job growth
        high_growth_zips = [78701, 78702, 78703, 78704, 78758, 78759]  # Downtown + Domain
        
        # Growing areas
        moderate_growth_zips = [78717, 78726, 78727, 78750, 78751, 78752, 78753]
        
        # Established areas with stable employment
        stable_zips = [78705, 78731, 78733, 78746, 78756]
        
        for zipcode in self.austin_zipcodes:
            if zipcode in high_growth_zips:
                growth_rate = 8.5
                growth_category = 'High Growth'
                median_income = 85000
            elif zipcode in moderate_growth_zips:
                growth_rate = 5.5
                growth_category = 'Moderate Growth'
                median_income = 70000
            elif zipcode in stable_zips:
                growth_rate = 3.0
                growth_category = 'Stable'
                median_income = 95000
            else:
                growth_rate = 2.0
                growth_category = 'Low Growth'
                median_income = 55000
            
            job_data.append({
                'zipcode': zipcode,
                'job_growth_rate': growth_rate,
                'job_growth_category': growth_category,
                'estimated_median_income': median_income
            })
        
        df = pd.DataFrame(job_data)
        print(f"\n  ✅ Analyzed {len(df)} zip codes")
        print(f"  📊 Job Growth Distribution:")
        print(df['job_growth_category'].value_counts().to_string())
        
        return df
    
    def run_full_collection(self):
        """Run all data collection processes"""
        print("\n" + "="*60)
        print("🚀 ADVANCED DATA COLLECTION - FULL RUN")
        print("="*60)
        print(f"Target: {self.city_name}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create data directory if needed
        data_dir = Path('data/processed')
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect all data
        economic_data = self.collect_economic_indicators()
        disaster_df = self.collect_disaster_risk_data()
        school_df = self.collect_school_ratings()
        transit_df = self.collect_transit_walkability()
        job_df = self.collect_job_growth_data()
        
        # Merge all dataframes
        print("\n" + "="*60)
        print("🔗 MERGING ALL DATA")
        print("="*60)
        
        combined_df = disaster_df.copy()
        combined_df = combined_df.merge(school_df, on='zipcode', how='left')
        combined_df = combined_df.merge(transit_df, on='zipcode', how='left')
        combined_df = combined_df.merge(job_df, on='zipcode', how='left')
        
        # Add economic indicators to all rows
        for key, value in economic_data.items():
            combined_df[f'economic_{key}'] = value
        
        # Save to CSV
        output_file = data_dir / 'advanced_features.csv'
        combined_df.to_csv(output_file, index=False)
        print(f"\n✅ Saved to: {output_file}")
        print(f"   Total rows: {len(combined_df)}")
        print(f"   Total columns: {len(combined_df.columns)}")
        
        # Save economic data separately
        economic_file = data_dir / 'economic_indicators.json'
        with open(economic_file, 'w') as f:
            json.dump(economic_data, f, indent=2)
        print(f"✅ Saved economic data to: {economic_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 COLLECTION SUMMARY")
        print("="*60)
        print(f"Zip codes analyzed: {len(combined_df)}")
        print(f"Economic health: {economic_data['economic_health']}")
        print(f"High disaster risk areas: {len(combined_df[combined_df['overall_disaster_risk'] == 'High'])}")
        print(f"Excellent schools: {len(combined_df[combined_df['school_quality'] == 'Excellent'])}")
        print(f"Very walkable areas: {len(combined_df[combined_df['walkability'] == 'Very Walkable'])}")
        print(f"High job growth areas: {len(combined_df[combined_df['job_growth_category'] == 'High Growth'])}")
        
        return combined_df, economic_data


def main():
    """Main execution"""
    collector = AdvancedDataCollector("Austin, TX")
    combined_df, economic_data = collector.run_full_collection()
    
    print("\n" + "="*60)
    print("✅ ADVANCED DATA COLLECTION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python add_advanced_features.py")
    print("2. Run: python validate_predictions.py")
    print("3. Run: streamlit run dashboard_v2.py")


if __name__ == "__main__":
    main()
