"""
Test script for Project Samarth Phase 2 API
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_api():
    """Test the API with sample questions"""
    
    # Test questions
    questions = [
        "Compare the average annual rainfall in Maharashtra and Punjab",
        "Which state has the highest rice production?",
        "Show me the correlation between rainfall and crop production",
        "What is the average wheat production in Punjab?",
        "Analyze the production trend of cotton from 2010 to 2014"
    ]
    
    print("🌾 Testing Project Samarth Q&A API")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure to start the API server first:")
        print("python -m api.main")
        return
    
    # Test datasets endpoint
    try:
        response = requests.get(f"{API_BASE}/datasets")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} datasets")
        else:
            print("❌ Datasets endpoint failed")
    except Exception as e:
        print(f"❌ Datasets test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Testing Q&A functionality:")
    print("=" * 50)
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n🔍 Test {i}: {question}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            response = requests.post(f"{API_BASE}/ask", json={"question": question})
            
            if response.status_code == 200:
                data = response.json()
                processing_time = time.time() - start_time
                
                print(f"✅ Response received in {processing_time:.2f}s")
                print(f"📝 Answer: {data['answer_text'][:100]}...")
                print(f"📊 Results: {len(data['structured_results'])} records")
                print(f"📚 Citations: {len(data['citations'])} sources")
                
                results.append({
                    "question": question,
                    "success": True,
                    "processing_time": processing_time,
                    "results_count": len(data['structured_results']),
                    "citations_count": len(data['citations'])
                })
                
            else:
                print(f"❌ API error: {response.status_code}")
                results.append({
                    "question": question,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            results.append({
                "question": question,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Successful queries: {successful}/{total}")
    
    if successful > 0:
        avg_time = sum(r.get('processing_time', 0) for r in results if r['success']) / successful
        print(f"⏱️  Average response time: {avg_time:.2f}s")
        
        total_results = sum(r.get('results_count', 0) for r in results if r['success'])
        total_citations = sum(r.get('citations_count', 0) for r in results if r['success'])
        
        print(f"📊 Total data records returned: {total_results}")
        print(f"📚 Total citations provided: {total_citations}")
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to test_results.json")
    
    if successful == total:
        print("\n🎉 All tests passed! Phase 2 is working correctly.")
    else:
        print(f"\n⚠️  {total - successful} tests failed. Check the logs for details.")

if __name__ == "__main__":
    test_api()