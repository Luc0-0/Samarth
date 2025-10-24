"""
Answer Synthesis module for Project Samarth
Converts query results into human-readable answers with citations
"""

import pandas as pd
from typing import Dict, List, Any
import json
from datetime import datetime

class AnswerSynthesizer:
    def __init__(self):
        pass
        
    def synthesize_answer(self, intent: Dict, query_result: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Synthesize human-readable answer from query results"""
        
        if 'error' in query_result:
            return {
                'answer_text': f"I encountered an error: {query_result['error']}",
                'structured_results': [],
                'citations': []
            }
            
        results_df = query_result['results']
        
        if results_df.empty:
            return {
                'answer_text': "I couldn't find any data matching your query.",
                'structured_results': [],
                'citations': self._generate_citations(sources)
            }
        
        # Generate answer based on query type
        if intent['query_type'] == 'comparison':
            answer_text = self._synthesize_comparison_answer(intent, query_result, results_df)
        elif intent['query_type'] == 'trend':
            answer_text = self._synthesize_trend_answer(intent, query_result, results_df)
        elif intent['query_type'] == 'correlation':
            answer_text = self._synthesize_correlation_answer(intent, query_result, results_df)
        elif intent['query_type'] == 'ranking':
            answer_text = self._synthesize_ranking_answer(intent, query_result, results_df)
        else:
            answer_text = self._synthesize_general_answer(intent, query_result, results_df)
        
        # Convert DataFrame to structured results
        structured_results = results_df.to_dict('records')
        
        # Generate citations
        citations = self._generate_citations(sources)
        
        return {
            'answer_text': answer_text,
            'structured_results': structured_results,
            'citations': citations
        }
    
    def _synthesize_comparison_answer(self, intent: Dict, query_result: Dict, results_df: pd.DataFrame) -> str:
        """Synthesize comparison answer"""
        metric = query_result.get('metric', 'value')
        
        if len(results_df) < 2:
            return "Insufficient data for comparison."
            
        top_state = results_df.iloc[0]
        bottom_state = results_df.iloc[-1]
        
        answer = f"Comparing {metric.replace('_', ' ')} across the requested states:\n\n"
        answer += f"**Highest**: {top_state['state']} with an average of {top_state['avg_value']:.2f}\n"
        answer += f"**Lowest**: {bottom_state['state']} with an average of {bottom_state['avg_value']:.2f}\n\n"
        
        if len(results_df) > 2:
            answer += "**Complete ranking**:\n"
            for i, row in results_df.iterrows():
                answer += f"{i+1}. {row['state']}: {row['avg_value']:.2f}\n"
                
        return answer
    
    def _synthesize_trend_answer(self, intent: Dict, query_result: Dict, results_df: pd.DataFrame) -> str:
        """Synthesize trend analysis answer"""
        metric = query_result.get('metric', 'value')
        
        if len(results_df) < 2:
            return "Insufficient data for trend analysis."
            
        first_year = results_df.iloc[0]
        last_year = results_df.iloc[-1]
        
        change = last_year['avg_value'] - first_year['avg_value']
        change_pct = (change / first_year['avg_value']) * 100 if first_year['avg_value'] != 0 else 0
        
        trend_direction = "increased" if change > 0 else "decreased"
        
        answer = f"**Trend Analysis for {metric.replace('_', ' ')}**:\n\n"
        answer += f"From {first_year['year']} to {last_year['year']}, the average {metric.replace('_', ' ')} "
        answer += f"has {trend_direction} by {abs(change):.2f} ({abs(change_pct):.1f}%).\n\n"
        
        answer += f"**Starting value** ({first_year['year']}): {first_year['avg_value']:.2f}\n"
        answer += f"**Ending value** ({last_year['year']}): {last_year['avg_value']:.2f}\n\n"
        
        # Find peak and trough
        max_row = results_df.loc[results_df['avg_value'].idxmax()]
        min_row = results_df.loc[results_df['avg_value'].idxmin()]
        
        answer += f"**Peak**: {max_row['avg_value']:.2f} in {max_row['year']}\n"
        answer += f"**Trough**: {min_row['avg_value']:.2f} in {min_row['year']}\n"
        
        return answer
    
    def _synthesize_correlation_answer(self, intent: Dict, query_result: Dict, results_df: pd.DataFrame) -> str:
        """Synthesize correlation analysis answer"""
        correlation = query_result.get('correlation')
        
        if correlation is None:
            return "Unable to calculate correlation with available data."
            
        # Interpret correlation strength
        if abs(correlation) > 0.7:
            strength = "strong"
        elif abs(correlation) > 0.3:
            strength = "moderate"
        else:
            strength = "weak"
            
        direction = "positive" if correlation > 0 else "negative"
        
        answer = f"**Correlation Analysis**:\n\n"
        answer += f"There is a **{strength} {direction} correlation** (r = {correlation:.3f}) "
        answer += f"between rainfall and crop production.\n\n"
        
        if correlation > 0:
            answer += "This suggests that higher rainfall is generally associated with higher crop production."
        else:
            answer += "This suggests that higher rainfall is generally associated with lower crop production."
            
        answer += f"\n\nAnalysis based on {len(results_df)} data points across multiple states and years."
        
        return answer
    
    def _synthesize_ranking_answer(self, intent: Dict, query_result: Dict, results_df: pd.DataFrame) -> str:
        """Synthesize ranking answer"""
        metric = query_result.get('metric', 'value')
        
        answer = f"**Top performers by {metric.replace('_', ' ')}**:\n\n"
        
        for i, row in results_df.head(5).iterrows():
            rank = i + 1
            state = row['state']
            value = row['avg_value']
            
            if 'crop' in row:
                answer += f"{rank}. {state} ({row['crop']}): {value:.2f}\n"
            else:
                answer += f"{rank}. {state}: {value:.2f}\n"
                
        if len(results_df) > 5:
            answer += f"\n... and {len(results_df) - 5} more entries."
            
        return answer
    
    def _synthesize_general_answer(self, intent: Dict, query_result: Dict, results_df: pd.DataFrame) -> str:
        """Synthesize general answer"""
        metric = query_result.get('metric', 'value')
        
        if len(results_df) == 1:
            row = results_df.iloc[0]
            value_col = [col for col in row.index if 'value' in col][0]
            value = row[value_col]
            
            answer = f"Based on the available data, the {intent['aggregation']} {metric.replace('_', ' ')} is {value:.2f}."
            
            if 'record_count' in row:
                answer += f"\n\nThis calculation is based on {row['record_count']} records."
        else:
            answer = "Here are the results from your query:\n\n"
            for i, row in results_df.iterrows():
                answer += f"• {row.to_dict()}\n"
                
        return answer
    
    def _generate_citations(self, sources: List[Dict]) -> List[Dict]:
        """Generate citations for used sources"""
        citations = []
        
        for source in sources:
            citation = {
                'dataset_title': source['dataset_title'],
                'resource_url': source['resource_url'],
                'publisher': source.get('publisher', 'Unknown'),
                'query_summary': f"Used {source['table_name']} table for {source['geo_granularity']} level data"
            }
            citations.append(citation)
            
        return citations