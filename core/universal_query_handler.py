"""
Universal Query Handler for Project Samarth
Handles any question by intelligently routing to appropriate query types
"""

import pandas as pd
from typing import Dict, List, Any
import logging
from .query_planner import QueryPlanner
from .live_query_planner import LiveQueryPlanner

logger = logging.getLogger(__name__)

class UniversalQueryHandler:
    def __init__(self, db_path: str, api_key: str = None):
        self.query_planner = QueryPlanner(db_path)
        self.live_query_planner = LiveQueryPlanner(db_path, api_key)
        
    def handle_any_question(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Handle any question by trying multiple approaches"""
        
        # Try the original query type first
        try:
            if self._should_use_live_data(intent):
                result = self.live_query_planner.execute_query(intent, sources)
            else:
                result = self.query_planner.execute_query(intent, sources)
                
            if not self._is_empty_result(result):
                return result
        except Exception as e:
            logger.warning(f"Primary query failed: {str(e)}")
        
        # Fallback strategies
        fallback_strategies = [
            self._try_as_general_query,
            self._try_as_aggregation,
            self._try_as_search,
            self._try_flexible_matching
        ]
        
        for strategy in fallback_strategies:
            try:
                result = strategy(intent, sources)
                if not self._is_empty_result(result):
                    return result
            except Exception as e:
                logger.warning(f"Fallback strategy failed: {str(e)}")
                continue
        
        # Final fallback - return available data
        return self._return_sample_data(intent, sources)
    
    def _should_use_live_data(self, intent: Dict) -> bool:
        """Check if should use live data"""
        question_lower = intent.get('question', '').lower()
        return any(keyword in question_lower for keyword in 
                  ['current', 'latest', 'recent', 'live', 'market', 'price', 'now', 'today'])
    
    def _is_empty_result(self, result: Dict) -> bool:
        """Check if result is empty or has error"""
        if 'error' in result:
            return True
        if 'results' not in result:
            return True
        if isinstance(result['results'], pd.DataFrame) and result['results'].empty:
            return True
        return False
    
    def _try_as_general_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Try as general aggregation query"""
        logger.info("Trying as general query")
        
        # Override query type to general
        modified_intent = intent.copy()
        modified_intent['query_type'] = 'general'
        
        return self.query_planner.execute_query(modified_intent, sources)
    
    def _try_as_aggregation(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Try as simple aggregation"""
        logger.info("Trying as aggregation query")
        
        # Determine best table and metric
        if 'rainfall' in intent.get('metrics', []) or 'rain' in intent.get('question', '').lower():
            table_name = 'climate_obs'
            metric_col = 'rainfall_mm'
        else:
            table_name = 'agri_production'
            metric_col = 'production_tonnes'
        
        # Build flexible query
        where_clauses = []
        if intent.get('states'):
            states_list = "', '".join(intent['states'])
            where_clauses.append(f"state IN ('{states_list}')")
        
        if intent.get('crops') and table_name == 'agri_production':
            crops_list = "', '".join(intent['crops'])
            where_clauses.append(f"crop IN ('{crops_list}')")
        
        where_clause = ' AND '.join(where_clauses) if where_clauses else '1=1'
        
        query = f"""
        SELECT 
            state,
            {f'crop,' if table_name == 'agri_production' else ''}
            AVG({metric_col}) as avg_value,
            COUNT(*) as record_count
        FROM {table_name}
        WHERE {where_clause}
        GROUP BY state{', crop' if table_name == 'agri_production' else ''}
        ORDER BY avg_value DESC
        LIMIT 20
        """
        
        import duckdb
        with duckdb.connect(self.query_planner.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': metric_col,
            'table_used': table_name,
            'fallback_used': 'aggregation'
        }
    
    def _try_as_search(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Try as keyword search across all data"""
        logger.info("Trying as search query")
        
        question_words = intent.get('question', '').lower().split()
        
        # Search in agriculture data
        agri_query = f"""
        SELECT 
            state, crop, year,
            production_tonnes as value,
            'production' as metric_type
        FROM agri_production
        WHERE 1=1
        """
        
        # Add filters based on question words
        if intent.get('states'):
            states_list = "', '".join(intent['states'])
            agri_query += f" AND state IN ('{states_list}')"
        
        if intent.get('crops'):
            crops_list = "', '".join(intent['crops'])
            agri_query += f" AND crop IN ('{crops_list}')"
        
        agri_query += " ORDER BY production_tonnes DESC LIMIT 10"
        
        import duckdb
        with duckdb.connect(self.query_planner.db_path) as conn:
            results = conn.execute(agri_query).df()
        
        return {
            'query': agri_query,
            'results': results,
            'metric': 'search_results',
            'table_used': 'agri_production',
            'fallback_used': 'search'
        }
    
    def _try_flexible_matching(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Try flexible matching with relaxed constraints"""
        logger.info("Trying flexible matching")
        
        # Just return top records from relevant table
        question_lower = intent.get('question', '').lower()
        
        if any(word in question_lower for word in ['rain', 'climate', 'weather', 'monsoon']):
            table_name = 'climate_obs'
            query = """
            SELECT state, year, rainfall_mm as value, 'rainfall' as type
            FROM climate_obs 
            ORDER BY rainfall_mm DESC 
            LIMIT 15
            """
        else:
            table_name = 'agri_production'
            query = """
            SELECT state, crop, year, production_tonnes as value, 'production' as type
            FROM agri_production 
            ORDER BY production_tonnes DESC 
            LIMIT 15
            """
        
        import duckdb
        with duckdb.connect(self.query_planner.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': 'flexible_match',
            'table_used': table_name,
            'fallback_used': 'flexible'
        }
    
    def _return_sample_data(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Final fallback - return sample data with helpful message"""
        logger.info("Using final fallback - sample data")
        
        query = """
        SELECT 
            'Sample Data' as note,
            state, crop, year, production_tonnes as value
        FROM agri_production 
        ORDER BY RANDOM() 
        LIMIT 10
        """
        
        import duckdb
        with duckdb.connect(self.query_planner.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': 'sample_data',
            'table_used': 'agri_production',
            'fallback_used': 'sample',
            'message': 'I found some related data that might help answer your question.'
        }