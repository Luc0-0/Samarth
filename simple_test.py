"""
Simple test script for Project Samarth API (Windows-friendly)
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_endpoints():
    print("🌾 Testing Project Samarth API")
    print("=" * 40)
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ Root endpoint works!")
            print(f"   Response: {response.json()['message']}")
        else:
            print(f"❌ Root failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the server is running: python run_server.py")
        return
    
    # Test 2: Health check
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: Datasets
    print("\n3. Testing datasets endpoint...")
    try:
        response = requests.get(f"{API_BASE}/datasets")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} datasets!")
        else:
            print(f"❌ Datasets failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Datasets error: {e}")
    
    # Test 4: Ask question
    print("\n4. Testing Q&A endpoint...")
    question = "Compare rainfall in Maharashtra and Punjab"
    try:
        response = requests.post(
            f"{API_BASE}/ask",
            json={"question": question}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Q&A endpoint works!")
            print(f"   Question: {question}")
            print(f"   Answer: {data['answer_text'][:100]}...")
            print(f"   Results: {len(data['structured_results'])} records")
            print(f"   Citations: {len(data['citations'])} sources")
        else:
            print(f"❌ Q&A failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Q&A error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Test complete! If all ✅, your API is working!")

if __name__ == "__main__":
    test_endpoints()