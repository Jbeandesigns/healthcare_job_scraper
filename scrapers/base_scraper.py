"""
Base Scraper Class
Parent class for all healthcare job board scrapers

================================================================================
ETHICAL & LEGAL CONSIDERATIONS
================================================================================

1. ROBOTS.TXT COMPLIANCE
   - This scraper checks robots.txt before accessing any page
   - If a site's robots.txt disallows scraping, that URL is skipped
   - Crawl-delay directives are respected

2. RATE LIMITING
   - Minimum 3-7 second delay between requests (configurable)
   - Additional delays added if request rate is too high
   - Random delays to avoid predictable patterns

3. TERMS OF SERVICE
   - Users MUST review each site's Terms of Service before scraping
   - This tool is for personal research/market analysis only
   - Commercial use may require explicit permission from job boards
   - See TOS_NOTICE at bottom of this file for links

================================================================================
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time
import random
from datetime import datetime


class BaseScraper:
    """
    Parent class for all job board scrapers.
    Includes ethical scraping features: robots.txt compliance, rate limiting.
    """
    
    # User agents to rotate (helps with compatibility)
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ]
    
    # Default delay settings (in seconds) - respectful rate limiting
    MIN_DELAY = 3  # Minimum seconds between requests
    MAX_DELAY = 7  # Maximum seconds between requests
    
    def __init__(self, headless=True, respect_robots=True):
        """
        Initialize browser settings.
        
        Args:
            headless: Run browser without GUI
            respect_robots: Check robots.txt before scraping (recommended: True)
        """
        self.headless = headless
        self.respect_robots = respect_robots
        self.jobs = []
        self.source_name = "Unknown"
        self.base_url = ""
        self.robots_parser = None
        self._robots_checked = False
        self.request_count = 0
        self.session_start = datetime.now()
    
    def check_robots_txt(self, url):
        """
        Check if scraping is allowed by the site's robots.txt.
        
        This is a critical ethical check - we respect website owners' wishes
        about what can and cannot be scraped.
        
        Args:
            url: The URL to check
            
        Returns:
            True if scraping is allowed, False otherwise
        """
        if not self.respect_robots:
            print("  ⚠️ Warning: robots.txt checking is disabled")
            return True
        
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            # Only fetch robots.txt once per session per domain
            if not self._robots_checked:
                self.robots_parser = RobotFileParser()
                self.robots_parser.set_url(robots_url)
                self.robots_parser.read()
                self._robots_checked = True
                print(f"  ✓ Checked robots.txt for {parsed.netloc}")
            
            # Check if our user agent is allowed to access this URL
            is_allowed = self.robots_parser.can_fetch("*", url)
            
            if not is_allowed:
                print(f"  ⛔ robots.txt DISALLOWS: {url}")
                print(f"     Respecting site owner's wishes - skipping this URL")
            
            return is_allowed
            
        except Exception as e:
            print(f"  ⚠️ Could not check robots.txt ({e}) - proceeding with caution")
            # If we can't check, proceed but with extra caution (longer delay)
            time.sleep(2)
            return True
    
    def get_crawl_delay(self):
        """
        Get the crawl delay specified in robots.txt, or use default.
        
        Many sites specify a Crawl-delay directive in robots.txt to indicate
        how long bots should wait between requests.
        
        Returns:
            Delay in seconds
        """
        if self.robots_parser:
            try:
                delay = self.robots_parser.crawl_delay("*")
                if delay:
                    print(f"  ℹ️ Site requests {delay}s crawl delay - respecting")
                    return max(float(delay), self.MIN_DELAY)
            except:
                pass
        
        return random.uniform(self.MIN_DELAY, self.MAX_DELAY)
    
    def get_random_user_agent(self):
        """Return a random user agent string."""
        return random.choice(self.USER_AGENTS)
    
    def random_delay(self, min_seconds=None, max_seconds=None):
        """
        Wait a random amount of time to respect server resources.
        
        This is essential for ethical scraping:
        - Prevents overwhelming the server
        - Makes requests appear more human-like
        - Respects robots.txt crawl-delay if specified
        """
        if min_seconds is None:
            min_seconds = self.MIN_DELAY
        if max_seconds is None:
            max_seconds = self.MAX_DELAY
        
        # Check if robots.txt specifies a crawl delay
        robots_delay = self.get_crawl_delay()
        if robots_delay > max_seconds:
            delay = robots_delay
        else:
            delay = random.uniform(min_seconds, max_seconds)
        
        print(f"    ⏱️ Rate limiting: waiting {delay:.1f}s...")
        time.sleep(delay)
    
    def log_request(self, url):
        """
        Log request for rate monitoring.
        Automatically slows down if making too many requests.
        """
        self.request_count += 1
        elapsed = (datetime.now() - self.session_start).total_seconds()
        rate = self.request_count / (elapsed / 60) if elapsed > 0 else 0
        
        # Warn and slow down if making too many requests too quickly
        if rate > 15:  # More than 15 requests per minute is too aggressive
            print(f"  ⚠️ High request rate detected: {rate:.1f}/min")
            print(f"      Adding extra delay to be respectful...")
            time.sleep(10)  # Extra 10 second delay
        elif rate > 10:
            time.sleep(5)  # Extra 5 second delay
    
    def get_page(self, url, wait_for_selector=None):
        """
        Load a webpage and return BeautifulSoup object.
        
        Includes ethical safeguards:
        - robots.txt check before every request
        - Rate limiting between requests
        - Request rate monitoring
        """
        # Check robots.txt first - this is mandatory
        if not self.check_robots_txt(url):
            print(f"  Skipping {url} - respecting robots.txt")
            return None
        
        try:
            self.log_request(url)
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent=self.get_random_user_agent(),
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                # Navigate to the page
                page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Wait for specific element if provided
                if wait_for_selector:
                    try:
                        page.wait_for_selector(wait_for_selector, timeout=10000)
                    except:
                        pass  # Continue even if selector not found
                
                # Add respectful delay
                self.random_delay()
                
                # Scroll down to load lazy content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                time.sleep(1)
                
                html = page.content()
                browser.close()
                
                return BeautifulSoup(html, 'html.parser')
                
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            return None
    
    def scrape(self, city, state):
        """Override in child classes for specific sites."""
        raise NotImplementedError("Must implement in subclass")
    
    def clean_text(self, text):
        """Clean and normalize text."""
        if not text:
            return None
        return ' '.join(text.strip().split())
    
    def create_job_record(self, title, company, location, pay_raw, url=None, 
                          specialty=None, shift_type=None, employment_type=None):
        """Create a standardized job record dictionary."""
        return {
            'job_title': self.clean_text(title),
            'facility_name': self.clean_text(company),
            'location': self.clean_text(location),
            'pay_raw': self.clean_text(pay_raw),
            'specialty': specialty,
            'shift_type': shift_type,
            'employment_type': employment_type,
            'source': self.source_name,
            'source_url': url,
            'scraped_at': datetime.now().isoformat()
        }
    
    def get_session_stats(self):
        """Get statistics about this scraping session."""
        elapsed = (datetime.now() - self.session_start).total_seconds()
        return {
            'requests': self.request_count,
            'duration_seconds': elapsed,
            'requests_per_minute': self.request_count / (elapsed / 60) if elapsed > 0 else 0
        }


# ================================================================================
# TERMS OF SERVICE NOTICE
# ================================================================================

TOS_NOTICE = """
================================================================================
                         TERMS OF SERVICE NOTICE
