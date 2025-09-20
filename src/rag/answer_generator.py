"""Answer generation for medical queries."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List
from transformers import pipeline

class AnswerGenerator:
    """Generate conversational answers for medical queries."""
    
    def __init__(self):
        # Initialize text generation pipeline
        self.generator = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-medium",
            max_length=200,
            do_sample=True,
            temperature=0.7
        )
    
    def generate_answer(self, processed_query: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate answer based on query and context."""
        query = processed_query['original_query']
        condition = processed_query['condition']
        query_type = processed_query['query_type']
        
        # Create structured response
        answer_data = {
            'answer': self._create_answer_text(query, condition, query_type, context),
            'citations': self._create_citations(context),
            'confidence_score': self._calculate_confidence(context),
            'disclaimer': self._get_disclaimer()
        }
        
        return answer_data
    
    def _create_answer_text(self, query: str, condition: str, query_type: str, context: Dict[str, Any]) -> str:
        """Create answer text based on context."""
        medical_facts = context['medical_facts']
        
        # Build answer based on query type
        if query_type == 'symptoms':
            answer = self._build_symptoms_answer(condition, medical_facts)
        elif query_type == 'causes':
            answer = self._build_causes_answer(condition, medical_facts)
        elif query_type == 'treatments':
            answer = self._build_treatments_answer(condition, medical_facts)
        else:
            answer = self._build_general_answer(condition, medical_facts)
        
        return answer
    
    def _build_symptoms_answer(self, condition: str, facts: Dict[str, List[str]]) -> str:
        """Build answer for symptoms query."""
        symptoms = facts.get('symptoms', [])
        
        if symptoms:
            symptom_list = ', '.join(symptoms[:5])  # Top 5 symptoms
            answer = f"Common symptoms of {condition} include: {symptom_list}."
        else:
            answer = f"I don't have specific symptom information for {condition} in my current database."
        
        return answer
    
    def _build_causes_answer(self, condition: str, facts: Dict[str, List[str]]) -> str:
        """Build answer for causes query."""
        causes = facts.get('causes', [])
        
        if causes:
            cause_list = ', '.join(causes[:3])  # Top 3 causes
            answer = f"Common causes of {condition} include: {cause_list}."
        else:
            answer = f"I don't have specific cause information for {condition} in my current database."
        
        return answer
    
    def _build_treatments_answer(self, condition: str, facts: Dict[str, List[str]]) -> str:
        """Build answer for treatments query."""
        treatments = facts.get('treatments', [])
        
        if treatments:
            treatment_list = ', '.join(treatments[:3])  # Top 3 treatments
            answer = f"Common treatments for {condition} include: {treatment_list}."
        else:
            answer = f"I don't have specific treatment information for {condition} in my current database."
        
        return answer
    
    def _build_general_answer(self, condition: str, facts: Dict[str, List[str]]) -> str:
        """Build general answer."""
        symptoms = facts.get('symptoms', [])
        causes = facts.get('causes', [])
        treatments = facts.get('treatments', [])
        
        answer_parts = []
        
        if symptoms:
            answer_parts.append(f"Symptoms may include: {', '.join(symptoms[:3])}")
        
        if causes:
            answer_parts.append(f"Common causes include: {', '.join(causes[:2])}")
        
        if treatments:
            answer_parts.append(f"Treatments may include: {', '.join(treatments[:2])}")
        
        if answer_parts:
            answer = f"About {condition}: " + ". ".join(answer_parts) + "."
        else:
            answer = f"I have limited information about {condition} in my current database."
        
        return answer
    
    def _create_citations(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create citations from context."""
        citations = []
        
        # Add evidence sources
        for source in context.get('evidence_sources', []):
            citations.append({
                'type': 'Evidence-based',
                'source': source['source'],
                'title': source['title'],
                'url': source['url'],
                'confidence': source['confidence']
            })
        
        # Add community sources
        for source in context.get('community_sources', []):
            citations.append({
                'type': 'Community insight',
                'source': source['source'],
                'title': source['title'],
                'url': source['url'],
                'confidence': 0.5  # Lower confidence for community sources
            })
        
        return citations
    
    def _calculate_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence score for the answer."""
        evidence_sources = len(context.get('evidence_sources', []))
        community_sources = len(context.get('community_sources', []))
        medical_facts = context.get('medical_facts', {})
        
        # Base confidence
        confidence = 0.3
        
        # Add confidence for evidence sources
        confidence += min(evidence_sources * 0.2, 0.4)
        
        # Add confidence for medical facts
        fact_count = sum(len(facts) for facts in medical_facts.values())
        confidence += min(fact_count * 0.05, 0.3)
        
        return min(confidence, 1.0)
    
    def _get_disclaimer(self) -> str:
        """Get medical disclaimer."""
        return "This information is for educational purposes only and should not replace professional medical advice. Please consult a healthcare provider for medical concerns."

def main():
    """Test answer generator."""
    generator = AnswerGenerator()
    
    # Test with sample context
    test_context = {
        'medical_facts': {
            'symptoms': ['Thirst', 'Frequent urination', 'Fatigue'],
            'causes': ['Insulin resistance', 'Genetic factors'],
            'treatments': ['Medication', 'Diet changes', 'Exercise']
        },
        'evidence_sources': [
            {
                'source': 'Mayo Clinic',
                'title': 'Diabetes Overview',
                'url': 'https://example.com',
                'confidence': 0.8
            }
        ],
        'community_sources': []
    }
    
    test_query = {
        'original_query': 'What are the symptoms of diabetes?',
        'condition': 'Diabetes',
        'query_type': 'symptoms'
    }
    
    print("🤖 Testing Answer Generator")
    print("=" * 30)
    
    answer_data = generator.generate_answer(test_query, test_context)
    
    print(f"Answer: {answer_data['answer']}")
    print(f"Confidence: {answer_data['confidence_score']:.2f}")
    print(f"Citations: {len(answer_data['citations'])}")
    print(f"Disclaimer: {answer_data['disclaimer'][:50]}...")

if __name__ == "__main__":
    main()
