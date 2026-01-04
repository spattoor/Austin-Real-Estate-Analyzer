#!/usr/bin/env python3
"""
Add Confidence Scores and Data Quality Metrics
This makes the analysis more trustworthy by being honest about uncertainty
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("🛡️ ADDING TRUST METRICS TO ANALYSIS")
print("=" * 70)

# Load data
df = pd.read_csv('data/processed/neighborhoods_analyzed.csv')

# 1. ADD CONFIDENCE LEVEL based on sample size
def calculate_confidence(row):
    """Calculate confidence level based on data quality"""
    business_count = row['business_count']
    
    if business_count >= 20:
        return 'High'
    elif business_count >= 10:
        return 'Medium'
    elif business_count >= 5:
        return 'Low'
    else:
        return 'Very Low'

df['confidence_level'] = df.apply(calculate_confidence, axis=1)

# 2. ADD CONFIDENCE SCORE (0-100)
def calculate_confidence_score(row):
    """Numerical confidence based on data quality"""
    score = 0
    
    # Business count factor (max 40 points)
    if row['business_count'] >= 30:
        score += 40
    elif row['business_count'] >= 20:
        score += 35
    elif row['business_count'] >= 10:
        score += 25
    elif row['business_count'] >= 5:
        score += 15
    else:
        score += 5
    
    # Crime data factor (max 20 points)
    if row['crime_count'] > 0:
        score += 20
    else:
        score += 10  # Less confident without crime data
    
    # Amenity diversity (max 20 points)
    if row['amenity_diversity'] >= 3:
        score += 20
    elif row['amenity_diversity'] >= 2:
        score += 15
    else:
        score += 5
    
    # Review count factor (max 20 points)
    if row['total_reviews'] >= 1000:
        score += 20
    elif row['total_reviews'] >= 500:
        score += 15
    elif row['total_reviews'] >= 100:
        score += 10
    else:
        score += 5
    
    return score

df['confidence_score'] = df.apply(calculate_confidence_score, axis=1)

# 3. ADD DATA FRESHNESS
df['data_date'] = '2025-12-13'
df['data_age_days'] = 0

# 4. ADD RISK LEVEL
def calculate_risk_level(row):
    """Calculate investment risk level"""
    if row['confidence_score'] < 60:
        return 'High Risk'
    elif row['investment_score'] > 65:
        return 'Low Risk'
    elif row['investment_score'] > 55:
        return 'Medium Risk'
    else:
        return 'High Risk'

df['risk_level'] = df.apply(calculate_risk_level, axis=1)

# 5. ADD SCORE RANGE (confidence intervals)
# Simple approach: wider range for low confidence areas
def calculate_score_range(row):
    """Calculate score range based on confidence"""
    base_score = row['investment_score']
    confidence = row['confidence_score']
    
    if confidence >= 80:
        margin = 3  # ±3 points
    elif confidence >= 60:
        margin = 5  # ±5 points
    elif confidence >= 40:
        margin = 8  # ±8 points
    else:
        margin = 12  # ±12 points
    
    return f"{base_score-margin:.1f} - {base_score+margin:.1f}"

df['score_range'] = df.apply(calculate_score_range, axis=1)

# 6. ADD RECOMMENDATION CONFIDENCE
def get_recommendation_confidence(row):
    """How confident are we in our recommendation?"""
    if row['confidence_score'] >= 80 and row['business_count'] >= 20:
        return 'Strong Evidence'
    elif row['confidence_score'] >= 60 and row['business_count'] >= 10:
        return 'Moderate Evidence'
    elif row['confidence_score'] >= 40:
        return 'Limited Evidence'
    else:
        return 'Insufficient Data'

df['recommendation_strength'] = df.apply(get_recommendation_confidence, axis=1)

# 7. FLAG QUESTIONABLE SCORES
df['data_warning'] = df.apply(
    lambda x: 'Low sample size - use caution' if x['business_count'] < 5 else '', 
    axis=1
)

# Save enhanced data
df.to_csv('data/processed/neighborhoods_with_confidence.csv', index=False)

# Print summary
print("\n✅ TRUST METRICS ADDED:")
print(f"   • Confidence Level (High/Medium/Low/Very Low)")
print(f"   • Confidence Score (0-100)")
print(f"   • Risk Level (Low/Medium/High Risk)")
print(f"   • Score Range (confidence intervals)")
print(f"   • Recommendation Strength (Strong/Moderate/Limited/Insufficient)")
print(f"   • Data Warnings (flags for low sample sizes)")

print("\n📊 CONFIDENCE BREAKDOWN:")
print(df['confidence_level'].value_counts().to_string())

print("\n📊 RECOMMENDATION STRENGTH:")
print(df['recommendation_strength'].value_counts().to_string())

print("\n🎯 TOP 10 WITH CONFIDENCE SCORES:")
top = df.nlargest(10, 'investment_score')[
    ['zip_code', 'investment_score', 'confidence_level', 
     'confidence_score', 'recommendation_strength', 'business_count']
]
print(top.to_string(index=False))

print("\n⚠️  AREAS TO BE CAUTIOUS ABOUT (Low Confidence):")
low_conf = df[df['confidence_score'] < 50].nlargest(5, 'investment_score')[
    ['zip_code', 'investment_score', 'confidence_level', 
     'business_count', 'data_warning']
]
print(low_conf.to_string(index=False))

print("\n" + "=" * 70)
print("✅ Enhanced data saved to: data/processed/neighborhoods_with_confidence.csv")
print("=" * 70)
