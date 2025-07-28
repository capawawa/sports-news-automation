"""
Unit tests for the Sports News Scraper module.
Tests article fetching, filtering, and scoring functionality.
"""

import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the path so we can import the modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import SportsNewsScraper, NewsAPIError, RateLimitError


class TestSportsNewsScraper:
    """Test suite for the SportsNewsScraper class."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        with patch.dict(os.environ, {"NEWSAPI_KEY": "test_key"}):
            return SportsNewsScraper()

    @pytest.fixture
    def mock_article_data(self):
        """Sample article data for testing."""
        return {
            'articles': [
                {
                    'title': 'Test Article 1',
                    'description': 'This is a test article description with sufficient content to pass validation.',
                    'content': 'This is the full content of the test article with enough text to meet minimum requirements.',
                    'url': 'https://example.com/test-article-1',
                    'source': {'name': 'Test Source'},
                    'publishedAt': '2023-01-01T12:00:00Z',
                    'urlToImage': 'https://example.com/image1.jpg'
                },
                {
                    'title': 'Test Article 2',
                    'description': 'Another test article with different content.',
                    'content': 'Full content for the second test article with sufficient length for testing purposes.',
                    'url': 'https://example.com/test-article-2',
                    'source': {'name': 'Another Source'},
                    'publishedAt': '2023-01-02T14:30:00Z',
                    'urlToImage': 'https://example.com/image2.jpg'
                }
            ]
        }

    def test_init_with_valid_api_key(self, scraper):
        """Test scraper initialization with valid API key."""
        assert scraper.api_key == "test_key"
        assert scraper.base_url == "https://newsapi.org/v2"

    def test_init_without_api_key(self):
        """Test scraper initialization without API key raises ValueError."""
        with patch.dict(os.environ, {"NEWSAPI_KEY": ""}):
            with pytest.raises(ValueError, match="NEWSAPI_KEY environment variable is required"):
                SportsNewsScraper()

    def test_make_request_with_retry_success(self, scraper):
        """Test successful API request."""
        with patch('scraper.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": "data"}
            mock_get.return_value = mock_response

            result = scraper._make_request_with_retry("https://test.com", {"param": "value"})
            assert result == {"test": "data"}

    def test_make_request_with_retry_rate_limit(self, scraper):
        """Test rate limit handling with retries."""
        with patch('scraper.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers.get.return_value = "1"
            mock_get.return_value = mock_response

            with pytest.raises(RateLimitError):
                scraper._make_request_with_retry("https://test.com", {"param": "value"})

    def test_process_article_valid(self, scraper):
        """Test processing of a valid article."""
        league_info = {
            'full_name': 'Test League',
            'emoji': '🏆',
            'newsapi_keywords': ['test']
        }

        article = {
            'title': 'Test Article',
            'description': 'This is a test article description.',
            'content': 'Full content of the test article.',
            'url': 'https://example.com/test',
            'source': {'name': 'Test Source'},
            'publishedAt': '2023-01-01T12:00:00Z',
            'urlToImage': 'https://example.com/image.jpg'
        }

        result = scraper._process_article(article, 'TEST', league_info)

        assert result is not None
        assert result['title'] == 'Test Article'
        assert result['league'] == 'TEST'
        assert 'controversy_score' in result
        assert 'interest_score' in result
        assert 'recency_score' in result

    def test_process_article_invalid(self, scraper):
        """Test processing of an invalid article (missing title)."""
        league_info = {
            'full_name': 'Test League',
            'emoji': '🏆'
        }

        article = {
            'description': 'This is a test article description.',
            'url': 'https://example.com/test'
        }

        result = scraper._process_article(article, 'TEST', league_info)
        assert result is None

    def test_calculate_controversy_score(self, scraper):
        """Test controversy score calculation."""
        # Test with controversial content
        title = "Player arrested for corruption"
        description = "The star player was charged with corruption allegations today."
        score = scraper._calculate_controversy_score(title, description)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

        # Test with non-controversial content
        title = "Team wins championship"
        description = "The team celebrated their victory in the finals."
        score = scraper._calculate_controversy_score(title, description)
        assert score == 0.0

    def test_calculate_interest_score(self, scraper):
        """Test interest score calculation."""
        # Test with high interest content
        title = "Breaking: Historic upset in playoffs"
        description = "Underdog team achieves shocking victory in overtime thriller"
        score = scraper._calculate_interest_score(title, description)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

        # Test with low interest content
        title = "Team practices on Tuesday"
        description = "The team had a routine practice session."
        score = scraper._calculate_interest_score(title, description)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_calculate_recency_score(self, scraper):
        """Test recency score calculation."""
        # Test with recent article
        recent_date = datetime.now().isoformat() + 'Z'
        score = scraper._calculate_recency_score(recent_date)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

        # Test with old article
        old_date = (datetime.now() - timedelta(days=14)).isoformat() + 'Z'
        score = scraper._calculate_recency_score(old_date)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_rank_articles(self, scraper):
        """Test article ranking functionality."""
        articles = [
            {
                'title': 'High controversy article',
                'description': 'Controversial content with breaking news',
                'publishedAt': datetime.now().isoformat() + 'Z',
                'controversy_score': 0.8,
                'interest_score': 0.7,
                'recency_score': 0.9
            },
            {
                'title': 'Low interest article',
                'description': 'Routine practice session update',
                'publishedAt': datetime.now().isoformat() + 'Z',
                'controversy_score': 0.1,
                'interest_score': 0.1,
                'recency_score': 0.2
            }
        ]

        ranked = scraper._rank_articles(articles)
        assert len(ranked) == 2
        # First article should have higher total score
        assert ranked[0]['total_score'] > ranked[1]['total_score']

    def test_get_league_summary(self, scraper):
        """Test league summary generation."""
        articles_by_league = {
            'NFL': [
                {
                    'title': 'Test Article',
                    'description': 'Test description',
                    'publishedAt': '2023-01-01T12:00:00Z',
                    'controversy_score': 0.8,
                    'interest_score': 0.7,
                    'total_score': 0.75
                }
            ],
            'NBA': []
        }

        summary = scraper.get_league_summary(articles_by_league)
        
        assert 'total_articles' in summary
        assert 'leagues_covered' in summary
        assert 'high_controversy_articles' in summary
        assert 'high_interest_articles' in summary
        assert 'league_breakdown' in summary
        assert summary['total_articles'] == 1
        assert summary['leagues_covered'] == 1


if __name__ == '__main__':
    pytest.main([__file__])