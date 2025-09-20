"""End-to-end data processing pipeline."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.pubmed_client import PubMedClient
from src.ingestion.mayo_scraper import MayoClinicScraper
from src.ingestion.webmd_scraper import WebMDScraper
from src.processing.database import MedicalDatabase
from src.processing.vector_store import VectorStore
from src.processing.data_cleaner import DataCleaner
from typing import List, Dict, Any

class DataPipeline:
    """End-to-end data processing pipeline."""
    
    def __init__(self):
        self.database = MedicalDatabase()
        self.vector_store = VectorStore()
        self.data_cleaner = DataCleaner()
        
        # Initialize scrapers
        self.pubmed_client = PubMedClient()
        self.mayo_scraper = MayoClinicScraper()
        self.webmd_scraper = WebMDScraper()
    
    def ingest_all_sources(self, max_items_per_source: int = 10) -> List[Dict]:
        """Ingest data from all sources."""
        all_data = []
        
        print("🔄 Ingesting PubMed articles...")
        pubmed_articles = self.pubmed_client.fetch_recent_articles(max_per_journal=2)
        for article in pubmed_articles:
            article['condition'] = self._extract_condition_from_title(article.get('title', ''))
            all_data.append(article)
        
        print("🔄 Ingesting Mayo Clinic data...")
        mayo_data = self.mayo_scraper.scrape_multiple_diseases(max_diseases=3)
        all_data.extend(mayo_data)
        
        print("🔄 Ingesting WebMD data...")
        webmd_data = self.webmd_scraper.scrape_multiple_diseases(max_diseases=3)
        all_data.extend(webmd_data)
        
        print(f"✅ Total ingested: {len(all_data)} items")
        return all_data
    
    def process_and_store(self, data: List[Dict]) -> Dict[str, int]:
        """Process and store data in both databases."""
        processed_count = 0
        stored_count = 0
        
        for item in data:
            try:
                # Clean and validate data
                cleaned_data = self.data_cleaner.clean_medical_data(item)
                validation = self.data_cleaner.validate_medical_content(cleaned_data)
                
                if validation['is_valid']:
                    cleaned_data['confidence_score'] = validation['confidence_score']
                    
                    # Store in SQLite
                    entry_id = self.database.add_entry(cleaned_data)
                    processed_count += 1
                    
                    # Store in vector database
                    self.vector_store.add_documents([cleaned_data])
                    stored_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing item: {e}")
                continue
        
        return {
            'processed': processed_count,
            'stored': stored_count,
            'total': len(data)
        }
    
    def _extract_condition_from_title(self, title: str) -> str:
        """Extract medical condition from title."""
        # Simple extraction - look for common medical terms
        medical_terms = [
            'diabetes', 'hypertension', 'cancer', 'heart disease', 'stroke',
            'depression', 'anxiety', 'arthritis', 'asthma', 'migraine'
        ]
        
        title_lower = title.lower()
        for term in medical_terms:
            if term in title_lower:
                return term.title()
        
        return 'General'
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        sqlite_entries = self.database.get_all_entries()
        vector_stats = self.vector_store.get_collection_stats()
        
        return {
            'sqlite_entries': len(sqlite_entries),
            'vector_documents': vector_stats['total_documents'],
            'sources': list(set([entry['source'] for entry in sqlite_entries])),
            'conditions': list(set([entry['condition'] for entry in sqlite_entries]))
        }

def main():
    """Test the data pipeline."""
    pipeline = DataPipeline()
    
    print("🚀 Testing TrustMed AI Data Pipeline")
    print("=" * 50)
    
    # Test ingestion
    print("📥 Testing data ingestion...")
    data = pipeline.ingest_all_sources(max_items_per_source=5)
    
    # Test processing and storage
    print("\n🔄 Testing data processing and storage...")
    results = pipeline.process_and_store(data)
    
    print(f"✅ Processed: {results['processed']}/{results['total']}")
    print(f"✅ Stored: {results['stored']}/{results['total']}")
    
    # Test database stats
    print("\n📊 Database Statistics:")
    stats = pipeline.get_database_stats()
    print(f"   SQLite entries: {stats['sqlite_entries']}")
    print(f"   Vector documents: {stats['vector_documents']}")
    print(f"   Sources: {stats['sources']}")
    print(f"   Conditions: {stats['conditions']}")
    
    print("\n🎯 Phase B Data Processing: COMPLETE!")
    print("Ready for Phase C: RAG and Conversational Agent")

if __name__ == "__main__":
    main()
