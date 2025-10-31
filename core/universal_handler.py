"""
Universal Query Handler - Makes system answer any question
"""

import pandas as pd
import duckdb
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class UniversalHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def handle_any_question(self, intent: Dict, sources: List[Dict], original_result: Dict) -> Dict[str, Any]:
        """Handle any question with smart fallbacks"""
        
        # If original query worked, return it
        if not self._is_failed_result(original_result):
            return original_result
        
        logger.info(f"Original query failed, trying fallbacks for: {intent.get('question', 'Unknown')}")
        
        # Special handling for price queries
        if self._is_price_query(intent):
            return self._handle_price_query_fallback(intent)
        
        # Try fallback strategies in order
        strategies = [
            self._try_general_aggregation,
            self._try_keyword_search,
            self._try_sample_data
        ]
        
        for strategy in strategies:
            try:
                result = strategy(intent, sources)
                if not self._is_failed_result(result):
                    return result
            except Exception as e:
                logger.warning(f"Fallback strategy failed: {str(e)}")
                continue
        
        # Final fallback
        return self._return_helpful_message(intent)
    
    def _is_failed_result(self, result: Dict) -> bool:
        """Check if result failed"""
        if not result:
            return True
        if 'error' in result:
            return True
        if 'results' not in result:
            return True
        if isinstance(result.get('results'), pd.DataFrame) and result['results'].empty:
            return True
        return False
    
    def _try_general_aggregation(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Try general aggregation query"""
        logger.info("Trying general aggregation")
        
        question_lower = intent.get('question', '').lower()
        
        # Determine table and metric
        if any(word in question_lower for word in ['rain', 'climate', 'weather', 'monsoon']):
            table = 'climate_obs'
            metric = 'rainfall_mm'
        else:
            table = 'agri_production'
            metric = 'production_tonnes'
        
        # Build flexible query
        where_parts = []
        if intent.get('states'):
            states = "', '".join(intent['states'])
            where_parts.append(f"state IN ('{states}')")
        
        if intent.get('crops') and table == 'agri_production':
            crops = "', '".join(intent['crops'])
            where_parts.append(f"crop IN ('{crops}')")
        
        where_clause = ' AND '.join(where_parts) if where_parts else '1=1'
        
        query = f"""
        SELECT 
            state,
            {f'crop,' if table == 'agri_production' else ''}
            AVG({metric}) as avg_value,
            COUNT(*) as record_count
        FROM {table}
        WHERE {where_clause}
        GROUP BY state{', crop' if table == 'agri_production' else ''}
        ORDER BY avg_value DESC
        LIMIT 15
        """
        
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': metric,
            'table_used': table,
            'fallback_used': 'general_aggregation'
        }
    
    def _try_keyword_search(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Try keyword-based search"""
        logger.info("Trying keyword search")
        
        question_lower = intent.get('question', '').lower()
        
        # Search agriculture data for any matches
        query = """
        SELECT 
            state, crop, year,
            production_tonnes as value,
            'Agriculture Data' as source
        FROM agri_production
        WHERE 1=1
        """
        
        # Add any available filters
        if intent.get('states'):
            states = "', '".join(intent['states'])
            query += f" AND state IN ('{states}')"
        
        if intent.get('crops'):
            crops = "', '".join(intent['crops'])
            query += f" AND crop IN ('{crops}')"
        
        query += " ORDER BY production_tonnes DESC LIMIT 10"
        
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': 'search_results',
            'table_used': 'agri_production',
            'fallback_used': 'keyword_search'
        }
    
    def _try_sample_data(self, intent: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Return sample data with context"""
        logger.info("Returning sample data")
        
        query = """
        SELECT 
            state, crop, year, production_tonnes as value
        FROM agri_production 
        ORDER BY production_tonnes DESC 
        LIMIT 8
        """
        
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(query).df()
        
        return {
            'query': query,
            'results': results,
            'metric': 'sample_data',
            'table_used': 'agri_production',
            'fallback_used': 'sample_data'
        }
    
    def _is_price_query(self, intent: Dict) -> bool:
        """Check if this is a price query"""
        question_lower = intent.get('question', '').lower()
        return ('price' in intent.get('metrics', []) or 
                any(word in question_lower for word in ['price', 'market', 'cost', 'rate', 'mandi']))
    
    def _handle_price_query_fallback(self, intent: Dict) -> Dict[str, Any]:
        """Handle price query when live API is not available"""
        logger.info("Handling price query fallback with mock data")
        
        states = intent.get('states', [])
        crops = intent.get('crops', [])
        
        # Generate mock price data for demo
        mock_prices = {
            'Rice': {'Punjab': 2200, 'Maharashtra': 2100, 'West Bengal': 2000},
            'Cotton': {'Punjab': 5500, 'Gujarat': 5800, 'Maharashtra': 5400},
            'Wheat': {'Punjab': 2000, 'Uttar Pradesh': 1950, 'Haryana': 2050}
        }
        
        results = []
        for crop in crops if crops else ['Rice', 'Cotton', 'Wheat']:
            for state in states if states else ['Punjab', 'Maharashtra', 'Gujarat']:
                if crop in mock_prices and state in mock_prices[crop]:
                    results.append({
                        'crop': crop,
                        'state': state,
                        'price_per_quintal': mock_prices[crop][state],
                        'date': '2024-01-15',
                        'source': 'Mock Data'
                    })
        
        if not results:
            # Fallback to generic mock data
            results = [{
                'crop': crops[0] if crops else 'Rice',
                'state': states[0] if states else 'Punjab', 
                'price_per_quintal': 2200,
                'date': '2024-01-15',
                'source': 'Mock Data'
            }]
        
        crop_text = f" for {', '.join(crops)}" if crops else ""
        state_text = f" in {', '.join(states)}" if states else ""
        
        answer = f"**Mock Market Prices{crop_text}{state_text}** (Demo Data):\n\n"
        for result in results:
            answer += f"• {result['crop']} in {result['state']}: ₹{result['price_per_quintal']} per quintal\n"
        
        answer += "\n*Note: This is mock data for demonstration. For real prices, a government API key is required.*"
        
        return {
            'answer_text': answer,
            'structured_results': results,
            'citations': [{
                'dataset_title': 'Mock Market Price Data',
                'resource_url': 'https://data.gov.in/',
                'publisher': 'Demo System',
                'query_summary': 'Mock data for demonstration purposes'
            }],
            'suggestion': 'Get a real API key from data.gov.in for live market prices',
            'error_type': 'using_mock_data',
            'query_type': 'price_query_mock'
        }
    
    def _return_helpful_message(self, intent: Dict) -> Dict[str, Any]:
        """Final fallback with helpful message"""
        return {
            'answer_text': 'I understand you\'re asking about agriculture or climate data, but I need more specific information. Try asking about specific states, crops, or time periods.',
            'structured_results': [],
            'citations': [],
            'suggestion': 'Example: "Compare rice production in Punjab and Maharashtra" or "Show rainfall trends in Gujarat"'
        }