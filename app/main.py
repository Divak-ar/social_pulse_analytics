"""
FastAPI backend for Social Pulse Analytics
Provides REST API endpoints for data access and analytics
(Optional - for future scaling beyond Streamlit)
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uvicorn

from app.config import config
from app.database import db
from app.models import RedditPost, NewsArticle, SentimentMetrics
from collectors.reddit_collector import reddit_collector
from collectors.news_collector import news_collector
from collectors.scheduler import data_scheduler
from analyzers.sentiment_analyzer import sentiment_analyzer
from analyzers.trend_detector import trend_detector
from analyzers.correlation_engine import correlation_engine

# Initialize FastAPI app
app = FastAPI(
    title="Social Pulse Analytics API",
    description="Understanding Human Nature Through Social Media Patterns",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting Social Pulse Analytics API...")
    
    # Ensure database tables exist
    db.create_tables()
    
    # Start data collection scheduler
    # data_scheduler.start_scheduler()  # Uncomment for automatic collection
    
    print("✅ API ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("⏹️ Shutting down Social Pulse Analytics API...")
    data_scheduler.stop_scheduler()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Data collection endpoints
@app.post("/collect/reddit")
async def collect_reddit_data(background_tasks: BackgroundTasks):
    """Trigger Reddit data collection"""
    background_tasks.add_task(data_scheduler.collect_reddit_data)
    return {"message": "Reddit data collection started"}

@app.post("/collect/news")
async def collect_news_data(background_tasks: BackgroundTasks):
    """Trigger news data collection"""
    background_tasks.add_task(data_scheduler.collect_news_data)
    return {"message": "News data collection started"}

@app.post("/collect/all")
async def collect_all_data(background_tasks: BackgroundTasks):
    """Trigger complete data collection"""
    background_tasks.add_task(data_scheduler.run_data_collection)
    return {"message": "Full data collection started"}

# Data retrieval endpoints
@app.get("/data/reddit")
async def get_reddit_data(hours: int = 24, limit: Optional[int] = None):
    """Get recent Reddit posts"""
    try:
        df = db.get_recent_reddit_posts(hours=hours)
        
        if df.empty:
            return {"data": [], "count": 0}
        
        if limit:
            df = df.head(limit)
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        return {
            "data": data,
            "count": len(data),
            "hours_covered": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/news")
async def get_news_data(hours: int = 24, limit: Optional[int] = None):
    """Get recent news articles"""
    try:
        df = db.get_recent_news_articles(hours=hours)
        
        if df.empty:
            return {"data": [], "count": 0}
        
        if limit:
            df = df.head(limit)
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        return {
            "data": data,
            "count": len(data),
            "hours_covered": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/analytics/sentiment")
async def get_sentiment_analysis(hours: int = 24):
    """Get sentiment analysis comparison"""
    try:
        reddit_df = db.get_recent_reddit_posts(hours=hours)
        news_df = db.get_recent_news_articles(hours=hours)
        
        if reddit_df.empty and news_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Convert to model objects
        reddit_posts = []
        for _, row in reddit_df.iterrows():
            post = RedditPost(row.to_dict())
            reddit_posts.append(post)
        
        news_articles = []
        for _, row in news_df.iterrows():
            article = NewsArticle(row.to_dict())
            news_articles.append(article)
        
        # Get sentiment comparison
        sentiment_comparison = sentiment_analyzer.compare_platform_sentiment(
            reddit_posts, news_articles
        )
        
        return sentiment_comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/trends")
async def get_trending_topics(hours: int = 24, limit: int = 20):
    """Get trending topics analysis"""
    try:
        reddit_df = db.get_recent_reddit_posts(hours=hours)
        news_df = db.get_recent_news_articles(hours=hours)
        
        if reddit_df.empty and news_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Convert to model objects
        reddit_posts = []
        for _, row in reddit_df.iterrows():
            post = RedditPost(row.to_dict())
            reddit_posts.append(post)
        
        news_articles = []
        for _, row in news_df.iterrows():
            article = NewsArticle(row.to_dict())
            news_articles.append(article)
        
        # Get trending topics
        trending_topics = trend_detector.find_cross_platform_trends(
            reddit_posts, news_articles
        )
        
        # Convert to dictionaries for JSON response
        topics_data = [topic.to_dict() for topic in trending_topics[:limit]]
        
        return {
            "trending_topics": topics_data,
            "count": len(topics_data),
            "hours_analyzed": hours
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/predictions")
async def get_viral_predictions(hours: int = 6, limit: int = 10):
    """Get viral content predictions"""
    try:
        reddit_df = db.get_recent_reddit_posts(hours=hours)
        news_df = db.get_recent_news_articles(hours=hours)
        
        if reddit_df.empty:
            raise HTTPException(status_code=404, detail="No Reddit data available")
        
        # Convert to model objects
        reddit_posts = []
        for _, row in reddit_df.iterrows():
            post = RedditPost(row.to_dict())
            reddit_posts.append(post)
        
        news_articles = []
        for _, row in news_df.iterrows():
            article = NewsArticle(row.to_dict())
            news_articles.append(article)
        
        # Get predictions
        predictions = trend_detector.predict_trending_topics(
            reddit_posts, news_articles
        )
        
        return {
            "predictions": predictions[:limit],
            "count": len(predictions[:limit]),
            "hours_analyzed": hours
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/correlation")
async def get_correlation_analysis(hours: int = 24):
    """Get cross-platform correlation analysis"""
    try:
        reddit_df = db.get_recent_reddit_posts(hours=hours)
        news_df = db.get_recent_news_articles(hours=hours)
        
        if reddit_df.empty or news_df.empty:
            raise HTTPException(status_code=404, detail="Insufficient data for correlation analysis")
        
        # Convert to model objects
        reddit_posts = []
        for _, row in reddit_df.iterrows():
            post = RedditPost(row.to_dict())
            reddit_posts.append(post)
        
        news_articles = []
        for _, row in news_df.iterrows():
            article = NewsArticle(row.to_dict())
            news_articles.append(article)
        
        # Generate correlation report
        correlation_report = correlation_engine.generate_correlation_report(
            reddit_posts, news_articles
        )
        
        return correlation_report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Scheduler management endpoints
@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get data collection scheduler status"""
    return data_scheduler.get_status()

