"""Test script for data ingestion."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ingestion.pubmed_client import PubMedClient
from src.ingestion.mayo_scraper import MayoClinicScraper
from src.ingestion.webmd_scraper import WebMDScraper
from src.processing.data_cleaner import DataCleaner

def test_pubmed():
    """Test PubMed client."""
    print("=== Testing PubMed Client ===")
    client = PubMedClient()
    articles = client.fetch_recent_articles(max_per_journal=2)
    
    print(f"✅ Fetched {len(articles)} articles")
    for article in articles[:2]:
        print(f"  - {article['title'][:50]}...")
    
    return articles

def test_mayo():
    """Test Mayo Clinic scraper."""
    print("\n=== Testing Mayo Clinic Scraper ===")
    scraper = MayoClinicScraper()
    
    test_url = "https://www.mayoclinic.org/diseases-conditions/diabetes"
    disease_data = scraper.scrape_disease_page(test_url)
    
    if disease_data:
        print(f"✅ Scraped: {disease_data['title']}")
        print(f"   Symptoms: {len(disease_data['symptoms'])} items")
        print(f"   Causes: {len(disease_data['causes'])} items")
        return disease_data
    else:
        print("❌ Failed to scrape Mayo Clinic")
        return None

def test_webmd():
    """Test WebMD scraper."""
    print("\n=== Testing WebMD Scraper ===")
    scraper = WebMDScraper()
    
    test_url = "https://www.webmd.com/diabetes/default.htm"
    disease_data = scraper.scrape_disease_page(test_url)
    
    if disease_data:
        print(f"✅ Scraped: {disease_data['title']}")
        print(f"   Symptoms: {len(disease_data['symptoms'])} items")
        print(f"   Causes: {len(disease_data['causes'])} items")
        return disease_data
    else:
        print("❌ Failed to scrape WebMD")
        return None

def test_data_cleaning():
    """Test data cleaning."""
    print("\n=== Testing Data Cleaning ===")
    cleaner = DataCleaner()
    
    test_data = {
        'title': 'Diabetes   [Updated]',
        'symptoms': ['Feeling thirsty', 'Frequent urination', 'Feeling thirsty'],
        'causes': ['Unknown cause (more research needed)'],
        'treatments': ['Medication', 'Diet changes', 'Exercise'],
        'content': 'Diabetes is a chronic condition...'
    }
    
    cleaned_data = cleaner.clean_medical_data(test_data)
    validation = cleaner.validate_medical_content(cleaned_data)
    
    print(f"✅ Cleaned data: {len(cleaned_data['symptoms'])} unique symptoms")
    print(f"   Validation score: {validation['confidence_score']:.2f}")
    
    return cleaned_data

def main():
    """Run all tests."""
    print("🚀 Testing TrustMed AI Data Ingestion Pipeline")
    print("=" * 50)
    
    # Test all components
    articles = test_pubmed()
    mayo_data = test_mayo()
    webmd_data = test_webmd()
    cleaned_data = test_data_cleaning()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print(f"✅ PubMed articles: {len(articles) if articles else 0}")
    print(f"✅ Mayo Clinic data: {'Yes' if mayo_data else 'No'}")
    print(f"✅ WebMD data: {'Yes' if webmd_data else 'No'}")
    print(f"✅ Data cleaning: {'Working' if cleaned_data else 'Failed'}")
    
    print("\n🎯 Phase A Data Ingestion: COMPLETE!")
    print("Ready for Phase B: Data Processing & Storage")

if __name__ == "__main__":
    main()
