"""
Enhanced RAG Pipeline with Community Integration for TrustMed AI
Blends evidence-based medical information with community insights
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from src.ingestion.live_data_pipeline import LiveDataPipeline
from src.ingestion.community_pipeline import CommunityDataPipeline
from src.rag.vector_store import TrustMedVectorStore
from src.rag.citation_manager import CitationManager
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class EnhancedRAGPipeline:
    """Enhanced RAG pipeline that blends medical evidence with community insights"""
    
    def __init__(self):
        self.live_data_pipeline = LiveDataPipeline()
        self.community_pipeline = CommunityDataPipeline()
        self.vector_store = TrustMedVectorStore()
        self.citation_manager = CitationManager()
        logger.info("Enhanced RAG pipeline initialized")
    
    def generate_enhanced_response(self, query: str, condition: str = None) -> Dict[str, Any]:
        """Generate response blending medical evidence with community insights"""
        logger.info(f"Generating enhanced response for: {query}")
        
        # Extract condition from query if not provided
        if not condition:
            condition = self._extract_condition_from_query(query)
        
        if not condition:
            return self._generate_general_response(query)
        
        # Get medical evidence
        medical_data = self.live_data_pipeline.ingest_medical_condition(condition)
        medical_summary = self.live_data_pipeline.get_condition_summary(medical_data)
        
        # Get community insights
        community_insights = self.community_pipeline.get_condition_summary_with_community(condition)
        
        # Blend evidence and community insights
        blended_response = self._blend_evidence_and_community(
            query, condition, medical_summary, community_insights
        )
        
        return blended_response
    
    def _extract_condition_from_query(self, query: str) -> str:
        """Extract medical condition from user query"""
        # Simple keyword matching for common conditions
        conditions = [
            "diabetes", "hypertension", "asthma", "depression", "cancer",
            "heart disease", "migraine", "arthritis", "allergies", "anxiety"
        ]
        
        query_lower = query.lower()
        for condition in conditions:
            if condition in query_lower:
                return condition
        
        return None
    
    def _generate_general_response(self, query: str) -> Dict[str, Any]:
        """Generate general medical response when no specific condition is identified"""
        return {
            "answer": f"I understand you're asking about: {query}. For specific medical information, please mention the condition you're interested in (e.g., diabetes, hypertension, asthma). I can provide evidence-based information combined with community insights.",
            "sources": ["TrustMed AI General Response"],
            "confidence": 0.5,
            "evidence_type": "general",
            "community_insights": False
        }
    
    def _blend_evidence_and_community(self, query: str, condition: str, 
                                    medical_summary: Dict[str, Any], 
                                    community_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Blend medical evidence with community insights"""
        
        # Start with medical evidence
        answer_parts = []
        
        # Medical evidence section
        if medical_summary.get("symptoms"):
            answer_parts.append(f"**Medical Evidence for {condition.title()}:**")
            answer_parts.append(f"Symptoms: {', '.join(medical_summary['symptoms'][:5])}")
        
        if medical_summary.get("treatments"):
            answer_parts.append(f"Treatments: {', '.join(medical_summary['treatments'][:5])}")
        
        if medical_summary.get("causes"):
            answer_parts.append(f"Causes: {', '.join(medical_summary['causes'][:5])}")
        
        # Recent research
        if medical_summary.get("recent_research"):
            answer_parts.append(f"\n**Recent Research:**")
            for research in medical_summary["recent_research"][:3]:
                answer_parts.append(f"- {research['title']} ({research['journal']}, {research['year']})")
        
        # Community insights section
        if community_insights.get("patient_experiences", 0) > 0:
            answer_parts.append(f"\n**Community Insights:**")
            answer_parts.append(f"Patient experiences: {community_insights['patient_experiences']} shared")
        
        if community_insights.get("common_questions", 0) > 0:
            answer_parts.append(f"Common questions: {community_insights['common_questions']} found")
        
        if community_insights.get("treatment_discussions", 0) > 0:
            answer_parts.append(f"Treatment discussions: {community_insights['treatment_discussions']} found")
        
        # Sources
        sources = []
        if medical_summary.get("recent_research"):
            for research in medical_summary["recent_research"]:
                sources.append(f"{research['journal']} ({research['year']})")
        
        if community_insights.get("sources"):
            sources.extend(community_insights["sources"])
        
        # Calculate confidence
        confidence = self._calculate_enhanced_confidence(medical_summary, community_insights)
        
        return {
            "answer": "\n".join(answer_parts),
            "sources": sources,
            "confidence": confidence,
            "evidence_type": "blended",
            "community_insights": community_insights["community_sources"] > 0,
            "medical_sources": medical_summary.get("total_sources", 0),
            "community_sources": community_insights["community_sources"]
        }
    
    def _calculate_enhanced_confidence(self, medical_summary: Dict[str, Any], 
                                     community_insights: Dict[str, Any]) -> float:
        """Calculate confidence score for blended response"""
        base_confidence = 0.6  # Base confidence for blended responses
        
        # Medical evidence bonus
        if medical_summary.get("total_sources", 0) > 0:
            base_confidence += 0.2
        
        # Community insights bonus
        if community_insights["community_sources"] > 0:
            base_confidence += 0.1
        
        # Recent research bonus
        if medical_summary.get("recent_research"):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def get_condition_overview(self, condition: str) -> Dict[str, Any]:
        """Get comprehensive overview of a condition"""
        # Get medical data
        medical_data = self.live_data_pipeline.ingest_medical_condition(condition)
        medical_summary = self.live_data_pipeline.get_condition_summary(medical_data)
        
        # Get community insights
        community_insights = self.community_pipeline.get_condition_summary_with_community(condition)
        
        return {
            "condition": condition,
            "medical_evidence": medical_summary,
            "community_insights": community_insights,
            "overview_generated_at": datetime.now().isoformat()
        }

# Test the enhanced RAG pipeline
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    pipeline = EnhancedRAGPipeline()
    
    # Test with a specific condition
    test_condition = "diabetes"
    test_query = f"What are the symptoms and treatments for {test_condition}?"
    
    print(f"Testing enhanced RAG pipeline with: {test_query}")
    response = pipeline.generate_enhanced_response(test_query, test_condition)
    
    print(f"\nEnhanced Response:")
    print(f"Answer: {response['answer']}")
    print(f"Sources: {len(response['sources'])}")
    print(f"Confidence: {response['confidence']}")
    print(f"Evidence Type: {response['evidence_type']}")
    print(f"Community Insights: {response['community_insights']}")
    print(f"Medical Sources: {response['medical_sources']}")
    print(f"Community Sources: {response['community_sources']}")
    
    # Test condition overview
    print(f"\nCondition Overview for {test_condition}:")
    overview = pipeline.get_condition_overview(test_condition)
    print(f"Medical Sources: {overview['medical_evidence']['total_sources']}")
    print(f"Community Sources: {overview['community_insights']['community_sources']}")
    print(f"Patient Experiences: {overview['community_insights']['patient_experiences']}")
