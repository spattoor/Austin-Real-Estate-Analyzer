# ✅ Quick Start Checklist

Use this checklist to get started with your "Next Hot Neighborhood Predictor" project!

## 🎯 Phase 1: Initial Setup (15 minutes)

### Step 1: Verify Python Installation
```bash
python3 --version
```
- [ ] Python 3.9 or higher is installed

### Step 2: Create Virtual Environment
```bash
cd /Users/saiabhinavpattoor/winter_project
python3 -m venv venv
source venv/bin/activate
```
- [ ] Virtual environment created
- [ ] Virtual environment activated (you see `(venv)` in terminal)

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
- [ ] All packages installed without errors
- [ ] This takes ~3-5 minutes

### Step 4: Get Yelp API Key
1. Go to https://www.yelp.com/developers
2. Click "Create App"
3. Fill in the form (any website URL works)
4. Copy your API key

- [ ] Yelp account created
- [ ] API key obtained

### Step 5: Configure Environment
```bash
cp .env.example .env
open -a TextEdit .env
```
Replace `your_yelp_api_key_here` with your actual key

- [ ] `.env` file created
- [ ] API key added (no quotes!)

### Step 6: Verify Setup
```bash
python3 verify_setup.py
```
- [ ] All checks pass (5/5)
- [ ] If not, fix issues and re-run

---

## 🚀 Phase 2: First Data Collection (1-2 hours)

### Step 1: Choose Your City
Edit in notebook:
```python
SELECTED_CITY = "austin"  # or "chicago", "seattle", "atlanta"
```
- [ ] City selected

### Step 2: Launch Jupyter
```bash
jupyter notebook
```
- [ ] Jupyter opens in browser

### Step 3: Run First Notebook
Navigate to: `notebooks/01_data_collection.ipynb`

- [ ] Cell 1: Imports loaded successfully
- [ ] Cell 2: City configuration set
- [ ] Cell 3: API key verified (✅ Configured)
- [ ] Cell 4: Yelp functions defined
- [ ] Cell 5: Data collected (200-500 businesses)
- [ ] Cell 6: Data previewed (looks good!)
- [ ] Cell 7: Data saved to `data/raw/`

### Step 4: Verify Output
```bash
ls -lh data/raw/
```
- [ ] `yelp_[city]_[date].csv` file exists
- [ ] File size is > 10 KB

---

## 🎉 Success Criteria

After completing the checklist above, you should have:

✅ Working Python environment  
✅ All dependencies installed  
✅ API access configured  
✅ First dataset collected  
✅ Data saved for next phase  

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip list  # Check installed packages
```

### "API key invalid"
- Check `.env` file (no quotes around key)
- No spaces before/after the key
- Verify key at https://www.yelp.com/developers/v3/manage_app

### "GeoPandas installation failed"
```bash
pip install --no-build-isolation geopandas
```

### "Jupyter not opening"
```bash
pip install --upgrade jupyter
jupyter notebook --no-browser  # Get URL manually
```

---

## 📝 Next Steps

Once you complete this checklist:

1. **Review your data**: Look at the CSV file in Excel/Numbers
2. **Understand the output**: Read the notebook comments
3. **Let me know**: Tell me when you're ready for Phase 2!

---

## ⏱️ Time Estimates

- **Setup (first time)**: 15-20 minutes
- **Data collection**: 30-60 minutes (depending on API speed)
- **Verification**: 5 minutes

**Total**: ~1-1.5 hours for complete Phase 1

---

## 💬 Getting Help

If you get stuck:
1. Read the error message carefully
2. Check SETUP_GUIDE.md for detailed instructions
3. Run `python3 verify_setup.py` to diagnose issues
4. Ask me! I'm here to help.

---

**Remember**: Take your time, read the comments in the notebook, and have fun exploring the data! 🚀
