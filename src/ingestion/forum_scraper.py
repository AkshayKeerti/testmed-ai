"""
Discussion Board Scraper for TrustMed AI
Pulls community insights from medical forums and discussion boards
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional
import time
import re

logger = logging.getLogger(__name__)

class DiscussionBoardScraper:
    """Scraper for medical discussion boards and forums"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rate_limit_delay = 2.0  # Respect forum rate limits
        logger.info("Discussion board scraper initialized")
    
    def scrape_webmd_forums(self, condition: str) -> List[Dict[str, Any]]:
        """Scrape WebMD message boards for condition discussions"""
        try:
            # WebMD message boards URL
            base_url = "https://messageboards.webmd.com"
            search_url = f"{base_url}/search?q={condition}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract discussion threads
            discussions = []
            thread_links = soup.find_all('a', href=re.compile(r'/threads/'))
            
            for link in thread_links[:10]:  # Limit to 10 threads
                thread_url = urljoin(base_url, link.get('href'))
                thread_data = self._scrape_webmd_thread(thread_url, condition)
                if thread_data:
                    discussions.append(thread_data)
                
                time.sleep(self.rate_limit_delay)
            
            logger.info(f"Scraped {len(discussions)} WebMD discussions for: {condition}")
            return discussions
            
        except Exception as e:
            logger.error(f"Error scraping WebMD forums for {condition}: {e}")
            return []
    
    def _scrape_webmd_thread(self, url: str, condition: str) -> Optional[Dict[str, Any]]:
        """Scrape individual WebMD thread"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract thread title
            title_elem = soup.find('h1')
            title = title_elem.text.strip() if title_elem else "Unknown Title"
            
            # Extract posts
            posts = []
            post_elements = soup.find_all('div', class_='post-content')
            
            for post_elem in post_elements[:5]:  # Limit to 5 posts per thread
                post_text = post_elem.text.strip()
                if post_text and len(post_text) > 20:
                    posts.append(post_text)
            
            return {
                "title": title,
                "posts": posts,
                "url": url,
                "source": "WebMD Forums",
                "condition": condition,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error scraping WebMD thread {url}: {e}")
            return None
    
    def scrape_patients_like_me(self, condition: str) -> List[Dict[str, Any]]:
        """Scrape PatientsLikeMe for patient experiences"""
        try:
            # PatientsLikeMe search URL
            base_url = "https://www.patientslikeme.com"
            search_url = f"{base_url}/search?q={condition}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract patient experiences
            experiences = []
            experience_elements = soup.find_all('div', class_='experience')
            
            for elem in experience_elements[:10]:  # Limit to 10 experiences
                experience_text = elem.text.strip()
                if experience_text and len(experience_text) > 50:
                    experiences.append({
                        "content": experience_text,
                        "source": "PatientsLikeMe",
                        "condition": condition,
                        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            logger.info(f"Scraped {len(experiences)} PatientsLikeMe experiences for: {condition}")
            return experiences
            
        except Exception as e:
            logger.error(f"Error scraping PatientsLikeMe for {condition}: {e}")
            return []
    
    def scrape_healthboards(self, condition: str) -> List[Dict[str, Any]]:
        """Scrape HealthBoards for medical discussions"""
        try:
            # HealthBoards search URL
            base_url = "https://www.healthboards.com"
            search_url = f"{base_url}/search.php?searchid={condition}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract discussion threads
            discussions = []
            thread_links = soup.find_all('a', href=re.compile(r'/threads/'))
            
            for link in thread_links[:10]:  # Limit to 10 threads
                thread_url = urljoin(base_url, link.get('href'))
                thread_data = self._scrape_healthboards_thread(thread_url, condition)
                if thread_data:
                    discussions.append(thread_data)
                
                time.sleep(self.rate_limit_delay)
            
            logger.info(f"Scraped {len(discussions)} HealthBoards discussions for: {condition}")
            return discussions
            
        except Exception as e:
            logger.error(f"Error scraping HealthBoards for {condition}: {e}")
            return []
    
    def _scrape_healthboards_thread(self, url: str, condition: str) -> Optional[Dict[str, Any]]:
        """Scrape individual HealthBoards thread"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract thread title
            title_elem = soup.find('h1')
            title = title_elem.text.strip() if title_elem else "Unknown Title"
            
            # Extract posts
            posts = []
            post_elements = soup.find_all('div', class_='post-content')
            
            for post_elem in post_elements[:5]:  # Limit to 5 posts per thread
                post_text = post_elem.text.strip()
                if post_text and len(post_text) > 20:
                    posts.append(post_text)
            
            return {
                "title": title,
                "posts": posts,
                "url": url,
                "source": "HealthBoards",
                "condition": condition,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error scraping HealthBoards thread {url}: {e}")
            return None
    
    def scrape_all_forums(self, condition: str) -> Dict[str, Any]:
        """Scrape all available forums for a condition"""
        logger.info(f"Starting forum scraping for: {condition}")
        
        all_data = {
            "condition": condition,
            "webmd_forums": self.scrape_webmd_forums(condition),
            "patients_like_me": self.scrape_patients_like_me(condition),
            "healthboards": self.scrape_healthboards(condition),
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Calculate total discussions
        total_discussions = (
            len(all_data["webmd_forums"]) +
            len(all_data["patients_like_me"]) +
            len(all_data["healthboards"])
        )
        
        logger.info(f"Completed forum scraping for {condition}: {total_discussions} total discussions")
        return all_data

# Test the discussion board scraper
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = DiscussionBoardScraper()
    
    # Test with a common condition
    test_condition = "diabetes"
    forum_data = scraper.scrape_all_forums(test_condition)
    
    print(f"\nForum scraping results for {test_condition}:")
    print(f"WebMD Forums: {len(forum_data['webmd_forums'])} discussions")
    print(f"PatientsLikeMe: {len(forum_data['patients_like_me'])} experiences")
    print(f"HealthBoards: {len(forum_data['healthboards'])} discussions")
    
    # Show sample data
    if forum_data['webmd_forums']:
        sample = forum_data['webmd_forums'][0]
        print(f"\nSample WebMD discussion: {sample['title'][:60]}...")
    
    if forum_data['patients_like_me']:
        sample = forum_data['patients_like_me'][0]
        print(f"\nSample PatientsLikeMe experience: {sample['content'][:60]}...")
