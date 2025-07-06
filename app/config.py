import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Reddit API Configuration
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "SocialPulseAnalytics/1.0")
    
    # NewsAPI Configuration
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    
    # Database Configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/social_pulse.db")
    
    # Scheduling Configuration
    UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "30"))
    
    # Server Configuration
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Reddit Configuration (Optimized for faster loading)
    REDDIT_SUBREDDITS = [
        "technology", "science", "worldnews", "politics", 
        "datascience", "artificial", "environment", "AskReddit",
        "AmItheAsshole", "relationships", "news", "cryptocurrency",
        "movies", "sports", "conspiracy", "stocks", "investing", 
        "programming", "funny", "explainlikeimfive", "todayilearned", 
        "unpopularopinion", "changemyview", "legaladvice", 
        "personalfinance", "prorevenge", "gaming", "nba",
        "soccer", "nfl", "entertainment", "music", 
        "food", "cooking", "fitness", "meditation", "philosophy", 
        "psychology"
    ]
    
    # News Topics for Enhanced Coverage
    NEWS_TOPICS = [
        "artificial intelligence", "climate change", "politics",
        "stock market crash", "crypto volatility", "mass layoffs",
        "social justice movements", "economic inflation", 
        "cost of living crisis", "celebrity scandals", "public reactions", "nba" , "psychology" , "mental health",
        "economy", "technology", "science", "health",
        "cryptocurrency", "stocks", "inflation", "fitness", "celebrity", "sports", "entertainment"
    ]
    
    # Data Collection Limits
    REDDIT_POST_LIMIT = 25  # Posts per subreddit
    NEWS_ARTICLE_LIMIT = 50  # Total articles
    
    # Time Configuration  
    HOURS_LOOKBACK = 24  # Analyze last 24 hours
    
    @classmethod
    def validate_config(cls):
        """Validate that required API keys are present"""
        missing = []
        
        if not cls.REDDIT_CLIENT_ID:
            missing.append("REDDIT_CLIENT_ID")
        if not cls.REDDIT_CLIENT_SECRET:
            missing.append("REDDIT_CLIENT_SECRET") 
        if not cls.NEWS_API_KEY:
            missing.append("NEWS_API_KEY")
            
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True

# Global config instance
config = Config()