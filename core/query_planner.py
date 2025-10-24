"""
Query Planning and Execution module for Project Samarth
Generates and executes SQL queries against canonical tables
"""

import duckdb
import pandas as pd
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class QueryPlanner:
    def __init__(self, db_path: str = 'db/canonical.duckdb'):
        self.db_path = db_path
        
    def execute_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute query based on intent and selected sources"""
        try:
            if intent['query_type'] == 'comparison':
                return self._execute_comparison_query(intent, sources)
            elif intent['query_type'] == 'trend':
                return self._execute_trend_query(intent, sources)
            elif intent['query_type'] == 'correlation':
                return self._execute_correlation_query(intent, sources)
            elif intent['query_type'] == 'ranking':
                return self._execute_ranking_query(intent, sources)
            else:
                return self._execute_general_query(intent, sources)
                
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return {'error': str(e), 'results': pd.DataFrame()}
    
    def _execute_comparison_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute comparison queries"""
        if len(intent['states']) < 2:
            return {'error': 'Comparison requires at least 2 states', 'results': pd.DataFrame()}
            
        # Build comparison query
        if 'rainfall' in intent['metrics']:
            table_name = 'climate_obs'
            metric_col = 'rainfall_mm'
        else:
            table_name = 'agri_production'
            metric_col = 'production_tonnes'
            
        states_list = "', '".join(intent['states'])
        
        query = f"""
        SELECT 
            state,
            AVG({metric_col}) as avg_value,
            COUNT(*) as record_count
        FROM {table_name}
        WHERE state IN ('{states_list}')
        GROUP BY state
        ORDER BY avg_value DESC
        """
        
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': metric_col,
            'table_used': table_name
        }
    
    def _execute_trend_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute trend analysis queries"""
        # Determine table and metric
        if 'rainfall' in intent['metrics']:
            table_name = 'climate_obs'
            metric_col = 'rainfall_mm'
        else:
            table_name = 'agri_production'
            metric_col = 'production_tonnes'
            
        # Build trend query
        where_clauses = []
        if intent['states']:
            states_list = "', '".join(intent['states'])
            where_clauses.append(f"state IN ('{states_list}')")
            
        if intent['crops'] and table_name == 'agri_production':
            crops_list = "', '".join(intent['crops'])
            where_clauses.append(f"crop IN ('{crops_list}')")
            
        where_clause = ' AND '.join(where_clauses) if where_clauses else '1=1'
        
        query = f"""
        SELECT 
            year,
            AVG({metric_col}) as avg_value,
            COUNT(*) as record_count
        FROM {table_name}
        WHERE {where_clause}
        GROUP BY year
        ORDER BY year
        """
        
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': metric_col,
            'table_used': table_name
        }
    
    def _execute_correlation_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute correlation analysis queries"""
        # Join agriculture and climate data
        query = """
        SELECT 
            a.state,
            a.year,
            AVG(a.production_tonnes) as avg_production,
            AVG(c.rainfall_mm) as avg_rainfall
        FROM agri_production a
        JOIN climate_obs c ON a.state = c.state AND a.year = c.year
        GROUP BY a.state, a.year
        ORDER BY a.state, a.year
        """
        
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(query).df()
        
        # Calculate correlation if we have data
        correlation = None
        if len(results) > 1:
            correlation = results['avg_production'].corr(results['avg_rainfall'])
        
        return {
            'query': query,
            'results': results,
            'correlation': correlation,
            'table_used': 'agri_production + climate_obs'
        }
    
    def _execute_ranking_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute ranking queries"""
        # Determine table and metric
        if 'rainfall' in intent['metrics']:
            table_name = 'climate_obs'
            metric_col = 'rainfall_mm'
        else:
            table_name = 'agri_production'
            metric_col = 'production_tonnes'
            
        # Build ranking query
        where_clauses = []
        if intent['states']:
            states_list = "', '".join(intent['states'])
            where_clauses.append(f"state IN ('{states_list}')")
            
        if intent['crops'] and table_name == 'agri_production':
            crops_list = "', '".join(intent['crops'])
            where_clauses.append(f"crop IN ('{crops_list}')")
            
        where_clause = ' AND '.join(where_clauses) if where_clauses else '1=1'
        
        query = f"""
        SELECT 
            state,
            {f'crop,' if table_name == 'agri_production' and intent['crops'] else ''}
            AVG({metric_col}) as avg_value,
            COUNT(*) as record_count
        FROM {table_name}
        WHERE {where_clause}
        GROUP BY state{', crop' if table_name == 'agri_production' and intent['crops'] else ''}
        ORDER BY avg_value DESC
        LIMIT 10
        """
        
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': metric_col,
            'table_used': table_name
        }
    
    def _execute_general_query(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Execute general queries"""
        # Default to aggregation query
        if 'rainfall' in intent['metrics']:
            table_name = 'climate_obs'
            metric_col = 'rainfall_mm'
        else:
            table_name = 'agri_production'
            metric_col = 'production_tonnes'
            
        agg_func = intent['aggregation'].upper()
        
        query = f"""
        SELECT 
            {agg_func}({metric_col}) as {agg_func.lower()}_value,
            COUNT(*) as record_count
        FROM {table_name}
        """
        
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': metric_col,
            'table_used': table_name
        }