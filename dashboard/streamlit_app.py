"""
Enhanced Streamlit dashboard for Social Pulse Analytics
Beautiful, mobile-responsive dashboard with advanced behavioral insights
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import time
import numpy as np

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
from analyzers.content_analyzer import content_analyzer
from analyzers.behaviour_analyzer import behavioral_analyzer

# Page configuration
st.set_page_config(
    page_title="Social Pulse Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for beautiful mobile-responsive design
st.markdown("""
<style>
    /* Remove default Streamlit padding */
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        max-width: 100%;
    }
    
    /* Main styling */
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    
    /* Enhanced metrics */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }
    
    /* Insight cards */
    .insight-card {
        background: white;
        border-left: 5px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .insight-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .insight-text {
        color: #666;
        line-height: 1.5;
    }
    
    /* Status indicators */
    .status-good { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-danger { color: #dc3545; }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main-header { font-size: 2rem; }
        .metric-value { font-size: 2rem; }
        .metric-container { padding: 1rem; }
    }
    
    /* Chart containers with reduced spacing */
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Reduced spacing between sections */
    .section-spacer {
        margin: 1.5rem 0;
    }
    
    /* Tabs styling with enhanced background color */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, rgba(255, 87, 34, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%);
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(255, 87, 34, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        padding: 0.7rem 1.2rem;
        font-weight: 600;
        color: #ff5722;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #ff5722 0%, #ff9800 100%);
        color: white !important;
        border: 2px solid #ff5722;
        box-shadow: 0 4px 8px rgba(255, 87, 34, 0.3);
    }
    
    /* Enhanced section headers with orange-red colors */
    .section-header {
        font-size: 1.6rem;
        font-weight: bold;
        color: #ff5722 !important;
        margin-bottom: 1.2rem;
        padding: 0.6rem 0;
        border-bottom: 3px solid #ff5722 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Viral section headers with distinct styling */
    .viral-section-header {
        font-size: 1.4rem;
        font-weight: bold;
        color: #ff5722 !important;
        margin: 1.5rem 0 1rem 0;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, rgba(255, 87, 34, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%);
        border-left: 5px solid #ff5722;
        border-radius: 0 10px 10px 0;
    }
    
    /* Trending posts styling with enhanced orange-red colors */
    .trending-container {
        background: linear-gradient(135deg, rgba(255, 87, 34, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        border: 2px solid rgba(255, 87, 34, 0.2);
    }
    
    .trending-card {
        background: rgba(255, 255, 255, 0.9);
        border-left: 5px solid #ff5722;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
        padding: 16px;
        box-shadow: 0 3px 10px rgba(255, 87, 34, 0.15);
        transition: transform 0.2s ease;
    }
    
    .trending-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(255, 87, 34, 0.25);
    }
    
    .trending-title {
        color: #d84315 !important;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }
    
    .trending-meta {
        color: #bf360c !important;
        font-size: 0.95rem;
    }
    
    /* Viral predictions list styling */
    .viral-list-item {
        background: linear-gradient(135deg, rgba(255, 87, 34, 0.1) 0%, rgba(255, 193, 7, 0.1) 100%);
        border-left: 5px solid #ff5722;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
        padding: 16px 20px;
        box-shadow: 0 3px 10px rgba(255, 87, 34, 0.1);
        transition: all 0.2s ease;
    }
    
    .viral-list-item:hover {
        transform: translateX(3px);
        box-shadow: 0 5px 15px rgba(255, 87, 34, 0.2);
    }
    
    .viral-list-title {
        color: #ff5722 !important;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 6px;
    }
    
    .viral-list-meta {
        color: #e64a19 !important;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* Real-time indicators enhanced styling */
    .realtime-indicator {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(139, 195, 74, 0.15) 100%);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #4caf50;
        border: 2px solid rgba(76, 175, 80, 0.2);
    }
    
    /* Timeline enhanced styling */
    .timeline-container {
        background: linear-gradient(135deg, rgba(156, 39, 176, 0.12) 0%, rgba(103, 58, 183, 0.12) 100%);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid rgba(156, 39, 176, 0.2);
    }
    
    /* Post card styling */
    .post-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .post-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .post-meta {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Auto-refresh functionality
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

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
def get_enhanced_analytics_data():
    """Get comprehensive analytics data with behavioral insights"""
    reddit_df, news_df = load_data()
    
    if reddit_df.empty and news_df.empty:
        return None
    
    # Convert to model objects
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
    
    # Get comprehensive analytics
    analytics = {}
    
    # Basic analytics
    analytics['sentiment_comparison'] = sentiment_analyzer.compare_platform_sentiment(reddit_posts, news_articles)
    analytics['trending_topics'] = trend_detector.find_cross_platform_trends(reddit_posts, news_articles)
    analytics['subreddit_sentiment'] = sentiment_analyzer.get_subreddit_sentiment_ranking(reddit_posts)
    analytics['viral_predictions'] = trend_detector.predict_trending_topics(reddit_posts, news_articles)
    
    # Enhanced behavioral analytics
    analytics['behavioral_report'] = behavioral_analyzer.generate_comprehensive_behavioral_report(reddit_posts, news_articles)
    analytics['content_insights'] = content_analyzer.generate_content_insights([post.to_dict() for post in reddit_posts])
    
    # Add sample posts for sentiment analysis
    analytics['sample_posts'] = {
        'most_positive': get_extreme_sentiment_posts(reddit_posts, 'positive'),
        'most_negative': get_extreme_sentiment_posts(reddit_posts, 'negative')
    }
    
    return analytics, reddit_df, news_df

def get_extreme_sentiment_posts(posts, sentiment_type='positive'):
    """Get most positive or negative posts"""
    if not posts:
        return []
    
    if sentiment_type == 'positive':
        sorted_posts = sorted(posts, key=lambda x: x.sentiment_score, reverse=True)
    else:
        sorted_posts = sorted(posts, key=lambda x: x.sentiment_score)
    
    return sorted_posts[:5]  # Top 5

def show_enhanced_metrics(analytics, reddit_df, news_df):
    """Show enhanced key metrics with beautiful styling"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Engagement
    with col1:
        total_engagement = reddit_df['score'].sum() if 'score' in reddit_df.columns else 0
        engagement_delta = f"+{int(total_engagement * 0.1)}" if total_engagement > 0 else "0"
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_engagement:,}</div>
            <div class="metric-label">Total Engagement</div>
            <div class="metric-delta">📈 {engagement_delta}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sentiment Score
    with col2:
        try:
            avg_sentiment = analytics.get('sentiment_comparison', {}).get('comparison', {}).get('reddit_avg', 0)
        except:
            avg_sentiment = 0
        
        sentiment_emoji = "😊" if avg_sentiment > 0.1 else "😔" if avg_sentiment < -0.1 else "😐"
        sentiment_color = "#28a745" if avg_sentiment > 0 else "#dc3545" if avg_sentiment < -0.1 else "#ffc107"
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{avg_sentiment:.2f} {sentiment_emoji}</div>
            <div class="metric-label">Avg Sentiment</div>
            <div class="metric-delta" style="color: {sentiment_color};">Reddit vs News</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Viral Content
    with col3:
        try:
            viral_predictions = analytics.get('viral_predictions', [])
            viral_count = len([p for p in viral_predictions if p.get('viral_potential', 0) > 5])
        except:
            viral_count = 0
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{viral_count}</div>
            <div class="metric-label">Viral Predictions</div>
            <div class="metric-delta">🔥 High potential</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Behavioral Insights
    with col4:
        try:
            behavior_insights = len(analytics.get('behavioral_report', {}).get('executive_summary', []))
        except:
            behavior_insights = 0
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{behavior_insights}</div>
            <div class="metric-label">Behavior Insights</div>
            <div class="metric-delta">🧠 Human patterns</div>
        </div>
        """, unsafe_allow_html=True)

def show_human_behavior_insights(analytics):
    """Show key human behavior insights"""
    
    st.markdown("### 🧠 Human Behavior Insights")
    
    behavioral_report = analytics.get('behavioral_report', {})
    executive_summary = behavioral_report.get('executive_summary', [])
    
    if executive_summary:
        for insight in executive_summary:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-text">{insight}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔍 Collecting behavioral data... More insights will appear as data accumulates.")

def show_overview_tab(analytics, reddit_df, news_df):
    """Enhanced overview dashboard"""
    
    # Enhanced metrics
    show_enhanced_metrics(analytics, reddit_df, news_df)
    
    # Add spacing
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # Human behavior insights
    show_human_behavior_insights(analytics)
    
    # Add spacing
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # Main content area with better spacing
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown('<div class="section-header">📊 Social Media Pulse (Last 24h)</div>', unsafe_allow_html=True)
        
        if not reddit_df.empty:
            # Enhanced pulse visualization with containers
            reddit_df['hour'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.floor('H')
            hourly_data = reddit_df.groupby('hour').agg({
                'score': 'sum',
                'num_comments': 'sum',
                'sentiment_score': 'mean',
                'virality_score': 'mean'
            }).reset_index()
            
            # Create three separate charts with spacing
            st.markdown("#### 📈 Engagement Volume")
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig1.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['score'],
                    mode='lines+markers',
                    name='Upvotes',
                    line=dict(color='#667eea', width=3),
                    fill='tonexty'
                )
            )
            
            fig1.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['num_comments'],
                    mode='lines+markers',
                    name='Comments',
                    line=dict(color='#764ba2', width=3)
                ),
                secondary_y=True
            )
            
            fig1.update_layout(height=300, template='plotly_white', showlegend=True)
            fig1.update_yaxes(title_text="Upvotes", secondary_y=False)
            fig1.update_yaxes(title_text="Comments", secondary_y=True)
            
            st.plotly_chart(fig1, use_container_width=True)
            
            # Add spacing between charts
            st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
            
            # Sentiment chart
            st.markdown("#### 💭 Average Sentiment")
            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['sentiment_score'],
                    mode='lines+markers',
                    name='Sentiment',
                    line=dict(color='#28a745', width=3),
                    fill='tozeroy'
                )
            )
            fig2.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
            fig2.update_layout(height=300, template='plotly_white')
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Add spacing between charts
            st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
            
            # Virality chart
            st.markdown("#### 🚀 Virality Score")
            fig3 = go.Figure()
            fig3.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['virality_score'],
                    mode='lines+markers',
                    name='Virality',
                    line=dict(color='#dc3545', width=3),
                    fill='tozeroy'
                )
            )
            fig3.update_layout(height=300, template='plotly_white')
            
            st.plotly_chart(fig3, use_container_width=True)
            
        else:
            st.info("📈 No hourly data available yet")
    
    with col2:
        st.markdown('<div class="section-header">🔥 Top Trending Now</div>', unsafe_allow_html=True)
        
        # Get top posts from Reddit data instead of just topics
        if not reddit_df.empty:
            st.markdown('<div class="trending-container">', unsafe_allow_html=True)
            
            # Sort by engagement (score + comments) and get top posts
            reddit_df['total_engagement'] = reddit_df['score'] + reddit_df['num_comments']
            top_posts = reddit_df.nlargest(8, 'total_engagement')
            
            for i, (_, post) in enumerate(top_posts.iterrows()):
                sentiment_emoji = "😊" if post['sentiment_score'] > 0.1 else "😔" if post['sentiment_score'] < -0.1 else "😐"
                
                # Color coding based on subreddit activity
                if post['total_engagement'] > 1000:
                    border_color = "#ff5722"  # Orange-red for high engagement
                elif post['total_engagement'] > 500:
                    border_color = "#ff9800"  # Orange for medium engagement
                else:
                    border_color = "#ffeb3b"  # Yellow for normal engagement
                
                # Truncate title if too long
                title = post['title'][:60] + "..." if len(post['title']) > 60 else post['title']
                
                st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; padding: 12px; margin: 10px 0; background: rgba(255, 255, 255, 0.8); border-radius: 0 8px 8px 0; color: #333;">
                    <strong style="color: #d84315;">{i+1}. {title}</strong> {sentiment_emoji}<br>
                    <small style="color: #bf360c;">⬆️ {post['score']} | 💬 {post['num_comments']} | r/{post['subreddit']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("🔍 No trending posts found yet")
    
    # Add comprehensive overview insights
    st.markdown("---")
    st.markdown("### 📊 Platform Analytics Overview")
    
    if not reddit_df.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📈 Engagement Patterns**")
            
            # Calculate engagement statistics
            total_posts = len(reddit_df)
            total_upvotes = reddit_df['score'].sum()
            total_comments = reddit_df['num_comments'].sum()
            avg_engagement = (reddit_df['score'] + reddit_df['num_comments']).mean()
            
            # Time-based patterns
            reddit_df['hour'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.hour
            peak_hour = reddit_df.groupby('hour')['score'].sum().idxmax()
            peak_engagement = reddit_df.groupby('hour')['score'].sum().max()
            
            st.write(f"• Total posts analyzed: {total_posts:,}")
            st.write(f"• Total upvotes: {total_upvotes:,}")
            st.write(f"• Total comments: {total_comments:,}")
            st.write(f"• Avg engagement/post: {avg_engagement:.1f}")
            st.write(f"• Peak activity hour: {peak_hour}:00")
            st.write(f"• Peak engagement: {peak_engagement:,}")
        
        with col2:
            st.markdown("**🏆 Community Insights**")
            
            # Community analysis
            community_stats = reddit_df.groupby('subreddit').agg({
                'score': ['sum', 'mean', 'count'],
                'num_comments': 'sum',
                'sentiment_score': 'mean'
            }).round(2)
            
            community_stats.columns = ['total_score', 'avg_score', 'post_count', 'total_comments', 'avg_sentiment']
            community_stats = community_stats[community_stats['post_count'] >= 3].sort_values('total_score', ascending=False)
            
            # Most active community
            most_active = community_stats.index[0]
            most_engaging = community_stats.sort_values('avg_score', ascending=False).index[0]
            most_positive = community_stats.sort_values('avg_sentiment', ascending=False).index[0]
            
            st.write(f"• Most active: r/{most_active}")
            st.write(f"  ({community_stats.loc[most_active, 'post_count']} posts)")
            st.write(f"• Highest avg engagement: r/{most_engaging}")
            st.write(f"  ({community_stats.loc[most_engaging, 'avg_score']:.0f} points)")
            st.write(f"• Most positive: r/{most_positive}")
            st.write(f"  ({community_stats.loc[most_positive, 'avg_sentiment']:.2f} sentiment)")
            
            # Community diversity
            unique_communities = len(community_stats)
            st.write(f"• Communities tracked: {unique_communities}")
        
        with col3:
            st.markdown("**🎯 Content Performance**")
            
            # Content analysis
            reddit_df['title_length'] = reddit_df['title'].str.len()
            reddit_df['total_engagement'] = reddit_df['score'] + reddit_df['num_comments']
            
            # Performance metrics
            viral_threshold = reddit_df['total_engagement'].quantile(0.9)
            viral_posts = len(reddit_df[reddit_df['total_engagement'] > viral_threshold])
            low_performance = len(reddit_df[reddit_df['total_engagement'] < reddit_df['total_engagement'].quantile(0.1)])
            
            avg_title_length = reddit_df['title_length'].mean()
            optimal_length_posts = reddit_df.groupby(pd.cut(reddit_df['title_length'], bins=5))['total_engagement'].mean()
            best_length_range = optimal_length_posts.idxmax()
            
            avg_sentiment = reddit_df['sentiment_score'].mean()
            positive_posts = len(reddit_df[reddit_df['sentiment_score'] > 0.1])
            negative_posts = len(reddit_df[reddit_df['sentiment_score'] < -0.1])
            
            st.write(f"• Viral posts (top 10%): {viral_posts}")
            st.write(f"• Poor performers: {low_performance}")
            st.write(f"• Avg title length: {avg_title_length:.0f} chars")
            st.write(f"• Optimal length: {best_length_range}")
            st.write(f"• Platform sentiment: {avg_sentiment:.3f}")
            st.write(f"• Positive ratio: {positive_posts/total_posts:.1%}")
        
        # Additional insights section
        st.markdown("#### 🔍 Advanced Platform Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⏰ Temporal Patterns**")
            
            # Day of week analysis
            reddit_df['day_of_week'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.day_name()
            daily_engagement = reddit_df.groupby('day_of_week')['total_engagement'].mean().sort_values(ascending=False)
            
            st.write("**Best days for engagement:**")
            for i, (day, engagement) in enumerate(daily_engagement.head(3).items()):
                st.write(f"{i+1}. {day}: {engagement:.0f} avg engagement")
            
            # Hourly distribution
            hourly_posts = reddit_df.groupby('hour').size()
            busiest_hours = hourly_posts.sort_values(ascending=False).head(3)
            
            st.write(f"\n**Busiest posting hours:**")
            for hour, count in busiest_hours.items():
                st.write(f"• {hour}:00 - {count} posts")
        
        with col2:
            st.markdown("**🎭 Content Characteristics**")
            
            # Engagement velocity
            reddit_df['hours_old'] = (datetime.now().timestamp() - reddit_df['created_utc']) / 3600
            reddit_df['velocity'] = reddit_df['total_engagement'] / (reddit_df['hours_old'] + 0.1)
            
            fastest_growing = reddit_df.nlargest(3, 'velocity')[['title', 'subreddit', 'velocity']]
            
            st.write("**🚀 Fastest growing content:**")
            for i, (_, post) in enumerate(fastest_growing.iterrows()):
                title = post['title'][:50] + "..." if len(str(post['title'])) > 50 else post['title']
                st.write(f"{i+1}. {title}")
                st.write(f"   r/{post['subreddit']} • {post['velocity']:.1f}/hr")
            
            # Comment engagement patterns
            high_discussion = reddit_df[reddit_df['num_comments'] > reddit_df['num_comments'].quantile(0.8)]
            if len(high_discussion) > 0:
                discussion_communities = high_discussion['subreddit'].value_counts().head(3)
                st.write(f"\n**💬 Most discussion-heavy:**")
                for subreddit, count in discussion_communities.items():
                    st.write(f"• r/{subreddit}: {count} high-discussion posts")
    else:
        st.info("📊 No data available for platform analytics")

def show_sentiment_analysis_tab(analytics, reddit_df):
    """Enhanced sentiment analysis with behavioral insights"""
    
    st.markdown("### 💭 Sentiment vs Virality Analysis")
    
    # Sentiment-Virality correlation
    behavioral_report = analytics.get('behavioral_report', {})
    sentiment_virality = behavioral_report.get('sentiment_virality', {})
    
    if sentiment_virality and 'key_insights' in sentiment_virality:
        insights = sentiment_virality['key_insights']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Negative Sentiment Viral Rate",
                f"{insights.get('negative_sentiment_viral_rate', 0):.1f}%",
                help="Percentage of negative posts that go viral"
            )
        
        with col2:
            st.metric(
                "Positive Sentiment Viral Rate", 
                f"{insights.get('positive_sentiment_viral_rate', 0):.1f}%",
                help="Percentage of positive posts that go viral"
            )
        
        with col3:
            controversy_indicator = "🔥" if insights.get('controversy_breeds_engagement', False) else "✨"
            st.metric(
                "Controversy Effect",
                controversy_indicator,
                "Negative content drives more engagement" if insights.get('controversy_breeds_engagement', False) else "Positive content performs better"
            )
    
    st.markdown("---")
    
    # Platform sentiment comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Platform Sentiment Distribution")
        
        sentiment_comparison = analytics.get('sentiment_comparison', {})
        if sentiment_comparison:
            reddit_dist = sentiment_comparison['reddit']['distribution']
            news_dist = sentiment_comparison['news']['distribution']
            
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{'type':'domain'}, {'type':'domain'}]],
                subplot_titles=('Reddit Sentiment', 'News Sentiment')
            )
            
            colors = ['#28a745', '#dc3545', '#ffc107']  # Green, Red, Yellow
            
            fig.add_trace(
                go.Pie(
                    labels=['Positive', 'Negative', 'Neutral'],
                    values=[reddit_dist['positive'], reddit_dist['negative'], reddit_dist['neutral']],
                    name="Reddit",
                    marker_colors=colors,
                    hole=0.4
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Pie(
                    labels=['Positive', 'Negative', 'Neutral'],
                    values=[news_dist['positive'], news_dist['negative'], news_dist['neutral']],
                    name="News",
                    marker_colors=colors,
                    hole=0.4
                ),
                row=1, col=2
            )
            
            fig.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Sentiment Over Time")
        
        if not reddit_df.empty and 'sentiment_score' in reddit_df.columns:
            reddit_df['hour'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.floor('H')
            hourly_sentiment = reddit_df.groupby('hour')['sentiment_score'].agg(['mean', 'std']).reset_index()
            
            fig = go.Figure()
            
            # Add mean line
            fig.add_trace(go.Scatter(
                x=hourly_sentiment['hour'],
                y=hourly_sentiment['mean'],
                mode='lines+markers',
                name='Average Sentiment',
                line=dict(color='#667eea', width=3)
            ))
            
            # Add confidence band
            fig.add_trace(go.Scatter(
                x=hourly_sentiment['hour'],
                y=hourly_sentiment['mean'] + hourly_sentiment['std'],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=hourly_sentiment['hour'],
                y=hourly_sentiment['mean'] - hourly_sentiment['std'],
                mode='lines',
                line=dict(width=0),
                fillcolor='rgba(102, 126, 234, 0.2)',
                fill='tonexty',
                showlegend=False,
                name='Confidence Band'
            ))
            
            fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
            fig.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
    
    # Add spacing
    st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
    
    # Display most positive and negative posts in table format
    st.markdown("### 📝 Sentiment Analysis - Top Posts")
    
    if not reddit_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 😊 Most Positive Posts")
            # Get most positive posts from dataframe
            positive_posts = reddit_df.nlargest(5, 'sentiment_score')[['title', 'subreddit', 'score', 'num_comments', 'sentiment_score', 'url']]
            
            for i, (_, post) in enumerate(positive_posts.iterrows()):
                title = post['title'][:60] + "..." if len(str(post['title'])) > 60 else post['title']
                st.markdown(f"""
                <div class="post-card">
                    <div class="post-title">{i+1}. {title}</div>
                    <div class="post-meta">
                        💚 Sentiment: {post['sentiment_score']:.2f} | ⬆️ {post['score']} | 💬 {post['num_comments']} | r/{post['subreddit']}<br>
                        <a href="{post['url']}" target="_blank">🔗 View Post</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 😔 Most Negative Posts")
            # Get most negative posts from dataframe
            negative_posts = reddit_df.nsmallest(5, 'sentiment_score')[['title', 'subreddit', 'score', 'num_comments', 'sentiment_score', 'url']]
            
            for i, (_, post) in enumerate(negative_posts.iterrows()):
                title = post['title'][:60] + "..." if len(str(post['title'])) > 60 else post['title']
                st.markdown(f"""
                <div class="post-card">
                    <div class="post-title">{i+1}. {title}</div>
                    <div class="post-meta">
                        💔 Sentiment: {post['sentiment_score']:.2f} | ⬆️ {post['score']} | 💬 {post['num_comments']} | r/{post['subreddit']}<br>
                        <a href="{post['url']}" target="_blank">🔗 View Post</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No post data available for sentiment analysis")
    
    # Add comprehensive data-driven insights
    st.markdown("---")
    st.markdown("### 📊 Sentiment Analysis Insights")
    
    if not reddit_df.empty:
        # Calculate sentiment insights
        total_posts = len(reddit_df)
        avg_sentiment = reddit_df['sentiment_score'].mean()
        sentiment_std = reddit_df['sentiment_score'].std()
        positive_posts_count = len(reddit_df[reddit_df['sentiment_score'] > 0.1])
        negative_posts_count = len(reddit_df[reddit_df['sentiment_score'] < -0.1])
        
        # Subreddit sentiment analysis
        subreddit_sentiment = reddit_df.groupby('subreddit').agg({
            'sentiment_score': ['mean', 'count'],
            'score': 'mean'
        }).round(3)
        subreddit_sentiment.columns = ['avg_sentiment', 'post_count', 'avg_score']
        subreddit_sentiment = subreddit_sentiment[subreddit_sentiment['post_count'] >= 3].sort_values('avg_sentiment', ascending=False)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🏆 Most Positive Communities**")
            top_positive = subreddit_sentiment.head(5)
            for subreddit, data in top_positive.iterrows():
                st.write(f"r/{subreddit}: {data['avg_sentiment']:.2f} ({int(data['post_count'])} posts)")
        
        with col2:
            st.markdown("**😤 Most Negative Communities**")
            top_negative = subreddit_sentiment.tail(5)
            for subreddit, data in top_negative.iterrows():
                st.write(f"r/{subreddit}: {data['avg_sentiment']:.2f} ({int(data['post_count'])} posts)")
        
        with col3:
            st.markdown("**📈 Key Sentiment Facts**")
            st.write(f"• Average sentiment: {avg_sentiment:.3f}")
            st.write(f"• Sentiment volatility: {sentiment_std:.3f}")
            st.write(f"• Positive posts: {positive_posts_count} ({positive_posts_count/total_posts*100:.1f}%)")
            st.write(f"• Negative posts: {negative_posts_count} ({negative_posts_count/total_posts*100:.1f}%)")
            
            # Time-based sentiment insight
            if 'created_utc' in reddit_df.columns:
                reddit_df['hour'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.hour
                hourly_sentiment = reddit_df.groupby('hour')['sentiment_score'].mean()
                most_positive_hour = hourly_sentiment.idxmax()
                most_negative_hour = hourly_sentiment.idxmin()
                st.write(f"• Most positive hour: {most_positive_hour}:00")
                st.write(f"• Most negative hour: {most_negative_hour}:00")

def show_behavioral_insights_tab(analytics, reddit_df):
    """Show detailed behavioral insights with enhanced statistics"""
    
    st.markdown("### 🧠 Deep Behavioral Analysis")
    
    behavioral_report = analytics.get('behavioral_report', {})
    content_insights = analytics.get('content_insights', {})
    
    # Enhanced statistical insights section
    st.markdown("#### 📊 Content Length & Engagement Analysis")
    
    if not reddit_df.empty:
        # Calculate content statistics
        reddit_df['title_length'] = reddit_df['title'].str.len()
        reddit_df['total_engagement'] = reddit_df['score'] + reddit_df['num_comments']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_title_length = reddit_df['title_length'].mean()
            st.metric(
                "Avg Title Length",
                f"{avg_title_length:.0f} chars",
                help="Average character count in post titles"
            )
        
        with col2:
            # Find optimal title length for engagement
            reddit_df['length_bin'] = pd.cut(reddit_df['title_length'], bins=5, labels=['Very Short', 'Short', 'Medium', 'Long', 'Very Long'])
            avg_engagement_by_length = reddit_df.groupby('length_bin')['total_engagement'].mean()
            optimal_length = avg_engagement_by_length.idxmax()
            st.metric(
                "Optimal Title Length",
                f"{optimal_length}",
                help="Title length category with highest average engagement"
            )
        
        with col3:
            # Sentiment-performance correlation
            correlation = reddit_df[['sentiment_score', 'total_engagement']].corr().iloc[0, 1]
            correlation_strength = "Strong" if abs(correlation) > 0.5 else "Moderate" if abs(correlation) > 0.3 else "Weak"
            st.metric(
                "Sentiment-Engagement",
                f"{correlation:.2f}",
                f"{correlation_strength} correlation",
                help="Correlation between sentiment and engagement"
            )
        
        with col4:
            # Viral threshold
            viral_threshold = reddit_df['total_engagement'].quantile(0.9)
            viral_posts = (reddit_df['total_engagement'] > viral_threshold).sum()
            st.metric(
                "Viral Posts (Top 10%)",
                f"{viral_posts}",
                f">{viral_threshold:.0f} engagement",
                help="Posts in top 10% of engagement"
            )
        
        # Engagement distribution chart
        st.markdown("#### 📈 Engagement Distribution by Title Length")
        
        fig = px.box(
            reddit_df, 
            x='length_bin', 
            y='total_engagement',
            title="Post Engagement by Title Length Category",
            labels={'total_engagement': 'Total Engagement (Score + Comments)', 'length_bin': 'Title Length Category'}
        )
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment vs Engagement scatter plot
        st.markdown("#### 💭 Sentiment vs Engagement Correlation")
        
        fig = px.scatter(
            reddit_df.sample(min(500, len(reddit_df))),  # Sample for performance
            x='sentiment_score',
            y='total_engagement',
            color='subreddit',
            title="Sentiment Score vs Total Engagement",
            labels={'sentiment_score': 'Sentiment Score', 'total_engagement': 'Total Engagement'}
        )
        fig.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text="Neutral Sentiment")
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    # Profanity insights
    if content_insights and 'profanity_insights' in content_insights:
        st.markdown("#### 🤬 Language & Profanity Analysis")
        
        prof_insights = content_insights['profanity_insights']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Posts with Profanity",
                f"{prof_insights.get('percentage_with_profanity', 0):.1f}%"
            )
        
        with col2:
            st.metric(
                "Avg Curse Words/Post",
                f"{prof_insights.get('avg_curse_words_per_post', 0):.1f}"
            )
        
        with col3:
            st.metric(
                "Max Curse Words",
                f"{prof_insights.get('max_curse_words', 0)}"
            )
        
        with col4:
            sample_size = content_insights.get('sample_size', 0)
            st.metric(
                "Sample Size",
                f"{sample_size} posts"
            )
    
    # Subreddit behavior patterns
    if 'subreddit_patterns' in behavioral_report:
        st.markdown("#### 🏛️ Subreddit Behavior Patterns")
        
        subreddit_patterns = behavioral_report['subreddit_patterns']
        rankings = subreddit_patterns.get('rankings', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🤬 Most Profane Communities**")
            most_profane = rankings.get('most_profane', [])
            for i, (subreddit, data) in enumerate(most_profane[:5]):
                st.write(f"{i+1}. r/{subreddit} - {data['avg_profanity']:.1f} curse words/post")
        
        with col2:
            st.markdown("**✨ Cleanest Communities**")
            cleanest = rankings.get('cleanest_language', [])
            for i, (subreddit, data) in enumerate(cleanest[:5]):
                st.write(f"{i+1}. r/{subreddit} - {data['avg_profanity']:.1f} curse words/post")
    
        # Engagement factors
    if 'engagement_factors' in behavioral_report:
        st.markdown("#### 🎯 What Makes Posts More Engaging")
        
        engagement_factors = behavioral_report['engagement_factors']
        key_insights = engagement_factors.get('key_insights', [])
        
        for insight in key_insights:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-text">💡 {insight}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Add comprehensive behavioral data insights
    st.markdown("---")
    st.markdown("### 📊 Advanced Behavioral Data Insights")
    
    if not reddit_df.empty:
        # Calculate advanced metrics
        reddit_df['total_engagement'] = reddit_df['score'] + reddit_df['num_comments']
        reddit_df['comment_rate'] = reddit_df['num_comments'] / reddit_df['score'].replace(0, 1)
        reddit_df['title_length'] = reddit_df['title'].str.len()
        
        # Time-based analysis
        reddit_df['hour'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.hour
        reddit_df['day_of_week'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.day_name()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**⏰ Optimal Posting Times**")
            hourly_engagement = reddit_df.groupby('hour')['total_engagement'].mean().sort_values(ascending=False)
            best_hours = hourly_engagement.head(3)
            st.write("**Best hours to post:**")
            for hour, engagement in best_hours.items():
                st.write(f"• {hour}:00 - Avg engagement: {engagement:.0f}")
            
            st.write("\n**Day of week analysis:**")
            daily_engagement = reddit_df.groupby('day_of_week')['total_engagement'].mean().sort_values(ascending=False)
            best_day = daily_engagement.index[0]
            worst_day = daily_engagement.index[-1]
            st.write(f"• Best day: {best_day} ({daily_engagement.iloc[0]:.0f} avg)")
            st.write(f"• Worst day: {worst_day} ({daily_engagement.iloc[-1]:.0f} avg)")
        
        with col2:
            st.markdown("**📝 Content Length Insights**")
            
            # Title length analysis
            reddit_df['length_category'] = pd.cut(reddit_df['title_length'], 
                                                bins=[0, 50, 100, 150, 300], 
                                                labels=['Short', 'Medium', 'Long', 'Very Long'])
            length_engagement = reddit_df.groupby('length_category')['total_engagement'].mean()
            optimal_length = length_engagement.idxmax()
            
            st.write("**Title length performance:**")
            for category, engagement in length_engagement.items():
                emoji = "🏆" if category == optimal_length else "📊"
                st.write(f"• {emoji} {category}: {engagement:.0f} avg engagement")
            
            # Comment to upvote ratio insights
            avg_comment_rate = reddit_df['comment_rate'].mean()
            high_discussion_threshold = reddit_df['comment_rate'].quantile(0.8)
            controversial_posts = len(reddit_df[reddit_df['comment_rate'] > high_discussion_threshold])
            
            st.write(f"\n**Discussion patterns:**")
            st.write(f"• Avg comment rate: {avg_comment_rate:.2f}")
            st.write(f"• High-discussion posts: {controversial_posts}")
        
        with col3:
            st.markdown("**🏆 Community Performance**")
            
            # Subreddit performance analysis
            subreddit_stats = reddit_df.groupby('subreddit').agg({
                'total_engagement': ['mean', 'sum', 'count'],
                'comment_rate': 'mean',
                'sentiment_score': 'mean'
            }).round(2)
            
            subreddit_stats.columns = ['avg_engagement', 'total_engagement', 'post_count', 'avg_comment_rate', 'avg_sentiment']
            subreddit_stats = subreddit_stats[subreddit_stats['post_count'] >= 3].sort_values('avg_engagement', ascending=False)
            
            st.write("**Top performing communities:**")
            top_communities = subreddit_stats.head(5)
            for subreddit, data in top_communities.iterrows():
                st.write(f"• r/{subreddit}: {data['avg_engagement']:.0f} avg")
            
            # Engagement distribution
            viral_threshold = reddit_df['total_engagement'].quantile(0.9)
            viral_posts = len(reddit_df[reddit_df['total_engagement'] > viral_threshold])
            low_engagement = len(reddit_df[reddit_df['total_engagement'] < reddit_df['total_engagement'].quantile(0.1)])
            
            st.write(f"\n**Engagement distribution:**")
            st.write(f"• Viral posts (top 10%): {viral_posts}")
            st.write(f"• Low engagement (bottom 10%): {low_engagement}")
            st.write(f"• Viral threshold: {viral_threshold:.0f} points")
        
        # Advanced insights section
        st.markdown("#### 🔍 Deep Behavioral Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Correlation analysis
            st.markdown("**📈 Correlation Analysis**")
            correlations = reddit_df[['sentiment_score', 'total_engagement', 'title_length', 'comment_rate']].corr()['total_engagement'].sort_values(ascending=False)
            
            st.write("**Factors most correlated with engagement:**")
            for factor, corr in correlations.items():
                if factor != 'total_engagement':
                    strength = "Strong" if abs(corr) > 0.5 else "Moderate" if abs(corr) > 0.3 else "Weak"
                    direction = "positive" if corr > 0 else "negative"
                    st.write(f"• {factor}: {corr:.3f} ({strength} {direction})")
        
        with col2:
            # Engagement velocity patterns
            st.markdown("**⚡ Engagement Velocity Insights**")
            reddit_df['hours_old'] = (datetime.now().timestamp() - reddit_df['created_utc']) / 3600
            reddit_df['velocity'] = reddit_df['total_engagement'] / (reddit_df['hours_old'] + 0.1)
            
            velocity_stats = reddit_df['velocity'].describe()
            high_velocity_posts = len(reddit_df[reddit_df['velocity'] > reddit_df['velocity'].quantile(0.9)])
            
            st.write(f"• Average velocity: {velocity_stats['mean']:.1f} points/hour")
            st.write(f"• Fastest growing: {velocity_stats['max']:.1f} points/hour")
            st.write(f"• High-velocity posts: {high_velocity_posts}")
            
            # Find fastest growing posts
            fastest_posts = reddit_df.nlargest(3, 'velocity')[['title', 'subreddit', 'velocity']]
            st.write("\n**🚀 Fastest growing posts:**")
            for i, (_, post) in enumerate(fastest_posts.iterrows()):
                title = post['title'][:40] + "..." if len(str(post['title'])) > 40 else post['title']
                st.write(f"{i+1}. {title} ({post['velocity']:.1f}/hr)")
    else:
        st.info("📊 No data available for advanced behavioral analysis")

def show_viral_predictions_tab(analytics, reddit_df):
    """Show viral predictions as styled lists with enhanced colors and export at bottom"""
    
    # 🏆 Top Viral Predictions Section
    st.markdown('<div class="viral-section-header">🏆 Top Viral Predictions</div>', unsafe_allow_html=True)
    
    viral_predictions = analytics.get('viral_predictions', [])
    
    if viral_predictions:
        pred_df = pd.DataFrame(viral_predictions)
        
        # Display as a styled list instead of graph
        for i, pred in enumerate(pred_df.head(10).to_dict('records')):
            prediction_level = pred.get('prediction', 'emerging')
            emoji = "🚀" if prediction_level == 'emerging' else "👀" if prediction_level == 'trending' else "⭐"
            
            st.markdown(f"""
            <div class="viral-list-item">
                <div class="viral-list-title">{i+1}. {pred['keyword']} {emoji}</div>
                <div class="viral-list-meta">
                    Viral Score: <strong>{pred['viral_potential']:.1f}</strong> | 
                    Mentions: <strong>{pred['mention_count']}</strong> | 
                    Prediction: <strong style="color: #ff5722;">{prediction_level.title()}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔍 No viral predictions available. Run analytics to generate predictions.")
    
    # ⚡ Real-Time Viral Indicators Section
    st.markdown('<div class="viral-section-header">⚡ Real-Time Viral Indicators</div>', unsafe_allow_html=True)
    
    if not reddit_df.empty:
        # Calculate viral indicators
        reddit_df['engagement_rate'] = (reddit_df['num_comments'] / reddit_df['score'].replace(0, 1)).fillna(0)
        reddit_df['recency_hours'] = (datetime.now().timestamp() - reddit_df['created_utc']) / 3600
        reddit_df['velocity'] = reddit_df['score'] / (reddit_df['recency_hours'] + 1)
        
        # Get posts with high viral potential (last 12 hours only)
        potential_viral = reddit_df[
            (reddit_df['velocity'] > reddit_df['velocity'].quantile(0.8)) &
            (reddit_df['recency_hours'] < 12)
        ].nlargest(8, 'velocity')
        
        if not potential_viral.empty:
            for i, (_, post) in enumerate(potential_viral.iterrows()):
                title = post['title'][:75] + "..." if len(post['title']) > 75 else post['title']
                
                # Determine confidence level
                if post['velocity'] > reddit_df['velocity'].quantile(0.95):
                    confidence = "High"
                    confidence_color = "#4caf50"
                    confidence_emoji = "🔥"
                elif post['velocity'] > reddit_df['velocity'].quantile(0.9):
                    confidence = "Medium"
                    confidence_color = "#ff9800"
                    confidence_emoji = "�"
                else:
                    confidence = "Emerging"
                    confidence_color = "#ff5722"
                    confidence_emoji = "📈"
                
                st.markdown(f"""
                <div class="viral-list-item">
                    <div class="viral-list-title">{i+1}. {title} {confidence_emoji}</div>
                    <div class="viral-list-meta">
                        Velocity: <strong>{post['velocity']:.1f}/hr</strong> | 
                        Age: <strong>{post['recency_hours']:.1f}h</strong> | 
                        Confidence: <strong style="color: {confidence_color};">{confidence}</strong> | 
                        <span style="color: #ff5722; font-weight: bold;">r/{post['subreddit']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("� No high-velocity posts detected in the last 12 hours")
    else:
        st.warning("📊 No Reddit data available for real-time analysis")
    
    # 📈 Viral Content Timeline Section
    st.markdown('<div class="viral-section-header">📈 Viral Content Timeline</div>', unsafe_allow_html=True)
    
    if not reddit_df.empty:
        reddit_df['total_engagement'] = reddit_df['score'] + reddit_df['num_comments']
        viral_threshold = reddit_df['total_engagement'].quantile(0.9)
        viral_posts = reddit_df[reddit_df['total_engagement'] > viral_threshold]
        
        if len(viral_posts) > 0:
            viral_timeline = viral_posts.copy()
            viral_timeline['datetime'] = pd.to_datetime(viral_timeline['created_utc'], unit='s')
            viral_timeline = viral_timeline.sort_values('datetime', ascending=False)
            recent_viral = viral_timeline.head(8)[['title', 'subreddit', 'total_engagement', 'sentiment_score', 'datetime']]
            
            for i, (_, post) in enumerate(recent_viral.iterrows()):
                title = post['title'][:80] + "..." if len(str(post['title'])) > 80 else post['title']
                time_str = post['datetime'].strftime('%m/%d %H:%M')
                
                st.markdown(f"""
                <div class="viral-list-item">
                    <div class="viral-list-title">{i+1}. {title} 🔥</div>
                    <div class="viral-list-meta">
                        Engagement: <strong>{post['total_engagement']}</strong> | 
                        Sentiment: <strong>{post['sentiment_score']:.2f}</strong> | 
                        <span style="color: #ff5722; font-weight: bold;">r/{post['subreddit']}</span> | 
                        {time_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🔍 No viral posts found for timeline.")
    else:
        st.warning("📊 No data available for timeline analysis")
    
    # Export section moved to bottom
    st.markdown("---")
    st.markdown('<div class="viral-section-header">📤 Machine Learning Export</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **Ready for Advanced Analysis!**
        
        Export your data for:
        - Custom machine learning models
        - Google Colab analysis
        - External visualization tools
        - Academic research
        
        Data includes: sentiment scores, engagement metrics, temporal patterns, and behavioral insights.
        """)
    
    with col2:
        if st.button("📊 Export Dataset", type="primary"):
            # Generate export data
            if not reddit_df.empty:
                export_data = reddit_df[['title', 'subreddit', 'score', 'num_comments', 'sentiment_score', 'created_utc', 'url']].copy()
                
                # Add calculated features
                export_data['total_engagement'] = export_data['score'] + export_data['num_comments']
                export_data['title_length'] = export_data['title'].str.len()
                export_data['engagement_rate'] = export_data['num_comments'] / export_data['score'].replace(0, 1)
                
                csv_data = export_data.to_csv(index=False)
                
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"social_pulse_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.success("✅ Dataset ready for download!")
            else:
                st.warning("No data available for export")
    
    # Add comprehensive viral prediction insights
    st.markdown("---")
    st.markdown("### 🔍 Advanced Viral Pattern Analysis")
    
    if not reddit_df.empty:
        # Calculate comprehensive viral metrics
        reddit_df['total_engagement'] = reddit_df['score'] + reddit_df['num_comments']
        reddit_df['hours_old'] = (datetime.now().timestamp() - reddit_df['created_utc']) / 3600
        reddit_df['velocity'] = reddit_df['total_engagement'] / (reddit_df['hours_old'] + 0.1)
        reddit_df['comment_rate'] = reddit_df['num_comments'] / reddit_df['score'].replace(0, 1)
        reddit_df['title_length'] = reddit_df['title'].str.len()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🎯 Viral Characteristics Analysis**")
            
            # Define viral threshold (top 10% of posts)
            viral_threshold = reddit_df['total_engagement'].quantile(0.9)
            viral_posts = reddit_df[reddit_df['total_engagement'] > viral_threshold]
            normal_posts = reddit_df[reddit_df['total_engagement'] <= viral_threshold]
            
            if len(viral_posts) > 0:
                viral_avg_length = viral_posts['title_length'].mean()
                normal_avg_length = normal_posts['title_length'].mean()
                viral_avg_sentiment = viral_posts['sentiment_score'].mean()
                normal_avg_sentiment = normal_posts['sentiment_score'].mean()
                viral_avg_comment_rate = viral_posts['comment_rate'].mean()
                normal_avg_comment_rate = normal_posts['comment_rate'].mean()
                
                st.write("**Viral vs Normal Posts:**")
                st.write(f"• Title length: {viral_avg_length:.0f} vs {normal_avg_length:.0f} chars")
                st.write(f"• Sentiment: {viral_avg_sentiment:.3f} vs {normal_avg_sentiment:.3f}")
                st.write(f"• Comment rate: {viral_avg_comment_rate:.2f} vs {normal_avg_comment_rate:.2f}")
                
                # Most viral subreddits
                viral_subreddits = viral_posts['subreddit'].value_counts().head(3)
                st.write(f"\n**🏆 Most viral communities:**")
                for subreddit, count in viral_subreddits.items():
                    percentage = (count / len(viral_posts)) * 100
                    st.write(f"• r/{subreddit}: {count} posts ({percentage:.1f}%)")
        
        with col2:
            st.markdown("**⚡ Real-Time Trending Indicators**")
            
            # Recent high-velocity posts (last 6 hours)
            recent_posts = reddit_df[reddit_df['hours_old'] <= 6]
            if len(recent_posts) > 0:
                high_velocity = recent_posts[recent_posts['velocity'] > recent_posts['velocity'].quantile(0.8)]
                
                st.write(f"**🚀 Trending now ({len(high_velocity)} posts):**")
                trending_now = high_velocity.nlargest(5, 'velocity')[['title', 'subreddit', 'velocity', 'total_engagement']]
                
                for i, (_, post) in enumerate(trending_now.iterrows()):
                    title = post['title'][:35] + "..." if len(str(post['title'])) > 35 else post['title']
                    st.write(f"{i+1}. {title}")
                    st.write(f"   r/{post['subreddit']} • {post['velocity']:.1f}/hr • {post['total_engagement']:.0f} total")
                    st.write("")
                
                # Velocity distribution insights
                avg_velocity = recent_posts['velocity'].mean()
                max_velocity = recent_posts['velocity'].max()
                st.write(f"**Velocity stats (6hr window):**")
                st.write(f"• Average: {avg_velocity:.1f} points/hour")
                st.write(f"• Peak: {max_velocity:.1f} points/hour")
            else:
                st.write("No recent posts to analyze")
        
        with col3:
            st.markdown("**🔮 Virality Prediction Factors**")
            
            # Calculate prediction accuracy metrics
            reddit_df['predicted_viral'] = (
                (reddit_df['velocity'] > reddit_df['velocity'].quantile(0.8)) &
                (reddit_df['hours_old'] <= 12) &
                (reddit_df['sentiment_score'].abs() > 0.1)
            )
            
            actual_viral = reddit_df['total_engagement'] > viral_threshold
            predicted_viral = reddit_df['predicted_viral']
            
            # Confusion matrix values
            true_positives = sum(actual_viral & predicted_viral)
            false_positives = sum(~actual_viral & predicted_viral)
            true_negatives = sum(~actual_viral & ~predicted_viral)
            false_negatives = sum(actual_viral & ~predicted_viral)
            
            if (true_positives + false_positives) > 0:
                precision = true_positives / (true_positives + false_positives)
                recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
                accuracy = (true_positives + true_negatives) / len(reddit_df)
                
                st.write("**🎯 Prediction Performance:**")
                st.write(f"• Accuracy: {accuracy:.1%}")
                st.write(f"• Precision: {precision:.1%}")
                st.write(f"• Recall: {recall:.1%}")
            
            # Key viral indicators
            st.write(f"\n**📊 Key Viral Indicators:**")
            velocity_threshold = reddit_df['velocity'].quantile(0.8)
            sentiment_threshold = reddit_df['sentiment_score'].abs().quantile(0.7)
            
            st.write(f"• Velocity > {velocity_threshold:.1f}/hr")
            st.write(f"• |Sentiment| > {sentiment_threshold:.2f}")
            st.write(f"• Age < 12 hours")
            st.write(f"• High comment engagement")
            
            # Success stories
            if len(viral_posts) > 0:
                success_rate_by_subreddit = (viral_posts.groupby('subreddit').size() / 
                                           reddit_df.groupby('subreddit').size() * 100).sort_values(ascending=False)
                top_success_rate = success_rate_by_subreddit.head(3)
                
                st.write(f"\n**🏅 Highest viral success rates:**")
                for subreddit, rate in top_success_rate.items():
                    if rate > 10:  # Only show meaningful rates
                        st.write(f"• r/{subreddit}: {rate:.0f}%")
        
        # Viral prediction timeline
        st.markdown("#### 📈 Viral Content Timeline")
        
        if len(viral_posts) > 0:
            # Create timeline of viral posts
            viral_timeline = viral_posts.copy()
            viral_timeline['datetime'] = pd.to_datetime(viral_timeline['created_utc'], unit='s')
            viral_timeline = viral_timeline.sort_values('datetime')
            
            # Show recent viral posts
            recent_viral = viral_timeline.tail(10)[['title', 'subreddit', 'total_engagement', 'sentiment_score', 'datetime']]
            
            st.write("**🔥 Recent Viral Posts:**")
            for i, (_, post) in enumerate(recent_viral.iterrows()):
                title = post['title'][:80] + "..." if len(str(post['title'])) > 80 else post['title']
                time_str = post['datetime'].strftime("%m/%d %H:%M")
                sentiment_emoji = "😊" if post['sentiment_score'] > 0.1 else "😔" if post['sentiment_score'] < -0.1 else "😐"
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 8px; border-left: 3px solid #28a745;">
                    <strong>{i+1}. {title}</strong> {sentiment_emoji}<br>
                    <small>r/{post['subreddit']} • {post['total_engagement']:.0f} engagement • {time_str}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📊 No data available for viral pattern analysis")

def main():
    """Enhanced main dashboard function"""
    
    # Header with improved styling
    st.markdown('<h1 class="main-header">🧠 Social Pulse Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header"><strong>Understanding Human Nature Through Social Media Patterns</strong></p>', unsafe_allow_html=True)
    
    # Auto data collection status with better spacing
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        # Check if scheduler is running
        scheduler_status = "🟢 Active" if hasattr(st.session_state, 'scheduler_running') and st.session_state.scheduler_running else "🟡 Manual"
        next_update = datetime.now() + timedelta(minutes=30)
        st.markdown(f"**🔄 Auto-Collection: {scheduler_status}** | Updates every 30 minutes | Next: {next_update.strftime('%H:%M')}")
    
    with col2:
        if st.button("🔍 Force Refresh", type="secondary"):
            # Clear all cached data
            st.cache_data.clear()
            
            # Show refresh status
            with st.spinner("🔄 Refreshing data..."):
                # Force new data collection
                try:
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
                    
                    st.success("✅ Data refreshed successfully!")
                    time.sleep(1)  # Brief pause to show success message
                    
                except Exception as e:
                    st.error(f"❌ Refresh failed: {e}")
            
            # Rerun the app to show new data
            st.rerun()
    
    with col3:
        # Start/Stop scheduler button
        if st.button("⚡ Auto-Collect", type="primary"):
            try:
                from collectors.scheduler import DataCollectionScheduler
                if not hasattr(st.session_state, 'scheduler'):
                    st.session_state.scheduler = DataCollectionScheduler()
                
                if not st.session_state.get('scheduler_running', False):
                    st.session_state.scheduler.start()
                    st.session_state.scheduler_running = True
                    st.success("🟢 Auto-collection started!")
                else:
                    st.session_state.scheduler.stop()
                    st.session_state.scheduler_running = False
                    st.info("🟡 Auto-collection stopped!")
                    
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to toggle auto-collection: {e}")
    
    with col4:
        last_update = datetime.now().strftime("%H:%M:%S")
        data_age = "Fresh" if st.session_state.get('last_refresh') and (datetime.now() - st.session_state.last_refresh).seconds < 1800 else "Cached"
        st.caption(f"Updated: {last_update}")
        st.caption(f"Data: {data_age}")
    
    # Add spacing
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # Check for data and auto-collect if needed
    reddit_df, news_df = load_data()
    
    if reddit_df.empty and news_df.empty:
        st.warning("⚠️ No data available. Collecting initial data...")
        
        with st.spinner("🚀 Collecting data... This will take 2-3 minutes"):
            # Auto-collect data
            try:
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
                
            except Exception as e:
                st.error(f"❌ Data collection failed: {e}")
                st.stop()
    
    # Load analytics data
    analytics_result = get_enhanced_analytics_data()
    
    if not analytics_result:
        st.error("❌ Error processing analytics data")
        st.stop()
    
    analytics, reddit_df, news_df = analytics_result
    
    # Enhanced tabbed interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Overview", 
        "💭 Sentiment Analysis", 
        "🧠 Behavioral Insights", 
        "🔮 Viral Predictions"
    ])
    
    with tab1:
        show_overview_tab(analytics, reddit_df, news_df)
    
    with tab2:
        show_sentiment_analysis_tab(analytics, reddit_df)
    
    with tab3:
        show_behavioral_insights_tab(analytics, reddit_df)
    
    with tab4:
        show_viral_predictions_tab(analytics, reddit_df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        🧠 <strong>Social Pulse Analytics</strong> - Understanding human nature through data<br>
        <small>Analyzing patterns across Reddit & News • Powered by ML & Behavioral Science</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()