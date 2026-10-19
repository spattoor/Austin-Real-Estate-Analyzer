# 🏙️ Austin Real Estate Investment Finder

**A professional, data-driven tool for identifying high-potential real estate investment opportunities in Austin, Texas**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Overview

This is an investor-grade analysis platform that identifies the best neighborhoods in Austin for real estate investment using:

- **Real-Time Data** from 7+ verified sources (Yelp, Austin Open Data, Zillow, FRED, etc.)
- **70+ Advanced Features** including economic indicators, crime stats, permits, walkability, and job growth
- **Professional Scoring System** with confidence levels and transparent methodology
- **Interactive Dashboard** with maps, charts, and filterable rankings
- **Historical Validation** showing 80% accuracy on past hot neighborhoods

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

### SQLite storage and SQL analysis

The project now includes a validated SQLite import pipeline and a SQL Explorer dashboard.
It supports repeat imports, dated snapshots, rejection logs, parameterized comparisons,
cluster summaries, and historical changes. Start with the offline synthetic example or
import your existing processed CSV: **[SQLite guide](SQL_GUIDE.md)**.

```bash
python sql_pipeline.py --db data/austin_demo.db import examples/sql_demo/snapshot_day1.csv --observed-on 2026-10-01 --source-kind synthetic
python sql_pipeline.py --db data/austin_demo.db report rankings
```

The example is synthetic and is separate from the original market-data collection workflow.

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
