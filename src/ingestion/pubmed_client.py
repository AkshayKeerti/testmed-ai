"""
PubMed API Integration for TrustMed AI
Pulls live medical updates from NEJM, JAMA, and other medical journals
"""

import requests
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class PubMedClient:
    """Client for PubMed API to fetch medical journal abstracts"""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.rate_limit_delay = 0.5  # Respect PubMed rate limits
        logger.info("PubMed client initialized")
    
    def search_articles(self, query: str, max_results: int = 100, days_back: int = 7) -> List[str]:
        """Search for articles and return PMIDs"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Format query with date range
            date_query = f"{query} AND ({start_date.strftime('%Y/%m/%d')}[Date - Publication] : {end_date.strftime('%Y/%m/%d')}[Date - Publication])"
            
            # Search for PMIDs
            search_url = f"{self.base_url}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': date_query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            pmids = data.get('esearchresult', {}).get('idlist', [])
            
            logger.info(f"Found {len(pmids)} articles for query: {query}")
            return pmids
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    def get_article_details(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Get detailed article information"""
        try:
            # Fetch article details
            fetch_url = f"{self.base_url}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Extract article information
            article_info = self._parse_article_xml(root)
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return article_info
            
        except Exception as e:
            logger.error(f"Error fetching article {pmid}: {e}")
            return None
    
    def _parse_article_xml(self, root: ET.Element) -> Dict[str, Any]:
        """Parse PubMed XML response"""
        try:
            # Find article element
            article = root.find('.//PubmedArticle')
            if article is None:
                return {}
            
            # Extract basic information
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "Unknown Title"
            
            abstract_elem = article.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"
            
            # Extract authors
            authors = []
            author_list = article.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name = author.find('LastName')
                    first_name = author.find('ForeName')
                    if last_name is not None and first_name is not None:
                        authors.append(f"{first_name.text} {last_name.text}")
            
            # Extract journal information
            journal_elem = article.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else "Unknown Journal"
            
            # Extract publication date
            pub_date = article.find('.//PubDate')
            year = "2024"  # Default
            if pub_date is not None:
                year_elem = pub_date.find('Year')
                if year_elem is not None:
                    year = year_elem.text
            
            # Extract PMID
            pmid_elem = article.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else "Unknown PMID"
            
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal,
                "year": year,
                "source": "PubMed",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            
        except Exception as e:
            logger.error(f"Error parsing article XML: {e}")
            return {}
    
    def fetch_recent_medical_articles(self, conditions: List[str], days_back: int = 7) -> List[Dict[str, Any]]:
        """Fetch recent articles for specific medical conditions"""
        all_articles = []
        
        for condition in conditions:
            logger.info(f"Fetching articles for: {condition}")
            
            # Search for articles
            pmids = self.search_articles(condition, max_results=50, days_back=days_back)
            
            # Get article details
            for pmid in pmids[:20]:  # Limit to 20 per condition
                article = self.get_article_details(pmid)
                if article:
                    article["condition"] = condition
                    all_articles.append(article)
            
            # Rate limiting between conditions
            time.sleep(2)
        
        logger.info(f"Fetched {len(all_articles)} total articles")
        return all_articles

# Test the PubMed client
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    client = PubMedClient()
    
    # Test with common medical conditions
    test_conditions = ["diabetes", "hypertension", "cancer", "depression", "asthma"]
    articles = client.fetch_recent_medical_articles(test_conditions, days_back=30)
    
    print(f"\nFetched {len(articles)} articles:")
    for article in articles[:5]:  # Show first 5
        print(f"- {article['title'][:80]}... ({article['journal']}, {article['year']})")