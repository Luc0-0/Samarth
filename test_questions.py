#!/usr/bin/env python3
"""
Test script to verify which questions work with the current system
"""

import requests
import json
import time

# Test questions
WORKING_QUESTIONS = [
    "Compare average rainfall in Maharashtra and Punjab",
    "Which state has the highest rice production?", 
    "Show me cotton production trend from 2010 to 2014",
    "Average crop production in Karnataka",
    "Correlation between rainfall and rice production"
]

FAILING_QUESTIONS = [
    "What are current crop prices in Maharashtra?",
    "Latest market rates for wheat",
    "Current crop production in Gujarat",
    "Live mandi prices today"
]

def test_question(question, api_url="http://localhost:8000"):
    """Test a single question"""
    try:
        print(f"\n🔍 Testing: {question}")
        
        response = requests.post(
            f"{api_url}/ask",
            json={"question": question},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data.get('answer_text', ''):
                print(f"❌ FAILED: {data['answer_text']}")
                return False
            else:
                processing_time = data.get('processing_info', {}).get('processing_time_ms', 0)
                citations = len(data.get('citations', []))
                results = len(data.get('structured_results', []))
                
                print(f"✅ SUCCESS: {processing_time}ms, {citations} citations, {results} results")
                return True
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Backend not running")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("=== Project Samarth Question Testing ===")
    
    print("\n📊 TESTING HISTORICAL QUESTIONS (Should work):")
    working_count = 0
    for question in WORKING_QUESTIONS:
        if test_question(question):
            working_count += 1
        time.sleep(1)  # Rate limiting
    
    print(f"\n✅ Historical Questions: {working_count}/{len(WORKING_QUESTIONS)} working")
    
    print("\n⚡ TESTING LIVE DATA QUESTIONS (Expected to fail):")
    failing_count = 0
    for question in FAILING_QUESTIONS:
        if not test_question(question):
            failing_count += 1
        time.sleep(1)  # Rate limiting
    
    print(f"\n❌ Live Questions: {failing_count}/{len(FAILING_QUESTIONS)} failing (expected)")
    
    print("\n📋 SUMMARY:")
    print(f"- Historical data queries: {working_count}/{len(WORKING_QUESTIONS)} working")
    print(f"- Live data queries: {len(FAILING_QUESTIONS) - failing_count}/{len(FAILING_QUESTIONS)} working")
    print("\n💡 For demos, use historical questions for reliable results!")

if __name__ == "__main__":
    main()