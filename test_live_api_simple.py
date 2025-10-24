"""
Simple test for data.gov.in API
"""

import requests

def test_api():
    api_key = "579b464db66ec23bdd0000019ec8d2f81ad84120490e03027b8842b3"
    
    # Test different API endpoints
    endpoints = [
        "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
        "https://api.data.gov.in/catalog",
        "https://data.gov.in/api/datastore/resource.json"
    ]
    
    for url in endpoints:
        print(f"\nTesting: {url}")
        try:
            params = {'api-key': api_key, 'limit': 5}
            response = requests.get(url, params=params, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()