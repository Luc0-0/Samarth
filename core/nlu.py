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
        
        # Enhanced crop list with aliases
        self.crops = [
            'rice', 'wheat', 'maize', 'corn', 'bajra', 'jowar', 'ragi', 'cotton', 'sugarcane',
            'groundnut', 'peanut', 'sunflower', 'soybean', 'soya', 'mustard', 'sesame', 'safflower',
            'coconut', 'areca nut', 'cashew', 'tea', 'coffee', 'rubber', 'paddy', 'barley',
            'millets', 'pulses', 'lentils', 'chickpea', 'gram', 'onion', 'potato', 'tomato'
        ]
        
        # Enhanced metrics with more keywords
        self.metrics = {
            'production': ['production', 'yield', 'output', 'harvest', 'produce', 'grown', 'cultivation', 'farming'],
            'area': ['area', 'acreage', 'cultivation', 'land', 'hectare', 'acres', 'coverage', 'sown'],
            'rainfall': ['rainfall', 'precipitation', 'rain', 'monsoon', 'water', 'irrigation'],
            'temperature': ['temperature', 'temp', 'climate', 'weather', 'heat'],
            'price': ['price', 'cost', 'rate', 'market', 'mandi', 'selling', 'buying', 'value', 'worth'],
            'correlation': ['correlation', 'relationship', 'impact', 'effect', 'influence', 'connection']
        }
        
        # Query type patterns with enhanced keywords
        self.query_patterns = {
            'trend': [
                'trend', 'over time', 'change', 'pattern', 'analyse', 'analyze', 'analysis',
                'evolution', 'progress', 'development', 'growth', 'decline', 'increase', 'decrease',
                'trajectory', 'movement', 'shift', 'variation', 'fluctuation'
            ],
            'comparison': [
                'compare', 'comparison', 'versus', 'vs', 'against', 'between', 'difference',
                'contrast', 'relative', 'better', 'worse', 'higher', 'lower', 'more', 'less'
            ],
            'ranking': [
                'highest', 'maximum', 'top', 'best', 'ranking', 'rank', 'leading', 'first',
                'lowest', 'minimum', 'bottom', 'worst', 'last', 'least', 'order', 'sort'
            ],
            'correlation': [
                'correlation', 'relationship', 'impact', 'effect', 'influence', 'connection',
                'association', 'link', 'related', 'depends', 'affects', 'causes'
            ],
            'current': [
                'current', 'latest', 'recent', 'live', 'today', 'now', 'real-time',
                'up-to-date', 'fresh', 'new', 'present', 'contemporary', 'modern'
            ],
            'aggregation': [
                'average', 'mean', 'total', 'sum', 'overall', 'aggregate', 'combined'
            ]
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
            'aggregation': self._extract_aggregation(text_lower),
            'confidence': self._calculate_confidence(text_lower)
        }
        
        # Apply smart context rules
        intent = self._apply_context_rules(intent, text_lower)
        
        return intent
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for the parsed intent"""
        score = 0.0
        total_checks = 0
        
        # Check for clear query type indicators
        for query_type, keywords in self.query_patterns.items():
            if any(keyword in text for keyword in keywords):
                score += 0.3
                break
        total_checks += 1
        
        # Check for entities (states, crops)
        if any(state in text for state in self.states):
            score += 0.2
        total_checks += 1
        
        if any(crop in text for crop in self.crops):
            score += 0.2
        total_checks += 1
        
        # Check for metrics
        if any(any(keyword in text for keyword in keywords) for keywords in self.metrics.values()):
            score += 0.2
        total_checks += 1
        
        # Check for time indicators
        if any(word in text for word in ['year', 'month', 'season', 'annual', 'monthly']):
            score += 0.1
        total_checks += 1
        
        return min(score, 1.0)
    
    def _apply_context_rules(self, intent: Dict, text: str) -> Dict:
        """Apply smart context rules to improve intent accuracy"""
        
        # Rule 1: If no metrics detected but production words present, add production
        if not intent['metrics'] and any(word in text for word in ['production', 'yield', 'harvest', 'output']):
            intent['metrics'] = ['production']
        
        # Rule 2: If comparison query but no states, suggest it needs states
        if intent['query_type'] == 'comparison' and not intent['states']:
            intent['suggestion'] = 'Comparison queries work better with specific states mentioned'
        
        # Rule 3: If trend query but no time range, use default historical range
        if intent['query_type'] == 'trend' and not intent['time_range']['years']:
            intent['time_range']['expressions']['default_range'] = True
        
        # Rule 4: If price query, ensure it's marked for live data
        if 'price' in intent['metrics'] and intent['query_type'] != 'current':
            intent['query_type'] = 'current'
        
        return intent

    def _extract_states(self, text: str) -> List[str]:
        """Extract state names from text with abbreviations"""
        found_states = []
        
        # Direct matches
        for state in self.states:
            if state in text:
                found_states.append(state.title())
        
        # Handle common abbreviations
        state_abbrev = {
            'mh': 'maharashtra', 'up': 'uttar pradesh', 'mp': 'madhya pradesh',
            'tn': 'tamil nadu', 'ap': 'andhra pradesh', 'wb': 'west bengal',
            'hp': 'himachal pradesh', 'uk': 'uttarakhand'
        }
        
        for abbrev, state in state_abbrev.items():
            if abbrev in text.lower() and state.title() not in found_states:
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
        """Extract crop names from text with fuzzy matching"""
        found_crops = []
        
        # Direct matches
        for crop in self.crops:
            if crop in text:
                found_crops.append(crop.title())
        
        # Handle plurals and variations
        crop_variations = {
            'rices': 'rice', 'wheats': 'wheat', 'cottons': 'cotton',
            'corns': 'corn', 'maizes': 'maize', 'cereals': 'wheat',
            'grains': 'wheat', 'vegetables': 'potato'
        }
        
        for variation, crop in crop_variations.items():
            if variation in text and crop.title() not in found_crops:
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
        """Determine the type of query using enhanced pattern matching"""
        
        # Score each query type based on keyword matches
        scores = {}
        
        for query_type, keywords in self.query_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    # Give higher weight to exact matches
                    if keyword == text.strip():
                        score += 3
                    # Multi-word phrases get higher weight
                    elif ' ' in keyword:
                        score += 2
                    else:
                        score += 1
            scores[query_type] = score
        
        # Return the highest scoring query type
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'general'

    def _extract_aggregation(self, text: str) -> str:
        """Extract aggregation type with enhanced detection"""
        aggregation_patterns = {
            'avg': ['average', 'mean', 'typical', 'normal'],
            'sum': ['sum', 'total', 'combined', 'aggregate', 'overall'],
            'max': ['maximum', 'highest', 'peak', 'top', 'best'],
            'min': ['minimum', 'lowest', 'bottom', 'least', 'worst']
        }
        
        for agg_type, keywords in aggregation_patterns.items():
            if any(keyword in text for keyword in keywords):
                return agg_type
        
        return 'avg'  # default