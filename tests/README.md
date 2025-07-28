# Sports News Automation - Test Suite

This directory contains the test suite for the Sports News Automation system. The tests are written using pytest and cover all major components of the system.

## Test Structure

- `test_scraper.py` - Tests for the article scraping functionality
- `test_phrasing.py` - Tests for the content generation and phrasing engine
- `test_renderer.py` - Tests for the template rendering system
- `test_config.py` - Tests for configuration loading and validation
- `test_validation.py` - Tests for various validation functions
- `conftest.py` - pytest configuration and fixtures

## Requirements

To run the tests, you need to have the required dependencies installed:

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

## Running Tests

### Run all tests

```bash
cd sports-news-automation
python -m pytest tests/
```

### Run a specific test file

```bash
python -m pytest tests/test_scraper.py
```

### Run tests with coverage

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Run tests in verbose mode

```bash
python -m pytest tests/ -v
```

## Test Configuration

The tests use environment variables for configuration. For testing purposes, these are mocked in the `conftest.py` file.

## Writing New Tests

When adding new tests, follow these guidelines:

1. Create a new test file with the naming pattern `test_*.py`
2. Use pytest fixtures for setup and teardown
3. Mock external dependencies (APIs, file system, etc.)
4. Test both positive and negative cases
5. Use descriptive test function names that explain what is being tested

## Test Coverage

The test suite aims to cover:

- Article fetching, filtering, and scoring in the scraper
- Content generation including hooks, stats, and opinions
- Template rendering with various data inputs
- Configuration loading and validation
- Validation functions for content length and format
- Error handling and edge cases

## Continuous Integration

Tests are automatically run in the CI pipeline to ensure code quality and prevent regressions.