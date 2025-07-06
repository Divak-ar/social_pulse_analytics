import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta
from app.config import config

class Database:
    """SQLite database manager"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.ensure_database_exists()
        self.create_tables()
    
    def ensure_database_exists(self):
        """Create database directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Create all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Reddit posts table
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
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # News articles table  
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT UNIQUE,
                    source TEXT,
                    published_at TIMESTAMP,
                    sentiment_score REAL,
                    keywords TEXT,
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
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_subreddit ON reddit_posts(subreddit)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_created ON reddit_posts(created_utc)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trending_created ON trending_topics(created_at)")
            
            conn.commit()
    
    def insert_reddit_posts(self, posts):
        """Insert Reddit posts into database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for post in posts:
                cursor.execute("""
                    INSERT OR REPLACE INTO reddit_posts 
                    (id, title, subreddit, author, score, num_comments, url, selftext, 
                     created_utc, sentiment_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post['id'], post['title'], post['subreddit'], post['author'],
                    post['score'], post['num_comments'], post['url'], post['selftext'],
                    post['created_utc'], post['sentiment_score']
                ))
            
            conn.commit()
            return len(posts)
    
    def insert_news_articles(self, articles):
        """Insert news articles into database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            inserted = 0
            for article in articles:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO news_articles 
                        (title, description, url, source, published_at, sentiment_score, keywords)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article['title'], article['description'], article['url'], 
                        article['source'], article['published_at'], 
                        article['sentiment_score'], article['keywords']
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