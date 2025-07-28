"""
Unit tests for the Sports Newsletter Template Rendering System.
Tests template rendering with sample data.
"""

import pytest
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renderer import NewsletterRenderer


class TestNewsletterRenderer:
    """Test suite for the NewsletterRenderer class."""

    @pytest.fixture
    def renderer(self):
        """Create a renderer instance for testing."""
        with patch('renderer.FileSystemLoader'):
            with patch('renderer.Environment'):
                return NewsletterRenderer()

    @pytest.fixture
    def sample_articles_by_league(self):
        """Sample articles organized by league for testing."""
        return {
            'NFL': [
                {
                    'title': 'NFL Team Wins Championship',
                    'description': 'The NFL team won the championship in a thrilling game.',
                    'content': 'Full content about the NFL championship game.',
                    'url': 'https://example.com/nfl-championship',
                    'source': 'NFL News',
                    'publishedAt': '2023-01-01T12:00:00Z',
                    'total_score': 0.9,
                    'controversy_score': 0.1,
                    'interest_score': 0.8
                }
            ],
            'NBA': [
                {
                    'title': 'NBA Star Sets Record',
                    'description': 'The NBA star set a new record for points in a game.',
                    'content': 'Full content about the NBA record-setting performance.',
                    'url': 'https://example.com/nba-record',
                    'source': 'NBA News',
                    'publishedAt': '2023-01-02T14:30:00Z',
                    'total_score': 0.85,
                    'controversy_score': 0.05,
                    'interest_score': 0.8
                }
            ]
        }

    def test_init(self, renderer):
        """Test NewsletterRenderer initialization."""
        assert renderer is not None
        assert hasattr(renderer, 'template_dir')
        assert hasattr(renderer, 'content_generator')

    def test_render_newsletter(self, renderer, sample_articles_by_league):
        """Test newsletter rendering."""
        with patch.object(renderer.env, 'get_template') as mock_get_template:
            # Mock the template
            mock_template = Mock()
            mock_template.render.return_value = "# Test Newsletter\n\nThis is a test."
            mock_get_template.return_value = mock_template

            result = renderer.render_newsletter(sample_articles_by_league)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_prepare_template_data(self, renderer, sample_articles_by_league):
        """Test template data preparation."""
        with patch.object(renderer, '_process_league_content') as mock_process:
            mock_process.return_value = {
                'articles': [],
                'controversy_count': 0,
                'total_count': 0
            }

            template_data = renderer._prepare_template_data(sample_articles_by_league)
            
            assert isinstance(template_data, dict)
            assert 'newsletter_name' in template_data
            assert 'current_date' in template_data
            assert 'top_stories' in template_data
            assert 'league_content' in template_data

    def test_process_league_content(self, renderer):
        """Test league content processing."""
        league_code = 'NFL'
        articles = [
            {
                'title': 'Test Article',
                'description': 'Test description',
                'content': 'Test content',
                'url': 'https://example.com/test',
                'source': 'Test Source',
                'publishedAt': '2023-01-01T12:00:00Z',
                'controversy_score': 0.5,
                'interest_score': 0.7,
                'total_score': 0.6
            }
        ]

        with patch('renderer.SPORTS_LEAGUES', {
            'NFL': {
                'full_name': 'National Football League',
                'emoji': '🏈',
                'season_year': '2024-2025'
            }
        }):
            result = renderer._process_league_content(league_code, articles)
            
            assert isinstance(result, dict)
            assert 'code' in result
            assert 'name' in result
            assert 'emoji' in result
            assert 'articles' in result
            assert result['code'] == 'NFL'

    def test_generate_paid_tier_content(self, renderer, sample_articles_by_league):
        """Test paid tier content generation."""
        with patch('renderer.SPORTS_LEAGUES', {
            'NFL': {
                'full_name': 'National Football League',
                'sport': 'football'
            },
            'NBA': {
                'full_name': 'National Basketball Association',
                'sport': 'basketball'
            }
        }):
            paid_content = renderer._generate_paid_tier_content(sample_articles_by_league)
            
            assert isinstance(paid_content, list)
            # Should generate content for top articles
            assert len(paid_content) >= 0

    def test_create_story_block(self, renderer):
        """Test story block creation."""
        article = {
            'title': 'Test Article',
            'description': 'Test description',
            'url': 'https://example.com/test',
            'source': 'Test Source',
            'publishedAt': '2023-01-01T12:00:00Z',
            'total_score': 0.8
        }

        with patch('renderer.SPORTS_LEAGUES', {
            'NFL': {
                'full_name': 'National Football League',
                'emoji': '🏈'
            }
        }):
            story_block = renderer._create_story_block(article, 'NFL')
            
            assert isinstance(story_block, dict)
            assert 'title' in story_block
            assert 'description' in story_block
            assert 'url' in story_block
            assert 'score' in story_block
            assert story_block['title'] == 'Test Article'

    def test_format_date(self, renderer):
        """Test date formatting."""
        # Test valid date
        date_string = '2023-01-01T12:00:00Z'
        formatted = renderer._format_date(date_string)
        assert isinstance(formatted, str)
        assert len(formatted) > 0

        # Test invalid date
        invalid_date = 'invalid-date'
        formatted = renderer._format_date(invalid_date)
        assert formatted == invalid_date

    def test_truncate_words(self, renderer):
        """Test word truncation."""
        # Test short text
        short_text = "This is a short text."
        truncated = renderer._truncate_words(short_text, 10)
        assert truncated == short_text

        # Test long text
        long_text = "This is a longer text with many words that should be truncated."
        truncated = renderer._truncate_words(long_text, 5)
        assert truncated.endswith('...')

    def test_get_league_emoji(self, renderer):
        """Test league emoji retrieval."""
        with patch('renderer.SPORTS_LEAGUES', {
            'NFL': {'emoji': '🏈'},
            'NBA': {'emoji': '🏀'}
        }):
            # Test existing league
            emoji = renderer._get_league_emoji('NFL')
            assert emoji == '🏈'

            # Test non-existing league
            emoji = renderer._get_league_emoji('UNKNOWN')
            assert emoji == '🏆'

    def test_render_template_string(self, renderer):
        """Test template string rendering."""
        template_string = "Hello {{ name }}!"
        result = renderer.render_template_string(template_string, name="World")
        assert result == "Hello World!"

    def test_validate_template(self, renderer):
        """Test template validation."""
        with patch.object(renderer.env, 'get_template') as mock_get_template:
            # Test valid template
            mock_get_template.return_value = Mock()
            assert renderer.validate_template("test.j2") is True

            # Test invalid template
            mock_get_template.side_effect = Exception("Template not found")
            assert renderer.validate_template("invalid.j2") is False


if __name__ == '__main__':
    pytest.main([__file__])