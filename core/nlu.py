"""
Natural Language Understanding module for Project Samarth
Parses natural language questions into structured intents
"""

import re
from typing import Dict, List, Optional

class IntentParser:
    def __init__(self):
        self.states = [
            'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
            'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand', 'karnataka',
            'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
            'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim', 'tamil nadu',
            'telangana', 'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal'
        ]
        
        self.crops = [
            'rice', 'wheat', 'maize', 'bajra', 'jowar', 'ragi', 'cotton', 'sugarcane',
            'groundnut', 'sunflower', 'soybean', 'mustard', 'sesame', 'safflower',
            'coconut', 'areca nut', 'cashew', 'tea', 'coffee', 'rubber'
        ]
        
        self.metrics = {
            'production': ['production', 'yield', 'output', 'harvest'],
            'area': ['area', 'acreage', 'cultivation'],
            'rainfall': ['rainfall', 'precipitation', 'rain'],
            'temperature': ['temperature', 'temp'],
            'price': ['price', 'cost', 'rate', 'market', 'mandi'],
            'correlation': ['correlation', 'relationship', 'impact', 'effect']
        }

    def parse_question(self, text: str) -> Dict:
        """Parse natural language question into structured intent"""
        text_lower = text.lower()
        
        intent = {
            'question': text,
            'states': self._extract_states(text_lower),
            'districts': self._extract_districts(text_lower),
            'crops': self._extract_crops(text_lower),
            'metrics': self._extract_metrics(text_lower),
            'time_range': self._extract_time_range(text_lower),
            'query_type': self._determine_query_type(text_lower),
            'aggregation': self._extract_aggregation(text_lower)
        }
        
        return intent

    def _extract_states(self, text: str) -> List[str]:
        """Extract state names from text"""
        found_states = []
        for state in self.states:
            if state in text:
                found_states.append(state.title())
        return found_states

    def _extract_districts(self, text: str) -> List[str]:
        """Extract district names from text"""
        # Simple pattern matching for districts
        district_patterns = [
            r'(\w+)\s+district',
            r'district\s+(\w+)',
        ]
        
        districts = []
        for pattern in district_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            districts.extend([match.title() for match in matches])
        
        return districts

    def _extract_crops(self, text: str) -> List[str]:
        """Extract crop names from text"""
        found_crops = []
        for crop in self.crops:
            if crop in text:
                found_crops.append(crop.title())
        return found_crops

    def _extract_metrics(self, text: str) -> List[str]:
        """Extract metrics/measures from text"""
        found_metrics = []
        for metric, keywords in self.metrics.items():
            if any(keyword in text for keyword in keywords):
                found_metrics.append(metric)
        return found_metrics

    def _extract_time_range(self, text: str) -> Dict:
        """Extract time range from text"""
        # Extract years
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        
        # Extract relative time expressions
        time_expressions = {
            'last_n_years': re.search(r'last\s+(\d+)\s+years?', text),
            'recent_year': 'recent' in text or 'latest' in text,
            'decade': 'decade' in text,
            'annual': 'annual' in text or 'yearly' in text
        }
        
        return {
            'years': [int(y + match) for y, match in years] if years else [],
            'expressions': {k: v.group(1) if v and hasattr(v, 'group') else bool(v) 
                          for k, v in time_expressions.items()}
        }

    def _determine_query_type(self, text: str) -> str:
        """Determine the type of query"""
        # Check for specific analysis types first (higher priority)
        if any(word in text for word in ['trend', 'over time', 'change', 'pattern', 'analyse', 'analyze']):
            return 'trend'
        elif any(word in text for word in ['compare', 'comparison', 'versus', 'vs']):
            return 'comparison'
        elif any(word in text for word in ['correlation', 'relationship', 'impact']):
            return 'correlation'
        elif any(word in text for word in ['highest', 'maximum', 'top', 'best', 'ranking']):
            return 'ranking'
        # Check for live data keywords (lower priority than analysis types)
        elif any(keyword in text for keyword in ['current', 'latest', 'recent', 'live', 'today', 'now', 'real-time', 'up-to-date', 'fresh', 'new']):
            return 'current'
        elif any(word in text for word in ['average', 'mean']):
            return 'aggregation'
        else:
            return 'general'

    def _extract_aggregation(self, text: str) -> str:
        """Extract aggregation type"""
        if 'average' in text or 'mean' in text:
            return 'avg'
        elif 'sum' in text or 'total' in text:
            return 'sum'
        elif 'maximum' in text or 'highest' in text:
            return 'max'
        elif 'minimum' in text or 'lowest' in text:
            return 'min'
        else:
            return 'avg'  # default