@app.post("/scheduler/start")
async def start_scheduler():
    """Start the data collection scheduler"""
    data_scheduler.start_scheduler()
    return {"message": "Scheduler started"}

@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the data collection scheduler"""
    data_scheduler.stop_scheduler()
    return {"message": "Scheduler stopped"}

# Statistics endpoints
@app.get("/stats/summary")
async def get_data_summary():
    """Get data collection summary statistics"""
    try:
        reddit_df = db.get_recent_reddit_posts(hours=24)
        news_df = db.get_recent_news_articles(hours=24)
        
        summary = {
            "reddit": {
                "total_posts": len(reddit_df),
                "total_engagement": reddit_df['score'].sum() if not reddit_df.empty and 'score' in reddit_df.columns else 0,
                "avg_sentiment": reddit_df['sentiment_score'].mean() if not reddit_df.empty and 'sentiment_score' in reddit_df.columns else 0,
                "subreddits": reddit_df['subreddit'].nunique() if not reddit_df.empty and 'subreddit' in reddit_df.columns else 0
            },
            "news": {
                "total_articles": len(news_df),
                "avg_sentiment": news_df['sentiment_score'].mean() if not news_df.empty and 'sentiment_score' in news_df.columns else 0,
                "sources": news_df['source'].nunique() if not news_df.empty and 'source' in news_df.columns else 0
            },
            "scheduler": data_scheduler.get_status(),
            "last_updated": datetime.now().isoformat()
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoints
@app.get("/search/topics")
async def search_topics(query: str, hours: int = 24, limit: int = 50):
    """Search for specific topics across platforms"""
    try:
        reddit_df = db.get_recent_reddit_posts(hours=hours)
        news_df = db.get_recent_news_articles(hours=hours)
        
        query_lower = query.lower()
        
        # Filter Reddit posts
        reddit_matches = []
        if not reddit_df.empty:
            for _, row in reddit_df.iterrows():
                title = str(row.get('title', '')).lower()
                selftext = str(row.get('selftext', '')).lower()
                if query_lower in title or query_lower in selftext:
                    reddit_matches.append(row.to_dict())
        
        # Filter news articles
        news_matches = []
        if not news_df.empty:
            for _, row in news_df.iterrows():
                title = str(row.get('title', '')).lower()
                description = str(row.get('description', '')).lower()
                if query_lower in title or query_lower in description:
                    news_matches.append(row.to_dict())
        
        return {
            "query": query,
            "reddit_matches": reddit_matches[:limit//2],
            "news_matches": news_matches[:limit//2],
            "total_matches": len(reddit_matches) + len(news_matches)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.API_PORT,
        reload=True
    )