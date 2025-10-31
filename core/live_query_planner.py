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
        
        # For price queries, don't fall back to local data - use universal handler directly
        if self._is_price_query(intent):
            logger.info("Price query detected, using universal handler for proper error message")
            return self.universal_handler.handle_any_question(intent, sources, {'error': 'Live API not available for price data'})
        
        # Try local data for non-price queries
        logger.info("Using local database for query")
        try:
            result = super().execute_query(intent, sources)
        except Exception as e:
            logger.error(f"Local query failed: {str(e)}")
            result = {'error': str(e)}
        
        # Use universal handler for any failed queries
        return self.universal_handler.handle_any_question(intent, sources, result)
    
    def _generate_mock_price_data(self, intent: Dict) -> Dict[str, Any]:
        """Generate mock price data when live API fails"""
        
        mock_prices = {
            'Rice': {'Punjab': 2200, 'Maharashtra': 2100, 'Haryana': 2150},
            'Cotton': {'Punjab': 5500, 'Gujarat': 5800, 'Maharashtra': 5400},
            'Wheat': {'Punjab': 2000, 'Uttar Pradesh': 1950, 'Haryana': 2050}
        }
        
        results = []
        crops = intent.get('crops', ['Rice'])
        states = intent.get('states', ['Punjab'])
        
        for crop in crops:
            for state in states:
                price = mock_prices.get(crop, {}).get(state, 2200)
                results.append({
                    'state': state,
                    'crop': crop,
                    'avg_value': price,
                    'record_count': 1
                })
        
        return {
            'results': pd.DataFrame(results),
            'query': 'Mock price data (API unavailable)',
            'metric': 'price_per_quintal',
            'data_source': 'mock_data',
            'note': 'Using demo data - government API temporarily unavailable',
            'is_mock_data': True
        }
    
    def _is_price_query(self, intent: Dict) -> bool:
        """Check if this is a price query"""
        question_lower = intent.get('question', '').lower()
        return ('price' in intent.get('metrics', []) or 
                any(word in question_lower for word in ['price', 'market', 'cost', 'rate', 'mandi']))
    
    def _should_use_live_data(self, intent: Dict) -> bool:
        """Determine if we should fetch live data"""
        
        question_lower = intent.get('question', '').lower()
        
        # Always use live data for price queries
        if 'price' in intent.get('metrics', []):
            logger.info("Using live data: price metric detected")
            return True
        if any(keyword in question_lower for keyword in ['price', 'market', 'cost', 'rate', 'mandi']):
            logger.info("Using live data: price keywords detected")
            return True
        # Use live data for current/recent queries
        if intent.get('query_type') == 'current':
            logger.info("Using live data: current query type")
            return True
        # Check for live keywords in the question
        if any(keyword in question_lower for keyword in ['current', 'latest', 'recent', 'live', 'now', 'today']):
            logger.info("Using live data: temporal keywords detected")
            return True
            
        return False
    
    def _execute_live_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute query using live data from API with comprehensive data fetching"""
        
        results_df = pd.DataFrame()
        data_sources_used = []
        
        # Prioritize market data for price queries
        question_lower = intent.get('question', '').lower()
        if any(word in question_lower for word in ['price', 'market', 'cost', 'rate', 'mandi']) or 'price' in intent.get('metrics', []):
            fetch_strategies = [
                ('market_api', self._fetch_market_data),
                ('live_sources', self._fetch_from_live_sources),
                ('agriculture_api', self._fetch_agriculture_data)
            ]
            logger.info("Using price-prioritized fetch strategies")
        else:
            fetch_strategies = [
                ('live_sources', self._fetch_from_live_sources),
                ('agriculture_api', self._fetch_agriculture_data),
                ('rainfall_api', self._fetch_rainfall_data),
                ('market_api', self._fetch_market_data)
            ]
        
        for strategy_name, fetch_method in fetch_strategies:
            try:
                data = fetch_method(intent, sources)
                if not data.empty:
                    logger.info(f"Successfully fetched data using {strategy_name}")
                    data = self._standardize_agriculture_columns(data)
                    results_df = pd.concat([results_df, data], ignore_index=True)
                    data_sources_used.append(strategy_name)
                    break  # Use first successful fetch
            except Exception as e:
                logger.warning(f"Failed to fetch using {strategy_name}: {str(e)}")
                continue
        
        if results_df.empty:
            logger.warning(f"No live data found, using mock data for: {intent.get('question', 'Unknown')}")
            return self._generate_mock_price_data(intent)
        
        # Enhanced data processing
        processed_results = self._process_live_results_enhanced(results_df, intent)
        
        return {
            'results': processed_results,
            'query': f"Live data fetch from data.gov.in API ({', '.join(data_sources_used)})",
            'metric': self._get_actual_metric_from_results(processed_results),
            'data_source': 'live_api',
            'sources_used': data_sources_used,
            'total_records': len(results_df)
        }
    
    def _fetch_from_live_sources(self, intent: Dict, sources: List[Dict]) -> pd.DataFrame:
        """Fetch from explicitly live sources"""
        if any('live' in src['dataset_id'] for src in sources):
            return self.live_fetcher.get_agriculture_data(
                states=intent.get('states', []),
                crops=intent.get('crops', [])
            )
        return pd.DataFrame()
    
    def _fetch_agriculture_data(self, intent: Dict, sources: List[Dict]) -> pd.DataFrame:
        """Fetch agriculture production data"""
        return self.live_fetcher.get_agriculture_data(
            states=intent.get('states', []),
            crops=intent.get('crops', [])
        )
    
    def _fetch_rainfall_data(self, intent: Dict, sources: List[Dict]) -> pd.DataFrame:
        """Fetch rainfall data if query is about climate"""
        question_lower = intent.get('question', '').lower()
        if any(word in question_lower for word in ['rain', 'climate', 'weather', 'monsoon']):
            return self.live_fetcher.get_rainfall_data(
                states=intent.get('states', [])
            )
        return pd.DataFrame()
    
    def _fetch_market_data(self, intent: Dict, sources: List[Dict]) -> pd.DataFrame:
        """Fetch market price data if query is about prices"""
        question_lower = intent.get('question', '').lower()
        if any(word in question_lower for word in ['price', 'market', 'cost', 'rate', 'mandi']):
            # Try to get market price data specifically using price resource ID
            return self.live_fetcher.get_market_prices(
                states=intent.get('states', []),
                crops=intent.get('crops', [])
            )
        return pd.DataFrame()
    
    def _process_live_results_enhanced(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Enhanced processing of live results"""
        
        query_type = intent.get('query_type', 'general')
        
        # Log data characteristics for debugging
        logger.info(f"Processing {len(df)} records with columns: {list(df.columns)}")
        logger.info(f"Query type: {query_type}")
        
        # Enhanced processing based on query type
        if query_type == 'comparison':
            return self._process_comparison_live(df, intent)
        elif query_type == 'trend':
            return self._process_trend_live(df, intent)
        elif query_type == 'ranking':
            return self._process_ranking_live(df, intent)
        elif query_type == 'correlation':
            return self._process_correlation_live(df, intent)
        else:
            return self._process_general_live(df, intent)
    
    def _process_correlation_live(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process correlation analysis on live data"""
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) < 2:
            return pd.DataFrame({'error': ['Need at least 2 numeric columns for correlation analysis']})
        
        # Calculate correlations between all numeric columns
        corr_matrix = df[numeric_cols].corr()
        
        # Convert correlation matrix to readable format
        result_data = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:  # Avoid duplicates
                    result_data.append({
                        'metric_1': col1,
                        'metric_2': col2,
                        'correlation': corr_matrix.loc[col1, col2],
                        'strength': self._interpret_correlation(corr_matrix.loc[col1, col2])
                    })
        
        return pd.DataFrame(result_data).sort_values('correlation', key=abs, ascending=False)
    
    def _interpret_correlation(self, corr_value: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(corr_value)
        if abs_corr > 0.7:
            return 'Strong'
        elif abs_corr > 0.3:
            return 'Moderate'
        else:
            return 'Weak'
    
    def _get_actual_metric_from_results(self, df: pd.DataFrame) -> str:
        """Get the actual metric used in results"""
        if 'avg_value' in df.columns:
            # Try to determine what the avg_value represents
            if any('price' in str(col).lower() for col in df.columns):
                return 'price_per_quintal'
            elif any('production' in str(col).lower() for col in df.columns):
                return 'production_tonnes'
        return 'value'
    
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
        
        # Determine the metric based on query intent first
        if 'price' in intent.get('metrics', []) or 'market' in intent.get('question', '').lower():
            if 'price_per_quintal' in df.columns:
                metric = 'price_per_quintal'
            elif 'modal_price' in df.columns:
                metric = 'modal_price'
            else:
                # If price requested but not available, return error
                return pd.DataFrame({'error': ['Price data not available in current dataset']})
        elif 'price_per_quintal' in df.columns:
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
        """Process ranking query on live data with enhanced capabilities"""
        
        question_lower = intent.get('question', '').lower()
        
        # Determine ranking criteria
        if any(word in question_lower for word in ['price', 'cost', 'expensive', 'cheap']):
            return self._rank_by_price(df, intent)
        elif any(word in question_lower for word in ['production', 'yield', 'output', 'harvest']):
            return self._rank_by_production(df, intent)
        elif any(word in question_lower for word in ['area', 'acreage', 'land']):
            return self._rank_by_area(df, intent)
        else:
            return self._rank_by_best_available_metric(df, intent)
    
    def _rank_by_price(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Rank by price metrics"""
        
        price_cols = [col for col in df.columns if 'price' in col.lower()]
        if not price_cols:
            return pd.DataFrame({'error': ['No price data available for ranking']})
        
        price_col = price_cols[0]
        
        # Determine ranking dimension
        if 'state' in df.columns and 'crop' in df.columns:
            # Rank state-crop combinations
            result = df.groupby(['state', 'crop'])[price_col].agg(['mean', 'max', 'min', 'count']).reset_index()
            result.columns = ['state', 'crop', 'avg_price', 'max_price', 'min_price', 'record_count']
            
            # Determine if looking for highest or lowest
            if any(word in intent.get('question', '').lower() for word in ['cheap', 'lowest', 'minimum']):
                return result.sort_values('avg_price', ascending=True).head(15)
            else:
                return result.sort_values('avg_price', ascending=False).head(15)
        
        elif 'state' in df.columns:
            result = df.groupby('state')[price_col].agg(['mean', 'count']).reset_index()
            result.columns = ['state', 'avg_price', 'record_count']
            
            if any(word in intent.get('question', '').lower() for word in ['cheap', 'lowest', 'minimum']):
                return result.sort_values('avg_price', ascending=True)
            else:
                return result.sort_values('avg_price', ascending=False)
        
        elif 'crop' in df.columns:
            result = df.groupby('crop')[price_col].agg(['mean', 'count']).reset_index()
            result.columns = ['crop', 'avg_price', 'record_count']
            return result.sort_values('avg_price', ascending=False)
        
        return df.head(10)
    
    def _rank_by_production(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Rank by production metrics"""
        
        prod_cols = [col for col in df.columns if any(word in col.lower() for word in ['production', 'yield', 'output'])]
        if not prod_cols:
            return pd.DataFrame({'error': ['No production data available for ranking']})
        
        prod_col = prod_cols[0]
        
        if 'state' in df.columns and 'crop' in df.columns:
            result = df.groupby(['state', 'crop'])[prod_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['state', 'crop', 'total_production', 'avg_production', 'record_count']
            return result.sort_values('total_production', ascending=False).head(20)
        
        elif 'state' in df.columns:
            result = df.groupby('state')[prod_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['state', 'total_production', 'avg_production', 'record_count']
            return result.sort_values('total_production', ascending=False)
        
        elif 'crop' in df.columns:
            result = df.groupby('crop')[prod_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['crop', 'total_production', 'avg_production', 'record_count']
            return result.sort_values('total_production', ascending=False)
        
        return df.head(10)
    
    def _rank_by_area(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Rank by area metrics"""
        
        area_cols = [col for col in df.columns if 'area' in col.lower()]
        if not area_cols:
            return pd.DataFrame({'error': ['No area data available for ranking']})
        
        area_col = area_cols[0]
        
        if 'state' in df.columns and 'crop' in df.columns:
            result = df.groupby(['state', 'crop'])[area_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['state', 'crop', 'total_area', 'avg_area', 'record_count']
            return result.sort_values('total_area', ascending=False).head(20)
        
        elif 'state' in df.columns:
            result = df.groupby('state')[area_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['state', 'total_area', 'avg_area', 'record_count']
            return result.sort_values('total_area', ascending=False)
        
        return df.head(10)
    
    def _rank_by_best_available_metric(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Rank by best available numeric metric"""
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return df.head(10)
        
        # Use the first numeric column as ranking criteria
        metric_col = numeric_cols[0]
        
        if 'state' in df.columns:
            result = df.groupby('state')[metric_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['state', f'total_{metric_col}', f'avg_{metric_col}', 'record_count']
            return result.sort_values(f'total_{metric_col}', ascending=False)
        
        elif 'crop' in df.columns:
            result = df.groupby('crop')[metric_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['crop', f'total_{metric_col}', f'avg_{metric_col}', 'record_count']
            return result.sort_values(f'total_{metric_col}', ascending=False)
        
        return df.sort_values(metric_col, ascending=False).head(15)
    
    def _process_general_live(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process general query on live data with enhanced capabilities"""
        
        # Determine what type of general processing to do
        question_lower = intent.get('question', '').lower()
        
        # Price-specific processing
        if any(word in question_lower for word in ['price', 'cost', 'rate', 'market', 'mandi']):
            return self._process_price_query(df, intent)
        
        # Production-specific processing
        elif any(word in question_lower for word in ['production', 'yield', 'harvest', 'output']):
            return self._process_production_query(df, intent)
        
        # Area-specific processing
        elif any(word in question_lower for word in ['area', 'acreage', 'land', 'cultivation']):
            return self._process_area_query(df, intent)
        
        # Default aggregation
        return self._process_default_aggregation(df, intent)
    
    def _process_price_query(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process price-specific queries"""
        
        price_cols = [col for col in df.columns if 'price' in col.lower()]
        if not price_cols:
            return pd.DataFrame({'error': ['No price data available in current dataset']})
        
        price_col = price_cols[0]
        
        # Group by relevant dimensions
        if 'commodity' in df.columns or 'crop' in df.columns:
            crop_col = 'commodity' if 'commodity' in df.columns else 'crop'
            result = df.groupby([crop_col, 'state'] if 'state' in df.columns else [crop_col])[price_col].agg(['mean', 'min', 'max', 'count']).reset_index()
            result.columns = [crop_col] + (['state'] if 'state' in df.columns else []) + ['avg_price', 'min_price', 'max_price', 'record_count']
            return result.sort_values('avg_price', ascending=False)
        
        elif 'state' in df.columns:
            result = df.groupby('state')[price_col].agg(['mean', 'min', 'max', 'count']).reset_index()
            result.columns = ['state', 'avg_price', 'min_price', 'max_price', 'record_count']
            return result.sort_values('avg_price', ascending=False)
        
        else:
            # Overall price statistics
            stats = {
                'metric': ['Overall Price Statistics'],
                'avg_price': [df[price_col].mean()],
                'min_price': [df[price_col].min()],
                'max_price': [df[price_col].max()],
                'record_count': [len(df)]
            }
            return pd.DataFrame(stats)
    
    def _process_production_query(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process production-specific queries"""
        
        prod_cols = [col for col in df.columns if any(word in col.lower() for word in ['production', 'yield', 'output'])]
        if not prod_cols:
            return pd.DataFrame({'error': ['No production data available in current dataset']})
        
        prod_col = prod_cols[0]
        
        # Enhanced production analysis
        if 'crop' in df.columns and 'state' in df.columns:
            result = df.groupby(['state', 'crop'])[prod_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['state', 'crop', 'total_production', 'avg_production', 'record_count']
            return result.sort_values('total_production', ascending=False)
        
        elif 'state' in df.columns:
            result = df.groupby('state')[prod_col].agg(['sum', 'mean', 'std', 'count']).reset_index()
            result.columns = ['state', 'total_production', 'avg_production', 'std_production', 'record_count']
            return result.sort_values('total_production', ascending=False)
        
        elif 'crop' in df.columns:
            result = df.groupby('crop')[prod_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['crop', 'total_production', 'avg_production', 'record_count']
            return result.sort_values('total_production', ascending=False)
        
        else:
            return self._process_default_aggregation(df, intent)
    
    def _process_area_query(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Process area-specific queries"""
        
        area_cols = [col for col in df.columns if 'area' in col.lower()]
        if not area_cols:
            return pd.DataFrame({'error': ['No area data available in current dataset']})
        
        area_col = area_cols[0]
        
        if 'crop' in df.columns and 'state' in df.columns:
            result = df.groupby(['state', 'crop'])[area_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['state', 'crop', 'total_area', 'avg_area', 'record_count']
            return result.sort_values('total_area', ascending=False)
        
        elif 'state' in df.columns:
            result = df.groupby('state')[area_col].agg(['sum', 'mean', 'count']).reset_index()
            result.columns = ['state', 'total_area', 'avg_area', 'record_count']
            return result.sort_values('total_area', ascending=False)
        
        else:
            return self._process_default_aggregation(df, intent)
    
    def _process_default_aggregation(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Default aggregation processing"""
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return df.head(10)
        
        # Multi-dimensional aggregation
        if 'state' in df.columns and 'crop' in df.columns:
            result_data = []
            for col in numeric_cols[:3]:  # Limit to top 3 numeric columns
                state_crop_agg = df.groupby(['state', 'crop'])[col].mean().reset_index()
                state_crop_agg['metric'] = col
                state_crop_agg.columns = ['state', 'crop', 'avg_value', 'metric']
                result_data.append(state_crop_agg)
            
            if result_data:
                return pd.concat(result_data, ignore_index=True).sort_values('avg_value', ascending=False)
        
        elif 'state' in df.columns:
            result = df.groupby('state')[numeric_cols].mean().reset_index()
            return result.sort_values(numeric_cols[0], ascending=False)
        
        elif 'crop' in df.columns:
            result = df.groupby('crop')[numeric_cols].mean().reset_index()
            return result.sort_values(numeric_cols[0], ascending=False)
        
        else:
            # Overall statistics
            result = df[numeric_cols].agg(['mean', 'min', 'max', 'std']).T.reset_index()
            result.columns = ['metric', 'avg_value', 'min_value', 'max_value', 'std_value']
            return result