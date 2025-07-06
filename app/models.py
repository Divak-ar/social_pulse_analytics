from datetime import datetime
from typing import List, Optional, Dict, Any

class RedditPost:
    """Reddit post data model"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.title = data.get('title', '')
        self.subreddit = data.get('subreddit', '')
        self.author = data.get('author', '[deleted]')
        self.score = data.get('score', 0)
        self.num_comments = data.get('num_comments', 0)
        self.url = data.get('url', '')
        self.selftext = data.get('selftext', '')
        self.created_utc = data.get('created_utc', 0)
        self.sentiment_score = data.get('sentiment_score', 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'subreddit': self.subreddit,
            'author': self.author,
            'score': self.score,
            'num_comments': self.num_comments,
            'url': self.url,
            'selftext': self.selftext,
            'created_utc': self.created_utc,
            'sentiment_score': self.sentiment_score
        }
    
    @property
    def engagement_score(self) -> float:
        """Calculate engagement score based on upvotes and comments"""
        hours_old = (datetime.now().timestamp() - self.created_utc) / 3600
        if hours_old <= 0:
            hours_old = 0.1  # Prevent division by zero
        
        return (self.score + (self.num_comments * 2)) / hours_old
    
    @property
    def virality_index(self) -> float:
        """Calculate virality index"""
        if self.score <= 0:
            return 0
        
        comment_ratio = self.num_comments / max(self.score, 1)
        return self.engagement_score * (1 + comment_ratio)

class NewsArticle:
    """News article data model"""
    
    def __init__(self, data: Dict[str, Any]):
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.url = data.get('url', '')
        self.source = data.get('source', {}).get('name', '') if isinstance(data.get('source'), dict) else data.get('source', '')
        self.published_at = data.get('publishedAt', data.get('published_at', ''))
        self.sentiment_score = data.get('sentiment_score', 0.0)
        self.keywords = data.get('keywords', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'source': self.source,
            'published_at': self.published_at,
            'sentiment_score': self.sentiment_score,
            'keywords': self.keywords
        }

class TrendingTopic:
    """Trending topic data model"""
    
    def __init__(self, keyword: str):
        self.keyword = keyword
        self.reddit_mentions = 0
        self.news_mentions = 0
        self.sentiment_avg = 0.0
        self.momentum_score = 0.0
        self.created_at = datetime.now()
    
    def update_mentions(self, reddit_count: int, news_count: int):
        """Update mention counts"""
        self.reddit_mentions = reddit_count
        self.news_mentions = news_count
    
    def update_sentiment(self, sentiment_scores: List[float]):
        """Update average sentiment"""
        if sentiment_scores:
            self.sentiment_avg = sum(sentiment_scores) / len(sentiment_scores)
    
    def calculate_momentum(self, previous_mentions: int = 0):
        """Calculate trend momentum"""
        total_mentions = self.reddit_mentions + self.news_mentions
        if previous_mentions > 0:
            self.momentum_score = (total_mentions - previous_mentions) / previous_mentions
        else:
            self.momentum_score = total_mentions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'keyword': self.keyword,
            'reddit_mentions': self.reddit_mentions,
            'news_mentions': self.news_mentions,
            'sentiment_avg': self.sentiment_avg,
            'momentum_score': self.momentum_score,
            'total_mentions': self.reddit_mentions + self.news_mentions,
            'cross_platform': self.reddit_mentions > 0 and self.news_mentions > 0
        }

class SentimentMetrics:
    """Sentiment analysis metrics"""
    
    def __init__(self):
        self.positive_count = 0
        self.negative_count = 0
        self.neutral_count = 0
        self.average_score = 0.0
        self.total_items = 0
    
    def add_sentiment(self, score: float):
        """Add a sentiment score to metrics"""
        self.total_items += 1
        
        if score > 0.1:
            self.positive_count += 1
        elif score < -0.1:
            self.negative_count += 1
        else:
            self.neutral_count += 1
        
        # Update running average
        self.average_score = ((self.average_score * (self.total_items - 1)) + score) / self.total_items
    
    @property
    def sentiment_distribution(self) -> Dict[str, float]:
        """Get sentiment distribution as percentages"""
        if self.total_items == 0:
            return {'positive': 0, 'negative': 0, 'neutral': 0}
        
        return {
            'positive': (self.positive_count / self.total_items) * 100,
            'negative': (self.negative_count / self.total_items) * 100,
            'neutral': (self.neutral_count / self.total_items) * 100
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_items': self.total_items,
            'average_score': round(self.average_score, 3),
            'distribution': self.sentiment_distribution,
            'counts': {
                'positive': self.positive_count,
                'negative': self.negative_count,
                'neutral': self.neutral_count
            }
        }