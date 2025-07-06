"""
Reddit data collector for Social Pulse Analytics
Handles Reddit API integration and data collection
"""
import requests
import time
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.config import config
from app.models import RedditPost

class RedditCollector:
    """Reddit API data collector"""
    
    def __init__(self):
        self.client_id = config.REDDIT_CLIENT_ID
        self.client_secret = config.REDDIT_CLIENT_SECRET
        self.user_agent = config.REDDIT_USER_AGENT
        self.access_token = None
        self.token_expires_at = None
        self.base_url = "https://oauth.reddit.com"
        
    def get_access_token(self) -> str:
        """Get OAuth access token for Reddit API"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        # Prepare authentication
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'User-Agent': self.user_agent
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                headers=headers,
                data=data,
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Reddit tokens typically expire in 1 hour
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            
            return self.access_token
            
        except requests.RequestException as e:
            print(f"Error getting Reddit access token: {e}")
            return None
    
    def make_api_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Reddit API"""
        token = self.get_access_token()
        if not token:
            return {}
        
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': self.user_agent
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error making Reddit API request to {endpoint}: {e}")
            return {}
    
    def get_subreddit_posts(self, subreddit: str, limit: int = 25, sort: str = 'hot') -> List[RedditPost]:
        """Get posts from a specific subreddit"""
        endpoint = f"/r/{subreddit}/{sort}"
        params = {
            'limit': limit,
            't': 'day'  # Time filter for 'day'
        }
        
        data = self.make_api_request(endpoint, params)
        
        if not data or 'data' not in data or 'children' not in data['data']:
            return []
        
        posts = []
        cutoff_time = datetime.now().timestamp() - (config.HOURS_LOOKBACK * 3600)
        
        for item in data['data']['children']:
            post_data = item['data']
            
            # Skip if post is too old
            if post_data.get('created_utc', 0) < cutoff_time:
                continue
            
            # Create RedditPost object with enhanced data
            reddit_post = RedditPost({
                'id': post_data.get('id'),
                'title': post_data.get('title', ''),
                'subreddit': subreddit,
                'author': post_data.get('author', '[deleted]'),
                'score': post_data.get('score', 0),
                'num_comments': post_data.get('num_comments', 0),
                'url': post_data.get('url', ''),
                'selftext': post_data.get('selftext', ''),
                'created_utc': post_data.get('created_utc', 0),
                'sentiment_score': 0.0,  # Will be calculated later
                'upvote_ratio': post_data.get('upvote_ratio', 0.0),
                'post_flair': post_data.get('link_flair_text', ''),
                'is_nsfw': post_data.get('over_18', False),
                'is_spoiler': post_data.get('spoiler', False),
                'is_locked': post_data.get('locked', False),
                'post_type': 'link' if post_data.get('is_self', True) == False else 'text',
                'domain': post_data.get('domain', ''),
                'gilded': post_data.get('gilded', 0),
                'distinguished': post_data.get('distinguished', ''),
                'stickied': post_data.get('stickied', False),
                'total_awards_received': post_data.get('total_awards_received', 0),
                'curse_word_count': 0,  # Will be calculated later
                'readability_score': 0.0,  # Will be calculated later
                'engagement_velocity': 0.0,  # Will be calculated later
                'virality_score': 0.0  # Will be calculated later
            })
            
            posts.append(reddit_post)
        
        return posts
    
    def get_trending_subreddits(self) -> List[str]:
        """Get list of trending subreddits"""
        # For MVP, use predefined list. Can be enhanced later with actual trending API
        return config.REDDIT_SUBREDDITS
    
    def collect_all_posts(self) -> List[RedditPost]:
        """Collect posts from all configured subreddits"""
        all_posts = []
        
        subreddits = self.get_trending_subreddits()
        
        for subreddit in subreddits:
            try:
                print(f"Collecting posts from r/{subreddit}...")
                posts = self.get_subreddit_posts(subreddit, config.REDDIT_POST_LIMIT)
                all_posts.extend(posts)
                
                # Rate limiting - Reddit allows 60 requests per minute
                time.sleep(1)  # Wait 1 second between requests
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit}: {e}")
                continue
        
        print(f"Collected {len(all_posts)} Reddit posts total")
        return all_posts
    
    def get_post_comments(self, subreddit: str, post_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get comments for a specific post (for future enhancement)"""
        endpoint = f"/r/{subreddit}/comments/{post_id}"
        params = {'limit': limit}
        
        data = self.make_api_request(endpoint, params)
        
        comments = []
        if data and len(data) > 1 and 'data' in data[1]:
            for item in data[1]['data']['children']:
                if item['kind'] == 't1':  # Comment type
                    comment_data = item['data']
                    comments.append({
                        'id': comment_data.get('id'),
                        'body': comment_data.get('body', ''),
                        'score': comment_data.get('score', 0),
                        'author': comment_data.get('author', '[deleted]'),
                        'created_utc': comment_data.get('created_utc', 0)
                    })
        
        return comments
    
    def search_reddit(self, query: str, limit: int = 25) -> List[RedditPost]:
        """Search Reddit for specific topics"""
        endpoint = "/search"
        params = {
            'q': query,
            'sort': 'relevance',
            'limit': limit,
            't': 'day'
        }
        
        data = self.make_api_request(endpoint, params)
        
        if not data or 'data' not in data:
            return []
        
        posts = []
        for item in data['data']['children']:
            post_data = item['data']
            
            reddit_post = RedditPost({
                'id': post_data.get('id'),
                'title': post_data.get('title', ''),
                'subreddit': post_data.get('subreddit', ''),
                'author': post_data.get('author', '[deleted]'),
                'score': post_data.get('score', 0),
                'num_comments': post_data.get('num_comments', 0),
                'url': post_data.get('url', ''),
                'selftext': post_data.get('selftext', ''),
                'created_utc': post_data.get('created_utc', 0),
                'sentiment_score': 0.0
            })
            
            posts.append(reddit_post)
        
        return posts

# Global collector instance
reddit_collector = RedditCollector()