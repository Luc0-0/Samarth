#!/usr/bin/env python3
"""
Phase 1 Dataset Discovery for Project Samarth
Discovers agriculture and climate datasets from data.gov.in and IMD
"""

import requests
import pandas as pd
import json
import time
import logging
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import zipfile
import io
from datetime import datetime

# Setup logging
os.makedirs('ingestion/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion/logs/phase1.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatasetDiscoverer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; Samarth-DataDiscovery/1.0; +research@example.com)'
        })
        self.datasets = []
        self.dataset_counter = 0
        
    def rate_limit(self):
        """Polite 1-second delay between requests"""
        time.sleep(1)
        
    def safe_request(self, url, method='GET', **kwargs):
        """Make a safe HTTP request with error handling"""
        try:
            self.rate_limit()
            if method.upper() == 'HEAD':
                response = self.session.head(url, timeout=30, **kwargs)
            else:
                response = self.session.get(url, timeout=30, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
            
    def discover_datagovin_agriculture(self):
        """Discover agriculture datasets from data.gov.in"""
        logger.info("Starting data.gov.in agriculture dataset discovery...")
        
        search_terms = [
            'agriculture', 'crop production', 'farmers', 'agricultural statistics',
            'district wise crop', 'state wise agriculture', 'kharif', 'rabi'
        ]
        
        base_url = "https://data.gov.in"
        
        for term in search_terms:
            search_url = f"{base_url}/search?query={term}&sort=created_date+desc"
            logger.info(f"Searching for: {term}")
            
            response = self.safe_request(search_url)
            if not response or response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            dataset_links = soup.find_all('a', href=True)
            for link in dataset_links:
                href = link.get('href', '')
                if '/dataset/' in href and href not in [d.get('dataset_url') for d in self.datasets]:
                    dataset_url = urljoin(base_url, href)
                    self.process_datagovin_dataset(dataset_url)
                    
    def discover_datagovin_climate(self):
        """Discover climate datasets from data.gov.in"""
        logger.info("Starting data.gov.in climate dataset discovery...")
        
        search_terms = [
            'rainfall', 'weather', 'meteorological', 'IMD', 'precipitation',
            'climate', 'monsoon', 'temperature'
        ]
        
        base_url = "https://data.gov.in"
        
        for term in search_terms:
            search_url = f"{base_url}/search?query={term}&sort=created_date+desc"
            logger.info(f"Searching for: {term}")
            
            response = self.safe_request(search_url)
            if not response or response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            dataset_links = soup.find_all('a', href=True)
            for link in dataset_links:
                href = link.get('href', '')
                if '/dataset/' in href and href not in [d.get('dataset_url') for d in self.datasets]:
                    dataset_url = urljoin(base_url, href)
                    self.process_datagovin_dataset(dataset_url)
                    
    def process_datagovin_dataset(self, dataset_url):
        """Process individual dataset page from data.gov.in"""
        logger.info(f"Processing dataset: {dataset_url}")
        
        response = self.safe_request(dataset_url)
        if not response or response.status_code != 200:
            return
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_elem = soup.find('h1') or soup.find('title')
        dataset_title = title_elem.get_text().strip() if title_elem else "Unknown Dataset"
        
        publisher = "data.gov.in"
        org_elem = soup.find('span', class_='organization') or soup.find('div', class_='organization')
        if org_elem:
            publisher = org_elem.get_text().strip()
            
        license_info = "Open Government Licence"
        license_elem = soup.find('a', href=lambda x: x and 'license' in x.lower())
        if license_elem:
            license_info = license_elem.get_text().strip()
            
        resource_links = soup.find_all('a', href=True)
        
        self.dataset_counter += 1
        dataset_id = f"dgi-{self.dataset_counter}"
        
        for link in resource_links:
            href = link.get('href', '')
            link_text = link.get_text().strip().lower()
            
            if any(ext in href.lower() for ext in ['.csv', '.xlsx', '.json', '.zip']) or \
               any(word in link_text for word in ['download', 'csv', 'excel', 'json']):
                
                resource_url = urljoin('https://data.gov.in', href)
                resource_format = self.detect_format(resource_url, link_text)
                
                if resource_format:
                    resource_id = f"{dataset_id}-{len(self.datasets)+1}"
                    
                    dataset_record = {
                        'dataset_id': dataset_id,
                        'dataset_title': dataset_title,
                        'publisher': publisher,
                        'resource_id': resource_id,
                        'resource_title': link.get_text().strip() or f"Resource {len(self.datasets)+1}",
                        'resource_url': resource_url,
                        'resource_format': resource_format,
                        'license': license_info,
                        'geo_granularity': self.infer_geo_granularity(dataset_title),
                        'temporal_granularity': self.infer_temporal_granularity(dataset_title),
                        'available_years': self.extract_years(dataset_title),
                        'fields_summary': '',
                        'access_notes': '',
                        'dataset_url': dataset_url
                    }
                    
                    self.test_and_sample_resource(dataset_record)
                    self.datasets.append(dataset_record)
                    
    def discover_imd_datasets(self):
        """Discover IMD datasets"""
        logger.info("Starting IMD dataset discovery...")
        
        imd_urls = [
            "https://mausam.imd.gov.in/",
            "https://www.imd.gov.in/pages/services_climate.php",
            "https://www.imd.gov.in/pages/climate_data_1951_2000.php"
        ]
        
        for url in imd_urls:
            response = self.safe_request(url)
            if not response or response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                link_text = link.get_text().strip().lower()
                
                if any(word in link_text for word in ['data', 'download', 'rainfall', 'temperature']) and \
                   any(ext in href.lower() for ext in ['.csv', '.xlsx', '.txt', '.zip']):
                    
                    resource_url = urljoin(url, href)
                    self.process_imd_resource(resource_url, link_text)
                    
        self.add_fallback_climate_datasets()
        
    def process_imd_resource(self, resource_url, title):
        """Process IMD resource"""
        self.dataset_counter += 1
        dataset_id = f"imd-{self.dataset_counter}"
        resource_id = f"{dataset_id}-1"
        
        dataset_record = {
            'dataset_id': dataset_id,
            'dataset_title': f"IMD {title}",
            'publisher': "India Meteorological Department",
            'resource_id': resource_id,
            'resource_title': title,
            'resource_url': resource_url,
            'resource_format': self.detect_format(resource_url, title),
            'license': "IMD Terms of Use",
            'geo_granularity': self.infer_geo_granularity(title),
            'temporal_granularity': self.infer_temporal_granularity(title),
            'available_years': self.extract_years(title),
            'fields_summary': '',
            'access_notes': ''
        }
        
        self.test_and_sample_resource(dataset_record)
        self.datasets.append(dataset_record)
        
    def add_fallback_climate_datasets(self):
        """Add fallback climate datasets if IMD is inaccessible"""
        logger.info("Adding fallback climate datasets...")
        
        fallback_datasets = [
            {
                'dataset_id': 'fallback-1',
                'dataset_title': 'CHIRPS Rainfall Data (Fallback)',
                'publisher': 'USGS/CHG',
                'resource_id': 'chirps-1',
                'resource_title': 'CHIRPS Monthly Precipitation',
                'resource_url': 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/',
                'resource_format': 'netcdf',
                'license': 'Public Domain',
                'geo_granularity': 'gridded',
                'temporal_granularity': 'monthly',
                'available_years': '1981-present',
                'fields_summary': 'precipitation (mm/month)',
                'access_notes': 'Fallback dataset - requires processing for Indian districts'
            }
        ]
        
        self.datasets.extend(fallback_datasets)
        
    def test_and_sample_resource(self, dataset_record):
        """Test resource accessibility and create sample if possible"""
        url = dataset_record['resource_url']
        
        head_response = self.safe_request(url, method='HEAD')
        
        if head_response and head_response.status_code == 200:
            dataset_record['access_notes'] = f"{head_response.status_code} OK"
            if dataset_record['resource_format'] in ['csv', 'xlsx', 'json']:
                self.create_sample(dataset_record)
        else:
            status_code = head_response.status_code if head_response else "Connection Failed"
            dataset_record['access_notes'] = f"HTTP {status_code} - Access restricted or unavailable"
            
    def create_sample(self, dataset_record):
        """Create a sample of the resource"""
        url = dataset_record['resource_url']
        resource_id = dataset_record['resource_id']
        format_type = dataset_record['resource_format']
        
        try:
            response = self.safe_request(url)
            if not response or response.status_code != 200:
                return
                
            os.makedirs('samples', exist_ok=True)
            
            if format_type == 'csv':
                df = pd.read_csv(io.StringIO(response.text), nrows=100)
                sample_path = f"samples/{resource_id}_sample.csv"
                df.to_csv(sample_path, index=False)
                dataset_record['fields_summary'] = str(list(df.columns))
                dataset_record['access_notes'] += f", sampled {len(df)} rows"
                
            elif format_type == 'xlsx':
                df = pd.read_excel(io.BytesIO(response.content), nrows=100)
                sample_path = f"samples/{resource_id}_sample.xlsx"
                df.to_excel(sample_path, index=False)
                dataset_record['fields_summary'] = str(list(df.columns))
                dataset_record['access_notes'] += f", sampled {len(df)} rows"
                
            elif format_type == 'json':
                data = response.json()
                sample_path = f"samples/{resource_id}_sample.json"
                if isinstance(data, list) and len(data) > 0:
                    sample_data = data[:100]
                    with open(sample_path, 'w') as f:
                        json.dump(sample_data, f, indent=2)
                    dataset_record['fields_summary'] = str(list(data[0].keys())) if data else "[]"
                    
            meta_path = f"samples/{resource_id}_meta.json"
            metadata = {
                'http_status': response.status_code,
                'sample_rows': 100,
                'columns': dataset_record['fields_summary'],
                'sample_path': sample_path,
                'fetch_timestamp': datetime.now().isoformat()
            }
            
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to sample {url}: {str(e)}")
            dataset_record['access_notes'] += f", sampling failed: {str(e)}"
            
    def detect_format(self, url, text):
        """Detect resource format from URL or text"""
        url_lower = url.lower()
        text_lower = text.lower()
        
        if '.csv' in url_lower or 'csv' in text_lower:
            return 'csv'
        elif '.xlsx' in url_lower or '.xls' in url_lower or 'excel' in text_lower:
            return 'xlsx'
        elif '.json' in url_lower or 'json' in text_lower:
            return 'json'
        elif '.zip' in url_lower or 'zip' in text_lower:
            return 'zip'
        elif '.txt' in url_lower or 'text' in text_lower:
            return 'txt'
        elif '.nc' in url_lower or 'netcdf' in text_lower:
            return 'netcdf'
        return 'unknown'
        
    def infer_geo_granularity(self, title):
        """Infer geographical granularity from title"""
        title_lower = title.lower()
        if 'district' in title_lower:
            return 'district'
        elif 'state' in title_lower:
            return 'state'
        elif 'block' in title_lower or 'tehsil' in title_lower:
            return 'block'
        elif 'village' in title_lower:
            return 'village'
        elif 'grid' in title_lower or 'pixel' in title_lower:
            return 'gridded'
        return 'unknown'
        
    def infer_temporal_granularity(self, title):
        """Infer temporal granularity from title"""
        title_lower = title.lower()
        if 'daily' in title_lower or 'day' in title_lower:
            return 'daily'
        elif 'monthly' in title_lower or 'month' in title_lower:
            return 'monthly'
        elif 'annual' in title_lower or 'yearly' in title_lower or 'year' in title_lower:
            return 'yearly'
        elif 'seasonal' in title_lower or 'season' in title_lower:
            return 'seasonal'
        return 'unknown'
        
    def extract_years(self, title):
        """Extract year range from title"""
        import re
        year_pattern = r'(\d{4})'
        years = re.findall(year_pattern, title)
        if len(years) >= 2:
            return f"{min(years)}-{max(years)}"
        elif len(years) == 1:
            return years[0]
        return 'unknown'
        
    def save_inventory(self):
        """Save the dataset inventory to CSV"""
        if not self.datasets:
            logger.warning("No datasets found!")
            return
            
        df = pd.DataFrame(self.datasets)
        
        required_columns = [
            'dataset_id', 'dataset_title', 'publisher', 'resource_id', 
            'resource_title', 'resource_url', 'resource_format', 'license',
            'geo_granularity', 'temporal_granularity', 'available_years',
            'fields_summary', 'access_notes'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
                
        df = df[required_columns]
        df.to_csv('data_inventory_discovered.csv', index=False)
        logger.info(f"Saved {len(df)} datasets to data_inventory_discovered.csv")
        
    def run_discovery(self):
        """Run the complete discovery process"""
        logger.info("Starting Phase 1 dataset discovery...")
        
        self.discover_datagovin_agriculture()
        self.discover_datagovin_climate()
        self.discover_imd_datasets()
        
        self.save_inventory()
        logger.info("Discovery complete!")

if __name__ == "__main__":
    discoverer = DatasetDiscoverer()
    discoverer.run_discovery()