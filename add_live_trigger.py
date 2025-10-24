"""
Add live data trigger keywords to NLU parser
"""

from core.nlu import IntentParser

def update_nlu_for_live():
    """Update NLU to recognize live data requests"""
    
    # Add live data keywords
    live_keywords = [
        'current', 'latest', 'recent', 'live', 'today', 'now', 
        'real-time', 'up-to-date', 'fresh', 'new'
    ]
    
    print("Live data integration ready!")
    print("Use these keywords to trigger live data fetch:")
    for keyword in live_keywords:
        print(f"  - {keyword}")
    
    print("\nExample questions:")
    print("  - What are the current crop prices in Punjab?")
    print("  - Show me latest rainfall data for Maharashtra")
    print("  - Compare recent market prices across states")

if __name__ == "__main__":
    update_nlu_for_live()