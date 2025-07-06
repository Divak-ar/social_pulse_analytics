"""
Data collection scheduler for Social Pulse Analytics
Handles automated data collection from Reddit and News sources
"""
import schedule
import time
import threading
from datetime import datetime
from typing import Optional

from app.config import config
from app.database import db
from collectors.reddit_collector import reddit_collector
from collectors.news_collector import news_collector
from analyzers.sentiment_analyzer import sentiment_analyzer

class DataCollectionScheduler:
    """Automated data collection scheduler"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.last_collection_time: Optional[datetime] = None
        self.collection_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'last_error': None
        }
    
    def collect_reddit_data(self) -> bool:
        """Collect and analyze Reddit data"""
        try:
            print(f"📱 Collecting Reddit data at {datetime.now()}")
            
            # Collect posts
            reddit_posts = reddit_collector.collect_all_posts()
            
            if reddit_posts:
                print(f"   Found {len(reddit_posts)} Reddit posts")
                
                # Analyze sentiment
                analyzed_posts = sentiment_analyzer.analyze_reddit_posts(reddit_posts)
                
                # Save to database
                saved_count = db.insert_reddit_posts([post.to_dict() for post in analyzed_posts])
                print(f"   💾 Saved {saved_count} Reddit posts")
                
                return True
            else:
                print("   ⚠️ No Reddit posts collected")
                return False
                
        except Exception as e:
            print(f"   ❌ Reddit collection error: {e}")
            return False
    
    def collect_news_data(self) -> bool:
        """Collect and analyze news data"""
        try:
            print(f"📰 Collecting news data at {datetime.now()}")
            
            # Collect articles
            news_articles = news_collector.collect_all_articles()
            
            if news_articles:
                print(f"   Found {len(news_articles)} news articles")
                
                # Analyze sentiment
                analyzed_articles = sentiment_analyzer.analyze_news_articles(news_articles)
                
                # Save to database
                saved_count = db.insert_news_articles([article.to_dict() for article in analyzed_articles])
                print(f"   💾 Saved {saved_count} news articles")
                
                return True
            else:
                print("   ⚠️ No news articles collected")
                return False
                
        except Exception as e:
            print(f"   ❌ News collection error: {e}")
            return False
    
    def run_data_collection(self) -> bool:
        """Run complete data collection cycle"""
        print(f"\n🔄 Starting scheduled data collection at {datetime.now()}")
        
        self.collection_stats['total_runs'] += 1
        success = True
        
        try:
            # Validate configuration
            config.validate_config()
            
            # Collect Reddit data
            reddit_success = self.collect_reddit_data()
            
            # Wait a moment between collections
            time.sleep(2)
            
            # Collect news data
            news_success = self.collect_news_data()
            
            # Clean old data
            print("🧹 Cleaning old data...")
            db.clean_old_data(days=7)
            
            # Update stats
            if reddit_success or news_success:
                self.collection_stats['successful_runs'] += 1
                self.last_collection_time = datetime.now()
                print(f"✅ Data collection completed successfully")
            else:
                self.collection_stats['failed_runs'] += 1
                success = False
                print(f"⚠️ Data collection completed with warnings")
            
        except Exception as e:
            self.collection_stats['failed_runs'] += 1
            self.collection_stats['last_error'] = str(e)
            success = False
            print(f"❌ Data collection failed: {e}")
        
        return success
    
    def schedule_collection(self, interval_minutes: int = None):
        """Schedule regular data collection"""
        if interval_minutes is None:
            interval_minutes = config.UPDATE_INTERVAL
        
        # Clear any existing schedules
        schedule.clear()
        
        # Schedule the collection
        schedule.every(interval_minutes).minutes.do(self.run_data_collection)
        
        print(f"⏰ Scheduled data collection every {interval_minutes} minutes")
        
        # Run initial collection
        print("🎯 Running initial data collection...")
        self.run_data_collection()
    
    def start_scheduler(self, interval_minutes: int = None):
        """Start the scheduler in a background thread"""
        if self.is_running:
            print("⚠️ Scheduler is already running")
            return
        
        self.schedule_collection(interval_minutes)
        self.is_running = True
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("🚀 Data collection scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        print("⏹️ Data collection scheduler stopped")
    
    def get_status(self) -> dict:
        """Get scheduler status and statistics"""
        return {
            'is_running': self.is_running,
            'last_collection_time': self.last_collection_time.isoformat() if self.last_collection_time else None,
            'next_run_time': schedule.next_run() if schedule.jobs else None,
            'collection_stats': self.collection_stats.copy(),
            'success_rate': (
                self.collection_stats['successful_runs'] / max(self.collection_stats['total_runs'], 1)
            ) * 100
        }
    
    def force_collection(self) -> bool:
        """Force an immediate data collection"""
        print("🎯 Forcing immediate data collection...")
        return self.run_data_collection()

# Global scheduler instance
data_scheduler = DataCollectionScheduler()