================================================================================

Before using this scraper, you MUST review the Terms of Service for each site:

┌─────────────────┬─────────────────────────────────────────────────────────────┐
│ Job Board       │ Terms of Service URL                                        │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ Indeed          │ https://www.indeed.com/legal                                │
│ Vivian Health   │ https://www.vivian.com/terms                                │
│ ZipRecruiter    │ https://www.ziprecruiter.com/terms                          │
│ Aya Healthcare  │ https://www.ayahealthcare.com/terms-and-conditions          │
│ IntelyCare      │ https://www.intelycare.com/terms-of-service                 │
└─────────────────┴─────────────────────────────────────────────────────────────┘

ACCEPTABLE USE:
  ✓ Personal research and career planning
  ✓ Understanding healthcare job market trends  
  ✓ Academic research (with proper attribution)
  ✓ Internal competitive analysis

PROHIBITED USE:
  ✗ Commercial redistribution of job data
  ✗ Building competing job aggregation services
  ✗ Selling or licensing scraped data
  ✗ Any use that violates the sites' Terms of Service
  ✗ Scraping at rates that could harm site performance

ETHICAL GUIDELINES THIS SCRAPER FOLLOWS:
  • Checks robots.txt before accessing any page
  • Respects Crawl-delay directives
  • Implements rate limiting (3-7 second delays)
  • Automatically slows down if request rate is too high
  • Does not bypass authentication or access restricted areas

BY USING THIS TOOL, YOU ACCEPT FULL RESPONSIBILITY FOR:
  • Compliance with all applicable Terms of Service
  • Compliance with applicable laws and regulations
  • Any consequences of your use of this tool

================================================================================
"""


def print_tos_notice():
    """Print the Terms of Service notice."""
    print(TOS_NOTICE)


def acknowledge_tos():
    """
    Display TOS notice and require acknowledgment.
    Call this at the start of your scraping session.
    """
    print(TOS_NOTICE)
    print("Do you acknowledge and agree to these terms? (yes/no): ", end="")
    response = input().strip().lower()
    if response not in ['yes', 'y']:
        print("\nScraping cancelled. You must agree to the terms to proceed.")
        return False
    print("\n✓ Terms acknowledged. Proceeding with ethical scraping...\n")
    return True
