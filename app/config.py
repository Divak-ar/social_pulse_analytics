import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_config_value(key, default=""):
    """Get configuration value from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # Fallback to environment variables
    return os.getenv(key, default)

class Config:
    """Application configuration"""
    
    # Reddit API Configuration
    REDDIT_CLIENT_ID = get_config_value("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = get_config_value("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = get_config_value("REDDIT_USER_AGENT", "SocialPulseAnalytics/1.0")
    
    # NewsAPI Configuration
    NEWS_API_KEY = get_config_value("NEWS_API_KEY", "")
    
    # Database Configuration (use in-memory for cloud)
    DATABASE_PATH = get_config_value("DATABASE_PATH", ":memory:")
    
    # Scheduling Configuration
    UPDATE_INTERVAL = int(get_config_value("UPDATE_INTERVAL", "30"))
    
    # Server Configuration
    STREAMLIT_PORT = int(get_config_value("STREAMLIT_PORT", "8501"))
    API_PORT = int(get_config_value("API_PORT", "8000"))
    
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