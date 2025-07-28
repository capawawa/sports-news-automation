# Sports News Automation System

A complete Python-based sports news automation system that fetches sports articles, generates newsletter content, and publishes to Substack with automated scheduling.

## Features

- **Multi-League Coverage**: Supports NFL, NBA, MLB, NHL, and MLS with real-time season data
- **Automated Content Generation**: Intelligent content curation and newsletter generation
- **Substack Integration**: Automated publishing to Substack newsletters
- **Controversy Detection**: Advanced pattern matching for dramatic sports news
- **Growth Optimization**: UTM tracking and referral systems
- **Automated Scheduling**: GitHub Actions workflow for weekly execution

## Project Structure

```
sports-news-automation/
├── src/                         # Main application code
│   ├── config.py               # Configuration and constants
│   ├── scraper.py              # News API integration
│   ├── phrasing.py             # Content generation
│   ├── renderer.py             # Template rendering
│   ├── publish.py              # Substack publishing
│   └── __main__.py             # Main orchestration
├── templates/                   # Jinja2 templates
│   └── newsletter.j2           # Newsletter template
├── data/                       # Static data files
│   ├── lessons.yaml            # Sports education content
│   └── explainers.yaml         # Keyword explanations
├── .github/workflows/          # GitHub Actions
│   └── weekly.yml              # Automated workflow
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # Documentation
```

## Current Sports League Coverage (2024-2025 Season)

### NFL (National Football League)
- **Season**: 2024-2025
- **Playoffs**: January 11-13 (Wild Card), January 18-19 (Divisional), January 26 (Conference Championships)
- **Super Bowl LIX**: February 9, 2025

### NBA (National Basketball Association)
- **Regular Season**: October 22, 2024 - April 13, 2025
- **Trade Deadline**: February 6, 2025
- **All-Star Weekend**: February 14-16, 2025 (San Francisco, CA)
- **Play-In Tournament**: April 15-18, 2025

### MLB (Major League Baseball)
- **Season**: March 27 - September 28, 2025
- **Games per Team**: 162 games
- **Structure**: 13 games against each divisional team

### NHL (National Hockey League)
- **Season**: October 4, 2024 - June 17, 2025
- **Games per Team**: 82 games
- **Teams**: 32 total teams

### MLS (Major League Soccer)
- **Season**: February 22 - October 18, 2025
- **Matches per Team**: 34 matches
- **New Team**: San Diego FC joins in 2025
- **Key Events**: Rivalry Week (May 14-18), All-Star Game (July 23)

## Setup Instructions

### Prerequisites
- Python 3.8+
- NewsAPI account and API key
- Substack account credentials

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sports-news-automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# NewsAPI Configuration
NEWSAPI_KEY=your_newsapi_key_here

# Substack Configuration
SUBSTACK_EMAIL=your_substack_email@example.com
SUBSTACK_PASS=your_substack_password

