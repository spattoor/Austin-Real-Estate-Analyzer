# 🚀 Quick Start Guide - Next Hot Neighborhood Predictor

Welcome! This guide will help you get your project up and running in ~15 minutes.

## 📋 Prerequisites

- **macOS** (M2 MacBook Air ✅)
- **Python 3.9+** (Check: `python3 --version`)
- **Internet connection** (for API calls)

## 🛠️ Setup Instructions

### Step 1: Open Terminal

Press `Cmd + Space`, type "Terminal", and hit Enter.

### Step 2: Navigate to Project Directory

```bash
cd /Users/saiabhinavpattoor/winter_project
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your terminal should now show (venv) at the beginning
```

### Step 4: Install Required Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**⏱️ This will take 3-5 minutes.** The M2 chip handles this efficiently!

### Step 5: Get Your Yelp API Key

1. Go to: https://www.yelp.com/developers
2. Click **"Create App"**
3. Fill in the form:
   - **App Name**: Neighborhood Predictor
   - **Industry**: Data Science
   - **Website**: https://github.com/yourusername (or any URL)
   - **Description**: Analyzing neighborhood trends
4. Click **"Create App"**
5. Copy your **API Key** (it looks like: `xxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### Step 6: Create Your .env File

```bash
# Copy the example file
cp .env.example .env

# Open it in a text editor
open -a TextEdit .env
```

Replace `your_yelp_api_key_here` with your actual API key:

```
YELP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Save and close the file.**

### Step 7: Launch Jupyter Notebook

```bash
jupyter notebook
```

This will open Jupyter in your browser.

### Step 8: Open the First Notebook

In the Jupyter interface:
1. Navigate to `notebooks/`
2. Click on `01_data_collection.ipynb`
3. Run each cell by pressing `Shift + Enter`

## 🎯 What City Should I Choose?

I recommend starting with **Austin, TX** because:
- ✅ Excellent data quality
- ✅ Medium-sized dataset (not overwhelming)
- ✅ Well-documented APIs
- ✅ Interesting gentrification patterns

Other options: Chicago (large dataset), Seattle (tech hub), Atlanta (southern US).

## ⚠️ Common Issues & Solutions

### Issue: "Module not found" error
**Solution**: Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

### Issue: "API key invalid"
**Solution**: 
1. Check your `.env` file - no quotes around the key
2. Make sure there are no extra spaces
3. Verify the key at https://www.yelp.com/developers/v3/manage_app

### Issue: Jupyter not opening
**Solution**:
```bash
pip install --upgrade jupyter
jupyter notebook
```

### Issue: Import error for geopandas
**Solution**: If geopandas fails to install on M2:
```bash
pip install --no-build-isolation geopandas
```

## 📊 Expected Results

After running the first notebook, you should see:
- ✅ 200-500 businesses collected from Yelp
- ✅ CSV file saved in `data/raw/`
- ✅ Summary statistics displayed

## 🎉 You're Ready!

Once you complete the setup, come back and we'll work through:
1. Data collection (Notebook 01) ← **Start here**
2. Data cleaning
3. Feature engineering
4. Analysis & visualization
5. Building the predictor

## 💬 Need Help?

If you run into any issues:
1. Check the error message carefully
2. Verify your Python version: `python3 --version`
3. Make sure all packages installed: `pip list`
4. Let me know the specific error and I'll help debug!

---

**Time to complete setup: ~15 minutes**  
**Difficulty: Beginner-friendly** 🟢

Let's build something amazing! 🚀
