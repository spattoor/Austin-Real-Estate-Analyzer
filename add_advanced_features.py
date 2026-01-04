#!/usr/bin/env python3
"""
Merge Advanced Features into Neighborhood Analysis
Integrates economic, disaster, school, transit, and job data into recommendations
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

def calculate_safety_adjustment(row):
    """Adjust investment score based on disaster risk"""
    if row['overall_disaster_risk'] == 'High':
        return -15  # Significant penalty
    elif row['overall_disaster_risk'] == 'Moderate':
        return -5   # Moderate penalty
    else:
        return 0    # No penalty

def calculate_family_friendliness(row):
    """Calculate family friendliness score (0-100)"""
    school_weight = 0.5
    safety_weight = 0.3
    disaster_weight = 0.2
    
    # School score (0-100)
    school_score = (row['school_rating'] / 10) * 100
    
    # Safety score (inverse of crime, normalized)
    # Assuming we have crime rate from previous analysis
    safety_score = 100 - (row.get('crime_incidents', 50))  # Placeholder
    safety_score = max(0, min(100, safety_score))
    
    # Disaster safety (inverse risk)
    if row['disaster_risk_score'] <= 1.5:
        disaster_score = 100
    elif row['disaster_risk_score'] <= 2.0:
        disaster_score = 75
    elif row['disaster_risk_score'] <= 2.5:
        disaster_score = 50
    else:
        disaster_score = 25
    
    family_score = (
        school_score * school_weight +
        safety_score * safety_weight +
        disaster_score * disaster_weight
    )
    
    return round(family_score, 1)

def calculate_long_term_potential(row):
    """Calculate long-term investment potential (0-100)"""
    job_weight = 0.35
    school_weight = 0.25
    transit_weight = 0.20
    disaster_weight = 0.20
    
    # Job growth score
    if row['job_growth_category'] == 'High Growth':
        job_score = 90
    elif row['job_growth_category'] == 'Moderate Growth':
        job_score = 70
    elif row['job_growth_category'] == 'Stable':
        job_score = 50
    else:
        job_score = 30
    
    # School score
    school_score = (row['school_rating'] / 10) * 100
    
    # Transit score (walkability implies long-term value)
    transit_score = row['walk_score']
    
    # Disaster resistance (inverse risk)
    if row['disaster_risk_score'] <= 1.5:
        disaster_score = 90
    elif row['disaster_risk_score'] <= 2.0:
        disaster_score = 70
    elif row['disaster_risk_score'] <= 2.5:
        disaster_score = 50
    else:
        disaster_score = 30
    
    potential = (
        job_score * job_weight +
        school_score * school_weight +
        transit_score * transit_weight +
        disaster_score * disaster_weight
    )
    
    return round(potential, 1)

def generate_risk_warnings(row):
    """Generate specific risk warnings for each neighborhood"""
    warnings = []
    
    if row['flood_risk'] == 'High':
        warnings.append("⚠️ HIGH FLOOD RISK - Check flood insurance costs")
    elif row['flood_risk'] == 'Moderate':
        warnings.append("⚠️ Moderate flood risk - Consider elevation")
    
    if row['fire_risk'] == 'High':
        warnings.append("🔥 HIGH WILDFIRE RISK - Verify fire insurance availability")
    elif row['fire_risk'] == 'Moderate':
        warnings.append("🔥 Moderate wildfire risk")
    
    if row['school_quality'] == 'Below Average':
        warnings.append("📚 Below-average schools - May affect resale value")
    
    if row['walkability'] == 'Car-Dependent':
        warnings.append("🚗 Car-dependent area - Limited walkability")
    
    if row.get('economic_recession_warning', False):
        warnings.append("📉 Economic warning - High interest rates or unemployment")
    
    return " | ".join(warnings) if warnings else "✅ No major risk warnings"

def generate_best_for_category(row):
    """Determine what type of buyer this neighborhood is best for"""
    categories = []
    
    # Families
    if row['school_rating'] >= 8.0 and row['disaster_risk_score'] <= 2.0:
        categories.append("👨‍👩‍👧‍👦 Families")
    
    # Young professionals
    if row['walk_score'] >= 70 and row['transit_score'] >= 60:
        categories.append("💼 Young Professionals")
    
    # Investors
    if row['job_growth_category'] in ['High Growth', 'Moderate Growth'] and row['disaster_risk_score'] <= 2.5:
        categories.append("💰 Investors")
    
    # Retirees
    if row['school_rating'] >= 7.0 and row['disaster_risk_score'] <= 2.0 and row['walkability'] in ['Walkable', 'Very Walkable']:
        categories.append("🏖️ Retirees")
    
    # Budget-conscious
    if row.get('estimated_median_income', 70000) < 70000 and row['transit_score'] >= 45:
        categories.append("💵 Budget-Conscious")
    
    return " | ".join(categories) if categories else "🏘️ General Living"

def main():
    print("="*60)
    print("🔧 ADDING ADVANCED FEATURES TO ANALYSIS")
    print("="*60)
    print()
    
    # Load existing data
    data_dir = Path('data/processed')
    
    print("📂 Loading existing data...")
    neighborhoods_df = pd.read_csv(data_dir / 'neighborhoods_with_confidence.csv')
    print(f"  ✅ Loaded {len(neighborhoods_df)} neighborhoods")
    
    # Add neighborhood names
    from neighborhood_names import AUSTIN_NEIGHBORHOODS
    neighborhoods_df['neighborhood_name'] = neighborhoods_df['zip_code'].astype(str).str.zfill(5).map(AUSTIN_NEIGHBORHOODS)
    neighborhoods_df['neighborhood_name'] = neighborhoods_df['neighborhood_name'].fillna('ZIP ' + neighborhoods_df['zip_code'].astype(str))
    
    print("📂 Loading advanced features...")
    advanced_df = pd.read_csv(data_dir / 'advanced_features.csv')
    print(f"  ✅ Loaded advanced data for {len(advanced_df)} zip codes")
    
    print("📂 Loading economic indicators...")
    with open(data_dir / 'economic_indicators.json', 'r') as f:
        economic_data = json.load(f)
    print(f"  ✅ Loaded economic data (Health: {economic_data['economic_health']})")
    
    # Ensure zipcode is integer in both dataframes
    neighborhoods_df['zip_code'] = neighborhoods_df['zip_code'].astype(int)
    advanced_df['zipcode'] = advanced_df['zipcode'].astype(int)
    
    # Rename for consistency
    advanced_df = advanced_df.rename(columns={'zipcode': 'zip_code'})
    
    # Merge data
    print("\n🔗 Merging datasets...")
    enhanced_df = neighborhoods_df.merge(
        advanced_df,
        on='zip_code',
        how='left'
    )
    
    # Calculate new features
    print("\n⚙️  Calculating enhanced features...")
    
    print("  🏗️  Safety adjustments...")
    enhanced_df['disaster_adjustment'] = enhanced_df.apply(calculate_safety_adjustment, axis=1)
    
    print("  👨‍👩‍👧 Family friendliness scores...")
    enhanced_df['family_friendliness'] = enhanced_df.apply(calculate_family_friendliness, axis=1)
    
    print("  📈 Long-term potential scores...")
    enhanced_df['long_term_potential'] = enhanced_df.apply(calculate_long_term_potential, axis=1)
    
    print("  ⚠️  Risk warnings...")
    enhanced_df['risk_warnings'] = enhanced_df.apply(generate_risk_warnings, axis=1)
    
    print("  🎯 Best buyer categories...")
    enhanced_df['best_for'] = enhanced_df.apply(generate_best_for_category, axis=1)
    
    # Adjust investment scores
    print("\n📊 Adjusting investment scores...")
    enhanced_df['original_investment_score'] = enhanced_df['investment_score']
    enhanced_df['investment_score'] = enhanced_df['investment_score'] + enhanced_df['disaster_adjustment']
    enhanced_df['investment_score'] = enhanced_df['investment_score'].clip(0, 100)
    
    # Recalculate confidence based on new data
    print("\n🎯 Recalculating confidence scores...")
    
    # More data = higher confidence
    data_completeness = enhanced_df[[
        'flood_risk', 'fire_risk', 'school_rating', 
        'walk_score', 'job_growth_rate'
    ]].notna().sum(axis=1) / 5 * 100
    
    enhanced_df['confidence_score_v2'] = (
        enhanced_df['confidence_score'] * 0.7 +
        data_completeness * 0.3
    ).round(1)
    
    # Update confidence levels
    enhanced_df['confidence_level_v2'] = pd.cut(
        enhanced_df['confidence_score_v2'],
        bins=[0, 60, 75, 85, 100],
        labels=['Low', 'Medium', 'High', 'Very High']
    )
    
    # Generate updated recommendations
    print("\n💡 Generating updated recommendations...")
    
    def generate_enhanced_recommendation(row):
        rec = []
        
        # Investment potential
        if row['investment_score'] >= 80:
            rec.append(f"🌟 TOP PICK: High investment potential (Score: {row['investment_score']:.0f}/100)")
        elif row['investment_score'] >= 70:
            rec.append(f"✅ STRONG: Good investment opportunity (Score: {row['investment_score']:.0f}/100)")
        else:
            rec.append(f"⚠️ MODERATE: Consider carefully (Score: {row['investment_score']:.0f}/100)")
        
        # Best for
        rec.append(f"Best for: {row['best_for']}")
        
        # Key strengths
        strengths = []
        if row['school_rating'] >= 8.5:
            strengths.append("Excellent schools")
        if row['walk_score'] >= 75:
            strengths.append("Very walkable")
        if row['job_growth_category'] == 'High Growth':
            strengths.append("Strong job growth")
        if row['disaster_risk_score'] <= 1.5:
            strengths.append("Low disaster risk")
        
        if strengths:
            rec.append(f"Strengths: {', '.join(strengths)}")
        
        # Risks
        if row['risk_warnings'] != "✅ No major risk warnings":
            rec.append(f"⚠️ {row['risk_warnings']}")
        
        return " | ".join(rec)
    
    enhanced_df['enhanced_recommendation'] = enhanced_df.apply(generate_enhanced_recommendation, axis=1)
    
    # Sort by investment score
    enhanced_df = enhanced_df.sort_values('investment_score', ascending=False)
    
    # Save enhanced data
    print("\n💾 Saving enhanced data...")
    
    output_file = data_dir / 'neighborhoods_enhanced.csv'
    enhanced_df.to_csv(output_file, index=False)
    print(f"  ✅ Saved to: {output_file}")
    
    # Create a summary report
    print("\n" + "="*60)
    print("📊 ENHANCED ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nTotal neighborhoods analyzed: {len(enhanced_df)}")
    print(f"\nEconomic Context:")
    print(f"  • Interest Rate: {economic_data.get('interest_rate', 'N/A')}%")
    print(f"  • Unemployment: {economic_data.get('unemployment_rate', 'N/A')}%")
    print(f"  • Economic Health: {economic_data.get('economic_health', 'Unknown')}")
    if economic_data.get('recession_warning'):
        print(f"  ⚠️ Recession Warning: {economic_data.get('recession_reason')}")
    
    print(f"\nTop 5 Neighborhoods (Enhanced Scores):")
    for idx, row in enhanced_df.head(5).iterrows():
        print(f"\n{row['neighborhood_name']} (Zip: {row['zip_code']})")
        print(f"  Investment Score: {row['investment_score']:.1f}/100")
        print(f"  Family Friendliness: {row['family_friendliness']:.1f}/100")
        print(f"  Long-Term Potential: {row['long_term_potential']:.1f}/100")
        print(f"  Confidence: {row['confidence_level_v2']} ({row['confidence_score_v2']:.1f}%)")
        print(f"  Schools: {row['school_quality']} ({row['school_rating']:.1f}/10)")
        print(f"  Disaster Risk: {row['overall_disaster_risk']}")
        print(f"  Walkability: {row['walkability']}")
        print(f"  Best For: {row['best_for']}")
    
    print(f"\n⚠️ High-Risk Areas (Disaster):")
    high_risk = enhanced_df[enhanced_df['overall_disaster_risk'] == 'High']
    print(f"  {len(high_risk)} neighborhoods with high disaster risk")
    if len(high_risk) > 0:
        for _, row in high_risk.head(3).iterrows():
            print(f"    • {row['neighborhood_name']}: {row['flood_risk']} flood risk, {row['fire_risk']} fire risk")
    
    print("\n" + "="*60)
    print("✅ ENHANCEMENT COMPLETE!")
    print("="*60)
    print("\nNext step: Run 'streamlit run dashboard_v2.py' to see the enhanced dashboard")


if __name__ == "__main__":
    main()
