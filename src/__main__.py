"""
Sports News Automation System - Main Orchestration
Coordinates the complete workflow: scraping → content generation → rendering → publishing
"""

import os
import sys
import logging
import smtplib
import traceback
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Import system components
from config import (
    NEWSAPI_KEY, SUBSTACK_EMAIL, SUBSTACK_PASS, NEWSLETTER_NAME,
    ERROR_CONFIG, NOTIFICATION_CONFIG, CONTENT_SETTINGS
)
from scraper import SportsNewsScraper, NewsAPIError
from phrasing import ContentGenerator
from renderer import NewsletterRenderer
from publish import SubstackPublisher, SubstackPublishError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, ERROR_CONFIG["log_level"]),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sports_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AutomationError(Exception):
    """Base exception for automation system errors"""
    pass


class ConfigurationError(AutomationError):
    """Exception for configuration issues"""
    pass


class WorkflowError(AutomationError):
    """Exception for workflow execution issues"""
    pass


class SportsNewsAutomation:
    """
    Main orchestration class for the sports news automation system.
    Coordinates scraping, content generation, rendering, and publishing.
    """
    
    def __init__(self):
        """Initialize the automation system with all components."""
        self.scraper: Optional[SportsNewsScraper] = None
        self.content_generator: Optional[ContentGenerator] = None
        self.renderer: Optional[NewsletterRenderer] = None
        self.publisher: Optional[SubstackPublisher] = None
        
        # Validate configuration
        self._validate_configuration()
        
        # Initialize components
        self._initialize_components()
    
    def _validate_configuration(self):
        """Validate that all required environment variables are set."""
        required_vars = {
            'NEWSAPI_KEY': NEWSAPI_KEY,
            'SUBSTACK_EMAIL': SUBSTACK_EMAIL,
            'SUBSTACK_PASS': SUBSTACK_PASS
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            logger.info("Initializing system components...")
            
            # Initialize scraper
            self.scraper = SportsNewsScraper()
            logger.info("✓ News scraper initialized")
            
            # Initialize content generator
            self.content_generator = ContentGenerator()
            logger.info("✓ Content generator initialized")
            
            # Initialize renderer
            self.renderer = NewsletterRenderer()
            logger.info("✓ Newsletter renderer initialized")
            
            # Initialize publisher (will be used in context manager)
            logger.info("✓ All components initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize components: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
    
    def run_workflow(self, days_back: int = 7, is_draft: bool = False) -> bool:
        """
        Execute the complete automation workflow.
        
        Args:
            days_back: Number of days to look back for articles
            is_draft: Whether to save as draft instead of publishing
            
        Returns:
            True if workflow completed successfully, False otherwise
        """
        workflow_start_time = datetime.now()
        logger.info(f"Starting sports news automation workflow at {workflow_start_time}")
        
        try:
            # Step 1: Scrape articles
            logger.info("Step 1: Scraping sports articles...")
            articles_by_league = self._scrape_articles(days_back)
            
            if not any(articles_by_league.values()):
                raise WorkflowError("No articles found for any league")
            
            total_articles = sum(len(articles) for articles in articles_by_league.values())
            logger.info(f"✓ Scraped {total_articles} articles across {len(articles_by_league)} leagues")
            
            # Step 2: Generate newsletter content
            logger.info("Step 2: Rendering newsletter content...")
            newsletter_content = self._render_newsletter(articles_by_league)
            
            if not newsletter_content:
                raise WorkflowError("Failed to generate newsletter content")
            
            logger.info("✓ Newsletter content rendered successfully")
            
            # Step 3: Generate newsletter title
            newsletter_title = self._generate_newsletter_title(articles_by_league)
            logger.info(f"✓ Generated newsletter title: {newsletter_title}")
            
            # Step 4: Publish to Substack
            logger.info("Step 3: Publishing to Substack...")
            success = self._publish_newsletter(newsletter_title, newsletter_content, is_draft)
            
            if not success:
                raise WorkflowError("Failed to publish newsletter to Substack")
            
            logger.info(f"✓ Newsletter {'drafted' if is_draft else 'published'} successfully")
            
            # Calculate execution time
            execution_time = datetime.now() - workflow_start_time
            logger.info(f"Workflow completed successfully in {execution_time}")
            
            # Send success notification if configured
            if NOTIFICATION_CONFIG.get("send_success_notifications", False):
                self._send_notification(
                    subject=f"Sports Newsletter {'Draft Created' if is_draft else 'Published'} Successfully",
                    message=f"Newsletter workflow completed in {execution_time}\n"
                           f"Articles processed: {total_articles}\n"
                           f"Leagues covered: {len([l for l, a in articles_by_league.items() if a])}"
                )
            
            return True
            
        except Exception as e:
            error_msg = f"Workflow failed: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Send error notification
            self._send_error_notification(error_msg, traceback.format_exc())
            
            return False
    
    def _scrape_articles(self, days_back: int) -> Dict[str, List[Dict]]:
        """
        Scrape articles using the news scraper.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dictionary of articles by league
        """
        try:
            articles_by_league = self.scraper.fetch_sports_articles(days_back)
            
            # Filter articles based on content settings
            max_articles = CONTENT_SETTINGS.get("max_articles_per_league", 5)
            
            for league_code in articles_by_league:
                # Limit articles per league
                articles_by_league[league_code] = articles_by_league[league_code][:max_articles]
                
                # Filter by minimum length
                min_length = CONTENT_SETTINGS.get("min_article_length", 100)
                articles_by_league[league_code] = [
                    article for article in articles_by_league[league_code]
                    if len(article.get('description', '')) >= min_length
                ]
            
            return articles_by_league
            
        except NewsAPIError as e:
            raise WorkflowError(f"News scraping failed: {e}")
        except Exception as e:
            raise WorkflowError(f"Unexpected error during scraping: {e}")
    
    def _render_newsletter(self, articles_by_league: Dict[str, List[Dict]]) -> str:
        """
        Render newsletter content using the renderer.
        
        Args:
            articles_by_league: Articles organized by league
            
        Returns:
            Rendered newsletter content
        """
        try:
            newsletter_content = self.renderer.render_newsletter(articles_by_league)
            
            if not newsletter_content or len(newsletter_content.strip()) < 100:
                raise WorkflowError("Generated newsletter content is too short or empty")
            
            return newsletter_content
            
        except Exception as e:
            raise WorkflowError(f"Newsletter rendering failed: {e}")
    
    def _generate_newsletter_title(self, articles_by_league: Dict[str, List[Dict]]) -> str:
        """
        Generate an engaging newsletter title based on the content.
        
        Args:
            articles_by_league: Articles organized by league
            
        Returns:
            Newsletter title
        """
        try:
            # Get current date for title
            current_date = datetime.now()
            date_str = current_date.strftime("%B %d, %Y")
            
            # Count total articles and leagues
            total_articles = sum(len(articles) for articles in articles_by_league.values())
            active_leagues = len([league for league, articles in articles_by_league.items() if articles])
            
            # Generate title based on content
            if active_leagues == 1:
                # Single league focus
                league_name = next(league for league, articles in articles_by_league.items() if articles)
                title = f"{NEWSLETTER_NAME}: {league_name} Weekly Update - {date_str}"
            elif active_leagues <= 3:
                # Multi-league but focused
                active_league_names = [league for league, articles in articles_by_league.items() if articles]
                leagues_str = " & ".join(active_league_names)
                title = f"{NEWSLETTER_NAME}: {leagues_str} Weekly - {date_str}"
            else:
                # General sports roundup
                title = f"{NEWSLETTER_NAME}: Sports Weekly Roundup - {date_str}"
            
            return title
            
        except Exception as e:
            logger.warning(f"Error generating title: {e}")
            # Fallback title
            return f"{NEWSLETTER_NAME} - {datetime.now().strftime('%B %d, %Y')}"
    
    def _publish_newsletter(self, title: str, content: str, is_draft: bool = False) -> bool:
        """
        Publish newsletter to Substack.
        
        Args:
            title: Newsletter title
            content: Newsletter content
            is_draft: Whether to save as draft
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with SubstackPublisher(headless=True) as publisher:
                success = publisher.publish_newsletter(title, content, is_draft)
                return success
                
        except SubstackPublishError as e:
            raise WorkflowError(f"Substack publishing failed: {e}")
        except Exception as e:
            raise WorkflowError(f"Unexpected error during publishing: {e}")
    
    def _send_notification(self, subject: str, message: str):
        """
        Send notification email.
        
        Args:
            subject: Email subject
            message: Email message
        """
        if not NOTIFICATION_CONFIG.get("send_error_notifications", True):
            return
        
        notification_email = NOTIFICATION_CONFIG.get("notification_email")
        if not notification_email:
            logger.warning("No notification email configured")
            return
        
        try:
            # Try to send via SMTP (Gmail)
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_pass = os.getenv("SMTP_PASS")
            
            if smtp_user and smtp_pass:
                msg = MIMEMultipart()
                msg['From'] = smtp_user
                msg['To'] = notification_email
                msg['Subject'] = f"[Sports Automation] {subject}"
                
                msg.attach(MIMEText(message, 'plain'))
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                server.quit()
                
                logger.info("Notification email sent successfully")
            else:
                logger.warning("SMTP credentials not configured, skipping email notification")
                
        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")
            # Try alternative notification method (Pushbullet)
            self._send_pushbullet_notification(subject, message)
    
    def _send_error_notification(self, error_msg: str, traceback_str: str):
        """
        Send error notification with details.
        
        Args:
            error_msg: Error message
            traceback_str: Full traceback
        """
        subject = "Sports News Automation Failed"
        message = f"""
Sports News Automation System Error

Error: {error_msg}

Timestamp: {datetime.now().isoformat()}

Full Traceback:
{traceback_str}

Please check the system logs for more details.
        """.strip()
        
        self._send_notification(subject, message)
    
    def _send_pushbullet_notification(self, subject: str, message: str):
        """
        Send notification via Pushbullet API as fallback.
        
        Args:
            subject: Notification title
            message: Notification message
        """
        try:
            import requests
            
            pushbullet_token = os.getenv("PUSHBULLET_TOKEN")
            if not pushbullet_token:
                logger.warning("No Pushbullet token configured")
                return
            
            url = "https://api.pushbullet.com/v2/pushes"
            headers = {
                "Access-Token": pushbullet_token,
                "Content-Type": "application/json"
            }
            data = {
                "type": "note",
                "title": f"[Sports Automation] {subject}",
                "body": message
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            logger.info("Pushbullet notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send Pushbullet notification: {e}")


def main():
    """Main entry point for the automation system."""
    try:
        # Parse command line arguments
        import argparse
        
        parser = argparse.ArgumentParser(description="Sports News Automation System")
        parser.add_argument(
            "--days-back", 
            type=int, 
            default=7, 
            help="Number of days to look back for articles (default: 7)"
        )
        parser.add_argument(
            "--draft", 
            action="store_true", 
            help="Save as draft instead of publishing"
        )
        parser.add_argument(
            "--test", 
            action="store_true", 
            help="Run in test mode (validate configuration only)"
        )
        
        args = parser.parse_args()
        
        # Initialize automation system
        automation = SportsNewsAutomation()
        
        if args.test:
            logger.info("Test mode: Configuration validation passed")
            print("✓ All components initialized successfully")
            print("✓ Configuration validation passed")
            print("System is ready for production use")
            return True
        
        # Run the workflow
        success = automation.run_workflow(
            days_back=args.days_back,
            is_draft=args.draft
        )
        
        if success:
            print("✓ Sports news automation completed successfully")
            sys.exit(0)
        else:
            print("✗ Sports news automation failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
        print("\nAutomation interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        print(f"✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()