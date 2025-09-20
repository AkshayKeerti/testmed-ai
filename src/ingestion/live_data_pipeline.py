"""
Live Data Integration Pipeline for TrustMed AI
Combines PubMed API + Web Scraping for comprehensive medical updates
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import json

from src.ingestion.pubmed_client import PubMedClient
from src.ingestion.web_scraper import MedicalWebScraper

logger = logging.getLogger(__name__)

class LiveDataPipeline:
    """Pipeline for live medical data ingestion"""
    
    def __init__(self):
        self.pubmed_client = PubMedClient()
        self.web_scraper = MedicalWebScraper()
        logger.info("Live data pipeline initialized")
    
    def ingest_medical_condition(self, condition: str) -> Dict[str, Any]:
        """Ingest comprehensive data for a medical condition"""
        logger.info(f"Starting live data ingestion for: {condition}")
        
        # Fetch PubMed articles
        pubmed_articles = self.pubmed_client.fetch_recent_medical_articles([condition], days_back=30)
        
        # Scrape web sources
        web_data = self.web_scraper.scrape_multiple_sources(condition)
        
        # Combine and structure data
        combined_data = {
            "condition": condition,
            "ingestion_date": datetime.now().isoformat(),
            "pubmed_articles": pubmed_articles,
            "web_sources": web_data,
            "total_sources": len(pubmed_articles) + len(web_data)
        }
        
        logger.info(f"Completed ingestion for {condition}: {combined_data['total_sources']} sources")
        return combined_data
    
    def ingest_multiple_conditions(self, conditions: List[str]) -> List[Dict[str, Any]]:
        """Ingest data for multiple medical conditions"""
        all_data = []
        
        for condition in conditions:
            try:
                data = self.ingest_medical_condition(condition)
                all_data.append(data)
            except Exception as e:
                logger.error(f"Error ingesting {condition}: {e}")
                continue
        
        logger.info(f"Completed ingestion for {len(all_data)} conditions")
        return all_data
    
    def get_condition_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for a condition"""
        condition = data["condition"]
        
        # Extract symptoms from web sources
        all_symptoms = []
        for source in data["web_sources"]:
            all_symptoms.extend(source.get("symptoms", []))
        
        # Extract treatments from web sources
        all_treatments = []
        for source in data["web_sources"]:
            all_treatments.extend(source.get("treatments", []))
        
        # Extract causes from web sources
        all_causes = []
        for source in data["web_sources"]:
            all_causes.extend(source.get("causes", []))
        
        # Get recent research from PubMed
        recent_research = []
        for article in data["pubmed_articles"][:5]:  # Top 5 recent articles
            recent_research.append({
                "title": article["title"],
                "journal": article["journal"],
                "year": article["year"],
                "url": article["url"]
            })
        
        return {
            "condition": condition,
            "symptoms": list(set(all_symptoms)),  # Remove duplicates
            "treatments": list(set(all_treatments)),
            "causes": list(set(all_causes)),
            "recent_research": recent_research,
            "total_sources": data["total_sources"],
            "ingestion_date": data["ingestion_date"]
        }

# Test the live data pipeline
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    pipeline = LiveDataPipeline()
    
    # Test with common conditions
    test_conditions = ["diabetes", "hypertension", "asthma"]
    
    print("Starting live data ingestion...")
    all_data = pipeline.ingest_multiple_conditions(test_conditions)
    
    print(f"\nIngestion complete! Processed {len(all_data)} conditions:")
    for data in all_data:
        summary = pipeline.get_condition_summary(data)
        print(f"\n{summary['condition'].title()}:")
        print(f"  Sources: {summary['total_sources']}")
        print(f"  Symptoms: {len(summary['symptoms'])}")
        print(f"  Treatments: {len(summary['treatments'])}")
        print(f"  Recent Research: {len(summary['recent_research'])}")
        
        if summary['symptoms']:
            print(f"  Sample Symptoms: {', '.join(summary['symptoms'][:3])}")
        
        if summary['recent_research']:
            print(f"  Latest Research: {summary['recent_research'][0]['title'][:60]}...")
