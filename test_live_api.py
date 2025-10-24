"""
Test script for live data.gov.in API integration
"""

from core.live_fetcher import LiveDataFetcher
import pandas as pd

def test_live_api():
    """Test the live API connection"""
    
    api_key = "579b464db66ec23bdd0000019ec8d2f81ad84120490e03027b8842b3"
    fetcher = LiveDataFetcher(api_key)
    
    print("Testing data.gov.in API connection...")
    
    # Test 1: Search for agriculture resources
    print("\n1. Searching for agriculture resources...")
    agri_resources = fetcher.search_resources("agriculture crop production")
    print(f"Found {len(agri_resources)} agriculture resources")
    
    if agri_resources:
        for i, resource in enumerate(agri_resources[:3]):
            print(f"  {i+1}. {resource.get('title', 'Unknown')}")
            print(f"     ID: {resource.get('id', 'Unknown')}")
    
    # Test 2: Search for rainfall resources  
    print("\n2. Searching for rainfall resources...")
    rainfall_resources = fetcher.search_resources("rainfall climate")
    print(f"Found {len(rainfall_resources)} rainfall resources")
    
    if rainfall_resources:
        for i, resource in enumerate(rainfall_resources[:3]):
            print(f"  {i+1}. {resource.get('title', 'Unknown')}")
            print(f"     ID: {resource.get('id', 'Unknown')}")
    
    # Test 3: Try to fetch sample data
    print("\n3. Testing data fetch...")
    
    # Try common resource IDs
    test_resource_ids = [
        "9ef84268-d588-465a-a308-a864a43d0070",  # Common crop production ID
        "88f07c0b-e66b-4b8e-9c2e-4d0d8c6e8c8e",  # Common rainfall ID
        "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"   # Alternative ID
    ]
    
    for resource_id in test_resource_ids:
        print(f"\nTrying resource ID: {resource_id}")
        try:
            data = fetcher.fetch_dataset(resource_id, limit=10)
            if not data.empty:
                print(f"✅ Success! Fetched {len(data)} records")
                print(f"Columns: {list(data.columns)}")
                print(f"Sample data:\n{data.head(2)}")
                break
            else:
                print("❌ No data returned")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\nLive API test completed!")

if __name__ == "__main__":
    test_live_api()