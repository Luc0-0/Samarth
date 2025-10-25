"""
Dataset Source Selection module for Project Samarth
Selects appropriate datasets based on parsed intent
"""

import pandas as pd
from typing import Dict, List

class SourceSelector:
    def __init__(self, inventory_path: str = 'data_inventory.csv'):
        self.inventory = pd.read_csv(inventory_path)
        
    def select_sources(self, intent: Dict) -> List[Dict]:
        """Select relevant datasets based on intent"""
        relevant_sources = []
        
        # Filter by metrics needed
        if 'price' in intent['metrics'] or intent['query_type'] == 'current':
            live_sources = self._get_live_sources(intent)
            relevant_sources.extend(live_sources)
            
        if 'production' in intent['metrics'] or 'area' in intent['metrics']:
            agri_sources = self._get_agriculture_sources(intent)
            relevant_sources.extend(agri_sources)
            
        if 'rainfall' in intent['metrics'] or 'temperature' in intent['metrics']:
            climate_sources = self._get_climate_sources(intent)
            relevant_sources.extend(climate_sources)
            
        # If correlation analysis, need both agriculture and climate data
        if intent['query_type'] == 'correlation':
            if not any('agri' in src['dataset_id'] for src in relevant_sources):
                agri_sources = self._get_agriculture_sources(intent)
                relevant_sources.extend(agri_sources)
            if not any('climate' in src['dataset_id'] for src in relevant_sources):
                climate_sources = self._get_climate_sources(intent)
                relevant_sources.extend(climate_sources)
        
        # Remove duplicates and prioritize
        unique_sources = self._deduplicate_and_prioritize(relevant_sources, intent)
        
        return unique_sources
    
    def _get_agriculture_sources(self, intent: Dict) -> List[Dict]:
        """Get agriculture-related datasets"""
        agri_data = self.inventory[self.inventory['dataset_id'].str.startswith('agri')]
        
        sources = []
        for _, row in agri_data.iterrows():
            # Prioritize district-level data if districts mentioned
            if intent['districts'] and row['geo_granularity'] == 'district':
                priority = 1
            elif intent['states'] and row['geo_granularity'] in ['state', 'district']:
                priority = 2
            else:
                priority = 3
                
            sources.append({
                'dataset_id': row['dataset_id'],
                'dataset_title': row['dataset_title'],
                'publisher': row['publisher'],
                'resource_url': row['resource_url'],
                'resource_format': row['resource_format'],
                'geo_granularity': row['geo_granularity'],
                'temporal_granularity': row['temporal_granularity'],
                'available_years': row['available_years'],
                'fields_summary': row['fields_summary'],
                'priority': priority,
                'table_name': f"agri_{row['dataset_id'].replace('-', '_')}"
            })
            
        return sorted(sources, key=lambda x: x['priority'])
    
    def _get_climate_sources(self, intent: Dict) -> List[Dict]:
        """Get climate-related datasets"""
        climate_data = self.inventory[self.inventory['dataset_id'].str.startswith('climate')]
        
        sources = []
        for _, row in climate_data.iterrows():
            # Skip restricted datasets
            if 'registration' in row['access_notes'].lower():
                continue
                
            # Prioritize district-level data if districts mentioned
            if intent['districts'] and row['geo_granularity'] == 'district':
                priority = 1
            elif intent['states'] and row['geo_granularity'] in ['state', 'district']:
                priority = 2
            else:
                priority = 3
                
            sources.append({
                'dataset_id': row['dataset_id'],
                'dataset_title': row['dataset_title'],
                'publisher': row['publisher'],
                'resource_url': row['resource_url'],
                'resource_format': row['resource_format'],
                'geo_granularity': row['geo_granularity'],
                'temporal_granularity': row['temporal_granularity'],
                'available_years': row['available_years'],
                'fields_summary': row['fields_summary'],
                'priority': priority,
                'table_name': f"climate_{row['dataset_id'].replace('-', '_')}"
            })
            
        return sorted(sources, key=lambda x: x['priority'])
    
    def _get_live_sources(self, intent: Dict) -> List[Dict]:
        """Get live API datasets for current/price queries"""
        live_data = self.inventory[self.inventory['dataset_id'].str.startswith('live')]
        
        sources = []
        for _, row in live_data.iterrows():
            sources.append({
                'dataset_id': row['dataset_id'],
                'dataset_title': row['dataset_title'],
                'publisher': row['publisher'],
                'resource_url': row['resource_url'],
                'resource_format': row['resource_format'],
                'geo_granularity': row['geo_granularity'],
                'temporal_granularity': row['temporal_granularity'],
                'available_years': row['available_years'],
                'fields_summary': row['fields_summary'],
                'priority': 1,
                'table_name': f"live_{row['dataset_id'].replace('-', '_')}"
            })
            
        return sources
    
    def _deduplicate_and_prioritize(self, sources: List[Dict], intent: Dict) -> List[Dict]:
        """Remove duplicates and prioritize sources"""
        # Remove duplicates by dataset_id
        seen_ids = set()
        unique_sources = []
        
        for source in sorted(sources, key=lambda x: x['priority']):
            if source['dataset_id'] not in seen_ids:
                unique_sources.append(source)
                seen_ids.add(source['dataset_id'])
                
        # Limit to top 3 sources to avoid complexity
        return unique_sources[:3]