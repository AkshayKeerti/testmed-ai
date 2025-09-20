"""
Citation System for TrustMed AI
Manages source attribution and confidence scoring
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class CitationManager:
    """Manages citations and source attribution"""
    
    def __init__(self):
        self.citation_templates = {
            "medical_journal": "{author}. ({year}). {title}. {journal}, {volume}({issue}), {pages}.",
            "website": "{organization}. ({year}). {title}. Retrieved from {url}",
            "organization": "{organization}. ({year}). {title}.",
            "default": "{source}. ({year}). {title}."
        }
        logger.info("Citation manager initialized")
    
    def extract_sources_from_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Extract sources from retrieved documents"""
        sources = []
        
        for doc in documents:
            metadata = doc.metadata
            
            # Extract source information
            source_info = {
                "title": metadata.get("title", "Unknown Title"),
                "organization": self._extract_organization(metadata),
                "year": self._extract_year(metadata),
                "url": metadata.get("url", ""),
                "type": metadata.get("type", "medical_condition"),
                "relevance_score": self._calculate_relevance_score(doc)
            }
            
            sources.append(source_info)
        
        # Sort by relevance score
        sources.sort(key=lambda x: x["relevance_score"], reverse=True)
        return sources
    
    def _extract_organization(self, metadata: Dict[str, Any]) -> str:
        """Extract organization from metadata"""
        sources = metadata.get("sources", [])
        if isinstance(sources, list) and sources:
            return sources[0]  # Use first source
        return "Medical Source"
    
    def _extract_year(self, metadata: Dict[str, Any]) -> str:
        """Extract year from metadata"""
        return metadata.get("year", "2024")
    
    def _calculate_relevance_score(self, doc: Document) -> float:
        """Calculate relevance score for document"""
        # Simple scoring based on content length and metadata completeness
        score = 0.5  # Base score
        
        # Increase score for longer content
        content_length = len(doc.page_content)
        if content_length > 500:
            score += 0.2
        elif content_length > 200:
            score += 0.1
        
        # Increase score for complete metadata
        metadata = doc.metadata
        if metadata.get("title") and metadata.get("sources"):
            score += 0.2
        if metadata.get("type") == "medical_condition":
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def format_citations(self, sources: List[Dict[str, Any]], max_citations: int = 3) -> List[str]:
        """Format sources into proper citations"""
        citations = []
        
        for source in sources[:max_citations]:
            template = self.citation_templates.get(source["type"], self.citation_templates["default"])
            
            citation = template.format(
                author=source.get("author", source["organization"]),
                year=source["year"],
                title=source["title"],
                organization=source["organization"],
                journal=source.get("journal", ""),
                volume=source.get("volume", ""),
                issue=source.get("issue", ""),
                pages=source.get("pages", ""),
                url=source.get("url", ""),
                source=source["organization"]
            )
            
            citations.append(citation)
        
        return citations
    
    def calculate_confidence_score(self, sources: List[Dict[str, Any]], response_length: int) -> float:
        """Calculate confidence score for response"""
        if not sources:
            return 0.3  # Low confidence without sources
        
        # Base confidence from source quality
        avg_source_score = sum(s["relevance_score"] for s in sources) / len(sources)
        
        # Adjust based on number of sources
        source_bonus = min(len(sources) * 0.1, 0.3)
        
        # Adjust based on response length (longer responses might be more comprehensive)
        length_bonus = min(response_length / 1000 * 0.1, 0.2)
        
        confidence = avg_source_score + source_bonus + length_bonus
        return min(confidence, 1.0)  # Cap at 1.0
    
    def generate_citation_summary(self, sources: List[Dict[str, Any]]) -> str:
        """Generate a summary of sources used"""
        if not sources:
            return "No specific sources available for this response."
        
        source_count = len(sources)
        organizations = list(set(s["organization"] for s in sources))
        
        if len(organizations) == 1:
            return f"Information sourced from {organizations[0]} ({source_count} reference{'s' if source_count > 1 else ''})."
        else:
            return f"Information sourced from {source_count} references including {', '.join(organizations[:2])}{' and others' if len(organizations) > 2 else ''}."

# Test the citation manager
if __name__ == "__main__":
    # Test with sample documents
    test_docs = [
        Document(
            page_content="Diabetes is a chronic condition...",
            metadata={
                "title": "Diabetes Overview",
                "sources": ["American Diabetes Association"],
                "type": "medical_condition",
                "year": "2024"
            }
        ),
        Document(
            page_content="Hypertension affects millions...",
            metadata={
                "title": "High Blood Pressure Guide",
                "sources": ["Mayo Clinic"],
                "type": "medical_condition",
                "year": "2024"
            }
        )
    ]
    
    citation_manager = CitationManager()
    sources = citation_manager.extract_sources_from_documents(test_docs)
    citations = citation_manager.format_citations(sources)
    confidence = citation_manager.calculate_confidence_score(sources, 500)
    summary = citation_manager.generate_citation_summary(sources)
    
    print("Sources extracted:")
    for source in sources:
        print(f"- {source['title']} ({source['organization']})")
    
    print(f"\nCitations:")
    for citation in citations:
        print(f"- {citation}")
    
    print(f"\nConfidence Score: {confidence:.2f}")
    print(f"Summary: {summary}")
