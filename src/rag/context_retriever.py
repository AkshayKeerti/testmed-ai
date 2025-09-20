"""Context retrieval for RAG system."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.hybrid_search import HybridSearch
from typing import List, Dict, Any

class ContextRetriever:
    """Retrieve relevant context for medical queries."""
    
    def __init__(self):
        self.hybrid_search = HybridSearch()
    
    def retrieve_context(self, processed_query: Dict[str, Any], n_results: int = 5) -> Dict[str, Any]:
        """Retrieve relevant context for the processed query."""
        condition = processed_query['condition']
        query_type = processed_query['query_type']
        search_query = processed_query['processed_query']
        
        # Get structured medical facts
        medical_facts = self.hybrid_search.get_medical_facts(condition)
        
        # Get search results
        search_results = self.hybrid_search.search(search_query, n_results)
        
        # Get condition-specific results
        condition_results = self.hybrid_search.search_by_condition(condition, search_query, n_results)
        
        # Combine and rank context
        context = {
            'medical_facts': medical_facts,
            'search_results': search_results,
            'condition_results': condition_results,
            'evidence_sources': self._extract_evidence_sources(search_results),
            'community_sources': self._extract_community_sources(search_results)
        }
        
        return context
    
    def _extract_evidence_sources(self, results: List[Dict]) -> List[Dict]:
        """Extract evidence-based sources."""
        evidence_sources = []
        
        for result in results:
            source_type = result.get('source_type', '')
            if source_type in ['journal', 'health_site']:
                evidence_sources.append({
                    'title': result.get('title', ''),
                    'source': result.get('source', ''),
                    'url': result.get('url', ''),
                    'confidence': result.get('confidence_score', 0.0),
                    'content': result.get('content', '')[:200] + '...'
                })
        
        return evidence_sources[:3]  # Top 3 evidence sources
    
    def _extract_community_sources(self, results: List[Dict]) -> List[Dict]:
        """Extract community-based sources."""
        community_sources = []
        
        for result in results:
            source_type = result.get('source_type', '')
            if source_type == 'community':
                community_sources.append({
                    'title': result.get('title', ''),
                    'source': result.get('source', ''),
                    'url': result.get('url', ''),
                    'score': result.get('score', 0),
                    'content': result.get('content', '')[:200] + '...'
                })
        
        return community_sources[:3]  # Top 3 community sources

def main():
    """Test context retriever."""
    retriever = ContextRetriever()
    
    # Test query processing
    from src.rag.query_processor import QueryProcessor
    processor = QueryProcessor()
    
    test_query = "What are the symptoms of diabetes?"
    processed = processor.process_query(test_query)
    
    print("🔍 Testing Context Retriever")
    print("=" * 30)
    
    context = retriever.retrieve_context(processed)
    
    print(f"Query: {test_query}")
    print(f"Condition: {processed['condition']}")
    print(f"Medical Facts:")
    print(f"  Symptoms: {len(context['medical_facts']['symptoms'])} items")
    print(f"  Causes: {len(context['medical_facts']['causes'])} items")
    print(f"  Treatments: {len(context['medical_facts']['treatments'])} items")
    
    print(f"\nEvidence Sources: {len(context['evidence_sources'])}")
    for source in context['evidence_sources']:
        print(f"  - {source['source']}: {source['title'][:50]}...")
    
    print(f"\nCommunity Sources: {len(context['community_sources'])}")

if __name__ == "__main__":
    main()
