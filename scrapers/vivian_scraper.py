"""
Vivian Health Job Scraper
Scrapes travel nursing and healthcare jobs from Vivian.com

Note: Always check Vivian's robots.txt and Terms of Service before use.
https://www.vivian.com/robots.txt
https://www.vivian.com/terms
"""

from .base_scraper import BaseScraper
from urllib.parse import quote


class VivianScraper(BaseScraper):
    """Scraper for Vivian Health job listings."""
    
    BASE_URL = "https://www.vivian.com/search"
    
    def __init__(self, headless=True, respect_robots=True):
        super().__init__(headless, respect_robots)
        self.source_name = "Vivian Health"
        self.base_url = "https://www.vivian.com"
    
    def build_url(self, city, state, job_type="nurse"):
        """Build Vivian search URL."""
        location = quote(f"{city}, {state}")
        return f"{self.BASE_URL}?q={job_type}&location={location}"
    
    def parse_job_card(self, card):
        """Extract data from a Vivian job listing card."""
        try:
            # Job title
            title_elem = card.select_one('h2, [class*="JobTitle"], [class*="job-title"]')
            title = title_elem.text if title_elem else None
            
            # Facility/Company
            company_elem = card.select_one('[class*="facility"], [class*="company"], [class*="employer"]')
            company = company_elem.text if company_elem else None
            
            # Location
            location_elem = card.select_one('[class*="location"], [class*="city"]')
            location = location_elem.text if location_elem else None
            
            # Pay rate (Vivian typically shows weekly pay for travel)
            pay_elem = card.select_one('[class*="pay"], [class*="salary"], [class*="rate"], [class*="compensation"]')
            pay = pay_elem.text if pay_elem else None
            
            # Job URL
            link_elem = card.select_one('a[href*="/job/"], a[href*="/jobs/"]')
            job_url = None
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    job_url = f"https://www.vivian.com{href}"
                else:
                    job_url = href
            
            if title:
                return self.create_job_record(
                    title=title,
                    company=company,
                    location=location,
                    pay_raw=pay,
                    url=job_url,
                    employment_type='Travel'
                )
            return None
            
        except Exception as e:
            print(f"Error parsing Vivian job card: {e}")
            return None
    
    def scrape(self, city, state, max_results=50):
        """Scrape Vivian for healthcare jobs in a specific city."""
        all_jobs = []
        
        job_types = ['nurse', 'rn', 'lpn', 'cna', 'allied health']
        
        for job_type in job_types[:2]:  # Limit for speed
            print(f"  Searching Vivian for: {job_type}")
            
            url = self.build_url(city, state, job_type)
            soup = self.get_page(url, wait_for_selector='[class*="job"], [class*="Job"]')
            
            if not soup:
                continue
            
            # Find job cards - Vivian uses various class naming conventions
            job_cards = soup.select('[class*="JobCard"], [class*="job-card"], [class*="listing"]')
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.select('article, [role="article"], .card')
            
            for card in job_cards[:max_results]:
                job = self.parse_job_card(card)
                if job:
                    job['search_query'] = job_type
                    all_jobs.append(job)
            
            print(f"    Found {len(job_cards)} listings")
        
        self.jobs = all_jobs
        return all_jobs
