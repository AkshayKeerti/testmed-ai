"""Query processing for medical questions."""

import re
from typing import List, Dict, Any
from src.rag.hybrid_search import HybridSearch

class QueryProcessor:
    """Process and analyze medical queries."""
    
    def __init__(self):
        self.hybrid_search = HybridSearch()
        
        # Medical terminology patterns
        self.medical_terms = {
            'symptoms': ['symptom', 'sign', 'indication', 'manifestation'],
            'causes': ['cause', 'reason', 'trigger', 'risk factor'],
            'treatments': ['treatment', 'therapy', 'cure', 'medication', 'drug'],
            'conditions': ['condition', 'disease', 'disorder', 'syndrome', 'illness']
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query and extract intent."""
        query_lower = query.lower()
        
        # Extract medical condition
        condition = self._extract_condition(query_lower)
        
        # Determine query type
        query_type = self._determine_query_type(query_lower)
        
        # Extract key terms
        key_terms = self._extract_key_terms(query_lower)
        
        return {
            'original_query': query,
            'condition': condition,
            'query_type': query_type,
            'key_terms': key_terms,
            'processed_query': self._create_search_query(condition, query_type, key_terms)
        }
    
    def _extract_condition(self, query: str) -> str:
        """Extract medical condition from query."""
        # Common medical conditions
        conditions = [
            'diabetes', 'hypertension', 'cancer', 'heart disease', 'stroke',
            'depression', 'anxiety', 'arthritis', 'asthma', 'migraine',
            'covid', 'flu', 'cold', 'pneumonia', 'bronchitis'
        ]
        
        for condition in conditions:
            if condition in query:
                return condition.title()
        
        return 'General'
    
    def _determine_query_type(self, query: str) -> str:
        """Determine what type of information is being requested."""
        if any(term in query for term in self.medical_terms['symptoms']):
            return 'symptoms'
        elif any(term in query for term in self.medical_terms['causes']):
            return 'causes'
        elif any(term in query for term in self.medical_terms['treatments']):
            return 'treatments'
        else:
            return 'general'
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key medical terms from query."""
        # Remove common words
        stop_words = {'what', 'are', 'the', 'of', 'for', 'with', 'how', 'do', 'i', 'can'}
        
        words = re.findall(r'\b\w+\b', query)
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms
    
    def _create_search_query(self, condition: str, query_type: str, key_terms: List[str]) -> str:
        """Create optimized search query."""
        search_parts = []
        
        if condition != 'General':
            search_parts.append(condition)
        
        if query_type != 'general':
            search_parts.append(query_type)
        
        search_parts.extend(key_terms[:3])  # Limit to top 3 terms
        
        return ' '.join(search_parts)

def main():
    """Test query processor."""
    processor = QueryProcessor()
    
    test_queries = [
        "What are the symptoms of diabetes?",
        "What causes high blood pressure?",
        "How do you treat migraines?",
        "Tell me about heart disease"
    ]
    
    print("🔍 Testing Query Processor")
    print("=" * 30)
    
    for query in test_queries:
        result = processor.process_query(query)
        print(f"\nQuery: {query}")
        print(f"Condition: {result['condition']}")
        print(f"Type: {result['query_type']}")
        print(f"Search: {result['processed_query']}")

if __name__ == "__main__":
    main()
