"""
Community Data Integration Pipeline for TrustMed AI
Combines Reddit + Forum data to blend evidence-based + community perspectives
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import json

from src.ingestion.reddit_client import RedditClient
from src.ingestion.forum_scraper import DiscussionBoardScraper

logger = logging.getLogger(__name__)

class CommunityDataPipeline:
    """Pipeline for community data integration"""
    
    def __init__(self):
        self.reddit_client = RedditClient()
        self.forum_scraper = DiscussionBoardScraper()
        logger.info("Community data pipeline initialized")
    
    def get_community_insights(self, condition: str) -> Dict[str, Any]:
        """Get comprehensive community insights for a condition"""
        logger.info(f"Starting community data collection for: {condition}")
        
        # Get Reddit insights (requires API credentials)
        reddit_insights = {}
        try:
            reddit_insights = self.reddit_client.get_condition_insights(condition)
        except Exception as e:
            logger.warning(f"Reddit API not available: {e}")
            reddit_insights = {
                "condition": condition,
                "total_posts": 0,
                "subreddits": [],
                "common_themes": [],
                "patient_experiences": [],
                "questions": [],
                "note": "Reddit API credentials required"
            }
        
        # Get forum data
        forum_data = self.forum_scraper.scrape_all_forums(condition)
        
        # Combine community insights
        community_insights = {
            "condition": condition,
            "reddit_data": reddit_insights,
            "forum_data": forum_data,
            "combined_insights": self._combine_insights(reddit_insights, forum_data),
            "scraped_at": datetime.now().isoformat()
        }
        
        logger.info(f"Completed community data collection for {condition}")
        return community_insights
    
    def _combine_insights(self, reddit_data: Dict[str, Any], forum_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine Reddit and forum insights"""
        combined = {
            "total_community_sources": 0,
            "patient_experiences": [],
            "common_questions": [],
            "treatment_discussions": [],
            "symptom_experiences": [],
            "sources": []
        }
        
        # Count total sources
        combined["total_community_sources"] = (
            reddit_data.get("total_posts", 0) +
            len(forum_data.get("webmd_forums", [])) +
            len(forum_data.get("patients_like_me", [])) +
            len(forum_data.get("healthboards", []))
        )
        
        # Extract patient experiences
        if reddit_data.get("patient_experiences"):
            combined["patient_experiences"].extend(reddit_data["patient_experiences"])
        
        if forum_data.get("patients_like_me"):
            for experience in forum_data["patients_like_me"]:
                combined["patient_experiences"].append(experience["content"])
        
        # Extract common questions
        if reddit_data.get("questions"):
            combined["common_questions"].extend(reddit_data["questions"])
        
        # Extract treatment discussions
        for forum_type in ["webmd_forums", "healthboards"]:
            if forum_data.get(forum_type):
                for discussion in forum_data[forum_type]:
                    if discussion.get("posts"):
                        combined["treatment_discussions"].extend(discussion["posts"])
        
        # Extract symptom experiences
        for forum_type in ["webmd_forums", "healthboards"]:
            if forum_data.get(forum_type):
                for discussion in forum_data[forum_type]:
                    if discussion.get("posts"):
                        for post in discussion["posts"]:
                            if any(keyword in post.lower() for keyword in ["symptom", "feel", "experience"]):
                                combined["symptom_experiences"].append(post)
        
        # List sources
        sources = []
        if reddit_data.get("subreddits"):
            sources.extend([f"Reddit r/{sub}" for sub in reddit_data["subreddits"]])
        sources.extend(["WebMD Forums", "PatientsLikeMe", "HealthBoards"])
        combined["sources"] = sources
        
        return combined
    
    def get_condition_summary_with_community(self, condition: str) -> Dict[str, Any]:
        """Get comprehensive summary including community insights"""
        community_insights = self.get_community_insights(condition)
        
        summary = {
            "condition": condition,
            "community_sources": community_insights["combined_insights"]["total_community_sources"],
            "patient_experiences": len(community_insights["combined_insights"]["patient_experiences"]),
            "common_questions": len(community_insights["combined_insights"]["common_questions"]),
            "treatment_discussions": len(community_insights["combined_insights"]["treatment_discussions"]),
            "symptom_experiences": len(community_insights["combined_insights"]["symptom_experiences"]),
            "sources": community_insights["combined_insights"]["sources"],
            "scraped_at": community_insights["scraped_at"]
        }
        
        return summary
    
    def get_multiple_conditions_insights(self, conditions: List[str]) -> List[Dict[str, Any]]:
        """Get community insights for multiple conditions"""
        all_insights = []
        
        for condition in conditions:
            try:
                insights = self.get_condition_summary_with_community(condition)
                all_insights.append(insights)
            except Exception as e:
                logger.error(f"Error getting insights for {condition}: {e}")
                continue
        
        return all_insights

# Test the community data pipeline
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    pipeline = CommunityDataPipeline()
    
    # Test with common conditions
    test_conditions = ["diabetes", "hypertension", "asthma"]
    
    print("Starting community data collection...")
    all_insights = pipeline.get_multiple_conditions_insights(test_conditions)
    
    print(f"\nCommunity insights collected for {len(all_insights)} conditions:")
    for insights in all_insights:
        print(f"\n{insights['condition'].title()}:")
        print(f"  Community Sources: {insights['community_sources']}")
        print(f"  Patient Experiences: {insights['patient_experiences']}")
        print(f"  Common Questions: {insights['common_questions']}")
        print(f"  Treatment Discussions: {insights['treatment_discussions']}")
        print(f"  Symptom Experiences: {insights['symptom_experiences']}")
        print(f"  Sources: {', '.join(insights['sources'])}")
