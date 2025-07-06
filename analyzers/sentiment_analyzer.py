"""
Sentiment analysis for Social Pulse Analytics
Uses VADER sentiment analysis optimized for social media text
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from typing import List, Dict, Any, Tuple
from app.models import RedditPost, NewsArticle, SentimentMetrics

class SentimentAnalyzer:
    """Sentiment analysis engine using VADER and TextBlob"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using both VADER and TextBlob"""
        if not text or not text.strip():
            return {
                'compound': 0.0,
                'vader_score': 0.0,
                'textblob_score': 0.0,
                'final_score': 0.0,
                'confidence': 0.0
            }
        
        # VADER analysis (better for social media)
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # TextBlob analysis (good for formal text)
        try:
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
        except:
            textblob_polarity = 0.0
        
        # Combine scores with VADER weighted higher for social media
        final_score = (vader_compound * 0.7) + (textblob_polarity * 0.3)
        
        # Calculate confidence based on score magnitude
        confidence = abs(final_score)
        
        return {
            'compound': vader_compound,
            'vader_score': vader_compound,
            'textblob_score': textblob_polarity,
            'final_score': final_score,
            'confidence': confidence
        }
    
    def classify_sentiment(self, score: float) -> str:
        """Classify sentiment score into categories"""
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    def analyze_reddit_post(self, post: RedditPost) -> RedditPost:
        """Analyze sentiment and enhanced metrics of a Reddit post"""
        # Import here to avoid circular imports
        from analyzers.content_analyzer import content_analyzer
        from datetime import datetime
        
        # Combine title and selftext for analysis
        text_to_analyze = f"{post.title} {post.selftext}".strip()
        
        # Sentiment analysis
        sentiment_result = self.analyze_text(text_to_analyze)
        post.sentiment_score = sentiment_result['final_score']
        
        # Enhanced content analysis
        curse_analysis = content_analyzer.count_curse_words(text_to_analyze)
        post.curse_word_count = curse_analysis['curse_count']
        
        readability = content_analyzer.calculate_readability_score(text_to_analyze)
        post.readability_score = readability['score']
        
        # Calculate engagement velocity
        hours_old = max((datetime.now().timestamp() - post.created_utc) / 3600, 0.1)
        post.engagement_velocity = (post.score + post.num_comments * 2) / hours_old
        
        # Calculate virality score using content analyzer
        viral_analysis = content_analyzer.analyze_viral_potential(
            post.title,
            post.selftext,
            post.score,
            post.num_comments,
            hours_old
        )
        post.virality_score = viral_analysis['viral_score']
        
        return post
    
    def analyze_reddit_posts(self, posts: List[RedditPost]) -> List[RedditPost]:
        """Analyze sentiment for multiple Reddit posts"""
        analyzed_posts = []
        
        for post in posts:
            try:
                analyzed_post = self.analyze_reddit_post(post)
                analyzed_posts.append(analyzed_post)
            except Exception as e:
                print(f"Error analyzing Reddit post {post.id}: {e}")
                # Keep post with neutral sentiment
                post.sentiment_score = 0.0
                analyzed_posts.append(post)
        
        return analyzed_posts
    
    def analyze_news_article(self, article: NewsArticle) -> NewsArticle:
        """Analyze sentiment and enhanced metrics of a news article"""
        # Import here to avoid circular imports
        from analyzers.content_analyzer import content_analyzer
        
        # Combine title and description for analysis
        text_to_analyze = f"{article.title} {article.description}".strip()
        
        # Sentiment analysis
        sentiment_result = self.analyze_text(text_to_analyze)
        article.sentiment_score = sentiment_result['final_score']
        
        # Enhanced content analysis
        readability = content_analyzer.calculate_readability_score(text_to_analyze)
        article.readability_score = readability['score']
        
        # Word count
        article.word_count = len(text_to_analyze.split())
        
        # Engagement analysis for emotional tone
        engagement = content_analyzer.analyze_engagement_factors(text_to_analyze)
        article.emotional_tone = engagement['emotional_tone']
        
        # Calculate urgency score based on content
        urgent_words = ['breaking', 'urgent', 'alert', 'developing', 'live', 'update']
        urgency_count = sum(1 for word in urgent_words if word in text_to_analyze.lower())
        article.urgency_score = min(urgency_count * 2, 10)  # Scale to 0-10
        
        # Basic credibility score (can be enhanced with ML later)
        credibility_factors = 0
        if article.author and article.author != '':
            credibility_factors += 2
        if len(article.description) > 100:
            credibility_factors += 2
        if article.source in ['Reuters', 'Associated Press', 'BBC', 'NPR']:
            credibility_factors += 4
        elif article.source in ['CNN', 'Fox News', 'MSNBC']:
            credibility_factors += 3
        else:
            credibility_factors += 1
        
        article.credibility_score = min(credibility_factors, 10)
        
        return article
    
    def analyze_news_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Analyze sentiment for multiple news articles"""
        analyzed_articles = []
        
        for article in articles:
            try:
                analyzed_article = self.analyze_news_article(article)
                analyzed_articles.append(analyzed_article)
            except Exception as e:
                print(f"Error analyzing news article: {e}")
                # Keep article with neutral sentiment
                article.sentiment_score = 0.0
                analyzed_articles.append(article)
        
        return analyzed_articles
    
    def get_sentiment_metrics(self, items: List[Any], score_attr: str = 'sentiment_score') -> SentimentMetrics:
        """Calculate sentiment metrics for a collection of items"""
        metrics = SentimentMetrics()
        
        for item in items:
            score = getattr(item, score_attr, 0.0)
            if score is not None:
                metrics.add_sentiment(score)
        
        return metrics
    
    def compare_platform_sentiment(self, reddit_posts: List[RedditPost], 
                                 news_articles: List[NewsArticle]) -> Dict[str, Any]:
        """Compare sentiment between Reddit and news platforms"""
        reddit_metrics = self.get_sentiment_metrics(reddit_posts)
        news_metrics = self.get_sentiment_metrics(news_articles)
        
        return {
            'reddit': reddit_metrics.to_dict(),
            'news': news_metrics.to_dict(),
            'comparison': {
                'reddit_avg': reddit_metrics.average_score,
                'news_avg': news_metrics.average_score,
                'difference': reddit_metrics.average_score - news_metrics.average_score,
                'reddit_more_positive': reddit_metrics.average_score > news_metrics.average_score
            }
        }
    
    def get_sentiment_trends_by_time(self, posts: List[RedditPost], hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get sentiment trends over time"""
        from datetime import datetime, timedelta
        import pandas as pd
        
        # Convert to DataFrame for easier time analysis
        data = []
        for post in posts:
            data.append({
                'timestamp': datetime.fromtimestamp(post.created_utc),
                'sentiment': post.sentiment_score,
                'subreddit': post.subreddit
            })
        
        if not data:
            return []
        
        df = pd.DataFrame(data)
        
        # Group by hour and calculate average sentiment
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_sentiment = df.groupby('hour')['sentiment'].mean().reset_index()
        
        trends = []
        for _, row in hourly_sentiment.iterrows():
            trends.append({
                'hour': row['hour'].strftime('%Y-%m-%d %H:00'),
                'avg_sentiment': round(row['sentiment'], 3),
                'sentiment_label': self.classify_sentiment(row['sentiment'])
            })
        
        return sorted(trends, key=lambda x: x['hour'])
    
    def get_subreddit_sentiment_ranking(self, posts: List[RedditPost]) -> List[Dict[str, Any]]:
        """Get sentiment ranking by subreddit"""
        import pandas as pd
        
        if not posts:
            return []
        
        # Convert to DataFrame
        data = []
        for post in posts:
            data.append({
                'subreddit': post.subreddit,
                'sentiment': post.sentiment_score,
                'score': post.score,
                'comments': post.num_comments
            })
        
        df = pd.DataFrame(data)
        
        # Group by subreddit and calculate metrics
        subreddit_stats = df.groupby('subreddit').agg({
            'sentiment': ['mean', 'count'],
            'score': 'mean',
            'comments': 'mean'
        }).round(3)
        
        # Flatten column names
        subreddit_stats.columns = ['avg_sentiment', 'post_count', 'avg_score', 'avg_comments']
        subreddit_stats = subreddit_stats.reset_index()
        
        # Sort by average sentiment
        subreddit_stats = subreddit_stats.sort_values('avg_sentiment', ascending=False)
        
        ranking = []
        for _, row in subreddit_stats.iterrows():
            ranking.append({
                'subreddit': row['subreddit'],
                'avg_sentiment': row['avg_sentiment'],
                'sentiment_label': self.classify_sentiment(row['avg_sentiment']),
                'post_count': int(row['post_count']),
                'avg_score': row['avg_score'],
                'avg_comments': row['avg_comments']
            })
        
        return ranking

# Global analyzer instance
sentiment_analyzer = SentimentAnalyzer()