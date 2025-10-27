"""
Citation Helper - Provides working URLs and fallback options for dataset citations
"""

def get_working_citation_url(dataset_id: str, dataset_title: str, original_url: str) -> dict:
    """
    Returns working URLs and metadata for dataset citations
    """
    
    # Working URL mappings for known datasets
    working_urls = {
        'agri-1': {
            'primary_url': 'https://data.gov.in/catalog/district-wise-season-wise-crop-production-statistics',
            'search_url': 'https://data.gov.in/search?title=district+crop+production',
            'status': 'search_recommended'
        },
        'agri-2': {
            'primary_url': 'https://data.gov.in/catalog/state-wise-estimates-principal-crops',
            'search_url': 'https://data.gov.in/search?title=state+crop+estimates',
            'status': 'search_recommended'
        },
        'agri-3': {
            'primary_url': 'https://data.gov.in/search?title=agricultural+statistics+glance',
            'search_url': 'https://data.gov.in/search?title=agricultural+statistics',
            'status': 'search_recommended'
        },
        'climate-1': {
            'primary_url': 'https://data.gov.in/catalog/district-wise-rainfall-normal',
            'search_url': 'https://data.gov.in/search?title=district+rainfall',
            'status': 'search_recommended'
        },
        'climate-2': {
            'primary_url': 'https://data.gov.in/search?title=state+monthly+rainfall',
            'search_url': 'https://data.gov.in/search?title=rainfall',
            'status': 'search_recommended'
        },
        'live-1': {
            'primary_url': 'https://data.gov.in/catalog/daily-market-prices-commodity-wise',
            'search_url': 'https://data.gov.in/search?title=market+prices',
            'status': 'live_api'
        },
        'live-2': {
            'primary_url': 'https://data.gov.in/catalog/current-crop-production',
            'search_url': 'https://data.gov.in/search?title=crop+production',
            'status': 'live_api'
        }
    }
    
    # Get working URL or create search fallback
    if dataset_id in working_urls:
        return working_urls[dataset_id]
    else:
        # Create search URL from dataset title
        search_terms = dataset_title.lower().replace(' ', '+').replace(',', '')
        return {
            'primary_url': f'https://data.gov.in/search?title={search_terms}',
            'search_url': f'https://data.gov.in/search?title={search_terms}',
            'status': 'search_fallback'
        }

def get_citation_display_info(dataset_id: str, dataset_title: str) -> dict:
    """
    Returns display information for citations including status badges
    """
    
    url_info = get_working_citation_url(dataset_id, dataset_title, "")
    
    status_info = {
        'search_recommended': {
            'badge': 'Search Portal',
            'description': 'Links to data.gov.in search - original files may have moved',
            'color': 'amber'
        },
        'live_api': {
            'badge': 'Live API',
            'description': 'Real-time data from government API',
            'color': 'green'
        },
        'search_fallback': {
            'badge': 'Search',
            'description': 'Search data.gov.in for this dataset',
            'color': 'gray'
        }
    }
    
    status = url_info['status']
    
    return {
        'url': url_info['primary_url'],
        'search_url': url_info['search_url'],
        'badge': status_info[status]['badge'],
        'description': status_info[status]['description'],
        'color': status_info[status]['color']
    }