# 📚 Data Sources - What We Used & What We Could Add

## ✅ **ACTUALLY USED IN THIS PROJECT:**

### **1. Yelp API (1,000 businesses)**
**Categories collected:**
- ☕ Coffee shops (200)
- 🍺 Breweries (200)
- 🥗 Vegan restaurants (200)
- 🧘 Yoga studios (200)
- 🌱 Organic stores (200)

**Why these?** These are "hipster indicators" - early signals of gentrification

### **2. Austin Crime Data (10,000 incidents)**
**Source:** Austin Police Department
**Used for:** Safety Score calculation

### **3. Building Permits (4,995 permits)**
**Source:** City of Austin
**Used for:** Development activity tracking

---

## ❌ **NOT USED (But Could Be Added):**

### **Shopping Complexes**
- ❌ Walmart, Target, malls
- ❌ Big box stores
- ❌ Shopping center data

### **Social Media & Reviews**
- ❌ Reddit posts (r/Austin)
- ❌ Twitter sentiment
- ❌ Nextdoor reviews
- ❌ People's living experiences

### **Traditional Metrics**
- ❌ School ratings
- ❌ Home prices (Zillow)
- ❌ Census demographics
- ❌ Walk scores

---

## 💡 **WHY THIS IS ACTUALLY GOOD:**

Your project focuses on **alternative data** that others don't use:
- ✅ Coffee shop density = unique indicator
- ✅ Leading signals (not lagging)
- ✅ Proprietary methodology

**You're not trying to be Zillow. You're finding signals they miss!**

---

## 🎯 Original API Documentation Below:

### 1. Yelp Fusion API (Primary)

**What it provides**: Business listings with ratings, reviews, and locations

**Required**: ✅ Yes

**Data we collect**:
- Coffee shops
- Breweries
- Restaurants (vegan, organic)
- Yoga studios
- Other lifestyle amenities

**API Details**:
- **Endpoint**: `https://api.yelp.com/v3/businesses/search`
- **Rate Limit**: 5000 calls/day (free tier)
- **Max Results**: 1000 businesses per search
- **Authentication**: Bearer token in header

**Get API Key**: https://www.yelp.com/developers

**Example Response**:
```json
{
  "businesses": [
    {
      "id": "cafe-123",
      "name": "Blue Bottle Coffee",
      "rating": 4.5,
      "review_count": 523,
      "price": "$$",
      "coordinates": {
        "latitude": 30.2672,
        "longitude": -97.7431
      },
      "location": {
        "address1": "1234 Main St",
        "city": "Austin",
        "zip_code": "78701"
      }
    }
  ]
}
```

---

### 2. City Open Data Portals

Each city has its own data portal with crime, permits, and other datasets.

#### Austin, TX
- **Portal**: https://data.austintexas.gov
- **Crime Data**: https://data.austintexas.gov/Public-Safety/Crime-Reports/fdj4-gpfu
- **Permits**: https://data.austintexas.gov/Building-and-Development/Issued-Construction-Permits/3syk-w9eu
- **Format**: JSON, CSV (Socrata API)
- **API Key**: Not required for most datasets
- **Documentation**: https://dev.socrata.com/

**Example Crime Data Fields**:
- Incident Number
- Date & Time
- Location (address, zip, latitude/longitude)
- Category (e.g., Burglary, Theft, Assault)
- District/Zone

**Example Permit Data Fields**:
- Permit Number
- Issue Date
- Project Type (Commercial, Residential)
- Total Job Value
- Address & Zip Code

#### Chicago, IL
- **Portal**: https://data.cityofchicago.org
- **Crime Data**: https://data.cityofchicago.org/Public-Safety/Crimes-2020-to-Present/5cd6-ry5g
- **Permits**: https://data.cityofchicago.org/Buildings/Building-Permits/ydr8-5enu
- **Format**: JSON, CSV (Socrata API)
- **Notes**: Very large dataset (millions of records)

#### Seattle, WA
- **Portal**: https://data.seattle.gov
- **Crime Data**: https://data.seattle.gov/Public-Safety/SPD-Crime-Data-2008-Present/tazs-3rd5
- **Permits**: https://data.seattle.gov/Permitting/Building-Permits-Current/mags-97de
- **Format**: JSON, CSV (Socrata API)

