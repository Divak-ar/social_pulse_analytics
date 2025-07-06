"""
Behavioral analysis engine for Social Pulse Analytics
Analyzes human behavior patterns, sentiment vs virality, engagement psychology
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import statistics

from app.models import RedditPost, NewsArticle
from analyzers.content_analyzer import content_analyzer

class BehavioralAnalyzer:
    """Advanced behavioral pattern analysis"""
    
    def __init__(self):
        self.engagement_thresholds = {
            'low': 10,
            'medium': 50,
            'high': 200,
            'viral': 1000
        }
        
        self.sentiment_categories = {
            'very_negative': (-1.0, -0.5),
            'negative': (-0.5, -0.1),
            'neutral': (-0.1, 0.1),
            'positive': (0.1, 0.5),
            'very_positive': (0.5, 1.0)
        }
    
    def analyze_sentiment_virality_correlation(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Analyze correlation between sentiment and viral potential"""
        
        if not posts:
            return {"error": "No posts provided"}
        
        # Categorize posts by sentiment and engagement
        sentiment_engagement = defaultdict(list)
        
        for post in posts:
            # Calculate engagement score
            hours_old = max((datetime.now().timestamp() - post.created_utc) / 3600, 0.1)
            engagement_score = (post.score + post.num_comments * 2) / hours_old
            
            # Categorize sentiment
            sentiment_cat = self._categorize_sentiment(post.sentiment_score)
            
            sentiment_engagement[sentiment_cat].append({
                'engagement_score': engagement_score,
                'score': post.score,
                'comments': post.num_comments,
                'sentiment': post.sentiment_score,
                'hours_old': hours_old
            })
        
        # Calculate statistics for each sentiment category
        analysis = {}
        
        for sentiment_cat, engagements in sentiment_engagement.items():
            if engagements:
                engagement_scores = [e['engagement_score'] for e in engagements]
                scores = [e['score'] for e in engagements]
                
                analysis[sentiment_cat] = {
                    'count': len(engagements),
                    'avg_engagement': round(statistics.mean(engagement_scores), 2),
                    'median_engagement': round(statistics.median(engagement_scores), 2),
                    'avg_score': round(statistics.mean(scores), 1),
                    'viral_posts': len([e for e in engagements if e['score'] > self.engagement_thresholds['viral']]),
                    'viral_percentage': round((len([e for e in engagements if e['score'] > self.engagement_thresholds['viral']]) / len(engagements)) * 100, 1)
                }
        
        # Compare negative vs positive sentiment virality
        neg_viral = analysis.get('negative', {}).get('viral_percentage', 0) + analysis.get('very_negative', {}).get('viral_percentage', 0)
        pos_viral = analysis.get('positive', {}).get('viral_percentage', 0) + analysis.get('very_positive', {}).get('viral_percentage', 0)
        
        insights = {
            'sentiment_engagement_analysis': analysis,
            'key_insights': {
                'negative_sentiment_viral_rate': round(neg_viral / 2, 1) if neg_viral else 0,
                'positive_sentiment_viral_rate': round(pos_viral / 2, 1) if pos_viral else 0,
                'sentiment_virality_difference': round(abs(neg_viral - pos_viral) / 2, 1),
                'most_viral_sentiment': max(analysis.keys(), key=lambda x: analysis[x].get('viral_percentage', 0)) if analysis else 'unknown',
                'controversy_breeds_engagement': analysis.get('negative', {}).get('avg_engagement', 0) > analysis.get('positive', {}).get('avg_engagement', 0)
            },
            'sample_size': len(posts)
        }
        
        return insights
    
    def analyze_engagement_factors(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Analyze what makes posts more engaging/liked"""
        
        if not posts:
            return {"error": "No posts provided"}
        
        # Sort posts by engagement
        sorted_posts = sorted(posts, key=lambda p: p.score + p.num_comments * 2, reverse=True)
        
        top_10_percent = int(len(sorted_posts) * 0.1) or 1
        bottom_10_percent = int(len(sorted_posts) * 0.1) or 1
        
        top_posts = sorted_posts[:top_10_percent]
        bottom_posts = sorted_posts[-bottom_10_percent:]
        
        # Analyze characteristics of top vs bottom posts
        top_analysis = self._analyze_post_characteristics(top_posts)
        bottom_analysis = self._analyze_post_characteristics(bottom_posts)
        
        # Find significant differences
        factors = {
            'title_length': {
                'top_avg': top_analysis['avg_title_length'],
                'bottom_avg': bottom_analysis['avg_title_length'],
                'difference': round(top_analysis['avg_title_length'] - bottom_analysis['avg_title_length'], 1),
                'insight': 'longer titles' if top_analysis['avg_title_length'] > bottom_analysis['avg_title_length'] else 'shorter titles'
            },
            'content_length': {
                'top_avg': top_analysis['avg_content_length'],
                'bottom_avg': bottom_analysis['avg_content_length'],
                'difference': round(top_analysis['avg_content_length'] - bottom_analysis['avg_content_length'], 1),
                'insight': 'longer content' if top_analysis['avg_content_length'] > bottom_analysis['avg_content_length'] else 'shorter content'
            },
            'readability': {
                'top_avg': top_analysis['avg_readability'],
                'bottom_avg': bottom_analysis['avg_readability'],
                'difference': round(top_analysis['avg_readability'] - bottom_analysis['avg_readability'], 1),
                'insight': 'more readable' if top_analysis['avg_readability'] > bottom_analysis['avg_readability'] else 'less readable'
            },
            'profanity_usage': {
                'top_avg': top_analysis['avg_curse_words'],
                'bottom_avg': bottom_analysis['avg_curse_words'],
                'difference': round(top_analysis['avg_curse_words'] - bottom_analysis['avg_curse_words'], 2),
                'insight': 'more profanity' if top_analysis['avg_curse_words'] > bottom_analysis['avg_curse_words'] else 'less profanity'
            },
            'emotional_tone': {
                'top_distribution': top_analysis['emotional_tone_dist'],
                'bottom_distribution': bottom_analysis['emotional_tone_dist'],
                'insight': 'Different emotional tones drive engagement'
            }
        }
        
        # Generate insights
        key_insights = []
        
        if abs(factors['title_length']['difference']) > 2:
            key_insights.append(f"Top posts have {factors['title_length']['insight']} (avg {factors['title_length']['top_avg']} vs {factors['title_length']['bottom_avg']} words)")
        
        if abs(factors['readability']['difference']) > 10:
            key_insights.append(f"Top posts are {factors['readability']['insight']} (score {factors['readability']['top_avg']} vs {factors['readability']['bottom_avg']})")
        
        if abs(factors['profanity_usage']['difference']) > 0.5:
            key_insights.append(f"Top posts use {factors['profanity_usage']['insight']} ({factors['profanity_usage']['top_avg']} vs {factors['profanity_usage']['bottom_avg']} curse words per post)")
        
        return {
            'engagement_factors': factors,
            'key_insights': key_insights,
            'top_posts_characteristics': top_analysis,
            'bottom_posts_characteristics': bottom_analysis,
            'sample_sizes': {
                'top_posts': len(top_posts),
                'bottom_posts': len(bottom_posts),
                'total_posts': len(posts)
            }
        }
    
    def analyze_subreddit_behavior_patterns(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Analyze behavioral patterns across different subreddits"""
        
        subreddit_data = defaultdict(list)
        
        for post in posts:
            subreddit_data[post.subreddit].append(post)
        
        subreddit_analysis = {}
        
        for subreddit, sub_posts in subreddit_data.items():
            if len(sub_posts) < 5:  # Skip subreddits with too few posts
                continue
            
            # Analyze profanity usage
            profanity_stats = []
            sentiment_scores = []
            engagement_scores = []
            
            for post in sub_posts:
                text = f"{post.title} {post.selftext}"
                curse_analysis = content_analyzer.count_curse_words(text)
                profanity_stats.append(curse_analysis['curse_count'])
                sentiment_scores.append(post.sentiment_score)
                
                hours_old = max((datetime.now().timestamp() - post.created_utc) / 3600, 0.1)
                engagement_score = (post.score + post.num_comments * 2) / hours_old
                engagement_scores.append(engagement_score)
            
            subreddit_analysis[subreddit] = {
                'post_count': len(sub_posts),
                'avg_profanity': round(statistics.mean(profanity_stats), 2),
                'profanity_posts_percentage': round((sum(1 for p in profanity_stats if p > 0) / len(profanity_stats)) * 100, 1),
                'avg_sentiment': round(statistics.mean(sentiment_scores), 3),
                'avg_engagement': round(statistics.mean(engagement_scores), 2),
                'behavior_profile': self._get_behavior_profile(statistics.mean(profanity_stats), statistics.mean(sentiment_scores), statistics.mean(engagement_scores))
            }
        
        # Rank subreddits by different metrics
        rankings = {
            'most_profane': sorted(subreddit_analysis.items(), key=lambda x: x[1]['avg_profanity'], reverse=True)[:5],
            'most_positive': sorted(subreddit_analysis.items(), key=lambda x: x[1]['avg_sentiment'], reverse=True)[:5],
            'most_engaging': sorted(subreddit_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)[:5],
            'cleanest_language': sorted(subreddit_analysis.items(), key=lambda x: x[1]['avg_profanity'])[:5]
        }
        
        # Generate overall insights
        all_profanity = [data['avg_profanity'] for data in subreddit_analysis.values()]
        overall_insights = {
            'total_subreddits_analyzed': len(subreddit_analysis),
            'avg_profanity_across_all': round(statistics.mean(all_profanity), 2) if all_profanity else 0,
            'profanity_variation': round(statistics.stdev(all_profanity), 2) if len(all_profanity) > 1 else 0,
            'most_profane_community': rankings['most_profane'][0][0] if rankings['most_profane'] else 'unknown',
            'cleanest_community': rankings['cleanest_language'][0][0] if rankings['cleanest_language'] else 'unknown'
        }
        
        return {
            'subreddit_analysis': subreddit_analysis,
            'rankings': rankings,
            'overall_insights': overall_insights
        }
    
    def analyze_temporal_behavior_patterns(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Analyze how behavior changes over time"""
        
        if not posts:
            return {"error": "No posts provided"}
        
        # Group posts by hour of day
        hourly_data = defaultdict(list)
        
        for post in posts:
            hour = datetime.fromtimestamp(post.created_utc).hour
            hourly_data[hour].append(post)
        
        hourly_analysis = {}
        
        for hour, hour_posts in hourly_data.items():
            if not hour_posts:
                continue
            
            sentiments = [p.sentiment_score for p in hour_posts]
            scores = [p.score for p in hour_posts]
            
            # Analyze profanity by hour
            profanity_counts = []
            for post in hour_posts:
                text = f"{post.title} {post.selftext}"
                curse_analysis = content_analyzer.count_curse_words(text)
                profanity_counts.append(curse_analysis['curse_count'])
            
            hourly_analysis[hour] = {
                'post_count': len(hour_posts),
                'avg_sentiment': round(statistics.mean(sentiments), 3),
                'avg_score': round(statistics.mean(scores), 1),
                'avg_profanity': round(statistics.mean(profanity_counts), 2),
                'mood': self._categorize_sentiment(statistics.mean(sentiments))
            }
        
        # Find patterns
        patterns = {
            'most_active_hour': max(hourly_analysis.keys(), key=lambda h: hourly_analysis[h]['post_count']) if hourly_analysis else 0,
            'most_positive_hour': max(hourly_analysis.keys(), key=lambda h: hourly_analysis[h]['avg_sentiment']) if hourly_analysis else 0,
            'most_negative_hour': min(hourly_analysis.keys(), key=lambda h: hourly_analysis[h]['avg_sentiment']) if hourly_analysis else 0,
            'most_profane_hour': max(hourly_analysis.keys(), key=lambda h: hourly_analysis[h]['avg_profanity']) if hourly_analysis else 0,
            'cleanest_hour': min(hourly_analysis.keys(), key=lambda h: hourly_analysis[h]['avg_profanity']) if hourly_analysis else 0
        }
        
        return {
            'hourly_analysis': hourly_analysis,
            'behavioral_patterns': patterns,
            'insights': self._generate_temporal_insights(hourly_analysis, patterns)
        }
    
    def _categorize_sentiment(self, sentiment_score: float) -> str:
        """Categorize sentiment score"""
        for category, (min_val, max_val) in self.sentiment_categories.items():
            if min_val <= sentiment_score < max_val:
                return category
        return 'neutral'
    
    def _analyze_post_characteristics(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Analyze characteristics of a group of posts"""
        
        if not posts:
            return {}
        
        title_lengths = []
        content_lengths = []
        readability_scores = []
        curse_counts = []
        emotional_tones = []
        
        for post in posts:
            title_lengths.append(len(post.title.split()))
            content_lengths.append(len(post.selftext.split()) if post.selftext else 0)
            
            text = f"{post.title} {post.selftext}"
            
            # Readability
            readability = content_analyzer.calculate_readability_score(text)
            readability_scores.append(readability['score'])
            
            # Profanity
            curse_analysis = content_analyzer.count_curse_words(text)
            curse_counts.append(curse_analysis['curse_count'])
            
            # Emotional tone
            engagement = content_analyzer.analyze_engagement_factors(text)
            emotional_tones.append(engagement['emotional_tone'])
        
        return {
            'avg_title_length': round(statistics.mean(title_lengths), 1),
            'avg_content_length': round(statistics.mean(content_lengths), 1),
            'avg_readability': round(statistics.mean(readability_scores), 1),
            'avg_curse_words': round(statistics.mean(curse_counts), 2),
            'emotional_tone_dist': dict(Counter(emotional_tones))
        }
    
    def _get_behavior_profile(self, profanity: float, sentiment: float, engagement: float) -> str:
        """Generate behavior profile for a community"""
        
        profiles = []
        
        if profanity > 1.5:
            profiles.append("High Profanity")
        elif profanity > 0.5:
            profiles.append("Moderate Profanity")
        else:
            profiles.append("Clean Language")
        
        if sentiment > 0.2:
            profiles.append("Positive Community")
        elif sentiment < -0.2:
            profiles.append("Critical Community")
        else:
            profiles.append("Balanced Community")
        
        if engagement > 10:
            profiles.append("Highly Engaged")
        elif engagement > 5:
            profiles.append("Moderately Engaged")
        else:
            profiles.append("Low Engagement")
        
        return " | ".join(profiles)
    
    def _generate_temporal_insights(self, hourly_analysis: Dict, patterns: Dict) -> List[str]:
        """Generate insights from temporal analysis"""
        
        insights = []
        
        if patterns['most_active_hour']:
            insights.append(f"Peak activity occurs at {patterns['most_active_hour']}:00")
        
        if patterns['most_positive_hour'] != patterns['most_negative_hour']:
            insights.append(f"Users are most positive at {patterns['most_positive_hour']}:00 and most negative at {patterns['most_negative_hour']}:00")
        
        if patterns['most_profane_hour']:
            insights.append(f"Language is most colorful at {patterns['most_profane_hour']}:00")
        
        return insights
    
    def generate_comprehensive_behavioral_report(self, reddit_posts: List[RedditPost], 
                                               news_articles: List[NewsArticle] = None) -> Dict[str, Any]:
        """Generate comprehensive behavioral analysis report"""
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'sample_size': {
                'reddit_posts': len(reddit_posts),
                'news_articles': len(news_articles) if news_articles else 0
            }
        }
        
        try:
            # Sentiment vs Virality Analysis
            report['sentiment_virality'] = self.analyze_sentiment_virality_correlation(reddit_posts)
            
            # Engagement Factors Analysis
            report['engagement_factors'] = self.analyze_engagement_factors(reddit_posts)
            
            # Subreddit Behavior Patterns
            report['subreddit_patterns'] = self.analyze_subreddit_behavior_patterns(reddit_posts)
            
            # Temporal Behavior Patterns
            report['temporal_patterns'] = self.analyze_temporal_behavior_patterns(reddit_posts)
            
            # Generate executive summary
            report['executive_summary'] = self._generate_executive_summary(report)
            
        except Exception as e:
            report['error'] = str(e)
        
        return report
    
    def _generate_executive_summary(self, report: Dict[str, Any]) -> List[str]:
        """Generate executive summary of behavioral insights"""
        
        summary = []
        
        try:
            # Sentiment-Virality insights
            sv = report.get('sentiment_virality', {}).get('key_insights', {})
            if sv.get('controversy_breeds_engagement'):
                summary.append("💥 Negative sentiment content often generates more engagement than positive content")
            
            neg_viral = sv.get('negative_sentiment_viral_rate', 0)
            pos_viral = sv.get('positive_sentiment_viral_rate', 0)
            if abs(neg_viral - pos_viral) > 2:
                if neg_viral > pos_viral:
                    summary.append(f"📊 Negative content is {neg_viral - pos_viral:.1f}% more likely to go viral")
                else:
                    summary.append(f"✨ Positive content is {pos_viral - neg_viral:.1f}% more likely to go viral")
            
            # Engagement factors insights
            ef = report.get('engagement_factors', {}).get('key_insights', [])
            summary.extend([f"🎯 {insight}" for insight in ef])
            
            # Profanity insights
            sp = report.get('subreddit_patterns', {}).get('overall_insights', {})
            if sp.get('avg_profanity_across_all', 0) > 1:
                summary.append(f"🤬 Average of {sp['avg_profanity_across_all']:.1f} curse words per post across communities")
            
            # Temporal insights
            tp = report.get('temporal_patterns', {}).get('insights', [])
            summary.extend([f"⏰ {insight}" for insight in tp])
            
        except Exception as e:
            summary.append(f"⚠️ Error generating summary: {str(e)}")
        
        return summary

# Global behavioral analyzer instance
behavioral_analyzer = BehavioralAnalyzer()