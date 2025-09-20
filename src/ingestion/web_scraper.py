"""
Web Scraping Pipeline for TrustMed AI
Pulls live medical updates from Mayo Clinic, WebMD, and other medical websites
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class MedicalWebScraper:
    """Scraper for medical websites to extract structured medical information"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rate_limit_delay = 1.0  # Respect website rate limits
        logger.info("Medical web scraper initialized")
    
    def scrape_mayo_clinic(self, condition: str) -> Optional[Dict[str, Any]]:
        """Scrape Mayo Clinic for medical condition information"""
        try:
            # Construct Mayo Clinic URL
            base_url = "https://www.mayoclinic.org"
            search_url = f"{base_url}/search/search-results?q={condition}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find condition-specific page
            condition_link = None
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and condition.lower() in href.lower() and '/diseases-conditions/' in href:
                    condition_link = urljoin(base_url, href)
                    break
            
            if not condition_link:
                logger.warning(f"No Mayo Clinic page found for: {condition}")
                return None
            
            # Scrape the condition page
            return self._scrape_mayo_condition_page(condition_link, condition)
            
        except Exception as e:
            logger.error(f"Error scraping Mayo Clinic for {condition}: {e}")
            return None
    
    def _scrape_mayo_condition_page(self, url: str, condition: str) -> Dict[str, Any]:
        """Scrape specific Mayo Clinic condition page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.text.strip() if title_elem else f"{condition.title()} - Mayo Clinic"
            
            # Extract overview
            overview_elem = soup.find('div', class_='content')
            overview = overview_elem.text.strip() if overview_elem else "No overview available"
            
            # Extract symptoms
            symptoms = self._extract_symptoms_mayo(soup)
            
            # Extract causes
            causes = self._extract_causes_mayo(soup)
            
            # Extract treatments
            treatments = self._extract_treatments_mayo(soup)
            
            return {
                "title": title,
                "overview": overview,
                "symptoms": symptoms,
                "causes": causes,
                "treatments": treatments,
                "source": "Mayo Clinic",
                "url": url,
                "condition": condition,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error scraping Mayo Clinic page {url}: {e}")
            return {}
    
    def _extract_symptoms_mayo(self, soup: BeautifulSoup) -> List[str]:
        """Extract symptoms from Mayo Clinic page"""
        symptoms = []
        
        # Look for symptoms section
        symptoms_section = soup.find('h2', string=re.compile(r'symptoms', re.I))
        if symptoms_section:
            # Find the next sibling with symptoms
            next_elem = symptoms_section.find_next_sibling()
            if next_elem:
                for li in next_elem.find_all('li'):
                    symptoms.append(li.text.strip())
        
        return symptoms
    
    def _extract_causes_mayo(self, soup: BeautifulSoup) -> List[str]:
        """Extract causes from Mayo Clinic page"""
        causes = []
        
        # Look for causes section
        causes_section = soup.find('h2', string=re.compile(r'causes?', re.I))
        if causes_section:
            next_elem = causes_section.find_next_sibling()
            if next_elem:
                for li in next_elem.find_all('li'):
                    causes.append(li.text.strip())
        
        return causes
    
    def _extract_treatments_mayo(self, soup: BeautifulSoup) -> List[str]:
        """Extract treatments from Mayo Clinic page"""
        treatments = []
        
        # Look for treatment section
        treatment_section = soup.find('h2', string=re.compile(r'treatment', re.I))
        if treatment_section:
            next_elem = treatment_section.find_next_sibling()
            if next_elem:
                for li in next_elem.find_all('li'):
                    treatments.append(li.text.strip())
        
        return treatments
    
    def scrape_webmd(self, condition: str) -> Optional[Dict[str, Any]]:
        """Scrape WebMD for medical condition information"""
        try:
            # Construct WebMD URL
            base_url = "https://www.webmd.com"
            search_url = f"{base_url}/search/search-results?query={condition}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find condition-specific page
            condition_link = None
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and condition.lower() in href.lower() and '/default.htm' in href:
                    condition_link = urljoin(base_url, href)
                    break
            
            if not condition_link:
                logger.warning(f"No WebMD page found for: {condition}")
                return None
            
            # Scrape the condition page
            return self._scrape_webmd_condition_page(condition_link, condition)
            
        except Exception as e:
            logger.error(f"Error scraping WebMD for {condition}: {e}")
            return None
    
    def _scrape_webmd_condition_page(self, url: str, condition: str) -> Dict[str, Any]:
        """Scrape specific WebMD condition page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.text.strip() if title_elem else f"{condition.title()} - WebMD"
            
            # Extract overview
            overview_elem = soup.find('div', class_='overview')
            overview = overview_elem.text.strip() if overview_elem else "No overview available"
            
            # Extract symptoms
            symptoms = self._extract_symptoms_webmd(soup)
            
            # Extract causes
            causes = self._extract_causes_webmd(soup)
            
            # Extract treatments
            treatments = self._extract_treatments_webmd(soup)
            
            return {
                "title": title,
                "overview": overview,
                "symptoms": symptoms,
                "causes": causes,
                "treatments": treatments,
                "source": "WebMD",
                "url": url,
                "condition": condition,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error scraping WebMD page {url}: {e}")
            return {}
    
    def _extract_symptoms_webmd(self, soup: BeautifulSoup) -> List[str]:
        """Extract symptoms from WebMD page"""
        symptoms = []
        
        # Look for symptoms section
        symptoms_section = soup.find('h2', string=re.compile(r'symptoms', re.I))
        if symptoms_section:
            next_elem = symptoms_section.find_next_sibling()
            if next_elem:
                for li in next_elem.find_all('li'):
                    symptoms.append(li.text.strip())
        
        return symptoms
    
    def _extract_causes_webmd(self, soup: BeautifulSoup) -> List[str]:
        """Extract causes from WebMD page"""
        causes = []
        
        # Look for causes section
        causes_section = soup.find('h2', string=re.compile(r'causes?', re.I))
        if causes_section:
            next_elem = causes_section.find_next_sibling()
            if next_elem:
                for li in next_elem.find_all('li'):
                    causes.append(li.text.strip())
        
        return causes
    
    def _extract_treatments_webmd(self, soup: BeautifulSoup) -> List[str]:
        """Extract treatments from WebMD page"""
        treatments = []
        
        # Look for treatment section
        treatment_section = soup.find('h2', string=re.compile(r'treatment', re.I))
        if treatment_section:
            next_elem = treatment_section.find_next_sibling()
            if next_elem:
                for li in next_elem.find_all('li'):
                    treatments.append(li.text.strip())
        
        return treatments
    
    def scrape_multiple_sources(self, condition: str) -> List[Dict[str, Any]]:
        """Scrape multiple medical sources for a condition"""
        results = []
        
        # Scrape Mayo Clinic
        mayo_result = self.scrape_mayo_clinic(condition)
        if mayo_result:
            results.append(mayo_result)
        
        # Rate limiting
        time.sleep(self.rate_limit_delay)
        
        # Scrape WebMD
        webmd_result = self.scrape_webmd(condition)
        if webmd_result:
            results.append(webmd_result)
        
        return results

# Test the web scraper
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = MedicalWebScraper()
    
    # Test with a common condition
    test_condition = "diabetes"
    results = scraper.scrape_multiple_sources(test_condition)
    
    print(f"\nScraped {len(results)} sources for {test_condition}:")
    for result in results:
        print(f"- {result['source']}: {result['title']}")
        print(f"  Symptoms: {len(result['symptoms'])}")
        print(f"  Causes: {len(result['causes'])}")
        print(f"  Treatments: {len(result['treatments'])}")
