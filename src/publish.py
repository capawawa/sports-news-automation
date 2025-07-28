"""
Substack Publishing System
Automates newsletter publishing to Substack using Playwright browser automation.
"""

import os
import re
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

from config import (
    SUBSTACK_EMAIL, SUBSTACK_PASS, NEWSLETTER_NAME, 
    UTM_PARAMETERS, ERROR_CONFIG, NOTIFICATION_CONFIG
)

# Configure logging
logging.basicConfig(level=getattr(logging, ERROR_CONFIG["log_level"]))
logger = logging.getLogger(__name__)


class SubstackPublishError(Exception):
    """Custom exception for Substack publishing errors"""
    pass


class SubstackAuthError(SubstackPublishError):
    """Exception for authentication failures"""
    pass


class SubstackPublisher:
    """
    Automates newsletter publishing to Substack using Playwright browser automation.
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize the Substack publisher.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        if not SUBSTACK_EMAIL or not SUBSTACK_PASS:
            raise ValueError("SUBSTACK_EMAIL and SUBSTACK_PASS environment variables are required")
        
        self.email = SUBSTACK_EMAIL
        self.password = SUBSTACK_PASS
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.newsletter_name = NEWSLETTER_NAME
        
        # Substack URLs (these are current as of 2024-2025)
        self.login_url = "https://substack.com/sign-in"
        self.dashboard_url = "https://substack.com/publish"
        
    def __enter__(self):
        """Context manager entry"""
        self.start_browser()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()
        
    def start_browser(self):
        """Start Playwright browser session"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.page = self.browser.new_page()
            
            # Set user agent to avoid detection
            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            logger.info("Browser started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise SubstackPublishError(f"Browser initialization failed: {e}")
    
    def close_browser(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
    
    def login(self) -> bool:
        """
        Login to Substack account.
        
        Returns:
            True if login successful, False otherwise
        """
        max_retries = ERROR_CONFIG["max_retries"]
        retry_delay = ERROR_CONFIG["retry_delay"]
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting login (attempt {attempt + 1}/{max_retries})")
                
                # Navigate to login page
                self.page.goto(self.login_url, timeout=30000)
                self.page.wait_for_load_state('networkidle')
                
                # Wait for and fill email field
                email_selector = 'input[type="email"], input[name="email"], input[placeholder*="email" i]'
                self.page.wait_for_selector(email_selector, timeout=10000)
                self.page.fill(email_selector, self.email)
                
                # Fill password field
                password_selector = 'input[type="password"], input[name="password"]'
                self.page.wait_for_selector(password_selector, timeout=10000)
                self.page.fill(password_selector, self.password)
                
                # Click login button
                login_button_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Sign in")',
                    'button:has-text("Log in")',
                    'input[type="submit"]'
                ]
                
                login_clicked = False
                for selector in login_button_selectors:
                    try:
                        if self.page.locator(selector).is_visible():
                            self.page.click(selector)
                            login_clicked = True
                            break
                    except:
                        continue
                
                if not login_clicked:
                    raise SubstackAuthError("Could not find login button")
                
                # Wait for navigation after login
                self.page.wait_for_load_state('networkidle', timeout=15000)
                
                # Check if login was successful
                current_url = self.page.url
                if 'sign-in' not in current_url.lower() and 'login' not in current_url.lower():
                    logger.info("Login successful")
                    return True
                else:
                    # Check for error messages
                    error_selectors = [
                        '[data-testid="error-message"]',
                        '.error-message',
                        '[role="alert"]',
                        '.alert-error'
                    ]
                    
                    error_message = "Unknown login error"
                    for selector in error_selectors:
                        try:
                            if self.page.locator(selector).is_visible():
                                error_message = self.page.locator(selector).text_content()
                                break
                        except:
                            continue
                    
                    raise SubstackAuthError(f"Login failed: {error_message}")
                    
            except PlaywrightTimeoutError as e:
                logger.warning(f"Login timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise SubstackAuthError(f"Login timeout after {max_retries} attempts")
                    
            except Exception as e:
                logger.warning(f"Login error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise SubstackAuthError(f"Login failed after {max_retries} attempts: {e}")
        
        return False
    
    def create_post(self, title: str, content: str, is_draft: bool = False) -> bool:
        """
        Create and publish a new Substack post.
        
        Args:
            title: Post title
            content: Post content (Markdown format)
            is_draft: Whether to save as draft instead of publishing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Creating post: {title}")
            
            # Navigate to publish page
            self.page.goto(self.dashboard_url, timeout=30000)
            self.page.wait_for_load_state('networkidle')
            
            # Look for "New post" or "Write" button
            new_post_selectors = [
                'button:has-text("New post")',
                'button:has-text("Write")',
                'a:has-text("New post")',
                'a:has-text("Write")',
                '[data-testid="new-post-button"]'
            ]
            
            new_post_clicked = False
            for selector in new_post_selectors:
                try:
                    if self.page.locator(selector).is_visible():
                        self.page.click(selector)
                        new_post_clicked = True
                        break
                except:
                    continue
            
            if not new_post_clicked:
                raise SubstackPublishError("Could not find new post button")
            
            # Wait for editor to load
            self.page.wait_for_load_state('networkidle', timeout=15000)
            
            # Fill in title
            title_selectors = [
                'input[placeholder*="Title" i]',
                'input[name="title"]',
                'textarea[placeholder*="Title" i]',
                '[data-testid="post-title"]'
            ]
            
            title_filled = False
            for selector in title_selectors:
                try:
                    if self.page.locator(selector).is_visible():
                        self.page.fill(selector, title)
                        title_filled = True
                        break
                except:
                    continue
            
            if not title_filled:
                raise SubstackPublishError("Could not find title field")
            
            # Fill in content
            content_selectors = [
                '[data-testid="editor"]',
                '.editor',
                '[contenteditable="true"]',
                'textarea[placeholder*="Tell your story" i]',
                'div[role="textbox"]'
            ]
            
            content_filled = False
            for selector in content_selectors:
                try:
                    if self.page.locator(selector).is_visible():
                        # Clear existing content and add new content
                        self.page.click(selector)
                        self.page.keyboard.press('Control+a')
                        self.page.keyboard.type(content)
                        content_filled = True
                        break
                except:
                    continue
            
            if not content_filled:
                raise SubstackPublishError("Could not find content editor")
            
            # Add UTM parameters to any links in content
            content_with_utm = self._add_utm_parameters(content)
            if content_with_utm != content:
                # Update content with UTM parameters
                self.page.keyboard.press('Control+a')
                self.page.keyboard.type(content_with_utm)
            
            # Wait a moment for content to be processed
            time.sleep(2)
            
            if is_draft:
                # Save as draft
                draft_selectors = [
                    'button:has-text("Save draft")',
                    'button:has-text("Draft")',
                    '[data-testid="save-draft"]'
                ]
                
                for selector in draft_selectors:
                    try:
                        if self.page.locator(selector).is_visible():
                            self.page.click(selector)
                            logger.info("Post saved as draft")
                            return True
                    except:
                        continue
                        
                raise SubstackPublishError("Could not find save draft button")
            else:
                # Publish post
                publish_selectors = [
                    'button:has-text("Publish now")',
                    'button:has-text("Publish")',
                    '[data-testid="publish-button"]'
                ]
                
                publish_clicked = False
                for selector in publish_selectors:
                    try:
                        if self.page.locator(selector).is_visible():
                            self.page.click(selector)
                            publish_clicked = True
                            break
                    except:
                        continue
                
                if not publish_clicked:
                    raise SubstackPublishError("Could not find publish button")
                
                # Wait for publish confirmation
                self.page.wait_for_load_state('networkidle', timeout=30000)
                
                # Check for success indicators
                success_indicators = [
                    ':has-text("Published")',
                    ':has-text("Your post is live")',
                    '[data-testid="publish-success"]'
                ]
                
                for indicator in success_indicators:
                    try:
                        if self.page.locator(indicator).is_visible():
                            logger.info("Post published successfully")
                            return True
                    except:
                        continue
                
                # If no success indicator found, check URL for post
                current_url = self.page.url
                if '/p/' in current_url:
                    logger.info("Post published successfully (detected from URL)")
                    return True
                
                logger.warning("Publish status unclear, but no errors detected")
                return True
                
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            raise SubstackPublishError(f"Failed to create post: {e}")
    
    def _add_utm_parameters(self, content: str) -> str:
        """
        Add UTM parameters to URLs in content for growth tracking.
        
        Args:
            content: Original content
            
        Returns:
            Content with UTM parameters added to URLs
        """
        try:
            # Find URLs in content
            url_pattern = r'https?://[^\s\)]+(?=\s|\)|$|")'
            
            def add_utm_to_url(match):
                url = match.group(0)
                # Don't add UTM to Substack URLs to avoid conflicts
                if 'substack.com' in url:
                    return url
                
                # Add UTM parameters
                separator = '&' if '?' in url else '?'
                utm_string = urlencode(UTM_PARAMETERS)
                return f"{url}{separator}{utm_string}"
            
            return re.sub(url_pattern, add_utm_to_url, content)
            
        except Exception as e:
            logger.warning(f"Error adding UTM parameters: {e}")
            return content
    
    def publish_newsletter(self, title: str, content: str, is_draft: bool = False) -> bool:
        """
        Complete workflow to publish newsletter to Substack.
        
        Args:
            title: Newsletter title
            content: Newsletter content
            is_draft: Whether to save as draft
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Login to Substack
            if not self.login():
                raise SubstackAuthError("Failed to login to Substack")
            
            # Create and publish post
            success = self.create_post(title, content, is_draft)
            
            if success:
                logger.info(f"Newsletter {'drafted' if is_draft else 'published'} successfully")
            else:
                logger.error(f"Failed to {'draft' if is_draft else 'publish'} newsletter")
            
            return success
            
        except Exception as e:
            logger.error(f"Newsletter publishing failed: {e}")
            raise SubstackPublishError(f"Publishing workflow failed: {e}")


def main():
    """Test function for the publisher."""
    try:
        # Test publisher initialization
        with SubstackPublisher(headless=False) as publisher:
            print("✓ Publisher initialized successfully")
            
            # Test login
            if publisher.login():
                print("✓ Login successful")
            else:
                print("✗ Login failed")
                
    except Exception as e:
        print(f"Error testing publisher: {e}")


if __name__ == "__main__":
    main()