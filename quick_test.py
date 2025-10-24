"""Quick test to verify Phase 2 setup"""

import os
import sys
import requests
import time

def check_setup():
    print("🌾 Project Samarth Phase 2 - Quick Setup Check")
    print("=" * 50)
    
    # Check files
    required_files = [
        'data_inventory.csv',
        'db/canonical.duckdb',
        'api/main.py',
        'core/nlu.py',
        'frontend/app.py'
    ]
    
    print("📁 Checking required files:")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
    
    # Check database
    try:
        import duckdb
        conn = duckdb.connect('db/canonical.duckdb')
        agri_count = conn.execute("SELECT COUNT(*) FROM agri_production").fetchone()[0]
        climate_count = conn.execute("SELECT COUNT(*) FROM climate_obs").fetchone()[0]
        conn.close()
        print(f"  ✅ Database: {agri_count} agri + {climate_count} climate records")
    except Exception as e:
        print(f"  ❌ Database error: {e}")
    
    print("\n🚀 To start the system:")
    print("1. Terminal 1: python -m api.main")
    print("2. Terminal 2: streamlit run frontend/app.py")
    print("3. Or run: python test_api.py")

if __name__ == "__main__":
    check_setup()