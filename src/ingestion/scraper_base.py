"""Base scraper class with common functionality for web scraping."""

import asyncio
import time
import requests
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
from src.utils.config import SCRAPING_DELAY, MAX_RETRIES, REQUEST_TIMEOUT
from src.utils.logging import logger

class BaseScraper:
    """Base class for web scrapers with common functionality."""
    
    def __init__(self, base_url: str, respect_robots: bool = True):
        self.base_url = base_url
        self.respect_robots = respect_robots
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def check_robots_txt(self, url: str) -> bool:
        """
        Check robots.txt to see if scraping is allowed.
        
        Args:
            url: URL to check
            
        Returns:
            True if scraping is allowed, False otherwise
        """
        if not self.respect_robots:
            return True
            
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            response = self.session.get(robots_url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                logger.warning(f"Could not fetch robots.txt for {parsed_url.netloc}")
                return True  # Assume allowed if can't check
            
            robots_content = response.text.lower()
            
            # Simple check for common disallow patterns
            disallow_patterns = [
                '/admin',
                '/private',
                '/internal'
            ]
            
            for pattern in disallow_patterns:
                if pattern in robots_content:
                    logger.warning(f"Robots.txt may disallow scraping pattern: {pattern}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return True  # Assume allowed if error
    
    async def get_page_content(self, url: str, wait_for: str = "networkidle") -> Optional[str]:
        """
        Get page content using Playwright for JavaScript-heavy sites.
        
        Args:
            url: URL to scrape
            wait_for: What to wait for before getting content
            
        Returns:
            HTML content or None if error
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set viewport and user agent
                await page.set_viewport_size({"width": 1920, "height": 1080})
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                
                # Navigate to page
                await page.goto(url, wait_until=wait_for, timeout=30000)
                
                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)
                
                # Get content
                content = await page.content()
                
                await browser.close()
                return content
                
        except Exception as e:
            logger.error(f"Error getting page content for {url}: {e}")
            return None
    
    def get_page_content_sync(self, url: str) -> Optional[str]:
        """
        Get page content using requests for simple sites.
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content or None if error
        """
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
            
        except Exception as e:
            logger.error(f"Error getting page content for {url}: {e}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_text_safely(self, element, default: str = "") -> str:
        """
        Safely extract text from BeautifulSoup element.
        
        Args:
            element: BeautifulSoup element
            default: Default value if element is None
            
        Returns:
            Extracted text or default
        """
        if element is None:
            return default
        return element.get_text(strip=True)
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all links from a page.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        return links
    
    def rate_limit(self, delay: float = SCRAPING_DELAY):
        """Apply rate limiting between requests."""
        time.sleep(delay)
    
    def retry_request(self, func, *args, **kwargs):
        """
        Retry a request function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if all retries fail
        """
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"All retries failed for {func.__name__}: {e}")
                    return None
                
                wait_time = (2 ** attempt) * SCRAPING_DELAY
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        return None
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common unwanted characters
        unwanted_chars = ['\n', '\t', '\r']
        for char in unwanted_chars:
            text = text.replace(char, ' ')
        
        return text.strip()
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and belongs to the same domain.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            base_parsed = urlparse(self.base_url)
            
            # Check if URL is valid
            if not parsed_url.scheme or not parsed_url.netloc:
                return False
            
            # Check if URL belongs to same domain
            if parsed_url.netloc != base_parsed.netloc:
                return False
            
            return True
            
        except Exception:
            return False

class MedicalScraper(BaseScraper):
    """Specialized scraper for medical websites."""
    
    def __init__(self, base_url: str, respect_robots: bool = True):
        super().__init__(base_url, respect_robots)
        
        # Common medical content selectors
        self.selectors = {
            'title': ['h1', '.page-title', '.article-title'],
            'symptoms': ['.symptoms', '#symptoms', '[data-section="symptoms"]'],
            'causes': ['.causes', '#causes', '[data-section="causes"]'],
            'treatments': ['.treatments', '#treatments', '[data-section="treatments"]'],
            'drugs': ['.drugs', '#drugs', '[data-section="drugs"]'],
            'side_effects': ['.side-effects', '#side-effects', '[data-section="side-effects"]'],
            'content': ['.content', '.main-content', '.article-content', 'main']
        }
    
    def extract_medical_content(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract medical content using common selectors.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with extracted medical content
        """
        content = {}
        
        for content_type, selectors in self.selectors.items():
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = self.extract_text_safely(element)
                    if text:
                        content[content_type] = self.clean_text(text)
                        break
        
        return content
    
    def extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """
        Extract structured medical data (symptoms, treatments, etc.).
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with structured medical data
        """
        structured_data = {
            'symptoms': [],
            'causes': [],
            'treatments': [],
            'drugs': [],
            'side_effects': []
        }
        
        # Look for lists and structured content
        for content_type in structured_data.keys():
            # Try different patterns for lists
            patterns = [
                f'[data-section="{content_type}"] ul li',
                f'[data-section="{content_type}"] ol li',
                f'.{content_type} ul li',
                f'.{content_type} ol li',
                f'#{content_type} ul li',
                f'#{content_type} ol li'
            ]
            
            for pattern in patterns:
                elements = soup.select(pattern)
                if elements:
                    structured_data[content_type] = [
                        self.clean_text(elem) for elem in elements
                    ]
                    break
        
        return structured_data

def main():
    """Test the base scraper functionality."""
    scraper = MedicalScraper("https://www.mayoclinic.org")
    
    # Test robots.txt check
    print("Testing robots.txt check...")
    allowed = scraper.check_robots_txt("https://www.mayoclinic.org/diseases-conditions/diabetes")
    print(f"Scraping allowed: {allowed}")
    
    # Test URL validation
    print("\nTesting URL validation...")
    valid_urls = [
        "https://www.mayoclinic.org/diseases-conditions/diabetes",
        "https://www.webmd.com/diabetes",
        "https://example.com/test"  # Should be invalid (different domain)
    ]
    
    for url in valid_urls:
        is_valid = scraper.is_valid_url(url)
        print(f"{url}: {is_valid}")

if __name__ == "__main__":
    main()
