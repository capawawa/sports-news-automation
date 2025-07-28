"""
Unit tests for the Sports News Content Generation System.
Tests content generation, hook creation, and phrase building functionality.
"""

import pytest
import os
from unittest.mock import patch, mock_open
import sys

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from phrasing import ContentGenerator


class TestContentGenerator:
    """Test suite for the ContentGenerator class."""

    @pytest.fixture
    def content_generator(self):
        """Create a content generator instance for testing."""
        # Mock the YAML file loading
        with patch('builtins.open', mock_open(read_data="")):
            with patch('yaml.safe_load', return_value={}):
                return ContentGenerator()

    @pytest.fixture
    def sample_article(self):
        """Sample article data for testing."""
        return {
            'title': 'Test Article About Football Trade',
            'description': 'This is a test article about a football trade with significant implications.',
            'content': 'Full content of the test article about a major football trade.',
            'url': 'https://example.com/test-article',
            'source': 'Test Source',
            'publishedAt': '2023-01-01T12:00:00Z'
        }

    def test_init(self, content_generator):
        """Test ContentGenerator initialization."""
        assert content_generator is not None
        assert hasattr(content_generator, 'lessons')
        assert hasattr(content_generator, 'explainers')

    def test_generate_hook_controversy(self, content_generator):
        """Test hook generation for controversial content."""
        article = {
            'title': 'Player arrested for corruption',
            'content': 'The star player was charged with corruption allegations today.'
        }
        
        hook = content_generator.generate_hook(article, 'NFL')
        assert isinstance(hook, str)
        assert len(hook) > 0
        # Should contain one of the controversy hook patterns
        assert any(phrase in hook for phrase in ['BREAKING', 'Alert', 'Drama', 'shocked'])

    def test_generate_hook_trade(self, content_generator):
        """Test hook generation for trade content."""
        article = {
            'title': 'Star player traded to new team',
            'content': 'In a blockbuster deal, the star player has been traded to a new team.'
        }
        
        hook = content_generator.generate_hook(article, 'NBA')
        assert isinstance(hook, str)
        assert len(hook) > 0
        # Should contain one of the trade hook patterns
        assert any(phrase in hook for phrase in ['TRADE', 'Move', 'deal', 'transaction'])

    def test_generate_hook_injury(self, content_generator):
        """Test hook generation for injury content."""
        article = {
            'title': 'Star player suffers serious injury',
            'content': 'The team\'s best player will be out for weeks with a serious injury.'
        }
        
        hook = content_generator.generate_hook(article, 'MLB')
        assert isinstance(hook, str)
        assert len(hook) > 0
        # Should contain one of the injury hook patterns
        assert any(phrase in hook for phrase in ['Injury', 'Health', 'hospitalized', 'sidelined'])

    def test_generate_hook_game_result(self, content_generator):
        """Test hook generation for game result content."""
        article = {
            'title': 'Team wins championship in overtime thriller',
            'content': 'The team won the championship in an overtime thriller with a buzzer beater.'
        }
        
        hook = content_generator.generate_hook(article, 'NHL')
        assert isinstance(hook, str)
        assert len(hook) > 0
        # Should contain one of the game result hook patterns
        assert any(phrase in hook for phrase in ['Recap', 'Thriller', 'Final', 'Action'])

    def test_generate_hook_general(self, content_generator):
        """Test hook generation for general content."""
        article = {
            'title': 'Team announces new schedule',
            'content': 'The team has announced their new schedule for the upcoming season.'
        }
        
        hook = content_generator.generate_hook(article, 'MLS')
        assert isinstance(hook, str)
        assert len(hook) > 0
        # Should contain one of the general hook patterns
        assert any(phrase in hook for phrase in ['News', 'Update', 'Spotlight', 'Focus'])

    def test_format_stats(self, content_generator):
        """Test statistics formatting."""
        article = {
            'content': 'The player scored 35 points and grabbed 12 rebounds in the game.'
        }
        
        stats = content_generator.format_stats(article, 'NBA')
        assert stats is not None
        assert isinstance(stats, str)
        # Should contain the emoji and some stats
        assert '📊' in stats or '🏈' in stats or '🏀' in stats or '⚾' in stats or '🏒' in stats or '⚽' in stats

    def test_generate_opinion(self, content_generator):
        """Test opinion generation."""
        # Test positive opinion
        article_positive = {
            'title': 'Player sets new record',
            'content': 'The player just set a new record for the best performance ever.'
        }
        
        opinion_positive = content_generator.generate_opinion(article_positive, 'NFL')
        assert isinstance(opinion_positive, str)
        assert len(opinion_positive) > 0

        # Test critical opinion
        article_critical = {
            'title': 'Team struggles with terrible performance',
            'content': 'The team had a disappointing showing with the worst performance of the season.'
        }
        
        opinion_critical = content_generator.generate_opinion(article_critical, 'NBA')
        assert isinstance(opinion_critical, str)
        assert len(opinion_critical) > 0

    def test_create_phrase_template(self, content_generator):
        """Test phrase template creation."""
        # Test breaking news template
        phrase = content_generator.create_phrase_template(
            'breaking_news', 'NFL', headline='Test headline'
        )
        assert isinstance(phrase, str)
        assert len(phrase) > 0
        assert '🏈' in phrase or 'BREAKING' in phrase or 'Alert' in phrase

        # Test game recap template
        phrase = content_generator.create_phrase_template(
            'game_recap', 'NBA', score='100-95'
        )
        assert isinstance(phrase, str)
        assert len(phrase) > 0

    def test_process_article_content(self, content_generator, sample_article):
        """Test article content processing."""
        processed = content_generator.process_article_content(sample_article, 'NFL')
        
        assert isinstance(processed, dict)
        assert 'original_article' in processed
        assert 'league' in processed
        assert 'hook' in processed
        assert 'opinion' in processed
        assert 'engagement_score' in processed
        assert 'content_type' in processed

    def test_calculate_engagement_score(self, content_generator):
        """Test engagement score calculation."""
        # Test high engagement article
        article_high = {
            'title': 'Breaking: Historic upset in playoffs',
            'content': 'Underdog team achieves shocking victory in overtime thriller',
            'publishedAt': '2023-01-01T12:00:00Z'
        }
        
        score_high = content_generator._calculate_engagement_score(article_high)
        assert isinstance(score_high, int)
        assert 0 <= score_high <= 10

        # Test low engagement article
        article_low = {
            'title': 'Team practices on Tuesday',
            'content': 'The team had a routine practice session.',
            'publishedAt': '2023-01-01T12:00:00Z'
        }
        
        score_low = content_generator._calculate_engagement_score(article_low)
        assert isinstance(score_low, int)
        assert 0 <= score_low <= 10

    def test_classify_content_type(self, content_generator):
        """Test content type classification."""
        # Test trade content
        article_trade = {
            'title': 'Player traded to new team',
            'content': 'In a blockbuster deal, the player has been traded.'
        }
        content_type = content_generator._classify_content_type(article_trade)
        assert content_type in ['trade', 'injury', 'game_result', 'controversy', 'general']

        # Test injury content
        article_injury = {
            'title': 'Player suffers injury',
            'content': 'The player will be out with a serious injury.'
        }
        content_type = content_generator._classify_content_type(article_injury)
        assert content_type in ['trade', 'injury', 'game_result', 'controversy', 'general']

    def test_is_controversy(self, content_generator):
        """Test controversy detection."""
        # Test with controversial text
        text_controversy = "Player arrested for corruption allegations"
        assert content_generator._is_controversy(text_controversy) is True

        # Test with non-controversial text
        text_normal = "Team wins championship"
        assert content_generator._is_controversy(text_normal) is False

    def test_is_trade_news(self, content_generator):
        """Test trade news detection."""
        # Test with trade text
        text_trade = "Player traded to new team in blockbuster deal"
        assert content_generator._is_trade_news(text_trade) is True

        # Test with non-trade text
        text_normal = "Team wins championship"
        assert content_generator._is_trade_news(text_normal) is False

    def test_is_injury_news(self, content_generator):
        """Test injury news detection."""
        # Test with injury text
        text_injury = "Player suffers serious injury, out for weeks"
        assert content_generator._is_injury_news(text_injury) is True

        # Test with non-injury text
        text_normal = "Team wins championship"
        assert content_generator._is_injury_news(text_normal) is False

    def test_is_game_result(self, content_generator):
        """Test game result detection."""
        # Test with game result text
        text_result = "Team beats opponent 21-14 in thrilling victory"
        assert content_generator._is_game_result(text_result) is True

        # Test with non-game result text
        text_normal = "Team announces new schedule"
        assert content_generator._is_game_result(text_normal) is False


if __name__ == '__main__':
    pytest.main([__file__])