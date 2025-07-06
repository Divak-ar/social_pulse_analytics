"""
Main Streamlit dashboard for Social Pulse Analytics
Interactive dashboard showing human behavior patterns across social media
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import time

# Import our modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.config import config
from collectors.reddit_collector import reddit_collector
from collectors.news_collector import news_collector
from analyzers.sentiment_analyzer import sentiment_analyzer
from analyzers.trend_detector import trend_detector

# Page configuration
st.set_page_config(
    page_title="Social Pulse Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better mobile responsiveness
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load recent data from database"""
    try:
        reddit_df = db.get_recent_reddit_posts(hours=24)
        news_df = db.get_recent_news_articles(hours=24)
        return reddit_df, news_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_analytics_data():
    """Get processed analytics data"""
    reddit_df, news_df = load_data()
    
    if reddit_df.empty and news_df.empty:
        return None, None, None, None
    
    # Convert to model objects for analysis
    reddit_posts = []
    if not reddit_df.empty:
        for _, row in reddit_df.iterrows():
            from app.models import RedditPost
            post = RedditPost(row.to_dict())
            reddit_posts.append(post)
    
    news_articles = []
    if not news_df.empty:
        for _, row in news_df.iterrows():
            from app.models import NewsArticle
            article = NewsArticle(row.to_dict())
            news_articles.append(article)
    
    # Get analytics
    sentiment_comparison = sentiment_analyzer.compare_platform_sentiment(reddit_posts, news_articles)
    trending_topics = trend_detector.find_cross_platform_trends(reddit_posts, news_articles)
    subreddit_sentiment = sentiment_analyzer.get_subreddit_sentiment_ranking(reddit_posts)
    viral_predictions = trend_detector.predict_trending_topics(reddit_posts, news_articles)
    
    return sentiment_comparison, trending_topics, subreddit_sentiment, viral_predictions

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Social Pulse Analytics</h1>', unsafe_allow_html=True)
    st.markdown("**Understanding Human Nature Through Social Media Patterns**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Auto-refresh toggle
        auto_refresh = st.toggle("🔄 Auto Refresh (30 min)", value=False)
        
        # Manual refresh button
        if st.button("🔍 Refresh Data Now"):
            st.cache_data.clear()
            st.rerun()
        
        # Data collection status
        st.header("📊 Data Status")
        reddit_df, news_df = load_data()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Reddit Posts", len(reddit_df) if not reddit_df.empty else 0)
        with col2:
            st.metric("News Articles", len(news_df) if not news_df.empty else 0)
        
        # Last update time
        if not reddit_df.empty:
            last_update = reddit_df['collected_at'].max()
            st.caption(f"Last updated: {last_update}")
        
        st.markdown("---")
        st.caption("🚀 Analyzing human behavior patterns across social platforms")
    
    # Check if we have data
    if reddit_df.empty and news_df.empty:
        st.warning("⚠️ No data available. Please collect some data first!")
        
        if st.button("🎯 Collect Data Now"):
            with st.spinner("Collecting data... This may take a few minutes"):
                # Collect Reddit data
                reddit_posts = reddit_collector.collect_all_posts()
                if reddit_posts:
                    analyzed_posts = sentiment_analyzer.analyze_reddit_posts(reddit_posts)
                    db.insert_reddit_posts([post.to_dict() for post in analyzed_posts])
                
                # Collect News data
                news_articles = news_collector.collect_all_articles()
                if news_articles:
                    analyzed_articles = sentiment_analyzer.analyze_news_articles(news_articles)
                    db.insert_news_articles([article.to_dict() for article in analyzed_articles])
                
                st.success("✅ Data collection completed!")
                st.rerun()
        return
    
    # Load analytics data
    sentiment_comparison, trending_topics, subreddit_sentiment, viral_predictions = get_analytics_data()
    
    if not sentiment_comparison:
        st.error("Error processing analytics data")
        return
    
    # Main dashboard layout
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Overview", "📈 Trends", "💭 Sentiment", "🔮 Predictions"])
    
    with tab1:
        show_overview_tab(sentiment_comparison, trending_topics, reddit_df, news_df)
    
    with tab2:
        show_trends_tab(trending_topics, subreddit_sentiment)
    
    with tab3:
        show_sentiment_tab(sentiment_comparison, reddit_df, news_df)
    
    with tab4:
        show_predictions_tab(viral_predictions, trending_topics)
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(1800)  # 30 minutes
        st.rerun()

def show_overview_tab(sentiment_comparison, trending_topics, reddit_df, news_df):
    """Show overview dashboard"""
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Sentiment", 
            f"{sentiment_comparison['comparison']['reddit_avg']:.2f}",
            f"{sentiment_comparison['comparison']['difference']:.2f} vs News"
        )
    
    with col2:
        total_engagement = reddit_df['score'].sum() if 'score' in reddit_df.columns else 0
        st.metric("Total Engagement", f"{total_engagement:,}")
    
    with col3:
        cross_platform_trends = len([t for t in trending_topics if t.reddit_mentions > 0 and t.news_mentions > 0])
        st.metric("Cross-Platform Trends", cross_platform_trends)
    
    with col4:
        hours_covered = 24
        st.metric("Data Coverage", f"{hours_covered}h")
    
    st.markdown("---")
    
    # Real-time pulse chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Social Media Pulse (Last 24h)")
        
        if not reddit_df.empty:
            # Create hourly engagement chart
            reddit_df['hour'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.floor('H')
            hourly_data = reddit_df.groupby('hour').agg({
                'score': 'sum',
                'num_comments': 'sum',
                'sentiment_score': 'mean'
            }).reset_index()
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Engagement Volume', 'Average Sentiment'),
                vertical_spacing=0.1
            )
            
            # Engagement volume
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['score'],
                    mode='lines+markers',
                    name='Upvotes',
                    line=dict(color='#1f77b4')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['num_comments'],
                    mode='lines+markers',
                    name='Comments',
                    line=dict(color='#ff7f0e'),
                    yaxis='y2'
                ),
                row=1, col=1
            )
            
            # Sentiment over time
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['sentiment_score'],
                    mode='lines+markers',
                    name='Sentiment',
                    line=dict(color='#2ca02c')
                ),
                row=2, col=1
            )
            
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hourly data available")
    
    with col2:
        st.subheader("🔥 Top Trending Now")
        
        if trending_topics:
            for i, topic in enumerate(trending_topics[:5]):
                total_mentions = topic.reddit_mentions + topic.news_mentions
                sentiment_emoji = "😊" if topic.sentiment_avg > 0.1 else "😔" if topic.sentiment_avg < -0.1 else "😐"
                
                st.markdown(f"""
                **{i+1}. {topic.keyword}** {sentiment_emoji}
                - 💬 {total_mentions} mentions
                - 📱 Reddit: {topic.reddit_mentions} | 📰 News: {topic.news_mentions}
                """)
        else:
            st.info("No trending topics found")

