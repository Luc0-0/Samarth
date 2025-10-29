"""
Live Query Planner for Project Samarth
Enhanced query planner that fetches live data from data.gov.in
"""

import pandas as pd
from typing import Dict, List, Any
import logging
from .live_fetcher import LiveDataFetcher
from .query_planner import QueryPlanner
from .universal_handler import UniversalHandler

logger = logging.getLogger(__name__)

class LiveQueryPlanner(QueryPlanner):
    def __init__(self, db_path: str, api_key: str = None):
        super().__init__(db_path)
        self.live_fetcher = LiveDataFetcher(api_key) if api_key else None
        self.universal_handler = UniversalHandler(db_path)
        
    def execute_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute query with live data fetching capability"""
        
        # Try live data first if API key available
        if self.live_fetcher and self._should_use_live_data(intent):
            try:
                logger.info(f"Attempting live data query for: {intent.get('question', 'Unknown')}")
                result = self._execute_live_query(intent, sources)
                logger.info(f"Live data query completed successfully")
                return result
            except Exception as e:
                logger.error(f"Live data fetch failed, falling back to local: {str(e)}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Try local data
        logger.info("Using local database for query")
        try:
            result = super().execute_query(intent, sources)
        except Exception as e:
            logger.error(f"Local query failed: {str(e)}")
            result = {'error': str(e)}
        
        # Use universal handler for any failed queries
        return self.universal_handler.handle_any_question(intent, sources, result)
    
    def _should_use_live_data(self, intent: Dict) -> bool:
        """Determine if we should fetch live data"""
        
        question_lower = intent.get('question', '').lower()
        
        # Use live data for current/recent queries or price queries
        if intent.get('query_type') == 'current':
            return True
        if 'price' in intent.get('metrics', []):
            return True
        # Check for live keywords in the question (even for trend analysis)
        if any(keyword in question_lower for keyword in ['current', 'latest', 'recent', 'live', 'market', 'now', 'today']):
            return True
            
        return False
    
    def _execute_live_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute query using live data from API"""
        
        results_df = pd.DataFrame()
        
        # Fetch live data if needed
        if any('live' in src['dataset_id'] for src in sources):
            live_data = self.live_fetcher.get_agriculture_data(
                states=intent.get('states', []),
                crops=intent.get('crops', [])
            )
            
            if not live_data.empty:
                # Standardize column names
                live_data = self._standardize_agriculture_columns(live_data)
                results_df = pd.concat([results_df, live_data], ignore_index=True)
        
        # Also try agriculture data for fallback
        if results_df.empty and any('agri' in src['dataset_id'] for src in sources):
            agri_data = self.live_fetcher.get_agriculture_data(
                states=intent.get('states', []),
                crops=intent.get('crops', [])
            )
            
            if not agri_data.empty:
                agri_data = self._standardize_agriculture_columns(agri_data)
                results_df = pd.concat([results_df, agri_data], ignore_index=True)
        
        if results_df.empty:
            logger.warning(f"No live data found for query: {intent.get('question', 'Unknown')}")
            return {
                'error': 'No live data available for your query. The government API may be temporarily unavailable or the resource IDs may have changed. Please try a historical query instead.',
                'suggestion': 'Try asking about historical data (2001-2014) or remove words like "current", "latest", "recent" from your question.'
            }
        
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
        
        try:
            logger.info(f"Processing trend analysis on {len(df)} records")
            logger.info(f"Available columns: {list(df.columns)}")
            
            # Determine the metric to use
            if 'production_tonnes' in df.columns:
                metric = 'production_tonnes'
            elif 'price_per_quintal' in df.columns:
                metric = 'price_per_quintal'
            elif 'area_hectares' in df.columns:
                metric = 'area_hectares'
            else:
                # Use first numeric column
                numeric_cols = df.select_dtypes(include=['number']).columns
                metric = numeric_cols[0] if len(numeric_cols) > 0 else None
            
            if not metric:
                logger.warning("No numeric columns found for trend analysis")
                return df.head(10)
            
            logger.info(f"Using metric: {metric}")
            
            # Try to group by year if available
            if 'year' in df.columns and metric in df.columns:
                logger.info("Grouping by year")
                result = df.groupby('year')[metric].mean().reset_index()
                result.columns = ['year', 'avg_value']
                result['record_count'] = df.groupby('year').size().reset_index(drop=True)
                return result.sort_values('year')
            
            # If no year column, try to group by date
            elif 'date' in df.columns and metric in df.columns:
                logger.info("Grouping by date (extracting year)")
                df_copy = df.copy()
                df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
                df_copy = df_copy.dropna(subset=['date'])
                if len(df_copy) == 0:
                    logger.warning("No valid dates found")
                    return self._fallback_trend_analysis(df, metric)
                
                df_copy['year'] = df_copy['date'].dt.year
                result = df_copy.groupby('year')[metric].mean().reset_index()
                result.columns = ['year', 'avg_value']
                result['record_count'] = df_copy.groupby('year').size().reset_index(drop=True)
                return result.sort_values('year')
            
            # If no time dimension, group by state for comparison
            elif 'state' in df.columns and metric in df.columns:
                logger.info("Grouping by state (no time dimension available)")
                result = df.groupby('state')[metric].mean().reset_index()
                result.columns = ['state', 'avg_value']
                result['record_count'] = df.groupby('state').size().reset_index(drop=True)
                return result.sort_values('avg_value', ascending=False)
            
            # Fallback: return summary statistics
            else:
                logger.info("Using fallback trend analysis")
                return self._fallback_trend_analysis(df, metric)
                
        except Exception as e:
            logger.error(f"Error in trend processing: {str(e)}")
            return df.head(10)
    
    def _fallback_trend_analysis(self, df: pd.DataFrame, metric: str) -> pd.DataFrame:
        """Fallback trend analysis when no time/state grouping is possible"""
        
        if metric and metric in df.columns:
            summary_data = {
                'metric': [metric],
                'avg_value': [df[metric].mean()],
                'record_count': [len(df)]
            }
            return pd.DataFrame(summary_data)
        
        return df.head(10)
    
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