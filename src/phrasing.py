"""
Sports News Content Generation System
Generates engaging newsletter content including hooks, stats, opinions, and educational content.
Uses real sports data and terminology for accurate content creation.
"""

import random
import re
import yaml
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os

from config import (
    SPORTS_LEAGUES, SPORTS_EMOJIS, CONTROVERSY_PATTERNS, 
    HIGH_INTEREST_KEYWORDS, CONTENT_SETTINGS
)


class ContentGenerator:
    """Main class for generating engaging sports newsletter content."""
    
    def __init__(self):
        self.lessons = self._load_lessons()
        self.explainers = self._load_explainers()
        
    def _load_lessons(self) -> Dict:
        """Load sports education lessons from YAML file."""
        try:
            with open('./data/lessons.yaml', 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return {}
    
    def _load_explainers(self) -> Dict:
        """Load sports terminology explainers from YAML file."""
        try:
            with open('./data/explainers.yaml', 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return {}
    
    def generate_hook(self, article: Dict, league: str) -> str:
        """Generate attention-grabbing opening lines based on article content."""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        # Detect article type and generate appropriate hook
        if self._is_controversy(title + ' ' + content):
            return self._generate_controversy_hook(article, league)
        elif self._is_trade_news(title + ' ' + content):
            return self._generate_trade_hook(article, league)
        elif self._is_injury_news(title + ' ' + content):
            return self._generate_injury_hook(article, league)
        elif self._is_game_result(title + ' ' + content):
            return self._generate_game_hook(article, league)
        else:
            return self._generate_general_hook(article, league)
    
    def _is_controversy(self, text: str) -> bool:
        """Detect if article contains controversial content."""
        for pattern in CONTROVERSY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_trade_news(self, text: str) -> bool:
        """Detect if article is about trades or transfers."""
        trade_patterns = [
            r'\b(trade|traded|trading|deal|acquired|signs?|signed)\b',
            r'\b(transfer|moved|joins?|joined)\b'
        ]
        for pattern in trade_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_injury_news(self, text: str) -> bool:
        """Detect if article is about injuries."""
        injury_patterns = [
            r'\b(injury|injured|hurt|hospitalized|surgery)\b',
            r'\b(out for|sidelined|questionable|doubtful)\b'
        ]
        for pattern in injury_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_game_result(self, text: str) -> bool:
        """Detect if article is about game results."""
        game_patterns = [
            r'\b(beat|beats|defeated|won|lost|victory|win)\b',
            r'\b(final score|overtime|buzzer beater|walk-off)\b'
        ]
        for pattern in game_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _generate_controversy_hook(self, article: Dict, league: str) -> str:
        """Generate hooks for controversial stories."""
        emoji = SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆')
        hooks = [
            f"{emoji} BREAKING: The {league} world is buzzing about this developing story...",
            f"🚨 {league} Alert: This story is sending shockwaves through the league",
            f"{emoji} Drama Alert: What just happened in {league} has everyone talking",
            f"⚡ {league} Breaking News: This could change everything we thought we knew"
        ]
        return random.choice(hooks)
    
    def _generate_trade_hook(self, article: Dict, league: str) -> str:
        """Generate hooks for trade/transfer stories."""
        emoji = SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆')
        hooks = [
            f"{emoji} TRADE ALERT: The {league} landscape just shifted dramatically",
            f"🔄 {league} Move: This deal could reshape the entire season",
            f"{emoji} Breaking: A blockbuster {league} transaction just went down",
            f"📈 {league} Trade News: This move has championship implications"
        ]
        return random.choice(hooks)
    
    def _generate_injury_hook(self, article: Dict, league: str) -> str:
        """Generate hooks for injury stories."""
        emoji = SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆')
        hooks = [
            f"{emoji} Injury Update: This could impact the entire {league} season",
            f"🏥 {league} News: A key player's status has everyone concerned",
            f"{emoji} Health Alert: This {league} development changes everything",
            f"⚕️ {league} Update: The latest on this crucial injury situation"
        ]
        return random.choice(hooks)
    
    def _generate_game_hook(self, article: Dict, league: str) -> str:
        """Generate hooks for game result stories."""
        emoji = SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆')
        hooks = [
            f"{emoji} Game Recap: What a finish in this {league} matchup!",
            f"🔥 {league} Thriller: This game had everything you could want",
            f"{emoji} Final Score: This {league} result shocked everyone",
            f"⚡ {league} Action: The highlights from this game are incredible"
        ]
        return random.choice(hooks)
    
    def _generate_general_hook(self, article: Dict, league: str) -> str:
        """Generate general hooks for other stories."""
        emoji = SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆')
        hooks = [
            f"{emoji} {league} News: Here's what you need to know",
            f"📰 {league} Update: This story is worth your attention",
            f"{emoji} {league} Spotlight: Don't miss this important development",
            f"🎯 {league} Focus: The latest news that matters to fans"
        ]
        return random.choice(hooks)
    
    def format_stats(self, article: Dict, league: str) -> Optional[str]:
        """Format and present statistics with context and significance."""
        content = article.get('content', '')
        
        # Extract numbers and potential stats from content
        stats_patterns = [
            r'(\d+)-(\d+)',  # Scores like 24-17
            r'(\d+)\s*points?',  # Points scored
            r'(\d+)\s*yards?',  # Yards gained
            r'(\d+)\s*goals?',  # Goals scored
            r'(\d+)\s*assists?',  # Assists
            r'(\d+)\s*rebounds?',  # Rebounds
            r'(\d+)\s*saves?',  # Saves
            r'(\d+)\s*strikeouts?',  # Strikeouts
            r'(\d+)\s*home runs?',  # Home runs
        ]
        
        found_stats = []
        for pattern in stats_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_stats.extend(matches)
        
        if found_stats:
            emoji = SPORTS_LEAGUES.get(league, {}).get('emoji', '📊')
            return f"{emoji} Key Stats: {', '.join(str(stat) for stat in found_stats[:3])}"
        
        return None
    
    def generate_opinion(self, article: Dict, league: str) -> str:
        """Generate opinion content based on article sentiment and league dynamics."""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        # Analyze sentiment and generate appropriate opinion
        if any(word in title + ' ' + content for word in ['record', 'historic', 'best', 'greatest']):
            return self._generate_positive_opinion(league)
        elif any(word in title + ' ' + content for word in ['worst', 'terrible', 'disappointing', 'struggle']):
            return self._generate_critical_opinion(league)
        elif self._is_controversy(title + ' ' + content):
            return self._generate_analytical_opinion(league)
        else:
            return self._generate_balanced_opinion(league)
    
    def _generate_positive_opinion(self, league: str) -> str:
        """Generate positive opinion content."""
        opinions = [
            f"This is exactly the kind of performance that makes {league} so exciting to watch.",
            f"What we're seeing here could define the entire {league} season.",
            f"This level of excellence is why {league} continues to grow its fanbase.",
            f"Moments like these remind us why {league} is must-watch entertainment."
        ]
        return random.choice(opinions)
    
    def _generate_critical_opinion(self, league: str) -> str:
        """Generate critical opinion content."""
        opinions = [
            f"This raises serious questions about the direction of {league}.",
            f"Something needs to change if {league} wants to maintain its reputation.",
            f"This situation highlights ongoing issues within {league}.",
            f"The {league} community deserves better than what we're seeing here."
        ]
        return random.choice(opinions)
    
    def _generate_analytical_opinion(self, league: str) -> str:
        """Generate analytical opinion content."""
        opinions = [
            f"This situation will likely have lasting implications for {league}.",
            f"The ripple effects of this {league} story will be felt for months.",
            f"This is a pivotal moment that could reshape {league} dynamics.",
            f"The {league} landscape may never be quite the same after this."
        ]
        return random.choice(opinions)
    
    def _generate_balanced_opinion(self, league: str) -> str:
        """Generate balanced opinion content."""
        opinions = [
            f"This development adds another interesting layer to the {league} season.",
            f"It will be fascinating to see how this {league} story unfolds.",
            f"This is the kind of storyline that makes {league} so compelling.",
            f"Another reminder of why {league} keeps fans on the edge of their seats."
        ]
        return random.choice(opinions)
    
    def create_phrase_template(self, template_type: str, league: str, **kwargs) -> str:
        """Create dynamic phrases using templates and article data."""
        emoji = SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆')
        
        templates = {
            'breaking_news': [
                f"{emoji} BREAKING: {{headline}}",
                f"🚨 {league} Alert: {{headline}}",
                f"⚡ Just In: {{headline}}"
            ],
            'game_recap': [
                f"{emoji} Final: {{score}} - What a game!",
                f"🔥 {league} Thriller: {{score}}",
                f"⚡ Game Over: {{score}}"
            ],
            'player_spotlight': [
                f"{emoji} Player Focus: {{player_name}} {{achievement}}",
                f"🌟 {league} Star: {{player_name}} {{achievement}}",
                f"👑 Spotlight: {{player_name}} {{achievement}}"
            ],
            'trade_news': [
                f"{emoji} TRADE: {{player_name}} to {{team}}",
                f"🔄 {league} Move: {{player_name}} → {{team}}",
                f"📈 Deal Done: {{player_name}} joins {{team}}"
            ]
        }
        
        if template_type in templates:
            template = random.choice(templates[template_type])
            return template.format(**kwargs)
        
        return f"{emoji} {league} News: {kwargs.get('headline', 'Latest Update')}"
    
    def get_educational_content(self, league: str, article: Dict) -> Optional[Dict]:
        """Select appropriate educational content based on article context."""
        if not self.lessons or league not in self.lessons:
            return None
        
        league_lessons = self.lessons[league]
        content = article.get('content', '').lower()
        title = article.get('title', '').lower()
        
        # Match article content to relevant educational topics
        for topic, lesson in league_lessons.items():
            if any(keyword in content + ' ' + title for keyword in lesson.get('keywords', [])):
                return {
                    'topic': topic,
                    'content': lesson.get('explanation', ''),
                    'emoji': SPORTS_LEAGUES.get(league, {}).get('emoji', '📚')
                }
        
        # Return a random lesson if no specific match
        if league_lessons:
            topic = random.choice(list(league_lessons.keys()))
            return {
                'topic': topic,
                'content': league_lessons[topic].get('explanation', ''),
                'emoji': SPORTS_LEAGUES.get(league, {}).get('emoji', '📚')
            }
        
        return None
    
    def get_term_explanation(self, term: str) -> Optional[str]:
        """Get 25-word explanation for sports terms and concepts."""
        if not self.explainers:
            return None
        
        # Check direct term match
        if term.lower() in self.explainers:
            return self.explainers[term.lower()]
        
        # Check for partial matches in categories
        for category, terms in self.explainers.items():
            if isinstance(terms, dict) and term.lower() in terms:
                return terms[term.lower()]
        
        return None
    
    def process_article_content(self, article: Dict, league: str) -> Dict:
        """Process scraped articles into newsletter-ready content blocks."""
        processed = {
            'original_article': article,
            'league': league,
            'emoji': SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆'),
            'hook': self.generate_hook(article, league),
            'opinion': self.generate_opinion(article, league),
            'stats': self.format_stats(article, league),
            'educational_content': self.get_educational_content(league, article),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add engagement elements
        processed['engagement_score'] = self._calculate_engagement_score(article)
        processed['content_type'] = self._classify_content_type(article)
        
        return processed
    
    def _calculate_engagement_score(self, article: Dict) -> int:
        """Calculate potential engagement score for article."""
        score = 0
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        # High-interest keywords boost score
        for keyword in HIGH_INTEREST_KEYWORDS:
            if keyword in title + ' ' + content:
                score += 2
        
        # Controversy adds engagement
        if self._is_controversy(title + ' ' + content):
            score += 3
        
        # Recent articles score higher
        published_at = article.get('publishedAt', '')
        if published_at:
            try:
                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                hours_old = (datetime.now().replace(tzinfo=pub_date.tzinfo) - pub_date).total_seconds() / 3600
                if hours_old < 6:
                    score += 3
                elif hours_old < 24:
                    score += 1
            except:
                pass
        
        return min(score, 10)  # Cap at 10
    
    def _classify_content_type(self, article: Dict) -> str:
        """Classify article content type for template selection."""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        if self._is_trade_news(title + ' ' + content):
            return 'trade'
        elif self._is_injury_news(title + ' ' + content):
            return 'injury'
        elif self._is_game_result(title + ' ' + content):
            return 'game_result'
        elif self._is_controversy(title + ' ' + content):
            return 'controversy'
        else:
            return 'general'
    
    def generate_newsletter_section(self, articles: List[Dict], league: str, section_type: str) -> Dict:
        """Generate complete newsletter section with processed articles."""
        processed_articles = []
        
        for article in articles[:CONTENT_SETTINGS['max_articles_per_league']]:
            processed = self.process_article_content(article, league)
            processed_articles.append(processed)
        
        # Sort by engagement score
        processed_articles.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        return {
            'league': league,
            'section_type': section_type,
            'emoji': SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆'),
            'articles': processed_articles,
            'total_articles': len(processed_articles),
            'generated_at': datetime.now().isoformat()
        }


# Utility functions for template rendering
def get_league_emoji(league: str) -> str:
    """Get emoji for specific league."""
    return SPORTS_LEAGUES.get(league, {}).get('emoji', '🏆')

def format_league_name(league: str) -> str:
    """Get formatted full name for league."""
    return SPORTS_LEAGUES.get(league, {}).get('full_name', league)

def get_current_season(league: str) -> str:
    """Get current season year for league."""
    return SPORTS_LEAGUES.get(league, {}).get('season_year', '2024-2025')