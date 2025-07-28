"""
Unit tests for the Sports News Automation System Configuration.
Tests configuration loading and validation.
"""

import pytest
import os
from unittest.mock import patch, mock_open
import sys

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import config module
import config


class TestConfig:
    """Test suite for the configuration module."""

    def test_newsapi_configuration(self):
        """Test NewsAPI configuration."""
        assert hasattr(config, 'NEWSAPI_BASE_URL')
        assert config.NEWSAPI_BASE_URL == "https://newsapi.org/v2"
        
        # Test that NEWSAPI_KEY is defined (value will depend on environment)
        assert hasattr(config, 'NEWSAPI_KEY')

    def test_substack_configuration(self):
        """Test Substack configuration."""
        assert hasattr(config, 'SUBSTACK_EMAIL')
        assert hasattr(config, 'SUBSTACK_PASS')

    def test_newsletter_configuration(self):
        """Test newsletter configuration."""
        assert hasattr(config, 'NEWSLETTER_NAME')
        assert hasattr(config, 'NEWSLETTER_DESCRIPTION')

    def test_sports_leagues_configuration(self):
        """Test sports leagues configuration."""
        assert hasattr(config, 'SPORTS_LEAGUES')
        assert isinstance(config.SPORTS_LEAGUES, dict)
        assert len(config.SPORTS_LEAGUES) > 0

        # Test specific league configurations
        for league_code in ['NFL', 'NBA', 'MLB', 'NHL', 'MLS']:
            assert league_code in config.SPORTS_LEAGUES
            league_info = config.SPORTS_LEAGUES[league_code]
            assert isinstance(league_info, dict)
            assert 'full_name' in league_info
            assert 'sport' in league_info
            assert 'emoji' in league_info

    def test_sports_emojis_configuration(self):
        """Test sports emojis configuration."""
        assert hasattr(config, 'SPORTS_EMOJIS')
        assert isinstance(config.SPORTS_EMOJIS, dict)
        assert len(config.SPORTS_EMOJIS) > 0

        # Test specific emoji mappings
        expected_emojis = ['football', 'basketball', 'baseball', 'hockey', 'soccer']
        for sport in expected_emojis:
            assert sport in config.SPORTS_EMOJIS

    def test_controversy_patterns(self):
        """Test controversy patterns configuration."""
        assert hasattr(config, 'CONTROVERSY_PATTERNS')
        assert isinstance(config.CONTROVERSY_PATTERNS, list)
        assert len(config.CONTROVERSY_PATTERNS) > 0

        # Test that patterns are valid regex strings
        import re
        for pattern in config.CONTROVERSY_PATTERNS:
            assert isinstance(pattern, str)
            # This will raise an exception if pattern is invalid
            re.compile(pattern)

    def test_high_interest_keywords(self):
        """Test high interest keywords configuration."""
        assert hasattr(config, 'HIGH_INTEREST_KEYWORDS')
        assert isinstance(config.HIGH_INTEREST_KEYWORDS, list)
        assert len(config.HIGH_INTEREST_KEYWORDS) > 0

        # Test that keywords are strings
        for keyword in config.HIGH_INTEREST_KEYWORDS:
            assert isinstance(keyword, str)

    def test_newsapi_config(self):
        """Test NewsAPI configuration settings."""
        assert hasattr(config, 'NEWSAPI_CONFIG')
        assert isinstance(config.NEWSAPI_CONFIG, dict)

        # Test required configuration keys
        required_keys = ['endpoints', 'sports_sources', 'categories', 'language', 
                         'country', 'page_size', 'sort_by']
        for key in required_keys:
            assert key in config.NEWSAPI_CONFIG

    def test_content_settings(self):
        """Test content settings configuration."""
        assert hasattr(config, 'CONTENT_SETTINGS')
        assert isinstance(config.CONTENT_SETTINGS, dict)

        # Test required content settings
        required_settings = ['max_articles_per_league', 'min_article_length', 
                           'max_summary_length', 'include_images', 'include_social_links']
        for setting in required_settings:
            assert setting in config.CONTENT_SETTINGS

    def test_utm_parameters(self):
        """Test UTM parameters configuration."""
        assert hasattr(config, 'UTM_PARAMETERS')
        assert isinstance(config.UTM_PARAMETERS, dict)

        # Test required UTM parameters
        required_params = ['utm_source', 'utm_medium', 'utm_campaign']
        for param in required_params:
            assert param in config.UTM_PARAMETERS

    def test_error_config(self):
        """Test error configuration."""
        assert hasattr(config, 'ERROR_CONFIG')
        assert isinstance(config.ERROR_CONFIG, dict)

        # Test required error config settings
        required_settings = ['max_retries', 'retry_delay', 'timeout', 'log_level']
        for setting in required_settings:
            assert setting in config.ERROR_CONFIG

    def test_notification_config(self):
        """Test notification configuration."""
        assert hasattr(config, 'NOTIFICATION_CONFIG')
        assert isinstance(config.NOTIFICATION_CONFIG, dict)

        # Test required notification config settings
        required_settings = ['send_error_notifications', 'send_success_notifications']
        for setting in required_settings:
            assert setting in config.NOTIFICATION_CONFIG

    def test_environment_variable_loading(self):
        """Test that configuration loads environment variables correctly."""
        # Test with specific environment variables
        test_env = {
            'NEWSAPI_KEY': 'test_api_key',
            'SUBSTACK_EMAIL': 'test@example.com',
            'SUBSTACK_PASS': 'test_password'
        }

        with patch.dict(os.environ, test_env):
            # Re-import config to test environment variable loading
            import importlib
            importlib.reload(config)

            assert config.NEWSAPI_KEY == 'test_api_key'
            assert config.SUBSTACK_EMAIL == 'test@example.com'
            assert config.SUBSTACK_PASS == 'test_password'

    def test_default_values(self):
        """Test default values for configuration settings."""
        # Test default newsletter name
        assert config.NEWSLETTER_NAME == os.getenv("NEWSLETTER_NAME", "Sports Weekly")
        
        # Test default newsletter description
        assert config.NEWSLETTER_DESCRIPTION == os.getenv("NEWSLETTER_DESCRIPTION", "Your weekly sports news digest")

    def test_league_priorities(self):
        """Test league priority settings."""
        for league_code, league_info in config.SPORTS_LEAGUES.items():
            # All major leagues should have priority 1
            if league_code in ['NFL', 'NBA', 'MLB', 'NHL']:
                assert league_info.get('priority', 999) == 1

    def test_season_information(self):
        """Test season information in league configurations."""
        # Test that leagues have season information
        for league_code, league_info in config.SPORTS_LEAGUES.items():
            # Major leagues should have season_year
            if league_code in ['NFL', 'NBA', 'MLB', 'NHL', 'MLS']:
                assert 'season_year' in league_info


if __name__ == '__main__':
    pytest.main([__file__])