#### Atlanta, GA
- **Portal**: http://opendata.atlantapd.org
- **Crime Data**: Available as CSV downloads
- **Format**: CSV (less API support)

---

### 3. US Census Bureau API (Optional)

**What it provides**: Demographics, income, housing data by census tract/zip code

**Required**: ⚪ Optional (enrichment)

**Useful Datasets**:
- **ACS (American Community Survey)**: Income, education, demographics
- **Decennial Census**: Population counts
- **TIGER/Line**: Geographic boundaries (shapefiles)

**API Details**:
- **Base URL**: `https://api.census.gov/data/`
- **Rate Limit**: None (but use responsibly)
- **Get API Key**: https://api.census.gov/data/key_signup.html

**Example: Median Income by Zip Code**:
```
https://api.census.gov/data/2021/acs/acs5?get=NAME,B19013_001E&for=zip%20code%20tabulation%20area:*&in=state:48
```

**Key Variables**:
- `B19013_001E`: Median household income
- `B01003_001E`: Total population
- `B25077_001E`: Median home value

---

### 4. Google Places API (Optional)

**What it provides**: Alternative to Yelp, more global coverage

**Required**: ⚪ Optional (backup)

**API Details**:
- **Endpoint**: `https://maps.googleapis.com/maps/api/place/nearbysearch/json`
- **Rate Limit**: $200 free credit/month (~28,000 requests)
- **Get API Key**: https://developers.google.com/maps/documentation/places/web-service

**When to use**: If Yelp doesn't have enough data for your city.

---

## 🗺️ Geospatial Data Sources

### Census TIGER/Line Shapefiles
- **What**: Geographic boundaries (zip codes, census tracts)
- **Format**: Shapefile (.shp)
- **Download**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html

### City Neighborhood Boundaries
- Austin: https://data.austintexas.gov/Locations-and-Maps/Neighborhood-Boundaries/nqw3-4xes
- Chicago: https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Neighborhoods/bbvz-uum9
- Seattle: https://data.seattle.gov/dataset/City-Clerk-Neighborhoods/md7w-5xgp

---

## 📊 Data Collection Strategy

### Phase 1: Quick Start (What we're doing now)
1. ✅ Yelp API → Lifestyle amenities
2. Store in `data/raw/`

### Phase 2: Enrichment (Next notebook)
1. City crime data → Safety trends
2. Building permits → Development activity
3. Join datasets by location

### Phase 3: Advanced (Optional)
1. Census demographics
2. Real estate prices (Zillow API - discontinued, use web scraping)
3. Walk scores, transit data

---

## ⚠️ API Rate Limits & Best Practices

| Service | Free Tier | Rate Limit | Best Practice |
|---------|-----------|------------|---------------|
| Yelp | 5000 calls/day | 5/second | Cache results, batch requests |
| Socrata (City Data) | Unlimited | Varies | Download CSVs for large datasets |
| Census | Unlimited | None | Use gzip compression |
| Google Places | $200/month | 50/second | Only if Yelp insufficient |

### Tips to Avoid Rate Limiting:
1. **Cache everything**: Save API responses to disk
2. **Sleep between requests**: Add `time.sleep(0.2)` in loops
3. **Use bulk exports**: Download CSVs when available
4. **Respect ToS**: Don't hammer APIs unnecessarily

---

## 🔐 API Key Security

### DO ✅
- Store keys in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables in code
- Rotate keys periodically

### DON'T ❌
- Commit keys to GitHub
- Share keys publicly
- Hard-code keys in notebooks
- Use keys in filenames

---

## 📖 Additional Resources

### Learning Resources
- **Yelp API Docs**: https://www.yelp.com/developers/documentation/v3
- **Socrata API Tutorial**: https://dev.socrata.com/foundry/data.austintexas.gov/fdj4-gpfu
- **Census API Guide**: https://www.census.gov/data/developers/guidance.html
- **GeoPandas Docs**: https://geopandas.org/

### Useful Python Libraries
- `requests`: HTTP requests
- `pandas`: Data manipulation
- `geopandas`: Geospatial data
- `folium`: Interactive maps
- `sodapy`: Socrata API client

---

**Last Updated**: December 11, 2025
