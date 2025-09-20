"""Mayo Clinic scraper for disease information."""

import asyncio
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from src.ingestion.scraper_base import MedicalScraper
from src.utils.config import REQUEST_TIMEOUT
from src.utils.logging import logger

class MayoClinicScraper(MedicalScraper):
    """Scraper for Mayo Clinic disease pages."""
    
    def __init__(self):
        super().__init__("https://www.mayoclinic.org", respect_robots=True)
        
        # Mayo Clinic specific selectors
        self.selectors.update({
            'title': ['h1.page-title', 'h1', '.page-title'],
            'overview': ['.overview', '.disease-overview', '.condition-overview'],
            'symptoms': ['.symptoms', '#symptoms', '.symptom-list'],
            'causes': ['.causes', '#causes', '.cause-list'],
            'risk_factors': ['.risk-factors', '#risk-factors', '.risk-factor-list'],
            'treatments': ['.treatments', '#treatments', '.treatment-list'],
            'drugs': ['.drugs', '#drugs', '.medication-list'],
            'side_effects': ['.side-effects', '#side-effects', '.side-effect-list'],
            'prevention': ['.prevention', '#prevention', '.prevention-list'],
            'content': ['.content', '.main-content', '.article-content', 'main']
        })
    
    def discover_disease_pages(self, max_pages: int = 50) -> List[str]:
        """
        Discover disease pages from Mayo Clinic.
        
        Args:
            max_pages: Maximum number of pages to discover
            
        Returns:
            List of disease page URLs
        """
        disease_urls = []
        
        try:
            # Start from the diseases and conditions page
            start_urls = [
                "https://www.mayoclinic.org/diseases-conditions",
                "https://www.mayoclinic.org/diseases-conditions/a-z"
            ]
            
            for start_url in start_urls:
                content = self.get_page_content_sync(start_url)
                if not content:
                    continue
                
                soup = self.parse_html(content)
                
                # Find disease links - more specific pattern
                disease_links = soup.find_all('a', href=re.compile(r'/diseases-conditions/[a-z-]+/?$'))
                
                for link in disease_links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        if self.is_valid_url(full_url):
                            disease_urls.append(full_url)
                            
                        if len(disease_urls) >= max_pages:
                            break
                
                if len(disease_urls) >= max_pages:
                    break
                
                self.rate_limit()
            
            logger.info(f"Discovered {len(disease_urls)} disease pages from Mayo Clinic")
            return disease_urls[:max_pages]
            
        except Exception as e:
            logger.error(f"Error discovering disease pages: {e}")
            return []
    
    def scrape_disease_page(self, url: str) -> Optional[Dict]:
        """
        Scrape a single disease page from Mayo Clinic.
        
        Args:
            url: URL of the disease page
            
        Returns:
            Dictionary with scraped disease information
        """
        try:
            # Check robots.txt
            if not self.check_robots_txt(url):
                logger.warning(f"Robots.txt may disallow scraping: {url}")
                return None
            
            # Get page content with redirect handling
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            
            # Check if redirected to site help
            if 'site help' in response.text.lower():
                logger.warning(f"Page redirected to site help: {url}")
                return None
            
            content = response.text
            if not content:
                return None
            
            soup = self.parse_html(content)
            
            # Extract basic information
            disease_data = {
                'url': url,
                'source': 'Mayo Clinic',
                'source_type': 'health_site',
                'title': self._extract_title(soup),
                'overview': self._extract_overview(soup),
                'symptoms': self._extract_symptoms(soup),
                'causes': self._extract_causes(soup),
                'risk_factors': self._extract_risk_factors(soup),
                'treatments': self._extract_treatments(soup),
                'drugs': self._extract_drugs(soup),
                'side_effects': self._extract_side_effects(soup),
                'prevention': self._extract_prevention(soup),
                'content': self._extract_main_content(soup)
            }
            
            # Clean and validate data
            disease_data = self._clean_disease_data(disease_data)
            
            logger.debug(f"Scraped disease page: {disease_data['title']}")
            return disease_data
            
        except Exception as e:
            logger.error(f"Error scraping disease page {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract disease title."""
        for selector in self.selectors['title']:
            element = soup.select_one(selector)
            if element:
                return self.clean_text(element.get_text())
        return ""
    
    def _extract_overview(self, soup: BeautifulSoup) -> str:
        """Extract disease overview."""
        for selector in self.selectors['overview']:
            element = soup.select_one(selector)
            if element:
                return self.clean_text(element.get_text())
        return ""
    
    def _extract_symptoms(self, soup: BeautifulSoup) -> List[str]:
        """Extract symptoms list."""
        symptoms = []
        
        # Look for headings containing 'symptom'
        symptom_headings = soup.find_all(['h2', 'h3', 'h4'], string=lambda text: text and 'symptom' in text.lower())
        
        for heading in symptom_headings:
            # Get content after this heading
            next_elements = heading.find_next_siblings(['p', 'ul', 'ol', 'div'])
            
            for elem in next_elements:
                text = elem.get_text().strip()
                if text and len(text) > 10:  # Skip very short text
                    # Split by common separators
                    if '\n' in text:
                        parts = [part.strip() for part in text.split('\n') if part.strip()]
                        symptoms.extend(parts)
                    elif '. ' in text:
                        parts = [part.strip() for part in text.split('. ') if part.strip()]
                        symptoms.extend(parts)
                    else:
                        symptoms.append(text)
                    
                    # Limit to avoid too much content
                    if len(symptoms) > 20:
                        break
            
            if symptoms:
                break
        
        # Clean and deduplicate
        symptoms = list(set([self.clean_text(s) for s in symptoms if s.strip()]))
        return symptoms[:15]  # Limit to top 15
    
    def _extract_causes(self, soup: BeautifulSoup) -> List[str]:
        """Extract causes list."""
        causes = []
        
        # Look for headings containing 'cause'
        cause_headings = soup.find_all(['h2', 'h3', 'h4'], string=lambda text: text and 'cause' in text.lower())
        
        for heading in cause_headings:
            # Get content after this heading
            next_elements = heading.find_next_siblings(['p', 'ul', 'ol', 'div'])
            
            for elem in next_elements:
                text = elem.get_text().strip()
                if text and len(text) > 10:  # Skip very short text
                    # Split by common separators
                    if '\n' in text:
                        parts = [part.strip() for part in text.split('\n') if part.strip()]
                        causes.extend(parts)
                    elif '. ' in text:
                        parts = [part.strip() for part in text.split('. ') if part.strip()]
                        causes.extend(parts)
                    else:
                        causes.append(text)
                    
                    # Limit to avoid too much content
                    if len(causes) > 20:
                        break
            
            if causes:
                break
        
        # Clean and deduplicate
        causes = list(set([self.clean_text(c) for c in causes if c.strip()]))
        return causes[:15]  # Limit to top 15
    
    def _extract_risk_factors(self, soup: BeautifulSoup) -> List[str]:
        """Extract risk factors list."""
        risk_factors = []
        
        patterns = [
            '.risk-factors ul li',
            '.risk-factors ol li',
            '#risk-factors ul li',
            '#risk-factors ol li',
            '.risk-factor-list li',
            '.risk-factors p'
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            if elements:
                risk_factors = [self.clean_text(elem.get_text()) for elem in elements]
                break
        
        return risk_factors
    
    def _extract_treatments(self, soup: BeautifulSoup) -> List[str]:
        """Extract treatments list."""
        treatments = []
        
        patterns = [
            '.treatments ul li',
            '.treatments ol li',
            '#treatments ul li',
            '#treatments ol li',
            '.treatment-list li',
            '.treatments p'
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            if elements:
                treatments = [self.clean_text(elem.get_text()) for elem in elements]
                break
        
        return treatments
    
    def _extract_drugs(self, soup: BeautifulSoup) -> List[str]:
        """Extract drugs/medications list."""
        drugs = []
        
        patterns = [
            '.drugs ul li',
            '.drugs ol li',
            '#drugs ul li',
            '#drugs ol li',
            '.medication-list li',
            '.drugs p'
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            if elements:
                drugs = [self.clean_text(elem.get_text()) for elem in elements]
                break
        
        return drugs
    
    def _extract_side_effects(self, soup: BeautifulSoup) -> List[str]:
        """Extract side effects list."""
        side_effects = []
        
        patterns = [
            '.side-effects ul li',
            '.side-effects ol li',
            '#side-effects ul li',
            '#side-effects ol li',
            '.side-effect-list li',
            '.side-effects p'
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            if elements:
                side_effects = [self.clean_text(elem.get_text()) for elem in elements]
                break
        
        return side_effects
    
    def _extract_prevention(self, soup: BeautifulSoup) -> List[str]:
        """Extract prevention list."""
        prevention = []
        
        patterns = [
            '.prevention ul li',
            '.prevention ol li',
            '#prevention ul li',
            '#prevention ol li',
            '.prevention-list li',
            '.prevention p'
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            if elements:
                prevention = [self.clean_text(elem.get_text()) for elem in elements]
                break
        
        return prevention
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content."""
        for selector in self.selectors['content']:
            element = soup.select_one(selector)
            if element:
                return self.clean_text(element.get_text())
        return ""
    
    def _clean_disease_data(self, data: Dict) -> Dict:
        """Clean and validate disease data."""
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, list):
                # Remove empty strings and duplicates
                cleaned_list = list(set([item for item in value if item.strip()]))
                cleaned_data[key] = cleaned_list
            elif isinstance(value, str):
                cleaned_data[key] = value.strip()
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def scrape_multiple_diseases(self, max_diseases: int = 20) -> List[Dict]:
        """
        Scrape multiple disease pages from Mayo Clinic.
        
        Args:
            max_diseases: Maximum number of diseases to scrape
            
        Returns:
            List of disease data dictionaries
        """
        logger.info(f"Starting to scrape {max_diseases} diseases from Mayo Clinic")
        
        # Discover disease pages
        disease_urls = self.discover_disease_pages(max_diseases)
        
        if not disease_urls:
            logger.warning("No disease pages discovered")
            return []
        
        # Scrape each disease page
        scraped_diseases = []
        
        for i, url in enumerate(disease_urls):
            logger.info(f"Scraping disease {i+1}/{len(disease_urls)}: {url}")
            
            disease_data = self.scrape_disease_page(url)
            if disease_data:
                scraped_diseases.append(disease_data)
            
            # Rate limiting
            self.rate_limit()
        
        logger.info(f"Successfully scraped {len(scraped_diseases)} diseases from Mayo Clinic")
        return scraped_diseases

def main():
    """Test the Mayo Clinic scraper."""
    scraper = MayoClinicScraper()
    
    # Test with known working URLs
    test_urls = [
        "https://www.mayoclinic.org/diseases-conditions/diabetes",
        "https://www.mayoclinic.org/diseases-conditions/high-blood-pressure",
        "https://www.mayoclinic.org/diseases-conditions/common-cold"
    ]
    
    print("Testing single page scraping...")
    for test_url in test_urls:
        print(f"\nTesting: {test_url}")
        disease_data = scraper.scrape_disease_page(test_url)
        if disease_data:
            print(f"✅ Title: {disease_data['title']}")
            print(f"   Symptoms: {len(disease_data['symptoms'])} items")
            print(f"   Causes: {len(disease_data['causes'])} items")
            print(f"   Treatments: {len(disease_data['treatments'])} items")
        else:
            print("❌ Failed to scrape disease page")
    
    # Test disease discovery
    print("\nTesting disease discovery...")
    disease_urls = scraper.discover_disease_pages(max_pages=10)
    print(f"Discovered {len(disease_urls)} disease pages:")
    for url in disease_urls[:5]:
        print(f"  - {url}")

if __name__ == "__main__":
    main()
