"""
Test working API integration
"""

from core.live_fetcher import LiveDataFetcher
import pandas as pd
import os

def test_working_api():
    api_key = os.getenv('GOV_API_KEY', 'your_api_key_here')
    fetcher = LiveDataFetcher(api_key)
    
    print("Testing live data fetcher...")
    
    # Test agriculture data
    print("\n1. Testing agriculture data fetch...")
    agri_data = fetcher.get_agriculture_data(states=['Punjab', 'Maharashtra'])
    
    if not agri_data.empty:
        print(f"SUCCESS: Fetched {len(agri_data)} agriculture records")
        print(f"Columns: {list(agri_data.columns)}")
        print("Sample data:")
        print(agri_data.head(3))
    else:
        print("No agriculture data fetched")
    
    # Test rainfall data  
    print("\n2. Testing rainfall data fetch...")
    rainfall_data = fetcher.get_rainfall_data(states=['Punjab', 'Maharashtra'])
    
    if not rainfall_data.empty:
        print(f"SUCCESS: Fetched {len(rainfall_data)} rainfall records")
        print(f"Columns: {list(rainfall_data.columns)}")
        print("Sample data:")
        print(rainfall_data.head(3))
    else:
        print("No rainfall data fetched")
    
    # Test direct resource fetch
    print("\n3. Testing direct resource fetch...")
    direct_data = fetcher.fetch_dataset("9ef84268-d588-465a-a308-a864a43d0070")
    
    if not direct_data.empty:
        print(f"SUCCESS: Fetched {len(direct_data)} direct records")
        print(f"Columns: {list(direct_data.columns)}")
    else:
        print("No direct data fetched")

if __name__ == "__main__":
    test_working_api()