def show_trends_tab(trending_topics, subreddit_sentiment):
    """Show trending topics analysis"""
    
    st.subheader("🔥 Cross-Platform Trending Topics")
    
    if trending_topics:
        # Create trending topics DataFrame
        trends_data = []
        for topic in trending_topics:
            trends_data.append({
                'Topic': topic.keyword,
                'Reddit Mentions': topic.reddit_mentions,
                'News Mentions': topic.news_mentions,
                'Total Mentions': topic.reddit_mentions + topic.news_mentions,
                'Sentiment': topic.sentiment_avg,
                'Cross-Platform': topic.reddit_mentions > 0 and topic.news_mentions > 0
            })
        
        trends_df = pd.DataFrame(trends_data)
        
        # Trending topics bubble chart
        fig = px.scatter(
            trends_df, 
            x='Reddit Mentions', 
            y='News Mentions',
            size='Total Mentions',
            color='Sentiment',
            hover_name='Topic',
            title="📊 Topics by Platform Coverage",
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0
        )
        
        fig.update_traces(marker=dict(line=dict(width=1, color='black')))
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top trending table
        st.subheader("📋 Trending Topics Details")
        st.dataframe(
            trends_df.sort_values('Total Mentions', ascending=False),
            use_container_width=True
        )
    
    # Subreddit sentiment ranking
    if subreddit_sentiment:
        st.subheader("🏆 Subreddit Sentiment Ranking")
        
        sentiment_df = pd.DataFrame(subreddit_sentiment)
        
        fig = px.bar(
            sentiment_df.head(10), 
            x='avg_sentiment', 
            y='subreddit',
            orientation='h',
            color='avg_sentiment',
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0,
            title="Most Positive vs Negative Subreddits"
        )
        
        fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

