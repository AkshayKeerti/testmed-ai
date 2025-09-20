"""
Reddit API Integration for TrustMed AI
Pulls community insights from medical subreddits to blend with evidence-based information
"""

import praw
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class RedditClient:
    """Client for Reddit API to fetch medical community insights"""
    
    def __init__(self):
        # Reddit API credentials (using public access)
        self.reddit = praw.Reddit(
            client_id="your_client_id",  # Replace with actual credentials
            client_secret="your_client_secret",  # Replace with actual credentials
            user_agent="TrustMedAI/1.0"
        )
        
        # Medical subreddits to monitor
        self.medical_subreddits = [
            "AskDocs",
            "Medical",
            "diabetes",
            "hypertension",
            "asthma",
            "depression",
            "cancer",
            "health",
            "medicine",
            "nursing"
        ]
        
        logger.info("Reddit client initialized")
    
    def search_medical_posts(self, condition: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for medical posts related to a condition"""
        try:
            posts = []
            
            # Search across medical subreddits
            for subreddit_name in self.medical_subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for posts about the condition
                    search_results = subreddit.search(condition, limit=limit//len(self.medical_subreddits))
                    
                    for post in search_results:
                        post_data = self._extract_post_data(post)
                        if post_data:
                            posts.append(post_data)
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error searching subreddit {subreddit_name}: {e}")
                    continue
            
            logger.info(f"Found {len(posts)} Reddit posts for: {condition}")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching Reddit for {condition}: {e}")
            return []
    
    def _extract_post_data(self, post) -> Optional[Dict[str, Any]]:
        """Extract relevant data from a Reddit post"""
        try:
            # Skip deleted or removed posts
            if post.selftext == "[deleted]" or post.selftext == "[removed]":
                return None
            
            # Extract post information
            post_data = {
                "title": post.title,
                "content": post.selftext,
                "subreddit": post.subreddit.display_name,
                "author": str(post.author) if post.author else "Unknown",
                "score": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
                "created_utc": post.created_utc,
                "url": f"https://reddit.com{post.permalink}",
                "source": "Reddit"
            }
            
            # Extract comments for additional insights
            comments = self._extract_top_comments(post)
            post_data["comments"] = comments
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None
    
    def _extract_top_comments(self, post, limit: int = 5) -> List[Dict[str, Any]]:
        """Extract top comments from a post"""
        try:
            comments = []
            
            # Get top comments
            post.comments.replace_more(limit=0)
            top_comments = post.comments.list()[:limit]
            
            for comment in top_comments:
                if hasattr(comment, 'body') and comment.body != "[deleted]":
                    comment_data = {
                        "content": comment.body,
                        "author": str(comment.author) if comment.author else "Unknown",
                        "score": comment.score,
                        "created_utc": comment.created_utc
                    }
                    comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            logger.error(f"Error extracting comments: {e}")
            return []
    
    def get_condition_insights(self, condition: str) -> Dict[str, Any]:
        """Get community insights for a medical condition"""
        try:
            # Search for posts
            posts = self.search_medical_posts(condition, limit=100)
            
            # Analyze posts for insights
            insights = {
                "condition": condition,
                "total_posts": len(posts),
                "subreddits": list(set(post["subreddit"] for post in posts)),
                "common_themes": self._extract_common_themes(posts),
                "patient_experiences": self._extract_patient_experiences(posts),
                "questions": self._extract_questions(posts),
                "scraped_at": datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting insights for {condition}: {e}")
            return {}
    
    def _extract_common_themes(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extract common themes from posts"""
        themes = []
        
        # Simple keyword extraction
        keywords = ["symptoms", "treatment", "medication", "side effects", "diagnosis", "experience"]
        
        for post in posts:
            content = f"{post['title']} {post['content']}".lower()
            for keyword in keywords:
                if keyword in content:
                    themes.append(keyword)
        
        # Return most common themes
        from collections import Counter
        theme_counts = Counter(themes)
        return [theme for theme, count in theme_counts.most_common(5)]
    
    def _extract_patient_experiences(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extract patient experience snippets"""
        experiences = []
        
        for post in posts:
            content = post["content"]
            if len(content) > 50 and len(content) < 500:  # Reasonable length
                experiences.append(content[:200] + "..." if len(content) > 200 else content)
        
        return experiences[:10]  # Limit to 10 experiences
    
    def _extract_questions(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extract questions from posts"""
        questions = []
        
        for post in posts:
            title = post["title"]
            if "?" in title:
                questions.append(title)
        
        return questions[:10]  # Limit to 10 questions

# Test the Reddit client
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Note: This will fail without proper Reddit API credentials
    print("Reddit API integration requires proper credentials.")
    print("To test this, you need to:")
    print("1. Create a Reddit app at https://www.reddit.com/prefs/apps")
    print("2. Get client_id and client_secret")
    print("3. Update the RedditClient initialization")
    
    # client = RedditClient()
    # insights = client.get_condition_insights("diabetes")
    # print(f"Insights: {insights}")
