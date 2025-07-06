"""
Advanced content analysis for Social Pulse Analytics
Analyzes text content for curse words, readability, engagement factors, and behavioral patterns
"""
import re
import string
from collections import Counter
from typing import Dict, List, Any, Tuple
import math

class ContentAnalyzer:
    """Advanced content analysis engine"""
    
    def __init__(self):
        # Common curse words and profanity (PG-13 list for analytics)
        self.curse_words = {
            'damn', 'hell', 'shit', 'fuck', 'fucking', 'fucked', 'bullshit', 'crap', 
            'piss', 'ass', 'asshole', 'bitch', 'bastard', 'wtf', 'omfg', 'ffs',
            'motherfucker', 'goddamn', 'goddammit', 'dammit', 'bloody', 'bugger',
            'shitty', 'crappy', 'sucks', 'dumbass', 'dickhead', 'moron', 'idiot',
            'stupid', 'retard', 'gay', 'fag', 'nigga', 'bro', 'dude', 'wtf',
            # Internet slang curse variations
            'f*ck', 'sh*t', 'b*tch', 'a**hole', 'fck', 'sht', 'fuk', 'fuc',
            'effing', 'frigging', 'freaking', 'darn', 'heck'
        }
        
        # Positive engagement words
        self.positive_engagement_words = {
            'amazing', 'awesome', 'incredible', 'fantastic', 'brilliant', 'genius',
            'revolutionary', 'breakthrough', 'stunning', 'spectacular', 'outstanding',
            'exceptional', 'remarkable', 'extraordinary', 'phenomenal', 'magnificent',
            'wow', 'omg', 'holy', 'mind-blowing', 'game-changer', 'life-changing',
            'love', 'adore', 'obsessed', 'addicted', 'excited', 'thrilled',
            'grateful', 'blessed', 'lucky', 'proud', 'impressed', 'inspired'
        }
        
        # Negative engagement words
        self.negative_engagement_words = {
            'terrible', 'awful', 'horrible', 'disgusting', 'pathetic', 'useless',
            'worthless', 'garbage', 'trash', 'waste', 'disaster', 'failure',
            'disappointed', 'frustrated', 'angry', 'furious', 'outraged', 'pissed',
            'hate', 'loathe', 'despise', 'annoyed', 'irritated', 'sick', 'tired',
            'broken', 'ruined', 'destroyed', 'screwed', 'doomed', 'hopeless'
        }
        
        # Question words that indicate engagement
        self.question_indicators = {
            'why', 'how', 'what', 'when', 'where', 'who', 'which', 'whose',
            'can', 'could', 'would', 'should', 'will', 'do', 'does', 'did',
            'is', 'are', 'was', 'were', 'has', 'have', 'had'
        }
        
        # Viral content indicators
        self.viral_indicators = {
            'breaking', 'urgent', 'alert', 'update', 'confirmed', 'exclusive',
            'leaked', 'revealed', 'exposed', 'shocking', 'unbelievable', 'insane',
            'crazy', 'wild', 'epic', 'massive', 'huge', 'biggest', 'first',
            'never', 'always', 'everyone', 'nobody', 'everything', 'nothing'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove Reddit formatting
        text = re.sub(r'/u/\w+', '', text)  # Remove username mentions
        text = re.sub(r'/r/\w+', '', text)  # Remove subreddit mentions
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold formatting
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic formatting
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def count_curse_words(self, text: str) -> Dict[str, Any]:
        """Count curse words and profanity in text"""
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        curse_count = 0
        found_curses = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = word.translate(str.maketrans('', '', string.punctuation))
            
            if clean_word in self.curse_words:
                curse_count += 1
                found_curses.append(clean_word)
        
        total_words = len(words)
        curse_ratio = (curse_count / total_words) * 100 if total_words > 0 else 0
        
        return {
            'curse_count': curse_count,
            'total_words': total_words,
            'curse_ratio': round(curse_ratio, 2),
            'profanity_level': self._get_profanity_level(curse_ratio),
            'found_curses': list(set(found_curses))  # Unique curses found
        }
    
    def _get_profanity_level(self, curse_ratio: float) -> str:
        """Categorize profanity level"""
        if curse_ratio == 0:
            return "Clean"
        elif curse_ratio < 2:
            return "Mild"
        elif curse_ratio < 5:
            return "Moderate"
        elif curse_ratio < 10:
            return "Heavy"
        else:
            return "Extreme"
    
    def calculate_readability_score(self, text: str) -> Dict[str, Any]:
        """Calculate readability score using Flesch Reading Ease"""
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text:
            return {'score': 0, 'level': 'Unknown', 'words': 0, 'sentences': 0}
        
        # Count sentences (approximate)
        sentences = len(re.findall(r'[.!?]+', text))
        if sentences == 0:
            sentences = 1  # Assume at least one sentence
        
        # Count words
        words = len(cleaned_text.split())
        if words == 0:
            return {'score': 0, 'level': 'Unknown', 'words': 0, 'sentences': sentences}
        
        # Count syllables (approximation)
        syllables = self._count_syllables(cleaned_text)
        
        # Flesch Reading Ease Score
        if sentences > 0 and words > 0:
            score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        else:
            score = 0
        
        # Clamp score between 0 and 100
        score = max(0, min(100, score))
        
        return {
            'score': round(score, 1),
            'level': self._get_reading_level(score),
            'words': words,
            'sentences': sentences,
            'syllables': syllables,
            'avg_words_per_sentence': round(words / sentences, 1) if sentences > 0 else 0
        }
    
    def _count_syllables(self, text: str) -> int:
        """Approximate syllable count"""
        words = text.split()
        syllable_count = 0
        
        for word in words:
            word = word.lower()
            count = 0
            vowels = "aeiouy"
            
            if word[0] in vowels:
                count += 1
            
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            
            if word.endswith("e"):
                count -= 1
            
            if count == 0:
                count += 1
            
            syllable_count += count
        
        return syllable_count
    
    def _get_reading_level(self, score: float) -> str:
        """Get reading level from Flesch score"""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def analyze_engagement_factors(self, text: str) -> Dict[str, Any]:
        """Analyze factors that drive engagement"""
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        # Count engagement indicators
        positive_words = sum(1 for word in words if word in self.positive_engagement_words)
        negative_words = sum(1 for word in words if word in self.negative_engagement_words)
        question_words = sum(1 for word in words if word in self.question_indicators)
        viral_words = sum(1 for word in words if word in self.viral_indicators)
        
        # Check for questions
        has_question = '?' in text
        
        # Check for exclamations
        exclamation_count = text.count('!')
        
        # Check for caps (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Calculate engagement score
        engagement_score = (
            positive_words * 2 +
            negative_words * 1.5 +
            question_words * 1.2 +
            viral_words * 3 +
            (5 if has_question else 0) +
            exclamation_count * 2 +
            caps_ratio * 10
        )
        
        total_words = len(words)
        engagement_score = engagement_score / total_words if total_words > 0 else 0
        
        return {
            'engagement_score': round(engagement_score, 3),
            'positive_words': positive_words,
            'negative_words': negative_words,
            'question_words': question_words,
            'viral_words': viral_words,
            'has_question': has_question,
            'exclamation_count': exclamation_count,
            'caps_ratio': round(caps_ratio * 100, 1),
            'total_words': total_words,
            'emotional_tone': self._get_emotional_tone(positive_words, negative_words, total_words)
        }
    
    def _get_emotional_tone(self, positive: int, negative: int, total: int) -> str:
        """Determine emotional tone of content"""
        if total == 0:
            return "Neutral"
        
        pos_ratio = positive / total
        neg_ratio = negative / total
        
        if pos_ratio > neg_ratio * 1.5:
            return "Very Positive"
        elif pos_ratio > neg_ratio:
            return "Positive"
        elif neg_ratio > pos_ratio * 1.5:
            return "Very Negative"
        elif neg_ratio > pos_ratio:
            return "Negative"
        else:
            return "Neutral"
    
    def analyze_viral_potential(self, title: str, content: str, score: int = 0, 
                              comments: int = 0, hours_old: float = 1) -> Dict[str, Any]:
        """Analyze viral potential of content"""
        
        # Combine title and content for analysis
        full_text = f"{title} {content}"
        
        # Get engagement factors
        engagement = self.analyze_engagement_factors(full_text)
        
        # Get readability
        readability = self.calculate_readability_score(full_text)
        
        # Calculate engagement velocity
        engagement_velocity = (score + comments * 2) / max(hours_old, 0.1)
        
        # Viral score components
        title_length_score = self._score_title_length(len(title.split()))
        readability_score = self._score_readability(readability['score'])
        engagement_factor_score = min(engagement['engagement_score'] * 10, 10)
        velocity_score = min(math.log(engagement_velocity + 1) * 2, 10)
        
        # Combined viral score
        viral_score = (
            title_length_score * 0.2 +
            readability_score * 0.2 +
            engagement_factor_score * 0.3 +
            velocity_score * 0.3
        )
        
        return {
            'viral_score': round(viral_score, 2),
            'viral_level': self._get_viral_level(viral_score),
            'engagement_velocity': round(engagement_velocity, 2),
            'title_length_score': title_length_score,
            'readability_score': readability_score,
            'engagement_factor_score': round(engagement_factor_score, 2),
            'velocity_score': round(velocity_score, 2),
            'components': {
                'title_optimal': 5 <= len(title.split()) <= 12,
                'readable': 30 <= readability['score'] <= 70,
                'engaging': engagement['engagement_score'] > 0.1,
                'fast_growth': engagement_velocity > 5
            }
        }
    
    def _score_title_length(self, word_count: int) -> float:
        """Score based on optimal title length"""
        if 5 <= word_count <= 12:
            return 10.0
        elif 3 <= word_count <= 15:
            return 8.0
        elif 2 <= word_count <= 20:
            return 6.0
        else:
            return 3.0
    
    def _score_readability(self, flesch_score: float) -> float:
        """Score based on readability (easier = better for viral)"""
        if flesch_score >= 70:
            return 10.0
        elif flesch_score >= 60:
            return 8.0
        elif flesch_score >= 50:
            return 6.0
        elif flesch_score >= 30:
            return 4.0
        else:
            return 2.0
    
    def _get_viral_level(self, viral_score: float) -> str:
        """Get viral potential level"""
        if viral_score >= 8:
            return "Very High"
        elif viral_score >= 6:
            return "High"
        elif viral_score >= 4:
            return "Medium"
        elif viral_score >= 2:
            return "Low"
        else:
            return "Very Low"
    
    def generate_content_insights(self, posts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from multiple posts"""
        
        if not posts_data:
            return {"error": "No data provided"}
        
        # Analyze all posts
        total_posts = len(posts_data)
        curse_counts = []
        readability_scores = []
        engagement_scores = []
        viral_scores = []
        emotional_tones = []
        
        for post in posts_data:
            text = f"{post.get('title', '')} {post.get('selftext', '')}"
            
            # Curse word analysis
            curse_analysis = self.count_curse_words(text)
            curse_counts.append(curse_analysis['curse_count'])
            
            # Readability analysis
            readability = self.calculate_readability_score(text)
            readability_scores.append(readability['score'])
            
            # Engagement analysis
            engagement = self.analyze_engagement_factors(text)
            engagement_scores.append(engagement['engagement_score'])
            emotional_tones.append(engagement['emotional_tone'])
            
            # Viral analysis
            viral = self.analyze_viral_potential(
                post.get('title', ''),
                post.get('selftext', ''),
                post.get('score', 0),
                post.get('num_comments', 0),
                1  # Assume 1 hour old for analysis
            )
            viral_scores.append(viral['viral_score'])
        
        # Generate insights
        insights = {
            'sample_size': total_posts,
            'profanity_insights': {
                'posts_with_curse_words': sum(1 for count in curse_counts if count > 0),
                'percentage_with_profanity': round((sum(1 for count in curse_counts if count > 0) / total_posts) * 100, 1),
                'avg_curse_words_per_post': round(sum(curse_counts) / total_posts, 2),
                'max_curse_words': max(curse_counts) if curse_counts else 0
            },
            'readability_insights': {
                'avg_readability': round(sum(readability_scores) / len(readability_scores), 1) if readability_scores else 0,
                'most_readable_percentage': round((sum(1 for score in readability_scores if score >= 70) / total_posts) * 100, 1),
                'difficult_to_read_percentage': round((sum(1 for score in readability_scores if score < 50) / total_posts) * 100, 1)
            },
            'engagement_insights': {
                'avg_engagement_score': round(sum(engagement_scores) / len(engagement_scores), 3) if engagement_scores else 0,
                'high_engagement_percentage': round((sum(1 for score in engagement_scores if score > 0.1) / total_posts) * 100, 1),
                'emotional_tone_distribution': dict(Counter(emotional_tones))
            },
            'viral_insights': {
                'avg_viral_score': round(sum(viral_scores) / len(viral_scores), 2) if viral_scores else 0,
                'high_viral_potential_percentage': round((sum(1 for score in viral_scores if score >= 6) / total_posts) * 100, 1),
                'low_viral_potential_percentage': round((sum(1 for score in viral_scores if score < 4) / total_posts) * 100, 1)
            }
        }
        
        return insights

# Global content analyzer instance
content_analyzer = ContentAnalyzer()