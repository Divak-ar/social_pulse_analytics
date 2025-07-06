"""
Main entry point for Social Pulse Analytics
Handles application startup, data collection scheduling, and dashboard launch
"""
import os
import sys
import threading
import time
import schedule
import subprocess
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import config
from app.database import db
from collectors.reddit_collector import reddit_collector
from collectors.news_collector import news_collector
from analyzers.sentiment_analyzer import sentiment_analyzer

def collect_and_analyze_data():
    """Collect data from all sources and perform analysis"""
    print(f"\n🔄 Starting data collection at {datetime.now()}")
    
    try:
        # Validate configuration
        config.validate_config()
        print("✅ Configuration validated")
        
        # Collect Reddit data
        print("📱 Collecting Reddit data...")
        reddit_posts = reddit_collector.collect_all_posts()
        
        if reddit_posts:
            print(f"   Found {len(reddit_posts)} Reddit posts")
            
            # Analyze sentiment
            print("   🔍 Analyzing Reddit sentiment...")
            analyzed_posts = sentiment_analyzer.analyze_reddit_posts(reddit_posts)
            
            # Save to database
            saved_count = db.insert_reddit_posts([post.to_dict() for post in analyzed_posts])
            print(f"   💾 Saved {saved_count} Reddit posts to database")
        else:
            print("   ⚠️ No Reddit posts collected")
        
        # Collect News data
        print("📰 Collecting News data...")
        news_articles = news_collector.collect_all_articles()
        
        if news_articles:
            print(f"   Found {len(news_articles)} news articles")
            
            # Analyze sentiment
            print("   🔍 Analyzing news sentiment...")
            analyzed_articles = sentiment_analyzer.analyze_news_articles(news_articles)
            
            # Save to database
            saved_count = db.insert_news_articles([article.to_dict() for article in analyzed_articles])
            print(f"   💾 Saved {saved_count} news articles to database")
        else:
            print("   ⚠️ No news articles collected")
        
        # Clean old data
        print("🧹 Cleaning old data...")
        db.clean_old_data(days=7)
        
        print(f"✅ Data collection completed at {datetime.now()}")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n🔧 Please check your .env file and ensure all API keys are set correctly.")
        return False
    except Exception as e:
        print(f"❌ Error during data collection: {e}")
        return False
    
    return True

def setup_scheduler():
    """Setup the data collection scheduler"""
    # Schedule data collection every 30 minutes
    schedule.every(config.UPDATE_INTERVAL).minutes.do(collect_and_analyze_data)
    print(f"⏰ Scheduled data collection every {config.UPDATE_INTERVAL} minutes")
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    # Run scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    return scheduler_thread

def launch_streamlit_dashboard():
    """Launch the Streamlit dashboard"""
    dashboard_file = os.path.join(os.path.dirname(__file__), "dashboard", "streamlit_app.py")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        dashboard_file,
        "--server.port", str(config.STREAMLIT_PORT),
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ]
    
    print(f"🚀 Launching Streamlit dashboard on http://localhost:{config.STREAMLIT_PORT}")
    
    try:
        # Launch Streamlit
        process = subprocess.Popen(cmd)
        return process
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        return None

def check_initial_setup():
    """Check if this is the first run and setup accordingly"""
    print("🔍 Checking initial setup...")
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        print("\n⚠️  No .env file found!")
        print("📝 Please create a .env file based on .env.example")
        print("🔑 You'll need API keys from:")
        print("   - Reddit: https://www.reddit.com/prefs/apps")
        print("   - NewsAPI: https://newsapi.org/register")
        return False
    
    # Check if database exists, create if not
    try:
        db.create_tables()
        print("✅ Database setup completed")
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False
    
    return True

def show_startup_info():
    """Show application startup information"""
    print("=" * 60)
    print("🧠 SOCIAL PULSE ANALYTICS")
    print("   Understanding Human Nature Through Social Media")
    print("=" * 60)
    print(f"📊 Database: {config.DATABASE_PATH}")
    print(f"⏰ Update Interval: {config.UPDATE_INTERVAL} minutes")
    print(f"🌐 Dashboard Port: {config.STREAMLIT_PORT}")
    print(f"📱 Reddit Subreddits: {len(config.REDDIT_SUBREDDITS)}")
    print("=" * 60)

def main():
    """Main application entry point"""
    show_startup_info()
    
    # Check initial setup
    if not check_initial_setup():
        print("\n❌ Setup incomplete. Please fix the issues above and try again.")
        return
    
    print("\n🎯 Choose an option:")
    print("1. Collect data once and exit")
    print("2. Launch dashboard with auto-collection")
    print("3. Launch dashboard only (no data collection)")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return
    
    if choice == "1":
        # One-time data collection
        print("\n🔄 Running one-time data collection...")
        success = collect_and_analyze_data()
        if success:
            print("\n✅ Data collection completed successfully!")
            print("💡 You can now run option 3 to view the dashboard")
        else:
            print("\n❌ Data collection failed. Please check your API keys.")
    
    elif choice == "2":
        # Launch dashboard with auto-collection
        print("\n🚀 Starting full application...")
        
        # Initial data collection
        print("🔄 Performing initial data collection...")
        initial_success = collect_and_analyze_data()
        
        if not initial_success:
            print("⚠️  Initial data collection failed, but continuing with dashboard...")
        
        # Setup scheduler
        scheduler_thread = setup_scheduler()
        
        # Launch dashboard
        dashboard_process = launch_streamlit_dashboard()
        
        if dashboard_process:
            try:
                print("\n✅ Application running!")
                print("🌐 Open your browser to view the dashboard")
                print("⏹️  Press Ctrl+C to stop the application")
                
                # Wait for user interrupt
                dashboard_process.wait()
                
            except KeyboardInterrupt:
                print("\n⏹️  Stopping application...")
                dashboard_process.terminate()
                print("👋 Goodbye!")
        else:
            print("❌ Failed to launch dashboard")
    
    elif choice == "3":
        # Dashboard only
        print("\n🚀 Launching dashboard only...")
        dashboard_process = launch_streamlit_dashboard()
        
        if dashboard_process:
            try:
                print("\n✅ Dashboard launched!")
                print("🌐 Open your browser to view the dashboard")
                print("⏹️  Press Ctrl+C to stop")
                
                dashboard_process.wait()
                
            except KeyboardInterrupt:
                print("\n⏹️  Stopping dashboard...")
                dashboard_process.terminate()
                print("👋 Goodbye!")
        else:
            print("❌ Failed to launch dashboard")
    
    else:
        print("❌ Invalid choice. Please run the application again.")

if __name__ == "__main__":
    main()