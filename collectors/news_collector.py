import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.config import config
from app.models import NewsArticle

class NewsCollector:
    """NewsAPI data collector"""
    
    def __init__(self):
        self.api_key = config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        
        # Popular news sources for balanced coverage
        self.sources = [
            'bbc-news', 'reuters', 'associated-press', 'cnn',
            'techcrunch', 'ars-technica', 'the-verge', 'wired',
            'bloomberg', 'fortune', 'business-insider'
        ]
        
        # Technology and science keywords for correlation with Reddit
        self.tech_keywords = [
            'artificial intelligence', 'machine learning', 'AI', 'technology',
            'science', 'space', 'climate', 'environment', 'breakthrough',
            'research', 'innovation', 'future', 'digital', 'cyber'
        ]
        
        # Trending social topics for comprehensive coverage
        self.social_topics = [
            'climate change', 'AI regulation', 'political polarization',
            'russia ukraine war', 'gaza conflict', 'covid aftermath',
            'vaccine discourse', 'stock market crash', 'crypto volatility',
            'mass layoffs', 'social justice movements', 'economic inflation',
            'cost of living crisis', 'celebrity scandals', 'public reactions',
            'social media', 'mental health', 'workplace culture',
            'remote work', 'housing crisis', 'student debt'
        ]
    
    def make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to NewsAPI"""
        params['apiKey'] = self.api_key
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error making NewsAPI request to {endpoint}: {e}")
            return {}
    
    def get_top_headlines(self, limit: int = 50) -> List[NewsArticle]:
        """Get top headlines from various sources"""
        endpoint = "/top-headlines"
        
        # Get articles from last 24 hours
        from_date = (datetime.now() - timedelta(hours=config.HOURS_LOOKBACK)).strftime('%Y-%m-%d')
        
        params = {
            'sources': ','.join(self.sources[:5]),  # Limit sources to avoid API limits
            'language': 'en',
            'pageSize': min(limit, 100),  # NewsAPI max is 100
            'from': from_date
        }
        
        data = self.make_api_request(endpoint, params)
        
        articles = []
        if data.get('status') == 'ok' and 'articles' in data:
            for article_data in data['articles']:
                if not article_data.get('title') or article_data.get('title') == '[Removed]':
                    continue
                
                article = NewsArticle({
                    'title': article_data.get('title', ''),
                    'description': article_data.get('description', ''),
                    'url': article_data.get('url', ''),
                    'source': article_data.get('source', {}),
                    'publishedAt': article_data.get('publishedAt', ''),
                    'sentiment_score': 0.0  # Will be calculated later
                })
                
                articles.append(article)
        
        return articles
    
    def search_news(self, query: str, limit: int = 20) -> List[NewsArticle]:
        """Search for news articles with specific keywords"""
        endpoint = "/everything"
        
        from_date = (datetime.now() - timedelta(hours=config.HOURS_LOOKBACK)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': min(limit, 100),
            'from': from_date
        }
        
        data = self.make_api_request(endpoint, params)
        
        articles = []
        if data.get('status') == 'ok' and 'articles' in data:
            for article_data in data['articles']:
                if not article_data.get('title') or article_data.get('title') == '[Removed]':
                    continue
                
                article = NewsArticle({
                    'title': article_data.get('title', ''),
                    'description': article_data.get('description', ''),
                    'url': article_data.get('url', ''),
                    'source': article_data.get('source', {}),
                    'publishedAt': article_data.get('publishedAt', ''),
                    'keywords': query,
                    'sentiment_score': 0.0
                })
                
                articles.append(article)
        
        return articles
    
    def get_tech_science_news(self) -> List[NewsArticle]:
        """Get technology and science news articles"""
        all_articles = []
        
        # Search for each keyword (with rate limiting)
        for keyword in self.tech_keywords[:5]:  # Limit to 5 keywords for MVP
            try:
                print(f"Searching news for: {keyword}")
                articles = self.search_news(keyword, limit=10)
                all_articles.extend(articles)
                
                # Rate limiting - NewsAPI allows 1000 requests per day on free tier
                import time
                time.sleep(0.5)  # Wait 0.5 seconds between requests
                
            except Exception as e:
                print(f"Error searching news for '{keyword}': {e}")
                continue
        
        # Remove duplicates by URL
        unique_articles = {}
        for article in all_articles:
            if article.url and article.url not in unique_articles:
                unique_articles[article.url] = article
        
        return list(unique_articles.values())
    
    def collect_all_articles(self) -> List[NewsArticle]:
        """Collect all relevant news articles"""
        all_articles = []
        
        try:
            # Get top headlines
            print("Collecting top headlines...")
            headlines = self.get_top_headlines(limit=25)
            all_articles.extend(headlines)
            
            # Get tech/science specific news
            print("Collecting tech/science news...")
            tech_articles = self.get_tech_science_news()
            all_articles.extend(tech_articles)
            
            # Remove duplicates by URL
            unique_articles = {}
            for article in all_articles:
                if article.url and article.url not in unique_articles:
                    unique_articles[article.url] = article
            
            final_articles = list(unique_articles.values())
            
        except Exception as e:
            print(f"Error in collect_all_articles: {e}")
            final_articles = []
        
        print(f"Collected {len(final_articles)} news articles total")
        return final_articles
    
    def get_trending_topics_from_news(self) -> List[str]:
        """Extract trending topics from recent news headlines"""
        articles = self.get_top_headlines(limit=30)
        
        # Simple keyword extraction from titles
        word_count = {}
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall', 'this', 'that', 'these', 'those'}
        
        for article in articles:
            if not article.title:
                continue
                
            words = article.title.lower().split()
            for word in words:
                word = word.strip('.,!?:;()[]{}"\'-')
                if len(word) > 3 and word not in stop_words and word.isalpha():
                    word_count[word] = word_count.get(word, 0) + 1
        
        # Return top trending words
        trending = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in trending[:20] if count >= 2]

# Global collector instance
news_collector = NewsCollector()