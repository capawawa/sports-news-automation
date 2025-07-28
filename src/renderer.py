"""
Sports Newsletter Template Rendering System
Integrates with Jinja2 templating engine to render newsletter content using processed articles and generated content.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader, Template, TemplateError

from config import (
    SPORTS_LEAGUES, SPORTS_EMOJIS, CONTENT_SETTINGS, 
    NEWSLETTER_NAME, NEWSLETTER_DESCRIPTION, UTM_PARAMETERS
)
from phrasing import ContentGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsletterRenderer:
    """
    Main class for rendering sports newsletter content using Jinja2 templates.
    Processes article data and generates formatted newsletter content.
    """
    
    def __init__(self, template_dir: str = "./templates"):
        """
        Initialize the renderer with Jinja2 environment.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self.content_generator = ContentGenerator()
        
        # Initialize Jinja2 environment
        try:
            self.env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # Add custom filters
            self.env.filters['format_date'] = self._format_date
            self.env.filters['truncate_words'] = self._truncate_words
            self.env.filters['get_league_emoji'] = self._get_league_emoji
            
        except Exception as e:
            logger.error(f"Failed to initialize Jinja2 environment: {e}")
            raise
    
    def render_newsletter(self, articles_by_league: Dict[str, List[Dict]], 
                         template_name: str = "newsletter.j2") -> str:
        """
        Render complete newsletter using article data and template.
        
        Args:
            articles_by_league: Dictionary of articles organized by league
            template_name: Name of the Jinja2 template file
            
        Returns:
            Rendered newsletter content as Markdown string
        """
        try:
            # Load template
            template = self.env.get_template(template_name)
            
            # Prepare template data
            template_data = self._prepare_template_data(articles_by_league)
            
            # Render template
            rendered_content = template.render(**template_data)
            
            logger.info("Newsletter rendered successfully")
            return rendered_content
            
        except TemplateError as e:
            logger.error(f"Template rendering error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during rendering: {e}")
            raise
    
    def _prepare_template_data(self, articles_by_league: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Prepare all data needed for template rendering.
        
        Args:
            articles_by_league: Dictionary of articles organized by league
            
        Returns:
            Dictionary containing all template variables
        """
        # Generate content blocks for each league
        league_content = {}
        top_stories = []
        educational_content = []
        
        # Process articles by league priority
        sorted_leagues = sorted(
            SPORTS_LEAGUES.items(), 
            key=lambda x: x[1].get('priority', 999)
        )
        
        for league_code, league_info in sorted_leagues:
            articles = articles_by_league.get(league_code, [])
            if not articles:
                continue
                
            # Generate content for this league
            league_data = self._process_league_content(league_code, articles)
            league_content[league_code] = league_data
            
            # Add top stories (highest scoring articles across all leagues)
            for article in articles[:2]:  # Top 2 per league for main stories
                if article.get('total_score', 0) > 0.6:  # High-quality threshold
                    story_data = self._create_story_block(article, league_code)
                    top_stories.append(story_data)
            
            # Generate educational content
            for article in articles[:1]:  # One educational piece per league
                edu_content = self.content_generator.get_educational_content(league_code, article)
                if edu_content:
                    educational_content.append(edu_content)
        
        # Sort top stories by score
        top_stories.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Prepare template variables
        template_data = {
            'newsletter_name': NEWSLETTER_NAME,
            'newsletter_description': NEWSLETTER_DESCRIPTION,
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'current_day': datetime.now().strftime('%A'),
            'top_stories': top_stories[:5],  # Limit to top 5 stories
            'league_content': league_content,
            'educational_content': educational_content[:3],  # Limit to 3 educational pieces
            'sports_leagues': SPORTS_LEAGUES,
            'sports_emojis': SPORTS_EMOJIS,
            'utm_params': UTM_PARAMETERS,
            'total_articles': sum(len(articles) for articles in articles_by_league.values()),
            'leagues_covered': len([l for l, a in articles_by_league.items() if a]),
            'referral_link': os.getenv('SUBSTACK_REFERRAL_LINK', 'https://your-newsletter.substack.com/subscribe?utm_source=referral'),
            'paid_tier_content': self._generate_paid_tier_content(articles_by_league),
            'archive_link': os.getenv('SUBSTACK_ARCHIVE_LINK', 'https://your-newsletter.substack.com/archive')
        }
        
        return template_data
    
    def _process_league_content(self, league_code: str, articles: List[Dict]) -> Dict[str, Any]:
        """
        Process articles for a specific league into template-ready format.
        
        Args:
            league_code: League identifier (e.g., 'NFL', 'NBA')
            articles: List of articles for this league
            
        Returns:
            Dictionary containing processed league content
        """
        league_info = SPORTS_LEAGUES.get(league_code, {})
        
        # Categorize articles
        controversy_articles = [a for a in articles if a.get('controversy_score', 0) > 0.5]
        regular_articles = [a for a in articles if a.get('controversy_score', 0) <= 0.5]
        
        # Generate content blocks
        league_data = {
            'code': league_code,
            'name': league_info.get('full_name', league_code),
            'emoji': league_info.get('emoji', '🏆'),
            'season': league_info.get('season_year', '2024-2025'),
            'articles': [],
            'controversy_count': len(controversy_articles),
            'total_count': len(articles)
        }
        
        # Process each article
        for article in articles:
            article_data = {
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'source': article['source'],
                'published_at': article['published_at'],
                'hook': self.content_generator.generate_hook(article, league_code),
                'opinion': self.content_generator.generate_opinion(article, league_code),
                'controversy_score': article.get('controversy_score', 0),
                'interest_score': article.get('interest_score', 0),
                'total_score': article.get('total_score', 0),
                'is_controversy': article.get('controversy_score', 0) > 0.5,
                'is_high_interest': article.get('interest_score', 0) > 0.5
            }
            
            league_data['articles'].append(article_data)
        
        return league_data
    
    def _generate_paid_tier_content(self, articles_by_league: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """
        Generate bonus content for paid subscribers.
        
        Args:
            articles_by_league: Dictionary of articles organized by league
            
        Returns:
            List of paid tier content blocks
        """
        paid_content = []
        
        # Generate bonus quizzes and insights for top stories
        all_articles = []
        for articles in articles_by_league.values():
            all_articles.extend(articles)
        
        # Sort by total score and take top articles for bonus content
        top_articles = sorted(all_articles, key=lambda x: x.get('total_score', 0), reverse=True)[:3]
        
        for i, article in enumerate(top_articles):
            league_code = article.get('league', 'GENERAL')
            league_info = SPORTS_LEAGUES.get(league_code, {})
            
            bonus_content = {
                'title': f"Bonus Insight #{i+1}: {league_info.get('full_name', 'Sports')} Deep Dive",
                'content': f"Exclusive analysis of {article['title'][:50]}... - This story has significant implications for the {league_info.get('full_name', 'league')} season.",
                'quiz': {
                    'question': f"What makes this {league_info.get('sport', 'sports')} story particularly significant?",
                    'answer': f"The high controversy and interest scores indicate major impact on {league_info.get('full_name', 'the league')}."
                }
            }
            paid_content.append(bonus_content)
        
        return paid_content
    
    def _create_story_block(self, article: Dict, league_code: str) -> Dict[str, Any]:
        """
        Create a story block for top stories section.
        
        Args:
            article: Article data
            league_code: League identifier
            
        Returns:
            Dictionary containing story block data
        """
        return {
            'title': article['title'],
            'description': article['description'],
            'url': article['url'],
            'source': article['source'],
            'league': league_code,
            'league_name': SPORTS_LEAGUES.get(league_code, {}).get('full_name', league_code),
            'emoji': SPORTS_LEAGUES.get(league_code, {}).get('emoji', '🏆'),
            'hook': self.content_generator.generate_hook(article, league_code),
            'score': article.get('total_score', 0),
            'published_at': article['published_at']
        }
    
    # Custom Jinja2 filters
    def _format_date(self, date_string: str) -> str:
        """Format ISO date string for display."""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return date_string
    
    def _truncate_words(self, text: str, word_count: int = 30) -> str:
        """Truncate text to specified word count."""
        words = text.split()
        if len(words) <= word_count:
            return text
        return ' '.join(words[:word_count]) + '...'
    
    def _get_league_emoji(self, league_code: str) -> str:
        """Get emoji for league code."""
        return SPORTS_LEAGUES.get(league_code, {}).get('emoji', '🏆')
    
    def render_template_string(self, template_string: str, **kwargs) -> str:
        """
        Render a template from string content.
        
        Args:
            template_string: Template content as string
            **kwargs: Template variables
            
        Returns:
            Rendered content
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"Error rendering template string: {e}")
            raise
    
    def validate_template(self, template_name: str) -> bool:
        """
        Validate that a template exists and can be loaded.
        
        Args:
            template_name: Name of template file
            
        Returns:
            True if template is valid, False otherwise
        """
        try:
            self.env.get_template(template_name)
            return True
        except Exception as e:
            logger.error(f"Template validation failed for {template_name}: {e}")
            return False


def main():
    """Test function for the renderer."""
    try:
        # Initialize renderer
        renderer = NewsletterRenderer()
        
        # Test template validation
        if renderer.validate_template("newsletter.j2"):
            print("✓ Newsletter template is valid")
        else:
            print("✗ Newsletter template validation failed")
            
        print("Renderer initialized successfully")
        
    except Exception as e:
        print(f"Error testing renderer: {e}")


if __name__ == "__main__":
    main()