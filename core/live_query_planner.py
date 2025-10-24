"""
Live Query Planner for Project Samarth
Enhanced query planner that fetches live data from data.gov.in
"""

import pandas as pd
from typing import Dict, List, Any
import logging
from .live_fetcher import LiveDataFetcher
from .query_planner import QueryPlanner

logger = logging.getLogger(__name__)

class LiveQueryPlanner(QueryPlanner):
    def __init__(self, db_path: str, api_key: str = None):
        super().__init__(db_path)
        self.live_fetcher = LiveDataFetcher(api_key) if api_key else None
        
    def execute_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute query with live data fetching capability"""
        
        # Try live data first if API key available
        if self.live_fetcher and self._should_use_live_data(intent):
            try:
                return self._execute_live_query(intent, sources)
            except Exception as e:
                logger.warning(f"Live data fetch failed, falling back to local: {str(e)}")
        
        # Fallback to local data
        return super().execute_query(intent, sources)
    
    def _should_use_live_data(self, intent: Dict) -> bool:
        """Determine if we should fetch live data"""
        
        # Use live data for current/recent queries or price queries
        if intent.get('query_type') == 'current':
            return True
        if 'price' in intent.get('metrics', []):
            return True
        if any(keyword in intent.get('question', '').lower() for keyword in ['current', 'latest', 'recent', 'live', 'market']):
            return True
            
        return False
    
    def _execute_live_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute query using live data from API"""
        
        results_df = pd.DataFrame()
        
        # Fetch agriculture data if needed
        if any('agri' in src['dataset_id'] for src in sources):
            agri_data = self.live_fetcher.get_agriculture_data(
                states=intent.get('states', []),
                crops=intent.get('crops', [])
            )
            
            if not agri_data.empty:
                # Standardize column names
                agri_data = self._standardize_agriculture_columns(agri_data)
                results_df = pd.concat([results_df, agri_data], ignore_index=True)
        
        # Fetch climate data if needed  
        if any('climate' in src['dataset_id'] for src in sources):
            climate_data = self.live_fetcher.get_rainfall_data(
                states=intent.get('states', [])
            )
            
            if not climate_data.empty:
                # Standardize column names
                climate_data = self._standardize_climate_columns(climate_data)
                results_df = pd.concat([results_df, climate_data], ignore_index=True)
        
        if results_df.empty:
            return {'error': 'No live data available for your query'}
        
        # Process the live data based on query type
        processed_results = self._process_live_results(results_df, intent)
        
        return {
            'results': processed_results,
            'query': f"Live data fetch from data.gov.in API",
            'metric': intent.get('metrics', ['value'])[0],
            'data_source': 'live_api'
        }
    
    def _standardize_agriculture_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize agriculture data column names"""
        
        # Handle market price data (what we're actually getting from API)
        if 'commodity' in df.columns and 'modal_price' in df.columns:
            column_mapping = {
                'state': 'state',
                'district': 'district',
                'commodity': 'crop',
                'modal_price': 'price_per_quintal',
                'arrival_date': 'date'
            }
        else:
            # Handle production data
            column_mapping = {
                'state_name': 'state',
                'district_name': 'district', 
                'crop_year': 'year',
                'season': 'season',
                'crop': 'crop',
                'area': 'area_hectares',
                'production': 'production_tonnes'
            }
        
        # Rename columns to match our schema
        df_renamed = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Convert numeric columns
        numeric_cols = ['area_hectares', 'production_tonnes', 'year', 'price_per_quintal']
        for col in numeric_cols:
            if col in df_renamed.columns:
                df_renamed[col] = pd.to_numeric(df_renamed[col], errors='coerce')
        
        # Extract year from date if available
        if 'date' in df_renamed.columns and 'year' not in df_renamed.columns:
            try:
                df_renamed['year'] = pd.to_datetime(df_renamed['date'], errors='coerce').dt.year
            except:
                pass
        
        return df_renamed
    
    def _standardize_climate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize climate data column names"""
        
        column_mapping = {
            'state': 'state',
            'district': 'district',
            'year': 'year', 
            'annual': 'rainfall_mm',
            'rainfall': 'rainfall_mm'
        }
        
        # Rename columns to match our schema
        df_renamed = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Convert numeric columns
        numeric_cols = ['rainfall_mm', 'year']
        for col in numeric_cols:
            if col in df_renamed.columns:
                df_renamed[col] = pd.to_numeric(df_renamed[col], errors='coerce')
        
        return df_renamed
    
    def _process_live_results(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process live results based on query intent"""
        
        query_type = intent.get('query_type', 'general')
        
        if query_type == 'comparison':
            return self._process_comparison_live(df, intent)
        elif query_type == 'trend':
            return self._process_trend_live(df, intent)
        elif query_type == 'ranking':
            return self._process_ranking_live(df, intent)
        else:
            return self._process_general_live(df, intent)
    
    def _process_comparison_live(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process comparison query on live data"""
        
        states = intent.get('states', [])
        
        # Determine the metric to use based on available columns
        if 'price_per_quintal' in df.columns:
            metric = 'price_per_quintal'
        elif 'production_tonnes' in df.columns:
            metric = 'production_tonnes'
        elif 'rainfall_mm' in df.columns:
            metric = 'rainfall_mm'
        else:
            # Use first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns
            metric = numeric_cols[0] if len(numeric_cols) > 0 else 'value'
        
        if 'state' in df.columns and metric in df.columns:
            state_data = df[df['state'].isin(states)] if states else df
            result = state_data.groupby('state')[metric].mean().reset_index()
            result.columns = ['state', 'avg_value']
            result['record_count'] = state_data.groupby('state').size().values
            return result.sort_values('avg_value', ascending=False)
        
        return df
    
    def _process_trend_live(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process trend analysis on live data"""
        
        metric = intent.get('metrics', ['production_tonnes'])[0]
        
        if 'year' in df.columns and metric in df.columns:
            result = df.groupby('year')[metric].mean().reset_index()
            result.columns = ['year', 'avg_value']
            return result.sort_values('year')
        
        return df
    
    def _process_ranking_live(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process ranking query on live data"""
        
        metric = intent.get('metrics', ['production_tonnes'])[0]
        
        if 'state' in df.columns and metric in df.columns:
            result = df.groupby('state')[metric].sum().reset_index()
            result.columns = ['state', 'total_value']
            return result.sort_values('total_value', ascending=False)
        
        return df
    
    def _process_general_live(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process general query on live data"""
        
        # Return aggregated results
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            result = df[numeric_cols].mean().to_frame('avg_value').reset_index()
            result.columns = ['metric', 'avg_value']
            return result
        
        return df.head(10)  # Return sample if no numeric data