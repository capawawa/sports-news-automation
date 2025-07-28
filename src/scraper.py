"""
Sports News Scraper Module
Fetches and categorizes sports articles using News API with league-specific filtering and ranking.
"""

import os
import re
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

from config import (
    NEWSAPI_BASE_URL, NEWSAPI_KEY, SPORTS_LEAGUES, CONTROVERSY_PATTERNS,
    HIGH_INTEREST_KEYWORDS, NEWSAPI_CONFIG, ERROR_CONFIG, CONTENT_SETTINGS
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, ERROR_CONFIG["log_level"]))
logger = logging.getLogger(__name__)


class NewsAPIError(Exception):
    """Custom exception for News API related errors"""
    pass


class RateLimitError(NewsAPIError):
    """Exception for rate limit errors"""
    pass


class SportsNewsScraper:
    """
    Sports news scraper that fetches articles from News API and categorizes them by league.
    """

    def __init__(self):
        """Initialize the scraper with API configuration."""
        if not NEWSAPI_KEY:
            raise ValueError("NEWSAPI_KEY environment variable is required")

        self.api_key = NEWSAPI_KEY
        self.base_url = NEWSAPI_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SportsNewsAutomation/1.0',
            'X-Api-Key': self.api_key
        })

        # Compile regex patterns for performance
        self.controversy_patterns = [re.compile(pattern, re.IGNORECASE) 
                                   for pattern in CONTROVERSY_PATTERNS]
        self.high_interest_pattern = re.compile(
            r'\b(' + '|'.join(HIGH_INTEREST_KEYWORDS) + r')\b', 
            re.IGNORECASE
        )

    def _make_request_with_retry(self, url: str, params: Dict) -> Dict:
        """
        Make API request with exponential backoff retry logic.

        Args:
            url: API endpoint URL
            params: Request parameters

        Returns:
            JSON response data

        Raises:
            NewsAPIError: For API-related errors
            RateLimitError: For persistent rate limiting
        """
        max_retries = ERROR_CONFIG["max_retries"]
        retry_delay = ERROR_CONFIG["retry_delay"]
        timeout = ERROR_CONFIG["timeout"]

        for attempt in range(max_retries):
            try:
                logger.info(f"Making API request (attempt {attempt + 1}/{max_retries})")
                response = self.session.get(url, params=params, timeout=timeout)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit hit
                    retry_after = int(response.headers.get('Retry-After', retry_delay))
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limit hit, waiting {retry_after} seconds")
                        time.sleep(retry_after)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        raise RateLimitError("Persistent rate limit error")
                elif response.status_code == 401:
                    raise NewsAPIError("Invalid API key")
                elif response.status_code == 400:
                    raise NewsAPIError(f"Bad request: {response.text}")
                else:
                    response.raise_for_status()

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Request failed: {e}, retrying in {retry_delay} seconds")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise NewsAPIError(f"Request failed after {max_retries} attempts: {e}")

        raise NewsAPIError("Max retries exceeded")

    def fetch_sports_articles(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """
        Fetch sports articles for all configured leagues.

        Args:
            days_back: Number of days to look back for articles

        Returns:
            Dictionary with league names as keys and article lists as values
        """
        logger.info(f"Fetching sports articles from last {days_back} days")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        all_articles = {}

        for league_code, league_info in SPORTS_LEAGUES.items():
            try:
                logger.info(f"Fetching articles for {league_code}")
                articles = self._fetch_league_articles(
                    league_code, league_info, start_date, end_date
                )
                all_articles[league_code] = articles

                # Small delay between requests to be respectful
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error fetching articles for {league_code}: {e}")
                all_articles[league_code] = []

        return all_articles

    def _fetch_league_articles(self, league_code: str, league_info: Dict, 
                              start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch articles for a specific league.

        Args:
            league_code: League identifier (e.g., 'NFL', 'NBA')
            league_info: League configuration from SPORTS_LEAGUES
            start_date: Start date for article search
            end_date: End date for article search

        Returns:
            List of processed articles for the league
        """
        # Build search query from league keywords
        keywords = league_info.get("newsapi_keywords", [league_code])
        query = " OR ".join(keywords)

        # API parameters
        params = {
            'q': query,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'language': NEWSAPI_CONFIG["language"],
            'sortBy': NEWSAPI_CONFIG["sort_by"],
            'pageSize': NEWSAPI_CONFIG["page_size"]
        }

        # Add sources if configured
        if NEWSAPI_CONFIG.get("sports_sources"):
            params['sources'] = ','.join(NEWSAPI_CONFIG["sports_sources"])

        url = f"{self.base_url}{NEWSAPI_CONFIG['endpoints']['everything']}"

        try:
            response_data = self._make_request_with_retry(url, params)
            articles = response_data.get('articles', [])

            logger.info(f"Retrieved {len(articles)} raw articles for {league_code}")

            # Process and filter articles
            processed_articles = []
            for article in articles:
                processed_article = self._process_article(article, league_code, league_info)
                if processed_article:
                    processed_articles.append(processed_article)

            # Rank articles by relevance and interest
            ranked_articles = self._rank_articles(processed_articles)

            # Limit to max articles per league
            max_articles = CONTENT_SETTINGS["max_articles_per_league"]
            final_articles = ranked_articles[:max_articles]

            logger.info(f"Processed {len(final_articles)} articles for {league_code}")
            return final_articles

        except Exception as e:
            logger.error(f"Error fetching articles for {league_code}: {e}")
            return []

    def _process_article(self, article: Dict, league_code: str, 
                        league_info: Dict) -> Optional[Dict]:
        """
        Process and validate a single article.

        Args:
            article: Raw article data from News API
            league_code: League identifier
            league_info: League configuration

        Returns:
            Processed article dictionary or None if invalid
        """
        # Basic validation
        if not article.get('title') or not article.get('description'):
            return None

        # Check minimum content length
        content = article.get('content', '') or article.get('description', '')
        if len(content) < CONTENT_SETTINGS["min_article_length"]:
            return None

        # Extract and clean data
        processed = {
            'title': article['title'].strip(),
            'description': article['description'].strip(),
            'url': article['url'],
            'source': article.get('source', {}).get('name', 'Unknown'),
            'published_at': article['publishedAt'],
            'url_to_image': article.get('urlToImage'),
            'content': content,
            'league': league_code,
            'league_info': league_info,
            'emoji': league_info.get('emoji', '🏆')
        }

        # Add controversy score
        processed['controversy_score'] = self._calculate_controversy_score(
            processed['title'], processed['description']
        )

        # Add interest score
        processed['interest_score'] = self._calculate_interest_score(
            processed['title'], processed['description']
        )

        # Calculate recency score (more recent = higher score)
        processed['recency_score'] = self._calculate_recency_score(
            processed['published_at']
        )

        return processed

    def _calculate_controversy_score(self, title: str, description: str) -> float:
        """
        Calculate controversy score based on patterns in title and description.

        Args:
            title: Article title
            description: Article description

        Returns:
            Controversy score (0.0 to 1.0)
        """
        text = f"{title} {description}".lower()
        matches = 0

        for pattern in self.controversy_patterns:
            if pattern.search(text):
                matches += 1

        # Normalize score (max possible matches = len(controversy_patterns))
        return min(matches / len(self.controversy_patterns), 1.0)

    def _calculate_interest_score(self, title: str, description: str) -> float:
        """
        Calculate interest score based on high-interest keywords.

        Args:
            title: Article title
            description: Article description

        Returns:
            Interest score (0.0 to 1.0)
        """
        text = f"{title} {description}"
        matches = len(self.high_interest_pattern.findall(text))

        # Normalize score (arbitrary max of 5 keywords for scaling)
        return min(matches / 5.0, 1.0)

    def _calculate_recency_score(self, published_at: str) -> float:
        """
        Calculate recency score based on publication time.

        Args:
            published_at: ISO format timestamp

        Returns:
            Recency score (0.0 to 1.0, where 1.0 is most recent)
        """
        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.now(pub_date.tzinfo)
            hours_ago = (now - pub_date).total_seconds() / 3600

            # Score decreases over 168 hours (7 days)
            return max(0.0, 1.0 - (hours_ago / 168.0))
        except Exception:
            return 0.5  # Default score if parsing fails

    def _rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Rank articles by combined score of controversy, interest, and recency.

        Args:
            articles: List of processed articles

        Returns:
            Articles sorted by ranking score (highest first)
        """
        def calculate_total_score(article):
            # Weighted scoring: controversy and interest are more important
            return (
                article['controversy_score'] * 0.4 +
                article['interest_score'] * 0.4 +
                article['recency_score'] * 0.2
            )

        # Add total score to each article
        for article in articles:
            article['total_score'] = calculate_total_score(article)

        # Sort by total score (descending)
        return sorted(articles, key=lambda x: x['total_score'], reverse=True)

    def get_league_summary(self, articles_by_league: Dict[str, List[Dict]]) -> Dict:
        """
        Generate summary statistics for fetched articles.

        Args:
            articles_by_league: Dictionary of articles organized by league

        Returns:
            Summary statistics dictionary
        """
        summary = {
            'total_articles': 0,
            'leagues_covered': 0,
            'high_controversy_articles': 0,
            'high_interest_articles': 0,
            'league_breakdown': {}
        }

        for league, articles in articles_by_league.items():
            if articles:
                summary['leagues_covered'] += 1
                summary['total_articles'] += len(articles)

                high_controversy = sum(1 for a in articles if a['controversy_score'] > 0.5)
                high_interest = sum(1 for a in articles if a['interest_score'] > 0.5)

                summary['high_controversy_articles'] += high_controversy
                summary['high_interest_articles'] += high_interest

                summary['league_breakdown'][league] = {
                    'article_count': len(articles),
                    'high_controversy': high_controversy,
                    'high_interest': high_interest,
                    'avg_score': sum(a['total_score'] for a in articles) / len(articles)
                }

        return summary


def main():
    """Test function for the scraper."""
    try:
        scraper = SportsNewsScraper()
        articles = scraper.fetch_sports_articles(days_back=3)
        summary = scraper.get_league_summary(articles)

        print("\n=== Sports News Scraper Test ===")
        print(f"Total articles fetched: {summary['total_articles']}")
        print(f"Leagues covered: {summary['leagues_covered']}")
        print(f"High controversy articles: {summary['high_controversy_articles']}")
        print(f"High interest articles: {summary['high_interest_articles']}")

        print("\n=== League Breakdown ===")
        for league, stats in summary['league_breakdown'].items():
            print(f"{league}: {stats['article_count']} articles (avg score: {stats['avg_score']:.2f})")

        # Show top article from each league
        print("\n=== Top Articles by League ===")
        for league, league_articles in articles.items():
            if league_articles:
                top_article = league_articles[0]
                print(f"\n{league} {top_article['emoji']}: {top_article['title']}")
                print(f"  Score: {top_article['total_score']:.2f} | Source: {top_article['source']}")
                print(f"  Controversy: {top_article['controversy_score']:.2f} | Interest: {top_article['interest_score']:.2f}")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
