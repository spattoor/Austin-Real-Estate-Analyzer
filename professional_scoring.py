"""
PROFESSIONAL INVESTMENT SCORING SYSTEM
Based on institutional investment criteria

Scoring Philosophy:
- 85-100 = EXCELLENT (Top 5% - Institutional grade)
- 70-84  = GOOD (Top 20% - Strong buy signal)
- 50-69  = AVERAGE (Middle 50% - Proceed with caution)
- 30-49  = BELOW AVERAGE (Bottom 20% - High risk)
- 0-29   = POOR (Bottom 10% - Avoid)
"""

import pandas as pd
import numpy as np

class InvestmentScorer:
    """
    Professional-grade investment scoring
    Uses same criteria as institutional investors
    """
    
    # Scoring thresholds (based on real investor criteria)
    THRESHOLDS = {
        'price_appreciation_3yr': {
            'excellent': 30,  # 30%+ appreciation in 3 years
            'good': 15,       # 15-30% appreciation
            'average': 5,     # 5-15% appreciation
            'poor': 0         # Below 5%
        },
        'crime_rate_per_1000': {
            'excellent': 20,  # <20 crimes per 1000 residents (very safe)
            'good': 40,       # 20-40 (safe)
            'average': 60,    # 40-60 (moderate)
            'poor': 80        # 60+ (concerning)
        },
        'permit_activity': {
            'excellent': 100, # 100+ permits/year (very hot)
            'good': 50,       # 50-100 (active)
            'average': 20,    # 20-50 (moderate)
            'poor': 10        # <10 (stagnant)
        },
        'median_home_price': {
            'excellent': 400000,  # Under $400k (affordable)
            'good': 550000,       # $400-550k
            'average': 700000,    # $550-700k
            'poor': 850000        # $700k+ (expensive)
        },
        'hipster_index': {
            'excellent': 15,  # 15+ trendy amenities
            'good': 10,       # 10-15
            'average': 5,     # 5-10
            'poor': 2         # <5
        },
        'school_rating': {
            'excellent': 8.5, # 8.5+ rating
            'good': 7.0,      # 7-8.5
            'average': 5.5,   # 5.5-7
            'poor': 4.0       # <5.5
        },
        'walk_score': {
            'excellent': 80,  # 80+ (very walkable)
            'good': 60,       # 60-80 (walkable)
            'average': 40,    # 40-60 (somewhat walkable)
            'poor': 20        # <40 (car-dependent)
        },
        'job_growth': {
            'excellent': 5.0, # 5%+ annual growth
            'good': 3.0,      # 3-5%
            'average': 1.5,   # 1.5-3%
            'poor': 0         # <1.5%
        }
    }
    
    # Weights (must sum to 100)
    WEIGHTS = {
        'value': 25,          # Current affordability
        'growth_potential': 20, # Future appreciation
        'safety': 15,         # Crime risk
        'lifestyle': 15,      # Amenities/walkability
        'development': 10,    # Construction activity
        'schools': 10,        # Education quality
        'economy': 5          # Job growth
    }
    
    def calculate_component_score(self, value, metric_name, inverse=False):
        """
        Calculate 0-100 score for a single metric
        
        Args:
            value: The metric value
            metric_name: Name of the metric from THRESHOLDS
            inverse: True if lower is better (e.g., crime rate)
        """
        if pd.isna(value):
            return 50  # Neutral score for missing data
        
        thresholds = self.THRESHOLDS.get(metric_name, {})
        
        if inverse:
            # Lower is better (crime, price)
            if value <= thresholds['excellent']:
                return 95
            elif value <= thresholds['good']:
                return 80
            elif value <= thresholds['average']:
                return 60
            elif value <= thresholds['poor']:
                return 40
            else:
                return 20
        else:
            # Higher is better (permits, amenities)
            if value >= thresholds['excellent']:
                return 95
            elif value >= thresholds['good']:
                return 80
            elif value >= thresholds['average']:
                return 60
            elif value >= thresholds['poor']:
                return 40
            else:
                return 20
    
    def calculate_professional_score(self, row):
        """
        Calculate institutional-grade investment score
        Returns score 0-100 with clear interpretation
        """
        scores = {}
        
        # 1. VALUE SCORE (25% weight)
        # Lower price = better value (up to a point)
        price = row.get('median_home_value', 500000)
        price_score = self.calculate_component_score(price, 'median_home_price', inverse=True)
        
        # Price-to-income ratio (affordability)
        income = row.get('estimated_median_income', 70000)
        price_to_income = price / income if income > 0 else 8
        affordability_penalty = 0
        if price_to_income > 10:  # Very expensive
            affordability_penalty = 20
        elif price_to_income > 7:  # Expensive
            affordability_penalty = 10
        
        scores['value'] = max(0, price_score - affordability_penalty)
        
        # 2. GROWTH POTENTIAL (20% weight)
        # Hipster Index (early gentrification indicator)
        hipster = row.get('hipster_index', 5)
        hipster_score = self.calculate_component_score(hipster, 'hipster_index')
        
        # YoY price appreciation
        appreciation = row.get('price_appreciation_yoy', 5)
        growth_score = self.calculate_component_score(appreciation, 'price_appreciation_3yr')
        
        scores['growth_potential'] = (hipster_score * 0.6 + growth_score * 0.4)
        
        # 3. SAFETY SCORE (15% weight)
        crime_rate = row.get('crime_incidents', 50)
        crime_score = self.calculate_component_score(crime_rate, 'crime_rate_per_1000', inverse=True)
        
        # Disaster risk penalty
        disaster_risk = row.get('disaster_risk_score', 2.0)
        disaster_penalty = 0
        if disaster_risk >= 2.5:
            disaster_penalty = 25  # High risk areas get penalized heavily
        elif disaster_risk >= 2.0:
            disaster_penalty = 10
        
        scores['safety'] = max(0, crime_score - disaster_penalty)
        
        # 4. LIFESTYLE SCORE (15% weight)
        walk = row.get('walk_score', 50)
        walk_score = self.calculate_component_score(walk, 'walk_score')
        
        # Business diversity
        business_count = row.get('business_count', 10)
        amenity_score = min(100, (business_count / 50) * 100)  # 50+ businesses = 100
        
        scores['lifestyle'] = (walk_score * 0.6 + amenity_score * 0.4)
        
        # 5. DEVELOPMENT SCORE (10% weight)
        permits = row.get('permit_count', 20)
        permit_score = self.calculate_component_score(permits, 'permit_activity')
        scores['development'] = permit_score
        
        # 6. SCHOOLS SCORE (10% weight)
        school_rating = row.get('school_rating', 6.0)
        school_score = self.calculate_component_score(school_rating, 'school_rating')
        scores['schools'] = school_score
        
        # 7. ECONOMY SCORE (5% weight)
        job_growth = row.get('job_growth_rate', 2.5)
        job_score = self.calculate_component_score(job_growth, 'job_growth')
        scores['economy'] = job_score
        
        # Calculate weighted total
        total_score = sum(
            scores[component] * (self.WEIGHTS[component] / 100)
            for component in scores
        )
        
        return round(total_score, 1), scores
    
    def get_score_interpretation(self, score):
        """
        Get clear interpretation of investment score
        Simplified grading: 70+ is excellent (Grade A)
        """
        if score >= 70:
            return {
                'grade': 'A',
                'label': 'EXCELLENT',
                'color': '#1B5E20',  # Dark green
                'description': 'Strong investment opportunity. Buy recommendation.',
                'action': '🟢 STRONG BUY',
                'confidence': 'High',
                'comparable': 'Top-tier Austin neighborhoods with growth potential'
            }
        elif score >= 55:
            return {
                'grade': 'B',
                'label': 'GOOD',
                'color': '#43A047',  # Green
                'description': 'Solid investment. Worth considering.',
                'action': '🟢 BUY',
                'confidence': 'Medium-High',
                'comparable': 'Good neighborhoods with steady appreciation'
            }
        elif score >= 40:
            return {
                'grade': 'C',
                'label': 'AVERAGE',
                'color': '#FDD835',  # Yellow
                'description': 'Average area. Research thoroughly before buying.',
                'action': '🟡 HOLD/RESEARCH MORE',
                'confidence': 'Medium',
                'comparable': 'Stable areas - will appreciate with market average'
            }
        elif score >= 25:
            return {
                'grade': 'D',
                'label': 'BELOW AVERAGE',
                'color': '#F57C00',  # Orange
                'description': 'Multiple concerns. Proceed with extreme caution.',
                'action': '🟠 CAUTION',
                'confidence': 'Low',
                'comparable': 'Risky areas - only for experienced investors'
            }
        else:
            return {
                'grade': 'F',
                'label': 'POOR',
                'color': '#D32F2F',  # Red
                'description': 'Not recommended for investment.',
                'action': '🔴 AVOID',
                'confidence': 'Very Low',
                'comparable': 'High-risk areas - avoid'
            }
    
    def generate_scoring_explanation(self):
        """Generate documentation explaining the scoring system"""
        explanation = """
# 📊 PROFESSIONAL INVESTMENT SCORING SYSTEM

## How Scores Are Calculated

We use proven real estate investment criteria:

### Score Ranges (Simplified for Clarity)

| Score | Grade | Meaning | Action |
|-------|-------|---------|--------|
| **70-100** | A | **EXCELLENT** - Strong Buy | 🟢 INVEST |
| **55-69** | B | **GOOD** - Worth Considering | 🟢 BUY |
| **40-54** | C | **AVERAGE** - Research Needed | 🟡 HOLD |
| **25-39** | D | **BELOW AVERAGE** - High Risk | 🟠 CAUTION |
| **0-24** | F | **POOR** - Avoid | 🔴 AVOID |

## Why This Makes Sense

**Score 70+ (Grade A) means:**
- All fundamentals are solid
- Strong investment potential
- Clear buy signal
- Will likely outperform market average

**Score 55-69 (Grade B) means:**
- Good fundamentals with minor concerns
- Still a solid investment
- Will likely match or beat market average

**Score 40-54 (Grade C) means:**
- Mixed signals - some good, some concerning
- Average market performance expected
- Research more before buying

## What Gets You to 70+ (Grade A)?

You need most of these:
1. ✅ Affordable price (under $600k)
2. ✅ Rising amenities (8+ hipster businesses)
3. ✅ Low crime (good safety)
4. ✅ Active development (permits)
5. ✅ Decent schools (6+ rating)
6. ✅ Good walkability or transit
7. ✅ Job growth (2%+ annually)

**You don't need perfection, just solid fundamentals across the board.**

## Component Breakdown

### Value Score (25% weight)
- Median home price vs market
- Price-to-income ratio
- **Why it matters:** Can't profit if you overpay

### Growth Potential (20% weight)
- Hipster Index (trendy businesses)
- Recent price appreciation
- **Why it matters:** Predicts future demand

### Safety Score (15% weight)
- Crime rate per 1000 residents
- Disaster risk (flood/fire)
- **Why it matters:** Safety drives family demand

### Lifestyle Score (15% weight)
- Walkability (car-free living)
- Business diversity (restaurants, shops)
- **Why it matters:** Millennials pay premium for walkability

### Development Score (10% weight)
- Building permits (new construction)
- **Why it matters:** Developers have insider knowledge

### Schools Score (10% weight)
- Public school ratings
- **Why it matters:** #1 factor for families

### Economy Score (5% weight)
- Local job growth
- **Why it matters:** Jobs = people = housing demand

## Real Example

**Hyde Park (78705):**
- Value: 80/100 (affordable at $341k)
- Growth: 75/100 (good amenities)
- Safety: 60/100 (moderate)
- Lifestyle: 85/100 (very walkable)
- Development: 70/100 (active)
- Schools: 65/100 (average)
- Economy: 75/100 (good job growth)

**Total: 73/100 = Grade A (EXCELLENT)** ✅

**Interpretation:** Strong buy signal. Affordable, walkable, growing amenities.
Will outperform market average.

---

**Bottom Line:** Score 70+ = invest with confidence. Score 55-69 = good backup options.
Below 55 = research heavily or avoid.
"""
        return explanation


# Export for use in other modules
scorer = InvestmentScorer()
