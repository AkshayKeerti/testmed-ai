"""Vector database for semantic search."""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import json
from src.utils.config import CHROMA_PERSIST_DIRECTORY, MODEL_NAME

class VectorStore:
    """Chroma vector database for medical information."""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="medical_knowledge",
            metadata={"description": "Medical information embeddings"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(MODEL_NAME)
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector store."""
        texts = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            # Create searchable text
            text_parts = []
            if doc.get('title'):
                text_parts.append(f"Title: {doc['title']}")
            if doc.get('content'):
                text_parts.append(f"Content: {doc['content']}")
            if doc.get('symptoms'):
                text_parts.append(f"Symptoms: {', '.join(doc['symptoms'])}")
            if doc.get('causes'):
                text_parts.append(f"Causes: {', '.join(doc['causes'])}")
            if doc.get('treatments'):
                text_parts.append(f"Treatments: {', '.join(doc['treatments'])}")
            
            text = " ".join(text_parts)
            texts.append(text)
            
            # Metadata
            metadata = {
                'condition': doc.get('condition', ''),
                'source': doc.get('source', ''),
                'source_type': doc.get('source_type', ''),
                'url': doc.get('url', ''),
                'confidence_score': doc.get('confidence_score', 0.0)
            }
            metadatas.append(metadata)
            ids.append(f"doc_{i}")
        
        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        search_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                result = {
                    'document': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if results['distances'] else 0.0
                }
                search_results.append(result)
        
        return search_results
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics."""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.collection.name
        }

def main():
    """Test vector store."""
    vector_store = VectorStore()
    
    # Test documents
    test_docs = [
        {
            'condition': 'Diabetes',
            'title': 'Diabetes Overview',
            'symptoms': ['Thirst', 'Frequent urination'],
            'causes': ['Insulin resistance'],
            'treatments': ['Medication', 'Diet'],
            'content': 'Diabetes is a chronic condition affecting blood sugar levels.',
            'source': 'Mayo Clinic',
            'source_type': 'health_site',
            'url': 'https://example.com/diabetes',
            'confidence_score': 0.8
        },
        {
            'condition': 'Hypertension',
            'title': 'High Blood Pressure',
            'symptoms': ['Headaches', 'Dizziness'],
            'causes': ['High sodium diet'],
            'treatments': ['ACE inhibitors', 'Lifestyle changes'],
            'content': 'Hypertension is high blood pressure that can lead to heart disease.',
            'source': 'WebMD',
            'source_type': 'health_site',
            'url': 'https://example.com/hypertension',
            'confidence_score': 0.7
        }
    ]
    
    print("Testing vector store...")
    vector_store.add_documents(test_docs)
    print("✅ Added documents to vector store")
    
    # Test search
    results = vector_store.search("diabetes symptoms", n_results=2)
    print(f"✅ Found {len(results)} results for 'diabetes symptoms'")
    
    for result in results:
        print(f"   - {result['metadata']['condition']}: {result['document'][:50]}...")
    
    # Stats
    stats = vector_store.get_collection_stats()
    print(f"✅ Collection stats: {stats}")

if __name__ == "__main__":
    main()
