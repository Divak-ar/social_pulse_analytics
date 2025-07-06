import re
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set, Tuple
from app.models import RedditPost, NewsArticle, TrendingTopic

class TrendDetector:
    """Trend detection and analysis engine"""
    
    def __init__(self):
        # Common stop words to filter out
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'its', 'our', 'their', 'just', 'now', 'then', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'get', 'got',
            'make', 'made', 'take', 'come', 'go', 'know', 'think', 'see', 'want', 'use', 'find', 'give',
            'tell', 'ask', 'work', 'seem', 'feel', 'try', 'leave', 'call', 'reddit', 'post', 'comment',
            'article', 'news', 'says', 'said', 'new', 'first', 'last', 'long', 'great', 'little', 'own',
            'good', 'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important',
            'public', 'bad', 'same', 'able'
        }
        
        # Technology and current affairs keywords that are always relevant
        self.priority_keywords = {
            'ai', 'artificial intelligence', 'machine learning', 'chatgpt', 'openai', 'bitcoin', 'crypto',
            'climate', 'tesla', 'spacex', 'twitter', 'meta', 'google', 'apple', 'microsoft', 'amazon',
            'ukraine', 'russia', 'china', 'election', 'covid', 'vaccine', 'inflation', 'economy',
            'stocks', 'market', 'technology', 'science', 'research', 'breakthrough', 'innovation'
        }
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract meaningful keywords from text"""
        if not text:
            return []
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = text.split()
        
        # Filter keywords
        keywords = []
        for word in words:
            word = word.strip()
            if (len(word) >= min_length and 
                word not in self.stop_words and 
                word.isalpha() and
                not word.isdigit()):
                keywords.append(word)
        
        return keywords
    
    def extract_phrases(self, text: str, max_phrase_length: int = 3) -> List[str]:
        """Extract meaningful phrases from text"""
        if not text:
            return []
        
        words = self.extract_keywords(text)
        phrases = []
        
        # Generate phrases of different lengths
        for i in range(len(words)):
            for phrase_len in range(1, min(max_phrase_length + 1, len(words) - i + 1)):
                phrase = ' '.join(words[i:i + phrase_len])
                if phrase_len == 1 or phrase_len > 1:  # Single words or multi-word phrases
                    phrases.append(phrase)
        
        return phrases
    
    def get_reddit_trending_topics(self, posts: List[RedditPost], top_n: int = 20) -> List[Tuple[str, int, float]]:
        """Extract trending topics from Reddit posts"""
        keyword_data = {}  # {keyword: {'count': int, 'total_score': int, 'total_comments': int}}
        
        for post in posts:
            # Extract keywords from title and selftext
            text = f"{post.title} {post.selftext}"
            keywords = self.extract_keywords(text)
            phrases = self.extract_phrases(text, max_phrase_length=2)
            
            all_terms = keywords + phrases
            
            for term in all_terms:
                if term not in keyword_data:
                    keyword_data[term] = {'count': 0, 'total_score': 0, 'total_comments': 0, 'sentiment_scores': []}
                
                keyword_data[term]['count'] += 1
                keyword_data[term]['total_score'] += post.score
                keyword_data[term]['total_comments'] += post.num_comments
                keyword_data[term]['sentiment_scores'].append(post.sentiment_score)
        
        # Calculate trending scores
        trending_topics = []
        for term, data in keyword_data.items():
            if data['count'] < 2:  # Filter out terms mentioned less than 2 times
                continue
            
            # Calculate trend score based on frequency, engagement, and recency
            avg_score = data['total_score'] / data['count']
            avg_comments = data['total_comments'] / data['count']
            avg_sentiment = sum(data['sentiment_scores']) / len(data['sentiment_scores'])
            
            # Trending score formula (can be tuned)
            trend_score = data['count'] * 1.0 + avg_score * 0.1 + avg_comments * 0.05
            
            # Boost priority keywords
            if term in self.priority_keywords:
                trend_score *= 1.5
            
            trending_topics.append((term, data['count'], trend_score, avg_sentiment))
        
        # Sort by trend score and return top N
        trending_topics.sort(key=lambda x: x[2], reverse=True)
        return trending_topics[:top_n]
    
    def get_news_trending_topics(self, articles: List[NewsArticle], top_n: int = 20) -> List[Tuple[str, int, float]]:
        """Extract trending topics from news articles"""
        keyword_data = {}
        
        for article in articles:
            # Extract keywords from title and description
            text = f"{article.title} {article.description}"
            keywords = self.extract_keywords(text)
            phrases = self.extract_phrases(text, max_phrase_length=2)
            
            all_terms = keywords + phrases
            
            for term in all_terms:
                if term not in keyword_data:
                    keyword_data[term] = {'count': 0, 'sentiment_scores': []}
                
                keyword_data[term]['count'] += 1
                keyword_data[term]['sentiment_scores'].append(article.sentiment_score)
        
        # Calculate trending scores
        trending_topics = []
        for term, data in keyword_data.items():
            if data['count'] < 2:  # Filter out terms mentioned less than 2 times
                continue
            
            avg_sentiment = sum(data['sentiment_scores']) / len(data['sentiment_scores'])
            trend_score = data['count']
            
            # Boost priority keywords
            if term in self.priority_keywords:
                trend_score *= 1.5
            
            trending_topics.append((term, data['count'], trend_score, avg_sentiment))
        
        # Sort by trend score and return top N
        trending_topics.sort(key=lambda x: x[2], reverse=True)
        return trending_topics[:top_n]
    
    def find_cross_platform_trends(self, reddit_posts: List[RedditPost], 
                                 news_articles: List[NewsArticle]) -> List[TrendingTopic]:
        """Find topics trending across both Reddit and news"""
        reddit_trends = dict([(term, (count, sentiment)) for term, count, score, sentiment in 
                             self.get_reddit_trending_topics(reddit_posts, 50)])
        news_trends = dict([(term, (count, sentiment)) for term, count, score, sentiment in 
                           self.get_news_trending_topics(news_articles, 50)])
        
        cross_platform_topics = []
        
        # Find topics mentioned in both platforms
        common_topics = set(reddit_trends.keys()) & set(news_trends.keys())
        
        for topic in common_topics:
            reddit_count, reddit_sentiment = reddit_trends[topic]
            news_count, news_sentiment = news_trends[topic]
            
            trending_topic = TrendingTopic(topic)
            trending_topic.update_mentions(reddit_count, news_count)
            trending_topic.update_sentiment([reddit_sentiment, news_sentiment])
            trending_topic.calculate_momentum()
            
            cross_platform_topics.append(trending_topic)
        
        # Add high-performing single-platform topics
        for topic, (count, sentiment) in reddit_trends.items():
            if topic not in common_topics and count >= 5:  # High Reddit activity
                trending_topic = TrendingTopic(topic)
                trending_topic.update_mentions(count, 0)
                trending_topic.update_sentiment([sentiment])
                trending_topic.calculate_momentum()
                cross_platform_topics.append(trending_topic)
        
        for topic, (count, sentiment) in news_trends.items():
            if topic not in common_topics and count >= 3:  # Significant news coverage
                trending_topic = TrendingTopic(topic)
                trending_topic.update_mentions(0, count)
                trending_topic.update_sentiment([sentiment])
                trending_topic.calculate_momentum()
                cross_platform_topics.append(trending_topic)
        
        # Sort by total mentions and momentum
        cross_platform_topics.sort(key=lambda x: x.reddit_mentions + x.news_mentions, reverse=True)
        
        return cross_platform_topics[:20]
    
    def analyze_trend_momentum(self, current_topics: List[TrendingTopic], 
                             previous_topics: List[TrendingTopic] = None) -> List[Dict[str, Any]]:
        """Analyze trend momentum by comparing with previous data"""
        if not previous_topics:
            previous_topics = []
        
        previous_dict = {topic.keyword: topic for topic in previous_topics}
        
        momentum_analysis = []
        
        for topic in current_topics:
            momentum_data = {
                'keyword': topic.keyword,
                'current_mentions': topic.reddit_mentions + topic.news_mentions,
                'reddit_mentions': topic.reddit_mentions,
                'news_mentions': topic.news_mentions,
                'sentiment': topic.sentiment_avg,
                'momentum': 'new',
                'momentum_score': 0,
                'cross_platform': topic.reddit_mentions > 0 and topic.news_mentions > 0
            }
            
            if topic.keyword in previous_dict:
                prev_topic = previous_dict[topic.keyword]
                prev_mentions = prev_topic.reddit_mentions + prev_topic.news_mentions
                current_mentions = topic.reddit_mentions + topic.news_mentions
                
                if current_mentions > prev_mentions:
                    momentum_data['momentum'] = 'rising'
                    momentum_data['momentum_score'] = (current_mentions - prev_mentions) / prev_mentions
                elif current_mentions < prev_mentions:
                    momentum_data['momentum'] = 'declining'
                    momentum_data['momentum_score'] = (prev_mentions - current_mentions) / prev_mentions
                else:
                    momentum_data['momentum'] = 'stable'
                    momentum_data['momentum_score'] = 0
            
            momentum_analysis.append(momentum_data)
        
        return momentum_analysis
    
    def get_viral_potential_score(self, post: RedditPost) -> float:
        """Calculate viral potential score for a Reddit post"""
        hours_old = (datetime.now().timestamp() - post.created_utc) / 3600
        if hours_old <= 0:
            hours_old = 0.1
        
        # Calculate engagement velocity
        engagement_velocity = (post.score + post.num_comments * 2) / hours_old
        
        # Comment to upvote ratio (higher ratio = more discussion)
        comment_ratio = post.num_comments / max(post.score, 1)
        
        # Sentiment boost (positive content tends to spread more)
        sentiment_boost = max(0, post.sentiment_score) * 0.1
        
        # Combine factors
        viral_score = engagement_velocity * (1 + comment_ratio) * (1 + sentiment_boost)
        
        return min(viral_score, 100)  # Cap at 100
    
    def predict_trending_topics(self, reddit_posts: List[RedditPost], 
                              news_articles: List[NewsArticle]) -> List[Dict[str, Any]]:
        """Predict which topics might become trending"""
        # Get recent posts (last 6 hours) with high engagement velocity
        recent_cutoff = datetime.now().timestamp() - (6 * 3600)
        recent_posts = [post for post in reddit_posts if post.created_utc > recent_cutoff]
        
        # Calculate viral potential for recent posts
        potential_trends = []
        keyword_scores = {}
        
        for post in recent_posts:
            viral_score = self.get_viral_potential_score(post)
            
            if viral_score > 1.0:  # Only consider posts with some viral potential
                keywords = self.extract_keywords(f"{post.title} {post.selftext}")
                
                for keyword in keywords:
                    if keyword not in keyword_scores:
                        keyword_scores[keyword] = []
                    keyword_scores[keyword].append(viral_score)
        
        # Calculate average viral potential by keyword
        for keyword, scores in keyword_scores.items():
            if len(scores) >= 2:  # Multiple mentions
                avg_score = sum(scores) / len(scores)
                potential_trends.append({
                    'keyword': keyword,
                    'viral_potential': avg_score,
                    'mention_count': len(scores),
                    'prediction': 'emerging' if avg_score > 5 else 'watch'
                })
        
        # Sort by viral potential
        potential_trends.sort(key=lambda x: x['viral_potential'], reverse=True)
        
        return potential_trends[:10]

# Global trend detector instance
trend_detector = TrendDetector()