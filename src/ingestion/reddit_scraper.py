"""Reddit scraper for medical community discussions."""

import praw
from typing import Dict, List, Optional
from src.utils.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, MEDICAL_SUBREDDITS
from src.utils.logging import logger

class RedditScraper:
    """Scraper for Reddit medical subreddits."""
    
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
    
    def scrape_subreddit(self, subreddit_name: str, max_posts: int = 50) -> List[Dict]:
        """Scrape posts from a medical subreddit."""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts_data = []
            
            logger.info(f"Scraping {max_posts} posts from r/{subreddit_name}")
            
            for post in subreddit.hot(limit=max_posts):
                post_data = {
                    'title': post.title,
                    'content': post.selftext,
                    'url': f"https://reddit.com{post.permalink}",
                    'source': f'Reddit r/{subreddit_name}',
                    'source_type': 'community',
                    'author': str(post.author) if post.author else 'deleted',
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'comments': self._extract_comments(post, max_comments=10)
                }
                
                posts_data.append(post_data)
            
            logger.info(f"Scraped {len(posts_data)} posts from r/{subreddit_name}")
            return posts_data
            
        except Exception as e:
            logger.error(f"Error scraping subreddit r/{subreddit_name}: {e}")
            return []
    
    def _extract_comments(self, post, max_comments: int = 10) -> List[Dict]:
        """Extract top comments from a post."""
        comments = []
        
        try:
            post.comments.replace_more(limit=0)
            
            for comment in post.comments[:max_comments]:
                if hasattr(comment, 'body') and comment.body and comment.body != '[deleted]':
                    comment_data = {
                        'content': comment.body,
                        'author': str(comment.author) if comment.author else 'deleted',
                        'score': comment.score,
                        'created_utc': comment.created_utc
                    }
                    comments.append(comment_data)
            
        except Exception as e:
            logger.error(f"Error extracting comments: {e}")
        
        return comments
    
    def scrape_medical_subreddits(self, max_posts_per_subreddit: int = 20) -> List[Dict]:
        """Scrape from multiple medical subreddits."""
        all_posts = []
        
        for subreddit_name in MEDICAL_SUBREDDITS:
            posts = self.scrape_subreddit(subreddit_name, max_posts_per_subreddit)
            all_posts.extend(posts)
        
        logger.info(f"Total posts scraped from all subreddits: {len(all_posts)}")
        return all_posts
    
    def search_medical_posts(self, query: str, max_posts: int = 50) -> List[Dict]:
        """Search for medical posts across subreddits."""
        try:
            posts_data = []
            
            for subreddit_name in MEDICAL_SUBREDDITS:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                for post in subreddit.search(query, limit=max_posts // len(MEDICAL_SUBREDDITS)):
                    post_data = {
                        'title': post.title,
                        'content': post.selftext,
                        'url': f"https://reddit.com{post.permalink}",
                        'source': f'Reddit r/{subreddit_name}',
                        'source_type': 'community',
                        'author': str(post.author) if post.author else 'deleted',
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'search_query': query
                    }
                    
                    posts_data.append(post_data)
            
            logger.info(f"Found {len(posts_data)} posts for query: {query}")
            return posts_data
            
        except Exception as e:
            logger.error(f"Error searching medical posts: {e}")
            return []

def main():
    """Test the Reddit scraper."""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("❌ Reddit API credentials not configured")
        print("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in environment")
        return
    
    scraper = RedditScraper()
    
    # Test scraping AskDocs subreddit
    print("Testing Reddit scraper...")
    posts = scraper.scrape_subreddit("AskDocs", max_posts=5)
    
    if posts:
        print(f"✅ Scraped {len(posts)} posts from r/AskDocs")
        for i, post in enumerate(posts[:3]):
            print(f"  {i+1}. {post['title'][:50]}...")
            print(f"     Score: {post['score']}, Comments: {post['num_comments']}")
    else:
        print("❌ Failed to scrape Reddit posts")

if __name__ == "__main__":
    main()