def show_sentiment_tab(sentiment_comparison, reddit_df, news_df):
    """Show sentiment analysis"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Platform Sentiment Comparison")
        
        # Sentiment distribution pie charts
        reddit_dist = sentiment_comparison['reddit']['distribution']
        news_dist = sentiment_comparison['news']['distribution']
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type':'domain'}, {'type':'domain'}]],
            subplot_titles=('Reddit Sentiment', 'News Sentiment')
        )
        
        # Reddit pie chart
        fig.add_trace(
            go.Pie(
                labels=['Positive', 'Negative', 'Neutral'],
                values=[reddit_dist['positive'], reddit_dist['negative'], reddit_dist['neutral']],
                name="Reddit",
                marker_colors=['#2ca02c', '#d62728', '#ff7f0e']
            ),
            row=1, col=1
        )
        
        # News pie chart
        fig.add_trace(
            go.Pie(
                labels=['Positive', 'Negative', 'Neutral'],
                values=[news_dist['positive'], news_dist['negative'], news_dist['neutral']],
                name="News",
                marker_colors=['#2ca02c', '#d62728', '#ff7f0e']
            ),
            row=1, col=2
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎭 Sentiment Metrics")
        
        # Sentiment metrics display
        reddit_avg = sentiment_comparison['reddit']['average_score']
        news_avg = sentiment_comparison['news']['average_score']
        
        st.metric("Reddit Average Sentiment", f"{reddit_avg:.3f}")
        st.metric("News Average Sentiment", f"{news_avg:.3f}")
        st.metric("Difference", f"{reddit_avg - news_avg:.3f}")
        
        # Interpretation
        if reddit_avg > news_avg:
            st.success("🌟 Reddit is more positive than news!")
        elif reddit_avg < news_avg:
            st.warning("📰 News is more positive than Reddit")
        else:
            st.info("⚖️ Similar sentiment across platforms")
    
    # Sentiment over time
    if not reddit_df.empty:
        st.subheader("📈 Sentiment Trends Over Time")
        
        reddit_df['hour'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.floor('H')
        hourly_sentiment = reddit_df.groupby('hour')['sentiment_score'].mean().reset_index()
        
        fig = px.line(
            hourly_sentiment, 
            x='hour', 
            y='sentiment_score',
            title="Average Sentiment Over Time",
            color_discrete_sequence=['#1f77b4']
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def show_predictions_tab(viral_predictions, trending_topics):
    """Show prediction and forecasting"""
    
    st.subheader("🔮 Viral Content Predictions")
    
    if viral_predictions:
        pred_df = pd.DataFrame(viral_predictions)
        
        fig = px.bar(
            pred_df.head(10),
            x='viral_potential',
            y='keyword',
            orientation='h',
            color='viral_potential',
            color_continuous_scale='Viridis',
            title="Topics with Highest Viral Potential"
        )
        
        fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(pred_df, use_container_width=True)
    else:
        st.info("No viral predictions available yet")
    
    # Human behavior insights
    st.subheader("🧠 Human Behavior Insights")
    
    if trending_topics:
        cross_platform_count = len([t for t in trending_topics if t.reddit_mentions > 0 and t.news_mentions > 0])
        reddit_only = len([t for t in trending_topics if t.reddit_mentions > 0 and t.news_mentions == 0])
        news_only = len([t for t in trending_topics if t.reddit_mentions == 0 and t.news_mentions > 0])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Cross-Platform Topics", cross_platform_count)
            st.caption("Topics trending on both platforms")
        
        with col2:
            st.metric("Reddit-Only Topics", reddit_only)
            st.caption("Grassroots discussions")
        
        with col3:
            st.metric("News-Only Topics", news_only)
            st.caption("Mainstream media focus")
        
        # Insights
        if cross_platform_count > 0:
            st.success("🌍 Strong cross-platform engagement indicates mainstream topics")
        
        if reddit_only > cross_platform_count:
            st.info("🗣️ Reddit users discussing topics not yet in mainstream news")
        
        if news_only > reddit_only:
            st.warning("📺 Mainstream media covering topics with limited social discussion")

if __name__ == "__main__":
    main()