# 🏙️ Next Hot Neighborhood Predictor

A data science project that identifies up-and-coming neighborhoods before they become expensive using alternative data sources and geospatial analysis.

## 🎯 Project Overview

This project predicts neighborhood gentrification by analyzing:
- **Building Permits** (New businesses, renovations)
- **Crime Data** (Safety trends)
- **Lifestyle Amenities** (Coffee shops, breweries, restaurants via APIs)

## 🛠️ Tech Stack

- **Data Collection**: Python (requests, BeautifulSoup, APIs)
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn (Clustering, Regression)
- **Geospatial Analysis**: GeoPandas, Folium, Kepler.gl
- **Visualization**: Plotly, Matplotlib, Seaborn

## 📁 Project Structure

```
winter_project/
├── data/
│   ├── raw/              # Raw data from APIs and scraping
│   ├── processed/        # Cleaned and transformed data
│   └── external/         # Reference data (zip codes, boundaries)
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_analysis.ipynb
│   └── 05_visualization.ipynb
├── src/
│   ├── data/            # Data collection scripts
│   ├── features/        # Feature engineering
│   ├── models/          # ML models
│   └── visualization/   # Plotting functions
├── outputs/
│   ├── figures/         # Generated plots
│   └── maps/            # Interactive maps
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Getting Started

### 1. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:
- Yelp API
- Google Places API (optional)
- Census API (optional)

### 3. Run the Notebooks

Start with `notebooks/01_data_collection.ipynb` and work through each notebook in order.

## 📊 Key Features

### The "Hipster Index"
Custom metric combining:
- Number of specialty coffee shops
- Craft breweries
- Average Yelp ratings
- Vegan/organic restaurants

### Predictive Models
- **K-Means Clustering**: Group neighborhoods into categories
- **Time-Lag Analysis**: Correlate amenity growth with housing price increases
- **Anomaly Detection**: Find undervalued neighborhoods

### Interactive Visualizations
- 3D heatmaps of housing prices
- Bubble maps showing the "Hipster Index"
- Time-series animations of neighborhood evolution

## 📈 Results

*(Will be updated as we progress)*

## 🔮 Future Improvements

- Real-time data pipeline
- Web dashboard (Streamlit/Dash)
- Additional data sources (Walkability scores, School ratings)
- Deep learning models for prediction

## 📝 License

MIT License

---

**Author**: Sai Abhinav Pattoor  
**Date**: December 2025