# Optional: Newsletter Configuration
NEWSLETTER_NAME=Sports Weekly
NEWSLETTER_DESCRIPTION=Your weekly sports news digest
```

## Configuration

The system is configured through `src/config.py` which includes:

- **Sports Leagues**: Real-time season data for major professional leagues
- **Controversy Detection**: Regex patterns for identifying dramatic sports news
- **Content Settings**: Article limits, summary lengths, and newsletter sections
- **API Configuration**: NewsAPI endpoints and parameters
- **Growth Optimization**: UTM tracking parameters

## Usage

### Manual Execution
```bash
python -m src
```

### Automated Execution
The system includes a GitHub Actions workflow (`.github/workflows/weekly.yml`) for automated weekly execution every Monday at 07:00 ET (12:00 UTC).

## GitHub Actions Setup and Deployment

### Setting Up Automated Execution

1. **Fork or Clone the Repository**
   ```bash
   git clone <your-repository-url>
   cd sports-news-automation
   ```

2. **Configure Repository Secrets**
   Go to your GitHub repository → Settings → Secrets and variables → Actions

   Add the following secrets:
   - `NEWSAPI_KEY`: Your NewsAPI.org API key
   - `SUBSTACK_EMAIL`: Your Substack account email
   - `SUBSTACK_PASS`: Your Substack account password
   - `NEWSLETTER_NAME`: Your newsletter name (optional)
   - `NEWSLETTER_DESCRIPTION`: Your newsletter description (optional)
   - `NOTIFICATION_EMAIL`: Email for error notifications (optional)

3. **Enable GitHub Actions**
   - Go to the Actions tab in your repository
   - Enable workflows if prompted
   - The workflow will automatically run every Monday at 07:00 ET

4. **Manual Trigger**
   You can manually trigger the workflow:
   - Go to Actions → Weekly Sports Newsletter
   - Click "Run workflow"

### Workflow Configuration

The GitHub Actions workflow (`weekly.yml`) includes:
- **Schedule**: Cron job for Monday 07:00 ET (12:00 UTC)
- **Environment Setup**: Python 3.11 with dependency caching
- **Playwright Installation**: Chromium browser for Substack automation
- **Error Handling**: Log upload and failure notifications
- **Security**: All sensitive data managed through GitHub Secrets

## Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NewsAPI       │    │   Content       │    │   Newsletter    │
│   Integration   │───▶│   Generation    │───▶│   Rendering     │
│   (scraper.py)  │    │   (phrasing.py) │    │   (renderer.py) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Configuration │    │   Data Storage  │    │   Substack      │
│   (config.py)   │    │   (YAML files)  │    │   Publishing    │
│                 │    │                 │    │   (publish.py)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **News Fetching**: `scraper.py` queries NewsAPI for sports articles
2. **Content Processing**: `phrasing.py` analyzes and categorizes articles
3. **Template Rendering**: `renderer.py` generates newsletter using Jinja2
4. **Publishing**: `publish.py` automates Substack publishing via Playwright
5. **Orchestration**: `__main__.py` coordinates the entire workflow

### Key Features

- **Multi-League Support**: Covers NFL, NBA, MLB, NHL, MLS with real-time data
- **Intelligent Curation**: Controversy detection and engagement optimization
- **Growth Tracking**: UTM parameters and referral link integration
- **Error Resilience**: Comprehensive retry logic and error handling
- **Automated Scheduling**: GitHub Actions for hands-free operation

## Dependencies

- **playwright**: Web automation for Substack publishing
- **requests**: HTTP requests for NewsAPI integration
- **python-dotenv**: Environment variable management
- **jinja2**: Template rendering for newsletters
- **pyyaml**: YAML file processing for data files

## Features in Detail

### Content Curation
- Fetches articles from NewsAPI with sports-specific filtering
- Detects controversial/dramatic content using pattern matching
- Prioritizes high-engagement keywords and breaking news

### Newsletter Generation
- Uses Jinja2 templates for consistent formatting
- Includes multiple sections: top stories, league updates, player news
- Supports educational content integration

### Growth Optimization
- UTM parameter tracking for analytics
- Referral system integration
- Social media link inclusion

### Error Handling
- Comprehensive retry logic with exponential backoff
- Detailed logging and error notifications
- Graceful degradation for API failures

## Troubleshooting

### Common Issues and Solutions

#### 1. NewsAPI Rate Limits
**Problem**: "API rate limit exceeded" errors
**Solution**: 
- Check your NewsAPI plan limits
- Reduce `page_size` in `config.py`
- Implement request throttling

#### 2. Substack Login Failures
**Problem**: Authentication errors or login timeouts
**Solution**:
- Verify `SUBSTACK_EMAIL` and `SUBSTACK_PASS` credentials
- Check for two-factor authentication (not currently supported)
- Ensure account is not locked or suspended

#### 3. Playwright Browser Issues
**Problem**: Browser launch failures or timeouts
**Solution**:
```bash
# Reinstall Playwright browsers
playwright install chromium
playwright install-deps
```

#### 4. GitHub Actions Workflow Failures
**Problem**: Workflow fails to execute
**Solution**:
- Check repository secrets are properly configured
- Verify workflow permissions in repository settings
- Review workflow logs in Actions tab

#### 5. Template Rendering Errors
**Problem**: Jinja2 template errors or missing variables
**Solution**:
- Check `templates/newsletter.j2` syntax
- Verify all required template variables are provided
- Review `renderer.py` for variable mapping

#### 6. Empty Newsletter Content
**Problem**: Newsletter generates with no articles
**Solution**:
- Verify NewsAPI key is valid and active
- Check internet connectivity
- Review sports league keywords in `config.py`

### Debugging Tips

1. **Enable Verbose Logging**:
   Set `log_level: "DEBUG"` in `config.py`

2. **Run Components Individually**:
   ```bash
   # Test news fetching
   python -c "from src.scraper import NewsAPIClient; client = NewsAPIClient(); print(client.get_sports_news())"
   
   # Test Substack connection
   python -c "from src.publish import SubstackPublisher; pub = SubstackPublisher(headless=False); pub.start_browser()"
   ```

3. **Check Log Files**:
   Review `sports_automation.log` for detailed error information

## Development Setup

### Local Development Environment

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd sports-news-automation
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install Development Dependencies**:
   ```bash
   pip install pytest black flake8 mypy
   ```

3. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your development credentials
   ```

4. **Run Tests**:
   ```bash
   pytest tests/  # If test directory exists
   ```

5. **Code Formatting**:
   ```bash
   black src/
   flake8 src/
   ```

### Contributing Guidelines

1. **Code Style**:
   - Follow PEP 8 guidelines
   - Use type hints where applicable
   - Add docstrings for all functions and classes

2. **Testing**:
   - Write unit tests for new features
   - Test with real API credentials in development
   - Ensure all tests pass before submitting PR

3. **Documentation**:
   - Update README.md for new features
   - Add inline comments for complex logic
   - Update configuration examples

4. **Pull Request Process**:
   - Fork the repository
   - Create feature branch: `git checkout -b feature/your-feature`
   - Commit changes: `git commit -m "Add your feature"`
   - Push to branch: `git push origin feature/your-feature`
   - Submit pull request with detailed description

## API Key Setup Instructions

### NewsAPI Setup
1. Visit [NewsAPI.org](https://newsapi.org/)
2. Create a free account
3. Generate an API key from your dashboard
4. Add the key to your environment variables as `NEWSAPI_KEY`

**Rate Limits**: Free tier allows 1,000 requests per day

### Substack Setup
1. Create a Substack account at [substack.com](https://substack.com)
2. Set up your newsletter publication
3. Use your login credentials for `SUBSTACK_EMAIL` and `SUBSTACK_PASS`

**Note**: Two-factor authentication is not currently supported

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software in accordance with the license terms.

## Acknowledgments

- **NewsAPI**: Provides comprehensive sports news data
- **Substack**: Newsletter publishing platform
- **Playwright**: Browser automation framework
- **GitHub Actions**: Automated workflow execution
- **Sports Leagues**: NFL, NBA, MLB, NHL, MLS for official data sources

## Support and Contact

- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/your-repo/sports-news-automation/issues)
- **Discussions**: Join community discussions in the repository
- **Documentation**: Comprehensive guides available in this README

## Version History

- **v1.0.0**: Initial release with multi-league support and automated publishing
- **Current**: Enhanced with growth optimization and comprehensive automation

---

**Note**: This system uses real-time sports data and is updated regularly to reflect current season information and league structures. All sports league data is sourced from official league websites and verified news sources.
