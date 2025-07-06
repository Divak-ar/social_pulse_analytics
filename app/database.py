"""
Database operations for Social Pulse Analytics
Handles SQLite database creation, connections, and basic operations
"""
import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta
from app.config import config

class Database:
    """SQLite database manager"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.is_memory_db = self.db_path == ":memory:"
        
        if not self.is_memory_db:
            self.ensure_database_exists()
        
        self.create_tables()
    
    def ensure_database_exists(self):
        """Create database directory if it doesn't exist (only for file databases)"""
        if not self.is_memory_db and self.db_path != ":memory:":
            dir_path = os.path.dirname(self.db_path)
            if dir_path:  # Only create directory if there's a path
                os.makedirs(dir_path, exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Create all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Reddit posts table (Enhanced with more fields)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reddit_posts (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    subreddit TEXT NOT NULL,
                    author TEXT,
                    score INTEGER DEFAULT 0,
                    num_comments INTEGER DEFAULT 0,
                    url TEXT,
                    selftext TEXT,
                    created_utc REAL,
                    sentiment_score REAL,
                    upvote_ratio REAL DEFAULT 0,
                    post_flair TEXT,
                    is_nsfw BOOLEAN DEFAULT 0,
                    is_spoiler BOOLEAN DEFAULT 0,
                    is_locked BOOLEAN DEFAULT 0,
                    post_type TEXT DEFAULT 'text',
                    domain TEXT,
                    gilded INTEGER DEFAULT 0,
                    distinguished TEXT,
                    stickied BOOLEAN DEFAULT 0,
                    total_awards_received INTEGER DEFAULT 0,
                    curse_word_count INTEGER DEFAULT 0,
                    readability_score REAL DEFAULT 0,
                    engagement_velocity REAL DEFAULT 0,
                    virality_score REAL DEFAULT 0,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # News articles table (Enhanced with more fields)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    content TEXT,
                    url TEXT UNIQUE,
                    source TEXT,
                    author TEXT,
                    category TEXT,
                    language TEXT DEFAULT 'en',
                    country TEXT,
                    published_at TIMESTAMP,
                    sentiment_score REAL,
                    keywords TEXT,
                    word_count INTEGER DEFAULT 0,
                    readability_score REAL DEFAULT 0,
                    urgency_score REAL DEFAULT 0,
                    credibility_score REAL DEFAULT 0,
                    emotional_tone TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Trending topics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trending_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    reddit_mentions INTEGER DEFAULT 0,
                    news_mentions INTEGER DEFAULT 0,
                    sentiment_avg REAL DEFAULT 0,
                    momentum_score REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # ML Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT,
                    prediction_type TEXT NOT NULL,
                    predicted_value REAL,
                    actual_value REAL,
                    model_version TEXT,
                    confidence_score REAL,
                    features_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES reddit_posts (id)
                )
            """)
            
            # Behavioral insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS behavioral_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    insight_text TEXT NOT NULL,
                    supporting_data TEXT,
                    confidence_level REAL,
                    sample_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Content analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    analysis_result TEXT,
                    score REAL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_subreddit ON reddit_posts(subreddit)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_created ON reddit_posts(created_utc)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_score ON reddit_posts(score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_virality ON reddit_posts(virality_score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_source ON news_articles(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trending_created ON trending_topics(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ml_predictions_type ON ml_predictions(prediction_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_behavioral_platform ON behavioral_insights(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_analysis_type ON content_analysis(analysis_type)")
            
            conn.commit()
    
    def insert_reddit_posts(self, posts):
        """Insert Reddit posts into database with enhanced fields"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for post in posts:
                cursor.execute("""
                    INSERT OR REPLACE INTO reddit_posts 
                    (id, title, subreddit, author, score, num_comments, url, selftext, 
                     created_utc, sentiment_score, upvote_ratio, post_flair, is_nsfw, 
                     is_spoiler, is_locked, post_type, domain, gilded, distinguished, 
                     stickied, total_awards_received, curse_word_count, readability_score, 
                     engagement_velocity, virality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post['id'], post['title'], post['subreddit'], post['author'],
                    post['score'], post['num_comments'], post['url'], post['selftext'],
                    post['created_utc'], post['sentiment_score'], post.get('upvote_ratio', 0),
                    post.get('post_flair', ''), post.get('is_nsfw', False), 
                    post.get('is_spoiler', False), post.get('is_locked', False),
                    post.get('post_type', 'text'), post.get('domain', ''), post.get('gilded', 0),
                    post.get('distinguished', ''), post.get('stickied', False),
                    post.get('total_awards_received', 0), post.get('curse_word_count', 0),
                    post.get('readability_score', 0), post.get('engagement_velocity', 0),
                    post.get('virality_score', 0)
                ))
            
            conn.commit()
            return len(posts)
    
    def insert_news_articles(self, articles):
        """Insert news articles into database with enhanced fields"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            inserted = 0
            for article in articles:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO news_articles 
                        (title, description, content, url, source, author, category, 
                         language, country, published_at, sentiment_score, keywords, 
                         word_count, readability_score, urgency_score, credibility_score, emotional_tone)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article['title'], article['description'], article.get('content', ''),
                        article['url'], article['source'], article.get('author', ''),
                        article.get('category', ''), article.get('language', 'en'),
                        article.get('country', ''), article['published_at'], 
                        article['sentiment_score'], article['keywords'],
                        article.get('word_count', 0), article.get('readability_score', 0),
                        article.get('urgency_score', 0), article.get('credibility_score', 0),
                        article.get('emotional_tone', '')
                    ))
                    if cursor.rowcount > 0:
                        inserted += 1
                except sqlite3.IntegrityError:
                    continue  # Skip duplicates
            
            conn.commit()
            return inserted
    
    def get_recent_reddit_posts(self, hours=24):
        """Get Reddit posts from last N hours"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        query = """
            SELECT * FROM reddit_posts 
            WHERE created_utc > ? 
            ORDER BY created_utc DESC
        """
        
        return pd.read_sql_query(query, self.get_connection(), params=[cutoff_time])
    
    def get_recent_news_articles(self, hours=24):
        """Get news articles from last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        query = """
            SELECT * FROM news_articles 
            WHERE published_at > ? 
            ORDER BY published_at DESC
        """
        
        return pd.read_sql_query(query, self.get_connection(), params=[cutoff_time])
    
    def get_sentiment_summary(self):
        """Get sentiment summary across platforms"""
        with self.get_connection() as conn:
            # Reddit sentiment
            reddit_sentiment = pd.read_sql_query("""
                SELECT 
                    subreddit,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(*) as post_count
                FROM reddit_posts 
                WHERE created_utc > ? 
                GROUP BY subreddit
            """, conn, params=[datetime.now().timestamp() - 86400])
            
            # News sentiment
            news_sentiment = pd.read_sql_query("""
                SELECT 
                    source,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(*) as article_count
                FROM news_articles 
                WHERE published_at > datetime('now', '-24 hours')
                GROUP BY source
            """, conn)
            
            return reddit_sentiment, news_sentiment
    
    def clean_old_data(self, days=7):
        """Clean data older than N days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean old Reddit posts
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            cursor.execute("DELETE FROM reddit_posts WHERE created_utc < ?", [cutoff_time])
            
            # Clean old news articles
            cursor.execute("""
                DELETE FROM news_articles 
                WHERE published_at < datetime('now', '-{} days')
            """.format(days))
            
            # Clean old trending topics
            cursor.execute("""
                DELETE FROM trending_topics 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days))
            
            conn.commit()

# Global database instance
db = Database()