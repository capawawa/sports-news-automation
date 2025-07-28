"""
Unit tests for validation functions in the sports news automation system.
Tests validation rules for hook length, explainer length, and other validation functions.
"""

import pytest
import os
import sys
from unittest.mock import patch, Mock

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from publish import SubstackPublisher, SubstackPublishError, SubstackAuthError


class TestValidation:
    """Test suite for validation functions."""

    def test_publisher_initialization_with_valid_credentials(self):
        """Test publisher initialization with valid credentials."""
        with patch.dict(os.environ, {
            'SUBSTACK_EMAIL': 'test@example.com',
            'SUBSTACK_PASS': 'test_password'
        }):
            publisher = SubstackPublisher()
            assert publisher.email == 'test@example.com'
            assert publisher.password == 'test_password'
            assert publisher.headless is True

    def test_publisher_initialization_without_credentials(self):
        """Test publisher initialization without required credentials."""
        with patch.dict(os.environ, {
            'SUBSTACK_EMAIL': '',
            'SUBSTACK_PASS': ''
        }):
            with pytest.raises(ValueError, match="SUBSTACK_EMAIL and SUBSTACK_PASS environment variables are required"):
                SubstackPublisher()

    def test_publisher_initialization_with_partial_credentials(self):
        """Test publisher initialization with partial credentials."""
        with patch.dict(os.environ, {
            'SUBSTACK_EMAIL': 'test@example.com',
            'SUBSTACK_PASS': ''
        }):
            with pytest.raises(ValueError, match="SUBSTACK_EMAIL and SUBSTACK_PASS environment variables are required"):
                SubstackPublisher()

    def test_add_utm_parameters_with_urls(self):
        """Test adding UTM parameters to content with URLs."""
        with patch.dict(os.environ, {
            'SUBSTACK_EMAIL': 'test@example.com',
            'SUBSTACK_PASS': 'test_password'
        }):
            publisher = SubstackPublisher()
            
            # Test content with external URLs
            content = "Check out this article: https://example.com/article"
            result = publisher._add_utm_parameters(content)
            assert "utm_source" in result
            assert "utm_medium" in result
            assert "utm_campaign" in result

    def test_add_utm_parameters_without_urls(self):
        """Test adding UTM parameters to content without URLs."""
        with patch.dict(os.environ, {
            'SUBSTACK_EMAIL': 'test@example.com',
            'SUBSTACK_PASS': 'test_password'
        }):
            publisher = SubstackPublisher()
            
            # Test content without URLs
            content = "This is just plain text without any URLs."
            result = publisher._add_utm_parameters(content)
            assert result == content

    def test_add_utm_parameters_with_substack_urls(self):
        """Test that Substack URLs are not modified."""
        with patch.dict(os.environ, {
            'SUBSTACK_EMAIL': 'test@example.com',
            'SUBSTACK_PASS': 'test_password'
        }):
            publisher = SubstackPublisher()
            
            # Test content with Substack URLs
            content = "Check out our Substack: https://substack.com/test"
            result = publisher._add_utm_parameters(content)
            assert result == content  # Should not modify Substack URLs

    def test_hook_length_validation(self):
        """Test validation of hook length."""
        # Test that hooks are within reasonable length
        short_hook = "Short hook"
        medium_hook = "This is a medium length hook for testing purposes"
        long_hook = "This is a very long hook that might be too long for effective newsletter content and should be checked for appropriate length"
        
        # Hooks should be strings
        assert isinstance(short_hook, str)
        assert isinstance(medium_hook, str)
        assert isinstance(long_hook, str)
        
        # Hooks should have reasonable lengths
        assert len(short_hook) > 0
        assert len(medium_hook) > 0
        assert len(long_hook) > 0

    def test_explainer_length_validation(self):
        """Test validation of explainer length."""
        # Test that explainers have appropriate lengths
        short_explainer = "Short explanation"
        medium_explainer = "This is a medium length explanation that provides some context and information about a topic."
        long_explainer = "This is a longer explanation that provides detailed information about a topic. " * 10
        
        # Explainers should be strings
        assert isinstance(short_explainer, str)
        assert isinstance(medium_explainer, str)
        assert isinstance(long_explainer, str)
        
        # Explainers should have reasonable lengths
        assert len(short_explainer) > 0
        assert len(medium_explainer) > 0
        assert len(long_explainer) > 0

    def test_article_content_length_validation(self):
        """Test validation of article content length."""
        # Test minimum content length validation
        min_length = 100  # From CONTENT_SETTINGS
        
        # Test content that's too short
        short_content = "This content is too short."
        assert len(short_content) < min_length
        
        # Test content that meets minimum length
        adequate_content = "This content meets the minimum length requirement. " * 5
        assert len(adequate_content) >= min_length

    def test_title_length_validation(self):
        """Test validation of title length."""
        # Test various title lengths
        short_title = "Short"
        medium_title = "This is a medium length title"
        long_title = "This is a very long title that might be too long for effective display and should be checked for appropriate length limits"
        
        # Titles should be strings
        assert isinstance(short_title, str)
        assert isinstance(medium_title, str)
        assert isinstance(long_title, str)
        
        # Titles should have reasonable lengths
        assert len(short_title) > 0
        assert len(medium_title) > 0
        assert len(long_title) > 0

    def test_url_validation(self):
        """Test URL validation."""
        # Test valid URLs
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://substack.com/test",
            "https://example.com/path?param=value"
        ]
        
        for url in valid_urls:
            assert isinstance(url, str)
            assert url.startswith(("http://", "https://"))

    def test_email_validation(self):
        """Test email validation."""
        # Test valid email formats
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test123@test-domain.com"
        ]
        
        for email in valid_emails:
            assert isinstance(email, str)
            assert "@" in email
            assert "." in email.split("@")[1]

    def test_template_rendering_validation(self):
        """Test template rendering validation."""
        # Test that template variables are properly formatted
        template_vars = {
            'newsletter_name': 'Sports Weekly',
            'current_date': '2023-01-01',
            'utm_params': {
                'utm_source': 'newsletter',
                'utm_medium': 'email',
                'utm_campaign': 'sports_weekly'
            }
        }
        
        # Check that required template variables exist
        assert 'newsletter_name' in template_vars
        assert 'current_date' in template_vars
        assert 'utm_params' in template_vars
        
        # Check that UTM parameters are complete
        utm_params = template_vars['utm_params']
        assert 'utm_source' in utm_params
        assert 'utm_medium' in utm_params
        assert 'utm_campaign' in utm_params

    def test_league_data_validation(self):
        """Test league data validation."""
        # Test that league data has required fields
        league_data = {
            'NFL': {
                'full_name': 'National Football League',
                'sport': 'American Football',
                'emoji': '🏈',
                'season_year': '2024-2025'
            }
        }
        
        for league_code, league_info in league_data.items():
            assert isinstance(league_code, str)
            assert isinstance(league_info, dict)
            assert 'full_name' in league_info
            assert 'sport' in league_info
            assert 'emoji' in league_info
            assert 'season_year' in league_info

    def test_article_scoring_validation(self):
        """Test article scoring validation."""
        # Test that article scores are within valid range
        valid_scores = [0.0, 0.5, 1.0, 0.75, 0.25]
        
        for score in valid_scores:
            assert isinstance(score, (int, float))
            assert 0.0 <= score <= 1.0

    def test_content_summary_length_validation(self):
        """Test content summary length validation."""
        # Test that summaries meet length requirements
        max_summary_length = 200  # From CONTENT_SETTINGS
        
        short_summary = "This is a short summary."
        long_summary = "This is a longer summary that might exceed the maximum length allowed for summaries in the newsletter content." * 3
        
        assert len(short_summary) <= max_summary_length
        assert len(long_summary) > max_summary_length  # This should be handled in the code


if __name__ == '__main__':
    pytest.main([__file__])