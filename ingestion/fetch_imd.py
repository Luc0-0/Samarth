#!/usr/bin/env python3
"""
Climate/IMD Data Fetcher for Project Samarth
Downloads climate datasets listed in the inventory CSV
"""

import pandas as pd
import requests
import os
import argparse
import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def download_resource(url, filename, logger, access_notes):
    """Download a resource with error handling"""
    try:
        # Check if requires special access
        if 'registration' in access_notes.lower() or 'approval' in access_notes.lower():
            logger.warning(f"Skipping {filename} - requires IMD registration/approval")
            logger.info(f"TODO: Register at IMD website and request access to {url}")
            return False
            
        if 'fallback' in access_notes.lower():
            logger.info(f"Skipping fallback dataset {filename} - use only if IMD data unavailable")
            return False
            
        logger.info(f"Downloading {filename} from {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        os.makedirs('data/climate', exist_ok=True)
        filepath = f"data/climate/{filename}"
        
        if filename.endswith('.csv') or filename.endswith('.txt'):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
        else:
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
        logger.info(f"Successfully downloaded {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {filename}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download climate datasets')
    parser.add_argument('--inventory', default='../data_inventory.csv', help='Path to inventory CSV')
    args = parser.parse_args()
    
    logger = setup_logging()
    
    # Load inventory
    try:
        df = pd.read_csv(args.inventory)
        climate_datasets = df[df['dataset_id'].str.startswith(('climate', 'fallback'))]
        
        logger.info(f"Found {len(climate_datasets)} climate datasets to process")
        
        success_count = 0
        for _, row in climate_datasets.iterrows():
            filename = f"{row['resource_id']}.{row['resource_format']}"
            if download_resource(row['resource_url'], filename, logger, row['access_notes']):
                success_count += 1
                
        logger.info(f"Successfully downloaded {success_count}/{len(climate_datasets)} climate datasets")
        
    except Exception as e:
        logger.error(f"Error processing inventory: {str(e)}")

if __name__ == "__main__":
    main()