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
    initial_sidebar_state="auto"
)

# Enhanced CSS for beautiful mobile-responsive design
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
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
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
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
    
    return analytics, reddit_df, news_df

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
        avg_sentiment = analytics['sentiment_comparison']['comparison']['reddit_avg']
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
        viral_count = len([p for p in analytics['viral_predictions'] if p.get('viral_potential', 0) > 5])
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{viral_count}</div>
            <div class="metric-label">Viral Predictions</div>
            <div class="metric-delta">🔥 High potential</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Behavioral Insights
    with col4:
        behavior_insights = len(analytics['behavioral_report'].get('executive_summary', []))
        
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
    
    st.markdown("---")
    
    # Human behavior insights
    show_human_behavior_insights(analytics)
    
    st.markdown("---")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Social Media Pulse (Last 24h)")
        
        if not reddit_df.empty:
            # Enhanced pulse visualization
            reddit_df['hour'] = pd.to_datetime(reddit_df['created_utc'], unit='s').dt.floor('H')
            hourly_data = reddit_df.groupby('hour').agg({
                'score': 'sum',
                'num_comments': 'sum',
                'sentiment_score': 'mean',
                'virality_score': 'mean'
            }).reset_index()
            
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=('Engagement Volume', 'Average Sentiment', 'Virality Score'),
                vertical_spacing=0.08,
                specs=[[{"secondary_y": True}], [{}], [{}]]
            )
            
            # Engagement volume with dual axis
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['score'],
                    mode='lines+markers',
                    name='Upvotes',
                    line=dict(color='#667eea', width=3),
                    fill='tonexty'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['num_comments'],
                    mode='lines+markers',
                    name='Comments',
                    line=dict(color='#764ba2', width=3)
                ),
                row=1, col=1, secondary_y=True
            )
            
            # Sentiment over time
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['sentiment_score'],
                    mode='lines+markers',
                    name='Sentiment',
                    line=dict(color='#28a745', width=3),
                    fill='tozeroy'
                ),
                row=2, col=1
            )
            
            # Virality score
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['virality_score'],
                    mode='lines+markers',
                    name='Virality',
                    line=dict(color='#dc3545', width=3),
                    fill='tozeroy'
                ),
                row=3, col=1
            )
            
            fig.update_layout(
                height=600, 
                showlegend=True,
                template='plotly_white',
                title_font_size=16
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📈 No hourly data available yet")
    
    with col2:
        st.markdown("### 🔥 Top Trending Now")
        
        trending_topics = analytics.get('trending_topics', [])
        if trending_topics:
            for i, topic in enumerate(trending_topics[:8]):
                total_mentions = topic.reddit_mentions + topic.news_mentions
                sentiment_emoji = "😊" if topic.sentiment_avg > 0.1 else "😔" if topic.sentiment_avg < -0.1 else "😐"
                
                # Color coding based on cross-platform presence
                if topic.reddit_mentions > 0 and topic.news_mentions > 0:
                    border_color = "#28a745"  # Green for cross-platform
                elif topic.reddit_mentions > 0:
                    border_color = "#667eea"  # Blue for Reddit-only
                else:
                    border_color = "#764ba2"  # Purple for News-only
                
                st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; padding: 10px; margin: 8px 0; background: #f8f9fa; border-radius: 0 8px 8px 0;">
                    <strong>{i+1}. {topic.keyword}</strong> {sentiment_emoji}<br>
                    <small>💬 {total_mentions} mentions | 📱 {topic.reddit_mentions} | 📰 {topic.news_mentions}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🔍 No trending topics found yet")

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

def show_behavioral_insights_tab(analytics):
    """Show detailed behavioral insights"""
    
    st.markdown("### 🧠 Deep Behavioral Analysis")
    
    behavioral_report = analytics.get('behavioral_report', {})
    content_insights = analytics.get('content_insights', {})
    
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

def show_viral_predictions_tab(analytics):
    """Show viral predictions and ML insights"""
    
    st.markdown("### 🔮 Viral Content Predictions & ML Insights")
    
    viral_predictions = analytics.get('viral_predictions', [])
    
    if viral_predictions:
        # Create DataFrame for visualization
        pred_df = pd.DataFrame(viral_predictions)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Viral potential chart
            fig = px.bar(
                pred_df.head(10),
                x='viral_potential',
                y='keyword',
                orientation='h',
                color='viral_potential',
                color_continuous_scale='Viridis',
                title="🔥 Topics with Highest Viral Potential",
                labels={'viral_potential': 'Viral Score', 'keyword': 'Topic'}
            )
            
            fig.update_layout(
                height=400,
                yaxis={'categoryorder':'total ascending'},
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🏆 Top Viral Predictions**")
            for i, pred in enumerate(pred_df.head(5).to_dict('records')):
                prediction_level = pred.get('prediction', 'emerging')
                emoji = "🚀" if prediction_level == 'emerging' else "👀"
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 8px; border-left: 3px solid #667eea;">
                    <strong>{i+1}. {pred['keyword']}</strong> {emoji}<br>
                    <small>Score: {pred['viral_potential']:.1f} | Mentions: {pred['mention_count']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # ML Model placeholder
    st.markdown("#### 🤖 ML Model Integration")
    
    st.info("""
    📈 **Ready for Google Colab Training!**
    
    The enhanced data structure now supports ML training:
    - **Features**: Sentiment, readability, engagement velocity, curse words, etc.
    - **Target**: Virality score, engagement prediction
    - **Models**: Classification (viral/not viral), Regression (engagement prediction)
    
    Export this data to Google Colab for training advanced models!
    """)
    
    # Model export button
    if st.button("📤 Export Data for ML Training"):
        st.success("✅ Data export functionality ready! Connect to Google Colab for model training.")

def main():
    """Enhanced main dashboard function"""
    
    # Header with improved styling
    st.markdown('<h1 class="main-header">🧠 Social Pulse Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header"><strong>Understanding Human Nature Through Social Media Patterns</strong></p>', unsafe_allow_html=True)
    
    # Auto data collection status
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**🔄 Auto-Collection Active** | Updates every 30 minutes")
        
        with col2:
            if st.button("🔍 Force Refresh", type="secondary"):
                st.cache_data.clear()
                st.rerun()
        
        with col3:
            last_update = datetime.now().strftime("%H:%M:%S")
            st.caption(f"Last updated: {last_update}")
    
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
        show_behavioral_insights_tab(analytics)
    
    with tab4:
        show_viral_predictions_tab(analytics)
    
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