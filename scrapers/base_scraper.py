from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random

class BaseScraper:
    """Parent class for all job board scrapers."""
    
    def __init__(self, headless=True):
        """Initialize browser settings."""
        self.headless = headless  # Run without visible browser
        self.jobs = []  # Store scraped jobs
    
    def get_page(self, url):
        """Load a webpage and return HTML content."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            # Set realistic user agent to avoid detection
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"
            })
            
            page.goto(url, wait_until='networkidle')
            time.sleep(random.uniform(2, 4))  # Human-like delay
            
            html = page.content()
            browser.close()
            return BeautifulSoup(html, 'html.parser')
    
    def scrape(self, city, state):
        """Override in child classes for specific sites."""
        raise NotImplementedError("Must implement in subclass")
