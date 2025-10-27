#!/usr/bin/env python3
"""
Test script to verify citation improvements
"""

from core.citation_helper import get_citation_display_info, get_working_citation_url

def test_citations():
    """Test citation URL improvements"""
    
    test_datasets = [
        ('agri-1', 'District wise Season wise Crop Production Statistics'),
        ('live-1', 'Live Market Prices'),
        ('climate-1', 'District wise Rainfall Normal'),
        ('unknown-dataset', 'Some Unknown Dataset')
    ]
    
    print("=== Citation URL Testing ===\n")
    
    for dataset_id, title in test_datasets:
        print(f"Dataset: {title}")
        print(f"ID: {dataset_id}")
        
        # Test URL mapping
        url_info = get_working_citation_url(dataset_id, title, "")
        print(f"Primary URL: {url_info['primary_url']}")
        print(f"Search URL: {url_info['search_url']}")
        print(f"Status: {url_info['status']}")
        
        # Test display info
        display_info = get_citation_display_info(dataset_id, title)
        print(f"Badge: {display_info['badge']}")
        print(f"Description: {display_info['description']}")
        print(f"Color: {display_info['color']}")
        print("-" * 50)

if __name__ == "__main__":
    test_citations()