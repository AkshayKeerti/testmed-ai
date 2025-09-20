"""Hybrid search combining structured and semantic search."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processing.database import MedicalDatabase
from src.processing.vector_store import VectorStore
from typing import List, Dict, Any

class HybridSearch:
    """Hybrid search combining SQLite and vector search."""
    
    def __init__(self):
        self.database = MedicalDatabase()
        self.vector_store = VectorStore()
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Perform hybrid search."""
        # Structured search (SQLite)
        structured_results = self.database.search_entries(query)
        
        # Semantic search (Vector)
        semantic_results = self.vector_store.search(query, n_results)
        
        # Combine and rank results
        combined_results = self._combine_results(structured_results, semantic_results)
        
        return combined_results[:n_results]
    
    def search_by_condition(self, condition: str, query: str = "", n_results: int = 5) -> List[Dict]:
        """Search by specific condition."""
        # Get entries for condition
        condition_entries = self.database.get_entries_by_condition(condition)
        
        # If query provided, filter by semantic similarity
        if query:
            semantic_results = self.vector_store.search(query, n_results)
            # Filter semantic results by condition
            filtered_results = [
                result for result in semantic_results 
                if result['metadata']['condition'].lower() == condition.lower()
            ]
            return filtered_results[:n_results]
        
        return condition_entries[:n_results]
    
    def get_medical_facts(self, condition: str) -> Dict[str, List[str]]:
        """Get structured medical facts for a condition."""
        entries = self.database.get_entries_by_condition(condition)
        
        facts = {
            'symptoms': [],
            'causes': [],
            'treatments': [],
            'drugs': [],
            'side_effects': []
        }
        
        for entry in entries:
            for key in facts.keys():
                if entry.get(key):
                    facts[key].extend(entry[key])
        
        # Remove duplicates
        for key in facts.keys():
            facts[key] = list(set(facts[key]))
        
        return facts
    
    def _combine_results(self, structured_results: List[Dict], semantic_results: List[Dict]) -> List[Dict]:
        """Combine structured and semantic search results."""
        combined = []
        
        # Add structured results with source type
        for result in structured_results:
            result['search_type'] = 'structured'
            result['relevance_score'] = 0.8  # Default score for structured
            combined.append(result)
        
        # Add semantic results with source type
        for result in semantic_results:
            result['search_type'] = 'semantic'
            result['relevance_score'] = 1.0 - result.get('distance', 0.5)  # Convert distance to relevance
            combined.append(result)
        
        # Sort by relevance score
        combined.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return combined

def main():
    """Test hybrid search."""
    search = HybridSearch()
    
    print("🔍 Testing Hybrid Search")
    print("=" * 30)
    
    # Test general search
    print("Testing general search...")
    results = search.search("diabetes symptoms", n_results=3)
    print(f"✅ Found {len(results)} results")
    
    for i, result in enumerate(results):
        print(f"  {i+1}. {result.get('title', 'No title')} ({result.get('search_type', 'unknown')})")
    
    # Test condition-specific search
    print("\nTesting condition-specific search...")
    facts = search.get_medical_facts("Diabetes")
    print(f"✅ Diabetes facts:")
    print(f"   Symptoms: {len(facts['symptoms'])} items")
    print(f"   Causes: {len(facts['causes'])} items")
    print(f"   Treatments: {len(facts['treatments'])} items")
    
    if facts['symptoms']:
        print(f"   Sample symptoms: {facts['symptoms'][:3]}")

if __name__ == "__main__":
    main()
