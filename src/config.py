"""
Sports News Automation System Configuration
Contains real, up-to-date configuration data for major sports leagues and system settings.
"""

import os
from datetime import datetime

# API Configuration
NEWSAPI_BASE_URL = "https://newsapi.org/v2"
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Substack Configuration
SUBSTACK_EMAIL = os.getenv("SUBSTACK_EMAIL")
SUBSTACK_PASS = os.getenv("SUBSTACK_PASS")

# Newsletter Configuration
NEWSLETTER_NAME = os.getenv("NEWSLETTER_NAME", "Sports Weekly")
NEWSLETTER_DESCRIPTION = os.getenv("NEWSLETTER_DESCRIPTION", "Your weekly sports news digest")

# Major Professional Sports Leagues Configuration (2024-2025 Season)
SPORTS_LEAGUES = {
    "NFL": {
        "full_name": "National Football League",
        "sport": "American Football",
        "emoji": "🏈",
        "season_year": "2024-2025",
        "regular_season_end": "2025-01-05",
        "playoffs": {
            "wild_card": "2025-01-11 to 2025-01-13",
            "divisional": "2025-01-18 to 2025-01-19",
            "conference_championships": "2025-01-26",
            "super_bowl": "2025-02-09"
        },
        "newsapi_keywords": ["NFL", "football", "Super Bowl", "playoffs"],
        "priority": 1
    },
    "NBA": {
        "full_name": "National Basketball Association",
        "sport": "Basketball",
        "emoji": "🏀",
        "season_year": "2024-2025",
        "regular_season_start": "2024-10-22",
        "regular_season_end": "2025-04-13",
        "key_dates": {
            "trade_deadline": "2025-02-06",
            "all_star_start": "2025-02-14",
            "all_star_end": "2025-02-16",
            "all_star_location": "San Francisco, CA",
            "play_in_start": "2025-04-15",
            "play_in_end": "2025-04-18"
        },
        "newsapi_keywords": ["NBA", "basketball", "All-Star", "trade deadline"],
        "priority": 1
    },
    "MLB": {
        "full_name": "Major League Baseball",
        "sport": "Baseball",
        "emoji": "⚾",
        "season_year": "2025",
        "season_start": "2025-03-27",
        "season_end": "2025-09-28",
        "total_games": 162,
        "structure": "13 games against each divisional team",
        "newsapi_keywords": ["MLB", "baseball", "World Series", "Opening Day"],
        "priority": 1
    },
    "NHL": {
        "full_name": "National Hockey League",
        "sport": "Ice Hockey",
        "emoji": "🏒",
        "season_year": "2024-2025",
        "season_start": "2024-10-04",
        "season_end": "2025-06-17",
        "total_games": 82,
        "total_teams": 32,
        "playoffs_end": "2025-06-17",
        "newsapi_keywords": ["NHL", "hockey", "Stanley Cup", "playoffs"],
        "priority": 1
    },
    "MLS": {
        "full_name": "Major League Soccer",
        "sport": "Soccer",
        "emoji": "⚽",
        "season_year": "2025",
        "season_start": "2025-02-22",
        "season_end": "2025-10-18",
        "total_matches": 34,
        "key_dates": {
            "rivalry_week": "2025-05-14 to 2025-05-18",
            "all_star_game": "2025-07-23",
            "leagues_cup_start": "2025-07-29"
        },
        "expansion_team": "San Diego FC",
        "newsapi_keywords": ["MLS", "soccer", "football", "MLS Cup"],
        "priority": 2
    }
}

# Sports Emoji Mapping
SPORTS_EMOJIS = {
    "football": "🏈",
    "basketball": "🏀", 
    "baseball": "⚾",
    "hockey": "🏒",
    "soccer": "⚽",
    "tennis": "🎾",
    "golf": "⛳",
    "olympics": "🏅",
    "general": "🏆"
}

# Controversy/Drama Detection Patterns
CONTROVERSY_PATTERNS = [
    r"\b(corruption|scandal|investigation|allegations?)\b",
    r"\b(controversy|controversial|dispute|conflict)\b",
    r"\b(suspended|banned|fined|penalty)\b",
    r"\b(mental health|depression|anxiety)\b",
    r"\b(arrest|charged|lawsuit|legal)\b",
    r"\b(fired|dismissed|terminated)\b",
    r"\b(cheating|doping|steroids|PED)\b",
    r"\b(injury|injured|hurt|hospitalized)\b",
    r"\b(trade demand|holdout|contract dispute)\b",
    r"\b(retirement|retiring|quit)\b"
]

# High-Interest Keywords for Engagement
HIGH_INTEREST_KEYWORDS = [
    "breaking", "exclusive", "shocking", "upset", "record", "historic",
    "comeback", "overtime", "buzzer beater", "walk-off", "playoff",
    "championship", "mvp", "rookie", "veteran", "legend", "hall of fame"
]

# NewsAPI Configuration
NEWSAPI_CONFIG = {
    "endpoints": {
        "everything": "/everything",
        "top_headlines": "/top-headlines"
    },
    "sports_sources": [
        "espn",
        "bleacher-report", 
        "nfl-news",
        "nhl-news",
        "nba-official",
        "mlb-news"
    ],
    "categories": ["sports"],
    "language": "en",
    "country": "us",
    "page_size": 100,
    "sort_by": "publishedAt"
}

# Content Generation Settings
CONTENT_SETTINGS = {
    "max_articles_per_league": 5,
    "min_article_length": 100,
    "max_summary_length": 200,
    "include_images": True,
    "include_social_links": True,
    "newsletter_sections": [
        "top_stories",
        "league_updates", 
        "player_news",
        "upcoming_games",
        "educational_content"
    ]
}

# UTM Tracking for Growth Optimization
UTM_PARAMETERS = {
    "utm_source": "newsletter",
    "utm_medium": "email",
    "utm_campaign": "sports_weekly"
}

# Error Handling Configuration
ERROR_CONFIG = {
    "max_retries": 3,
    "retry_delay": 5,  # seconds
    "timeout": 30,  # seconds
    "log_level": "INFO"
}

# Notification Settings
NOTIFICATION_CONFIG = {
    "send_error_notifications": True,
    "send_success_notifications": False,
    "notification_email": os.getenv("NOTIFICATION_EMAIL")
}
