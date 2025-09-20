"""WebMD scraper for disease information."""

import re
from typing import Dict, List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from src.ingestion.scraper_base import MedicalScraper
from src.utils.config import REQUEST_TIMEOUT
from src.utils.logging import logger

class WebMDScraper(MedicalScraper):
    """Scraper for WebMD disease pages."""
    
    def __init__(self):
        super().__init__("https://www.webmd.com", respect_robots=True)
    
    def discover_disease_pages(self, max_pages: int = 50) -> List[str]:
        """Discover disease pages from WebMD."""
        disease_urls = []
        
        try:
            # Start from conditions A-Z page
            start_url = "https://www.webmd.com/a-to-z-guides/health-topic-list"
            content = self.get_page_content_sync(start_url)
            
            if content:
                soup = self.parse_html(content)
                # Find condition links
                condition_links = soup.find_all('a', href=re.compile(r'/a-to-z-guides/[^/]+/?$'))
                
                for link in condition_links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        if self.is_valid_url(full_url):
                            disease_urls.append(full_url)
                            
                        if len(disease_urls) >= max_pages:
                            break
                
                self.rate_limit()
            
            logger.info(f"Discovered {len(disease_urls)} disease pages from WebMD")
            return disease_urls[:max_pages]
            
        except Exception as e:
            logger.error(f"Error discovering disease pages: {e}")
            return []
    
    def scrape_disease_page(self, url: str) -> Optional[Dict]:
        """Scrape a single disease page from WebMD."""
        try:
            if not self.check_robots_txt(url):
                logger.warning(f"Robots.txt may disallow scraping: {url}")
                return None
            
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            
            if 'site help' in response.text.lower():
                logger.warning(f"Page redirected to site help: {url}")
                return None
            
            soup = self.parse_html(response.text)
            
            disease_data = {
                'url': url,
                'source': 'WebMD',
                'source_type': 'health_site',
                'title': self._extract_title(soup),
                'overview': self._extract_overview(soup),
                'symptoms': self._extract_symptoms(soup),
                'causes': self._extract_causes(soup),
                'treatments': self._extract_treatments(soup),
                'drugs': self._extract_drugs(soup),
                'side_effects': self._extract_side_effects(soup),
                'content': self._extract_main_content(soup)
            }
            
            return self._clean_disease_data(disease_data)
            
        except Exception as e:
            logger.error(f"Error scraping disease page {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract disease title."""
        title_selectors = ['h1', '.page-title', '.article-title', '.condition-title']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return self.clean_text(element.get_text())
        return ""
    
    def _extract_overview(self, soup: BeautifulSoup) -> str:
        """Extract disease overview."""
        overview_selectors = ['.overview', '.summary', '.intro', '.description']
        for selector in overview_selectors:
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
            next_elements = heading.find_next_siblings(['p', 'ul', 'ol', 'div'])
            
            for elem in next_elements:
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    if '\n' in text:
                        parts = [part.strip() for part in text.split('\n') if part.strip()]
                        symptoms.extend(parts)
                    elif '. ' in text:
                        parts = [part.strip() for part in text.split('. ') if part.strip()]
                        symptoms.extend(parts)
                    else:
                        symptoms.append(text)
                    
                    if len(symptoms) > 20:
                        break
            
            if symptoms:
                break
        
        symptoms = list(set([self.clean_text(s) for s in symptoms if s.strip()]))
        return symptoms[:15]
    
    def _extract_causes(self, soup: BeautifulSoup) -> List[str]:
        """Extract causes list."""
        causes = []
        
        cause_headings = soup.find_all(['h2', 'h3', 'h4'], string=lambda text: text and 'cause' in text.lower())
        
        for heading in cause_headings:
            next_elements = heading.find_next_siblings(['p', 'ul', 'ol', 'div'])
            
            for elem in next_elements:
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    if '\n' in text:
                        parts = [part.strip() for part in text.split('\n') if part.strip()]
                        causes.extend(parts)
                    elif '. ' in text:
                        parts = [part.strip() for part in text.split('. ') if part.strip()]
                        causes.extend(parts)
                    else:
                        causes.append(text)
                    
                    if len(causes) > 20:
                        break
            
            if causes:
                break
        
        causes = list(set([self.clean_text(c) for c in causes if c.strip()]))
        return causes[:15]
    
    def _extract_treatments(self, soup: BeautifulSoup) -> List[str]:
        """Extract treatments list."""
        treatments = []
        
        treatment_headings = soup.find_all(['h2', 'h3', 'h4'], string=lambda text: text and ('treatment' in text.lower() or 'therapy' in text.lower()))
        
        for heading in treatment_headings:
            next_elements = heading.find_next_siblings(['p', 'ul', 'ol', 'div'])
            
            for elem in next_elements:
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    if '\n' in text:
                        parts = [part.strip() for part in text.split('\n') if part.strip()]
                        treatments.extend(parts)
                    elif '. ' in text:
                        parts = [part.strip() for part in text.split('. ') if part.strip()]
                        treatments.extend(parts)
                    else:
                        treatments.append(text)
                    
                    if len(treatments) > 20:
                        break
            
            if treatments:
                break
        
        treatments = list(set([self.clean_text(t) for t in treatments if t.strip()]))
        return treatments[:15]
    
    def _extract_drugs(self, soup: BeautifulSoup) -> List[str]:
        """Extract drugs list."""
        drugs = []
        
        drug_headings = soup.find_all(['h2', 'h3', 'h4'], string=lambda text: text and ('drug' in text.lower() or 'medication' in text.lower() or 'medicine' in text.lower()))
        
        for heading in drug_headings:
            next_elements = heading.find_next_siblings(['p', 'ul', 'ol', 'div'])
            
            for elem in next_elements:
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    if '\n' in text:
                        parts = [part.strip() for part in text.split('\n') if part.strip()]
                        drugs.extend(parts)
                    elif '. ' in text:
                        parts = [part.strip() for part in text.split('. ') if part.strip()]
                        drugs.extend(parts)
                    else:
                        drugs.append(text)
                    
                    if len(drugs) > 20:
                        break
            
            if drugs:
                break
        
        drugs = list(set([self.clean_text(d) for d in drugs if d.strip()]))
        return drugs[:15]
    
    def _extract_side_effects(self, soup: BeautifulSoup) -> List[str]:
        """Extract side effects list."""
        side_effects = []
        
        side_effect_headings = soup.find_all(['h2', 'h3', 'h4'], string=lambda text: text and ('side effect' in text.lower() or 'adverse' in text.lower()))
        
        for heading in side_effect_headings:
            next_elements = heading.find_next_siblings(['p', 'ul', 'ol', 'div'])
            
            for elem in next_elements:
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    if '\n' in text:
                        parts = [part.strip() for part in text.split('\n') if part.strip()]
                        side_effects.extend(parts)
                    elif '. ' in text:
                        parts = [part.strip() for part in text.split('. ') if part.strip()]
                        side_effects.extend(parts)
                    else:
                        side_effects.append(text)
                    
                    if len(side_effects) > 20:
                        break
            
            if side_effects:
                break
        
        side_effects = list(set([self.clean_text(s) for s in side_effects if s.strip()]))
        return side_effects[:15]
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content."""
        content_selectors = ['.content', '.main-content', '.article-content', 'main', '.article-body']
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return self.clean_text(element.get_text())
        return ""
    
    def _clean_disease_data(self, data: Dict) -> Dict:
        """Clean and validate disease data."""
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, list):
                cleaned_list = list(set([item for item in value if item.strip()]))
                cleaned_data[key] = cleaned_list
            elif isinstance(value, str):
                cleaned_data[key] = value.strip()
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def scrape_multiple_diseases(self, max_diseases: int = 20) -> List[Dict]:
        """Scrape multiple disease pages from WebMD."""
        logger.info(f"Starting to scrape {max_diseases} diseases from WebMD")
        
        disease_urls = self.discover_disease_pages(max_diseases)
        
        if not disease_urls:
            logger.warning("No disease pages discovered")
            return []
        
        scraped_diseases = []
        
        for i, url in enumerate(disease_urls):
            logger.info(f"Scraping disease {i+1}/{len(disease_urls)}: {url}")
            
            disease_data = self.scrape_disease_page(url)
            if disease_data:
                scraped_diseases.append(disease_data)
            
            self.rate_limit()
        
        logger.info(f"Successfully scraped {len(scraped_diseases)} diseases from WebMD")
        return scraped_diseases

def main():
    """Test the WebMD scraper."""
    scraper = WebMDScraper()
    
    # Test with known working URLs
    test_urls = [
        "https://www.webmd.com/diabetes/default.htm",
        "https://www.webmd.com/heart-disease/default.htm"
    ]
    
    print("Testing WebMD scraper...")
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

if __name__ == "__main__":
    main()
