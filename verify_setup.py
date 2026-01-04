#!/usr/bin/env python3
"""
Setup Verification Script
Run this to check if your environment is properly configured.
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Check Python version"""
    print_header("🐍 Python Version Check")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.9+ is required")
        return False

def check_packages():
    """Check if required packages are installed"""
    print_header("📦 Package Installation Check")
    
    required_packages = {
        'pandas': 'Data manipulation',
        'numpy': 'Numerical computing',
        'requests': 'HTTP requests',
        'dotenv': 'Environment variables',
        'matplotlib': 'Plotting',
        'seaborn': 'Statistical visualization',
        'jupyter': 'Jupyter notebooks'
    }
    
    optional_packages = {
        'geopandas': 'Geospatial analysis',
        'folium': 'Interactive maps',
        'plotly': 'Interactive plots'
    }
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    print("\nRequired Packages:")
    for package, description in required_packages.items():
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"  ✅ {package:15} - {description}")
        except ImportError:
            print(f"  ❌ {package:15} - {description} (MISSING)")
            missing_required.append(package)
    
    # Check optional packages
    print("\nOptional Packages:")
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package:15} - {description}")
        except ImportError:
            print(f"  ⚠️  {package:15} - {description} (not installed)")
            missing_optional.append(package)
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print(f"   Run: pip install {' '.join(missing_required)}")
        return False
    elif missing_optional:
        print(f"\n⚠️  Optional packages not installed: {', '.join(missing_optional)}")
        print("   These will be needed for visualization later")
        return True
    else:
        print("\n✅ All packages installed!")
        return True

def check_project_structure():
    """Check if project directories exist"""
    print_header("📁 Project Structure Check")
    
    required_dirs = [
        'data/raw',
        'data/processed',
        'data/external',
        'notebooks',
        'src/data',
        'src/features',
        'src/models',
        'src/visualization',
        'outputs/figures',
        'outputs/maps'
    ]
    
    project_root = Path.cwd()
    all_exist = True
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} (MISSING)")
            all_exist = False
    
    if all_exist:
        print("\n✅ All directories exist!")
        return True
    else:
        print("\n❌ Some directories are missing")
        print("   They will be created automatically when needed")
        return True  # Not critical

def check_env_file():
    """Check if .env file exists and has required keys"""
    print_header("🔑 API Configuration Check")
    
    env_file = Path.cwd() / '.env'
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Yelp API key")
        return False
    
    print("✅ .env file exists")
    
    # Try to load and check keys
    from dotenv import load_dotenv
    load_dotenv()
    
    yelp_key = os.getenv('YELP_API_KEY')
    
    if not yelp_key or yelp_key == 'your_yelp_api_key_here':
        print("⚠️  Yelp API key not configured")
        print("   Get your key at: https://www.yelp.com/developers")
        return False
    else:
        print(f"✅ Yelp API key configured (length: {len(yelp_key)})")
        return True

def check_notebook_exists():
    """Check if first notebook exists"""
    print_header("📓 Notebook Check")
    
    notebook = Path.cwd() / 'notebooks' / '01_data_collection.ipynb'
    
    if notebook.exists():
        print(f"✅ {notebook.name} exists")
        print(f"   Size: {notebook.stat().st_size / 1024:.2f} KB")
        return True
    else:
        print(f"❌ {notebook.name} not found")
        return False

def main():
    """Run all checks"""
    print("\n" + "🚀 " + "="*55)
    print("  NEXT HOT NEIGHBORHOOD PREDICTOR - SETUP VERIFICATION")
    print("="*58)
    
    results = []
    
    # Run all checks
    results.append(("Python Version", check_python_version()))
    results.append(("Packages", check_packages()))
    results.append(("Project Structure", check_project_structure()))
    results.append(("Environment File", check_env_file()))
    results.append(("Notebooks", check_notebook_exists()))
    
    # Summary
    print_header("📊 Setup Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
    
    print(f"\n  Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n  🎉 Your setup is complete! You're ready to start.")
        print("  Run: jupyter notebook")
        print("  Open: notebooks/01_data_collection.ipynb")
    elif passed >= total - 1:
        print("\n  ⚠️  Almost there! Fix the issues above and you're good to go.")
    else:
        print("\n  ❌ Several setup steps need attention.")
        print("  Refer to SETUP_GUIDE.md for detailed instructions.")
    
    print("\n" + "="*58 + "\n")

if __name__ == "__main__":
    main()
