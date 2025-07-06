"""
Correlation analysis engine for Social Pulse Analytics
Analyzes relationships between Reddit discussions and news coverage
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import re

from app.models import RedditPost, NewsArticle, TrendingTopic

class CorrelationEngine:
    """Engine for analyzing correlations between platforms"""
    
    def __init__(self):
        self.common_words = {
            'ai', 'artificial intelligence', 'machine learning', 'bitcoin', 'crypto', 'cryptocurrency',
            'climate', 'environment', 'tesla', 'spacex', 'twitter', 'meta', 'facebook', 'google',
            'apple', 'microsoft', 'amazon', 'netflix', 'ukraine', 'russia', 'china', 'election',
            'covid', 'vaccine', 'inflation', 'economy', 'stocks', 'market', 'technology', 'science',
            'research', 'breakthrough', 'innovation', 'startup', 'ipo', 'earnings', 'gaming',
            'iphone', 'android', 'cybersecurity', 'blockchain', 'nft', 'metaverse', 'space'
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def extract_keywords(self, text: str) -> set:
        """Extract normalized keywords from text"""
        normalized = self.normalize_text(text)
        words = set(normalized.split())
        
        # Filter out common stop words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = {word for word in words if len(word) > 2 and word not in stop_words}
        
        return keywords
    
    def find_topic_overlap(self, reddit_posts: List[RedditPost], 
                          news_articles: List[NewsArticle]) -> Dict[str, Any]:
        """Find overlapping topics between Reddit and news"""
        
        # Extract keywords from Reddit posts
        reddit_keywords = defaultdict(list)
        for post in reddit_posts:
            text = f"{post.title} {post.selftext}"
            keywords = self.extract_keywords(text)
            
            for keyword in keywords:
                reddit_keywords[keyword].append({
                    'post_id': post.id,
                    'score': post.score,
                    'comments': post.num_comments,
                    'sentiment': post.sentiment_score,
                    'subreddit': post.subreddit,
                    'created_utc': post.created_utc
                })
        
        # Extract keywords from news articles
        news_keywords = defaultdict(list)
        for article in news_articles:
            text = f"{article.title} {article.description}"
            keywords = self.extract_keywords(text)
            
            for keyword in keywords:
                news_keywords[keyword].append({
                    'title': article.title,
                    'source': article.source,
                    'sentiment': article.sentiment_score,
                    'published_at': article.published_at
                })
        
        # Find overlapping keywords
        reddit_set = set(reddit_keywords.keys())
        news_set = set(news_keywords.keys())
        overlap = reddit_set & news_set
        
        overlap_analysis = {
            'total_reddit_keywords': len(reddit_set),
            'total_news_keywords': len(news_set),
            'overlapping_keywords': len(overlap),
            'overlap_percentage': (len(overlap) / len(reddit_set | news_set)) * 100 if reddit_set | news_set else 0,
            'reddit_only': len(reddit_set - news_set),
            'news_only': len(news_set - reddit_set),
            'overlap_details': {}
        }
        
        # Analyze overlapping topics in detail
        for keyword in list(overlap)[:20]:  # Top 20 overlapping keywords
            reddit_data = reddit_keywords[keyword]
            news_data = news_keywords[keyword]
            
            reddit_sentiment = np.mean([item['sentiment'] for item in reddit_data])
            news_sentiment = np.mean([item['sentiment'] for item in news_data])
            
            overlap_analysis['overlap_details'][keyword] = {
                'reddit_mentions': len(reddit_data),
                'news_mentions': len(news_data),
                'reddit_sentiment': reddit_sentiment,
                'news_sentiment': news_sentiment,
                'sentiment_correlation': abs(reddit_sentiment - news_sentiment),
                'total_reddit_engagement': sum(item['score'] + item['comments'] for item in reddit_data)
            }
        
        return overlap_analysis
    
    def analyze_timing_correlation(self, reddit_posts: List[RedditPost], 
                                 news_articles: List[NewsArticle]) -> Dict[str, Any]:
        """Analyze timing patterns between Reddit discussions and news coverage"""
        
        # Convert to DataFrames for easier time analysis
        reddit_data = []
        for post in reddit_posts:
            reddit_data.append({
                'timestamp': datetime.fromtimestamp(post.created_utc),
                'keywords': ' '.join(self.extract_keywords(f"{post.title} {post.selftext}")),
                'sentiment': post.sentiment_score,
                'engagement': post.score + post.num_comments,
                'platform': 'reddit'
            })
        
        news_data = []
        for article in news_articles:
            try:
                timestamp = pd.to_datetime(article.published_at)
                news_data.append({
                    'timestamp': timestamp,
                    'keywords': ' '.join(self.extract_keywords(f"{article.title} {article.description}")),
                    'sentiment': article.sentiment_score,
                    'engagement': 1,  # News articles don't have engagement scores
                    'platform': 'news'
                })
            except:
                continue
        
        if not reddit_data or not news_data:
            return {'error': 'Insufficient data for timing analysis'}
        
        # Combine data
        all_data = reddit_data + news_data
        df = pd.DataFrame(all_data)
        
        # Group by hour to analyze patterns
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_stats = df.groupby(['hour', 'platform']).agg({
            'sentiment': 'mean',
            'engagement': 'sum'
        }).unstack(fill_value=0)
        
        timing_analysis = {
            'peak_reddit_hour': None,
            'peak_news_hour': None,
            'sentiment_lag': 0,
            'hourly_correlation': {}
        }
        
        if not hourly_stats.empty:
            # Find peak activity hours
            reddit_engagement = hourly_stats[('engagement', 'reddit')]
            news_engagement = hourly_stats[('engagement', 'news')]
            
            if not reddit_engagement.empty:
                timing_analysis['peak_reddit_hour'] = reddit_engagement.idxmax().strftime('%H:00')
            if not news_engagement.empty:
                timing_analysis['peak_news_hour'] = news_engagement.idxmax().strftime('%H:00')
            
            # Calculate correlation between platform activities
            if len(reddit_engagement) > 1 and len(news_engagement) > 1:
                correlation = np.corrcoef(reddit_engagement.fillna(0), news_engagement.fillna(0))[0, 1]
                timing_analysis['activity_correlation'] = correlation if not np.isnan(correlation) else 0
        
        return timing_analysis
    
    def detect_prediction_patterns(self, reddit_posts: List[RedditPost], 
                                 news_articles: List[NewsArticle]) -> Dict[str, Any]:
        """Detect if Reddit discussions predict news coverage"""
        
        # Sort posts by time
        reddit_posts.sort(key=lambda x: x.created_utc)
        
        prediction_patterns = {
            'reddit_first_topics': [],
            'simultaneous_topics': [],
            'news_first_topics': [],
            'prediction_accuracy': 0
        }
        
        # Group Reddit posts by keywords and time
        reddit_keywords_by_time = defaultdict(list)
        for post in reddit_posts:
            hour = datetime.fromtimestamp(post.created_utc).replace(minute=0, second=0, microsecond=0)
            keywords = self.extract_keywords(f"{post.title} {post.selftext}")
            
            for keyword in keywords:
                if keyword in self.common_words:  # Focus on important topics
                    reddit_keywords_by_time[keyword].append(hour)
        
        # Group news articles by keywords and time
        news_keywords_by_time = defaultdict(list)
        for article in news_articles:
            try:
                timestamp = pd.to_datetime(article.published_at)
                hour = timestamp.replace(minute=0, second=0, microsecond=0)
                keywords = self.extract_keywords(f"{article.title} {article.description}")
                
                for keyword in keywords:
                    if keyword in self.common_words:
                        news_keywords_by_time[keyword].append(hour)
            except:
                continue
        
        # Find prediction patterns
        predicted_count = 0
        total_comparisons = 0
        
        for keyword in set(reddit_keywords_by_time.keys()) & set(news_keywords_by_time.keys()):
            reddit_times = reddit_keywords_by_time[keyword]
            news_times = news_keywords_by_time[keyword]
            
            if reddit_times and news_times:
                earliest_reddit = min(reddit_times)
                earliest_news = min(news_times)
                
                time_diff = (earliest_news - earliest_reddit).total_seconds() / 3600  # Hours
                
                total_comparisons += 1
                
                if time_diff > 2:  # Reddit was at least 2 hours earlier
                    prediction_patterns['reddit_first_topics'].append({
                        'keyword': keyword,
                        'hours_ahead': round(time_diff, 1),
                        'reddit_first': earliest_reddit.strftime('%Y-%m-%d %H:%M'),
                        'news_first': earliest_news.strftime('%Y-%m-%d %H:%M')
                    })
                    predicted_count += 1
                elif abs(time_diff) <= 2:  # Simultaneous (within 2 hours)
                    prediction_patterns['simultaneous_topics'].append({
                        'keyword': keyword,
                        'time_diff': round(time_diff, 1)
                    })
                else:  # News was first
                    prediction_patterns['news_first_topics'].append({
                        'keyword': keyword,
                        'hours_ahead': round(abs(time_diff), 1)
                    })
        
        if total_comparisons > 0:
            prediction_patterns['prediction_accuracy'] = (predicted_count / total_comparisons) * 100
        
        return prediction_patterns
    
    def calculate_sentiment_correlation(self, reddit_posts: List[RedditPost], 
                                      news_articles: List[NewsArticle]) -> Dict[str, Any]:
        """Calculate sentiment correlation between platforms"""
        
        if not reddit_posts or not news_articles:
            return {'error': 'Insufficient data'}
        
        # Get sentiment scores
        reddit_sentiments = [post.sentiment_score for post in reddit_posts if post.sentiment_score is not None]
        news_sentiments = [article.sentiment_score for article in news_articles if article.sentiment_score is not None]
        
        if not reddit_sentiments or not news_sentiments:
            return {'error': 'No sentiment data available'}
        
        correlation_analysis = {
            'reddit_avg_sentiment': np.mean(reddit_sentiments),
            'news_avg_sentiment': np.mean(news_sentiments),
            'reddit_sentiment_std': np.std(reddit_sentiments),
            'news_sentiment_std': np.std(news_sentiments),
            'overall_correlation': 0,
            'sentiment_difference': 0
        }
        
        # Calculate overall difference
        correlation_analysis['sentiment_difference'] = correlation_analysis['reddit_avg_sentiment'] - correlation_analysis['news_avg_sentiment']
        
        # Try to calculate correlation if we have enough data points
        if len(reddit_sentiments) > 1 and len(news_sentiments) > 1:
            # For correlation, we need paired data - match by keywords or time
            paired_sentiments = self._get_paired_sentiments(reddit_posts, news_articles)
            
            if len(paired_sentiments) > 1:
                reddit_paired = [pair[0] for pair in paired_sentiments]
                news_paired = [pair[1] for pair in paired_sentiments]
                
                correlation = np.corrcoef(reddit_paired, news_paired)[0, 1]
                correlation_analysis['overall_correlation'] = correlation if not np.isnan(correlation) else 0
        
        return correlation_analysis
    
    def _get_paired_sentiments(self, reddit_posts: List[RedditPost], 
                              news_articles: List[NewsArticle]) -> List[Tuple[float, float]]:
        """Get paired sentiment scores for topics mentioned in both platforms"""
        
        paired_sentiments = []
        
        # Group by keywords
        reddit_by_keyword = defaultdict(list)
        for post in reddit_posts:
            keywords = self.extract_keywords(f"{post.title} {post.selftext}")
            for keyword in keywords:
                if keyword in self.common_words:
                    reddit_by_keyword[keyword].append(post.sentiment_score)
        
        news_by_keyword = defaultdict(list)
        for article in news_articles:
            keywords = self.extract_keywords(f"{article.title} {article.description}")
            for keyword in keywords:
                if keyword in self.common_words:
                    news_by_keyword[keyword].append(article.sentiment_score)
        
        # Find paired sentiments
        for keyword in set(reddit_by_keyword.keys()) & set(news_by_keyword.keys()):
            reddit_avg = np.mean(reddit_by_keyword[keyword])
            news_avg = np.mean(news_by_keyword[keyword])
            paired_sentiments.append((reddit_avg, news_avg))
        
        return paired_sentiments
    
    def generate_correlation_report(self, reddit_posts: List[RedditPost], 
                                  news_articles: List[NewsArticle]) -> Dict[str, Any]:
        """Generate comprehensive correlation analysis report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'data_summary': {
                'reddit_posts': len(reddit_posts),
                'news_articles': len(news_articles),
                'time_range': '24 hours'
            }
        }
        
        try:
            # Topic overlap analysis
            report['topic_overlap'] = self.find_topic_overlap(reddit_posts, news_articles)
            
            # Timing correlation
            report['timing_analysis'] = self.analyze_timing_correlation(reddit_posts, news_articles)
            
            # Prediction patterns
            report['prediction_patterns'] = self.detect_prediction_patterns(reddit_posts, news_articles)
            
            # Sentiment correlation
            report['sentiment_correlation'] = self.calculate_sentiment_correlation(reddit_posts, news_articles)
            
            # Summary insights
            report['insights'] = self._generate_insights(report)
            
        except Exception as e:
            report['error'] = str(e)
        
        return report
    
    def _generate_insights(self, report: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights from correlation analysis"""
        
        insights = []
        
        try:
            # Topic overlap insights
            overlap = report.get('topic_overlap', {})
            if overlap.get('overlap_percentage', 0) > 20:
                insights.append(f"Strong topic overlap: {overlap['overlap_percentage']:.1f}% of topics are discussed on both platforms")
            elif overlap.get('overlap_percentage', 0) > 10:
                insights.append(f"Moderate topic overlap: {overlap['overlap_percentage']:.1f}% of topics span both platforms")
            else:
                insights.append("Limited topic overlap - platforms focus on different subjects")
            
            # Prediction insights
            prediction = report.get('prediction_patterns', {})
            if prediction.get('prediction_accuracy', 0) > 50:
                insights.append(f"Reddit often predicts news: {prediction['prediction_accuracy']:.1f}% accuracy")
            elif len(prediction.get('reddit_first_topics', [])) > 0:
                insights.append(f"Reddit discusses {len(prediction['reddit_first_topics'])} topics before news coverage")
            
            # Sentiment insights
            sentiment = report.get('sentiment_correlation', {})
            if abs(sentiment.get('sentiment_difference', 0)) > 0.2:
                if sentiment['sentiment_difference'] > 0:
                    insights.append("Reddit users are significantly more positive than news coverage")
                else:
                    insights.append("News coverage is more positive than Reddit discussions")
            else:
                insights.append("Reddit and news sentiment are closely aligned")
            
        except Exception as e:
            insights.append(f"Analysis error: {str(e)}")
        
        return insights

# Global correlation engine instance
correlation_engine = CorrelationEngine()