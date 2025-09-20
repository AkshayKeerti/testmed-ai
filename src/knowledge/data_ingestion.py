"""
Data Ingestion Script for TrustMed AI
Populates knowledge base with medical data
"""

import os
import sys
from typing import List, Dict, Any
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.knowledge.medical_data import MedicalKnowledgeBase
from src.rag.vector_store import TrustMedVectorStore

logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    """Pipeline for ingesting medical data"""
    
    def __init__(self):
        self.knowledge_base = MedicalKnowledgeBase()
        self.vector_store = TrustMedVectorStore()
        logger.info("Data ingestion pipeline initialized")
    
    def ingest_medical_data(self) -> bool:
        """Ingest medical data into vector store"""
        try:
            # Get documents from knowledge base
            documents = self.knowledge_base.to_documents()
            
            # Add to vector store
            ids = self.vector_store.add_documents(documents)
            
            logger.info(f"Successfully ingested {len(documents)} medical documents")
            logger.info(f"Document IDs: {ids}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting medical data: {e}")
            return False
    
    def test_retrieval(self, query: str) -> List[Dict[str, Any]]:
        """Test retrieval from vector store"""
        try:
            documents = self.vector_store.similarity_search(query)
            
            results = []
            for doc in documents:
                results.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing retrieval: {e}")
            return []
    
    def run_full_pipeline(self) -> bool:
        """Run complete data ingestion pipeline"""
        logger.info("Starting data ingestion pipeline...")
        
        # Ingest data
        success = self.ingest_medical_data()
        if not success:
            return False
        
        # Test retrieval
        test_queries = [
            "diabetes symptoms",
            "high blood pressure",
            "asthma treatment",
            "depression causes",
            "heart disease"
        ]
        
        for query in test_queries:
            results = self.test_retrieval(query)
            logger.info(f"Query '{query}': Found {len(results)} results")
            for result in results:
                logger.info(f"  - {result['metadata']['title']}")
        
        logger.info("Data ingestion pipeline completed successfully!")
        return True

# Main execution
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    pipeline = DataIngestionPipeline()
    success = pipeline.run_full_pipeline()
    
    if success:
        print("✅ Data ingestion completed successfully!")
    else:
        print("❌ Data ingestion failed!")
