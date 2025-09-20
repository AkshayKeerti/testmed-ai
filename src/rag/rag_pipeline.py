"""Complete RAG pipeline for conversational medical agent."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.query_processor import QueryProcessor
from src.rag.context_retriever import ContextRetriever
from src.rag.answer_generator import AnswerGenerator
from typing import Dict, Any

class RAGPipeline:
    """Complete RAG pipeline for medical queries."""
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.context_retriever = ContextRetriever()
        self.answer_generator = AnswerGenerator()
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process user query through complete RAG pipeline."""
        # Step 1: Process query
        processed_query = self.query_processor.process_query(user_query)
        
        # Step 2: Retrieve context
        context = self.context_retriever.retrieve_context(processed_query)
        
        # Step 3: Generate answer
        answer_data = self.answer_generator.generate_answer(processed_query, context)
        
        # Step 4: Combine response
        response = {
            'query': user_query,
            'answer': answer_data['answer'],
            'citations': answer_data['citations'],
            'confidence_score': answer_data['confidence_score'],
            'disclaimer': answer_data['disclaimer'],
            'sources': {
                'evidence_based': len(context['evidence_sources']),
                'community_based': len(context['community_sources']),
                'total_sources': len(context['evidence_sources']) + len(context['community_sources'])
            },
            'medical_facts': context['medical_facts']
        }
        
        return response
    
    def get_conversation_summary(self, responses: list) -> Dict[str, Any]:
        """Get summary of conversation."""
        if not responses:
            return {'total_queries': 0, 'topics': [], 'confidence_avg': 0.0}
        
        topics = []
        confidence_scores = []
        
        for response in responses:
            # Extract condition from query
            condition = response.get('query', '').lower()
            if 'diabetes' in condition:
                topics.append('Diabetes')
            elif 'hypertension' in condition or 'blood pressure' in condition:
                topics.append('Hypertension')
            elif 'heart' in condition:
                topics.append('Heart Disease')
            else:
                topics.append('General Medical')
            
            confidence_scores.append(response.get('confidence_score', 0.0))
        
        return {
            'total_queries': len(responses),
            'topics': list(set(topics)),
            'confidence_avg': sum(confidence_scores) / len(confidence_scores),
            'total_sources_used': sum(r.get('sources', {}).get('total_sources', 0) for r in responses)
        }

def main():
    """Test complete RAG pipeline."""
    pipeline = RAGPipeline()
    
    test_queries = [
        "What are the symptoms of diabetes?",
        "What causes high blood pressure?",
        "How do you treat migraines?"
    ]
    
    print("🚀 Testing Complete RAG Pipeline")
    print("=" * 40)
    
    responses = []
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        response = pipeline.process_query(query)
        
        print(f"✅ Answer: {response['answer']}")
        print(f"📊 Confidence: {response['confidence_score']:.2f}")
        print(f"📚 Sources: {response['sources']['total_sources']} total")
        print(f"   - Evidence-based: {response['sources']['evidence_based']}")
        print(f"   - Community-based: {response['sources']['community_based']}")
        
        responses.append(response)
    
    # Test conversation summary
    print(f"\n📈 Conversation Summary:")
    summary = pipeline.get_conversation_summary(responses)
    print(f"   Total queries: {summary['total_queries']}")
    print(f"   Topics covered: {summary['topics']}")
    print(f"   Average confidence: {summary['confidence_avg']:.2f}")
    print(f"   Total sources used: {summary['total_sources_used']}")
    
    print(f"\n🎯 Phase C RAG Pipeline: COMPLETE!")
    print("Ready for Phase D: UI and System Integration")

if __name__ == "__main__":
    main()
