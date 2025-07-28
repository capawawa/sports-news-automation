"""
Configuration file for pytest.
Contains fixtures and configuration for the test suite.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def mock_config():
    """Mock configuration for tests."""
    with patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_api_key',
        'SUBSTACK_EMAIL': 'test@example.com',
        'SUBSTACK_PASS': 'test_password',
        'NEWSLETTER_NAME': 'Test Newsletter',
        'NEWSLETTER_DESCRIPTION': 'Test Description'
    }):
        yield


@pytest.fixture(scope="function")
def mock_filesystem():
    """Mock filesystem for tests."""
    with patch('builtins.open', mock_open()):
        yield


def mock_open():
    """Create a mock open function for testing."""
    return Mock()


# Configure logging for tests
import logging
logging.basicConfig(level=logging.DEBUG)