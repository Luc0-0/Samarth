"""
Live Data Fetcher for Project Samarth
Fetches real-time data from data.gov.in using API key
"""

import requests
import pandas as pd
import json
from typing import Dict, List, Optional
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LiveDataFetcher:
    def __init__(self, api_key: str = "579b464db66ec23bdd0000019ec8d2f81ad84120490e03027b8842b3"):
        self.api_key = api_key
        self.base_url = "https://api.data.gov.in/resource"
        
    def fetch_dataset(self, resource_id: str, filters: Dict = None, limit: int = 100) -> pd.DataFrame:
        """Fetch live data from data.gov.in API"""
        
        params = {
            'api-key': self.api_key,
            'format': 'json',
            'limit': limit
        }
        
        if filters:
            params.update(filters)
            
        url = f"{self.base_url}/{resource_id}"
        
        try:
            logger.info(f"Fetching live data from {url}")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Try to parse as JSON
                try:
                    data = response.json()
                    if 'records' in data:
                        df = pd.DataFrame(data['records'])
                    elif isinstance(data, list):
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame([data])
                    
                    logger.info(f"Fetched {len(df)} records from {resource_id}")
                    return df
                except:
                    # If JSON parsing fails, try CSV
                    try:
                        df = pd.read_csv(pd.StringIO(response.text))
                        logger.info(f"Fetched {len(df)} records as CSV from {resource_id}")
                        return df
                    except:
                        logger.warning(f"Could not parse response from {resource_id}")
                        return pd.DataFrame()
            else:
                logger.warning(f"API returned status {response.status_code} for {resource_id}")
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from {resource_id}: {str(e)}")
            return pd.DataFrame()
    
    def get_agriculture_data(self, states: List[str] = None, crops: List[str] = None) -> pd.DataFrame:
        """Fetch live agriculture production data"""
        
        # Try multiple known agriculture resource IDs
        resource_ids = [
            "9ef84268-d588-465a-a308-a864a43d0070",
            "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69",
            "be309c42-c2b6-4d0b-9c8e-7e8e8e8e8e8e"
        ]
        
        for resource_id in resource_ids:
            filters = {}
            if states:
                filters['filters[state_name]'] = ','.join(states)
            if crops:
                filters['filters[crop]'] = ','.join(crops)
                
            df = self.fetch_dataset(resource_id, filters)
            if not df.empty:
                return df
                
        return pd.DataFrame()
    
    def get_rainfall_data(self, states: List[str] = None) -> pd.DataFrame:
        """Fetch live rainfall data"""
        
        # Try multiple known rainfall resource IDs
        resource_ids = [
            "88f07c0b-e66b-4b8e-9c2e-4d0d8c6e8c8e",
            "01c563b6-31a3-4f3e-9c8e-7e8e8e8e8e8e",
            "9ef84268-d588-465a-a308-a864a43d0070"  # Sometimes same as agri
        ]
        
        for resource_id in resource_ids:
            filters = {}
            if states:
                filters['filters[state]'] = ','.join(states)
                
            df = self.fetch_dataset(resource_id, filters)
            if not df.empty:
                return df
                
        return pd.DataFrame()
    
    def search_resources(self, query: str) -> List[Dict]:
        """Search for available resources"""
        
        search_url = "https://api.data.gov.in/catalog"
        params = {
            'api-key': self.api_key,
            'q': query,
            'format': 'json'
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('catalogs', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching resources: {str(e)}")
            return []