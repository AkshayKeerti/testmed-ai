"""PubMed API client for fetching medical journal abstracts."""

import requests
import time
from typing import List, Dict, Optional
from urllib.parse import urlencode
from src.utils.config import PUBMED_EMAIL, MEDICAL_JOURNALS
from src.utils.logging import logger

class PubMedClient:
    """Client for interacting with PubMed E-utilities API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, email: str = PUBMED_EMAIL):
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TrustMedAI/1.0 (Educational Project)',
            'Email': email
        })
    
    def search_articles(self, 
                       journal: str, 
                       max_results: int = 100,
                       days_back: int = 7) -> List[str]:
        """
        Search for articles from a specific journal.
        
        Args:
            journal: Journal name to search
            max_results: Maximum number of results to return
            days_back: Number of days back to search
            
        Returns:
            List of PubMed IDs
        """
        try:
            # Build search query
            query = f'"{journal}"[Journal] AND ("{days_back}"[PDAT] : "3000"[PDAT])'
            
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'email': self.email
            }
            
            url = f"{self.BASE_URL}/esearch.fcgi"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pmids = data.get('esearchresult', {}).get('idlist', [])
            
            logger.info(f"Found {len(pmids)} articles for {journal}")
            return pmids
            
        except Exception as e:
            logger.error(f"Error searching articles for {journal}: {e}")
            return []
    
    def get_article_details(self, pmid: str) -> Optional[Dict]:
        """
        Get detailed information for a specific article.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary with article details or None if error
        """
        try:
            # Get summary
            summary_params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'json',
                'email': self.email
            }
            
            summary_url = f"{self.BASE_URL}/esummary.fcgi"
            summary_response = self.session.get(summary_url, params=summary_params, timeout=30)
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            # Get abstract
            abstract_params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml',
                'email': self.email
            }
            
            abstract_url = f"{self.BASE_URL}/efetch.fcgi"
            abstract_response = self.session.get(abstract_url, params=abstract_params, timeout=30)
            abstract_response.raise_for_status()
            
            # Parse XML for abstract (simplified)
            abstract_text = self._extract_abstract_from_xml(abstract_response.text)
            
            # Extract summary data
            result = summary_data.get('result', {}).get(pmid, {})
            
            article_data = {
                'pmid': pmid,
                'title': result.get('title', ''),
                'authors': result.get('authors', []),
                'journal': result.get('source', ''),
                'pub_date': result.get('pubdate', ''),
                'abstract': abstract_text,
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                'source_type': 'journal',
                'date_added': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.debug(f"Retrieved article details for PMID {pmid}")
            return article_data
            
        except Exception as e:
            logger.error(f"Error getting article details for PMID {pmid}: {e}")
            return None
    
    def _extract_abstract_from_xml(self, xml_content: str) -> str:
        """Extract abstract text from PubMed XML response."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(xml_content, 'xml')
            abstract_elem = soup.find('AbstractText')
            return abstract_elem.get_text() if abstract_elem else ""
        except Exception as e:
            logger.error(f"Error extracting abstract from XML: {e}")
            return ""
    
    def fetch_recent_articles(self, max_per_journal: int = 50) -> List[Dict]:
        """
        Fetch recent articles from all tracked medical journals.
        
        Args:
            max_per_journal: Maximum articles per journal
            
        Returns:
            List of article dictionaries
        """
        all_articles = []
        
        for journal in MEDICAL_JOURNALS:
            logger.info(f"Fetching articles from {journal}")
            
            # Search for articles
            pmids = self.search_articles(journal, max_per_journal)
            
            # Get details for each article
            for pmid in pmids:
                article = self.get_article_details(pmid)
                if article:
                    all_articles.append(article)
                
                # Rate limiting - PubMed requires delays
                time.sleep(0.5)
            
            # Delay between journals
            time.sleep(2)
        
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles

def main():
    """Test the PubMed client."""
    client = PubMedClient()
    
    # Test with a small sample
    articles = client.fetch_recent_articles(max_per_journal=5)
    
    for article in articles[:3]:  # Show first 3
        print(f"Title: {article['title']}")
        print(f"Journal: {article['journal']}")
        print(f"PMID: {article['pmid']}")
        print(f"Abstract: {article['abstract'][:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    main()

