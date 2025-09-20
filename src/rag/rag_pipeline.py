"""
RAG Pipeline for TrustMed AI
Retrieval-Augmented Generation with medical knowledge
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
import logging

from src.rag.vector_store import TrustMedVectorStore
from src.llm.llm_client import TrustMedLLMClient
from src.rag.citation_manager import CitationManager

logger = logging.getLogger(__name__)

class TrustMedRAGPipeline:
    """RAG Pipeline for medical conversations"""
    
    def __init__(self):
        self.llm = OllamaLLM(model="llama3.1:8b")
        self.vector_store = TrustMedVectorStore()
        self.citation_manager = CitationManager()
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are TrustMed AI, a medical information assistant. 
            Use the provided context to answer medical questions accurately and safely.
            Always cite your sources and remind users to consult healthcare professionals.
            
            Context: {context}
            
            Guidelines:
            - Provide evidence-based medical information
            - Always include disclaimers about consulting healthcare professionals
            - Cite sources when available
            - Be clear about limitations of AI medical advice"""),
            ("human", "{question}")
        ])
        
        # Create chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
        logger.info("RAG Pipeline initialized")
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant context for query"""
        try:
            # For now, return empty list since we don't have a populated vector store
            # In production, this would search the vector store
            logger.info(f"Retrieving context for query: {query}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def generate_response(self, query: str, context: List[Document] = None) -> Dict[str, Any]:
        """Generate response using RAG"""
        try:
            # Retrieve context if not provided
            if context is None:
                context = self.retrieve_context(query)
            
            # Format context
            context_text = self._format_context(context)
            
            # Generate response
            response = self.chain.invoke({
                "context": context_text,
                "question": query
            })
            
            # Extract sources
            sources = self._extract_sources(context)
            
            return {
                "answer": response,
                "sources": sources,
                "confidence": self._calculate_confidence(context),
                "context_used": len(context) > 0
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "answer": "I apologize, but I'm having trouble processing your request right now.",
                "sources": [],
                "confidence": 0.0,
                "context_used": False
            }
    
    def _format_context(self, context: List[Document]) -> str:
        """Format context documents for prompt"""
        if not context:
            return "No specific medical context available. Please provide general medical information."
        
        formatted_context = []
        for i, doc in enumerate(context, 1):
            formatted_context.append(f"Source {i}: {doc.page_content}")
            if doc.metadata:
                formatted_context.append(f"Metadata: {doc.metadata}")
        
        return "\n\n".join(formatted_context)
    
    def _extract_sources(self, context: List[Document]) -> List[str]:
        """Extract source information from context using citation manager"""
        sources = self.citation_manager.extract_sources_from_documents(context)
        citations = self.citation_manager.format_citations(sources)
        return citations
    
    def _calculate_confidence(self, context: List[Document]) -> float:
        """Calculate confidence score using citation manager"""
        sources = self.citation_manager.extract_sources_from_documents(context)
        response_length = sum(len(doc.page_content) for doc in context)
        confidence = self.citation_manager.calculate_confidence_score(sources, response_length)
        return confidence

# Test the RAG pipeline
if __name__ == "__main__":
    rag = TrustMedRAGPipeline()
    
    # Test query
    query = "What are the symptoms of diabetes?"
    response = rag.generate_response(query)
    
    print(f"Query: {query}")
    print(f"Answer: {response['answer']}")
    print(f"Sources: {len(response['sources'])}")
    print(f"Confidence: {response['confidence']}")
    print(f"Context Used: {response['context_used']}")