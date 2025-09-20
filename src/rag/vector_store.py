"""
Vector Store for TrustMed AI RAG Pipeline
Using PostgreSQL with PGVector for hybrid search
"""

import os
from typing import List, Dict, Any, Optional
from langchain_postgres import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import logging
from src.knowledge.medical_data import MedicalKnowledgeBase

logger = logging.getLogger(__name__)

class TrustMedVectorStore:
    """Vector store for medical knowledge"""
    
    def __init__(self):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize knowledge base
        self.knowledge_base = MedicalKnowledgeBase()
        
        # Initialize PGVector (simplified for demo)
        # In production, this would connect to a real PostgreSQL instance
        self.vector_store = None
        logger.info("Vector store initialized (demo mode - no PostgreSQL connection)")
        
        logger.info("Vector store initialized")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to vector store"""
        try:
            # Demo mode - return mock IDs
            ids = [f"doc_{i}" for i in range(len(documents))]
            logger.info(f"Added {len(documents)} documents to vector store (demo mode)")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return []
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search using knowledge base"""
        try:
            # Search knowledge base for relevant conditions
            results = self.knowledge_base.search_conditions(query)
            
            # Convert to documents and limit results
            documents = []
            for result in results[:k]:
                content = f"""
Title: {result['title']}
Condition: {result['condition']}

Overview:
{result['content']}

Symptoms: {', '.join(result['symptoms'])}
Causes: {', '.join(result['causes'])}
Treatments: {', '.join(result['treatments'])}

Sources: {', '.join(result['sources'])}
                """.strip()
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "condition": result["condition"],
                        "title": result["title"],
                        "sources": result["sources"],
                        "type": "medical_condition"
                    }
                )
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} relevant documents for '{query}'")
            return documents
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """Perform similarity search with scores"""
        try:
            # Demo mode - return empty results
            logger.info(f"Similarity search with score for '{query}' (demo mode - no results)")
            return []
        except Exception as e:
            logger.error(f"Error in similarity search with score: {e}")
            return []
    
    def hybrid_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform hybrid search (vector + metadata filtering)"""
        try:
            # Use similarity search for now
            # In production, this would combine vector search with metadata filtering
            return self.similarity_search(query, k)
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []

# Test the vector store
if __name__ == "__main__":
    # This is just for testing - in production, we'd use a real PostgreSQL instance
    print("Vector store module loaded successfully")
    print("Note: Requires PostgreSQL with PGVector extension for full functionality")
