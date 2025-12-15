"""
ZipRecruiter Healthcare Job Scraper
Scrapes nursing and healthcare jobs from ZipRecruiter.com
"""

from .base_scraper import BaseScraper
from urllib.parse import quote


class ZipRecruiterScraper(BaseScraper):
    """Scraper for ZipRecruiter healthcare job listings."""
    
    BASE_URL = "https://www.ziprecruiter.com/jobs-search"
    
    JOB_TYPES = [
        'Registered Nurse RN',
        'LPN',
        'CNA',
        'Travel Nurse',
        'ICU Nurse',
        'ER Nurse'
    ]
    
    def __init__(self, headless=True):
        super().__init__(headless)
        self.source_name = "ZipRecruiter"
    
    def build_url(self, job_type, city, state):
        """Build ZipRecruiter search URL."""
        query = quote(job_type)
        location = quote(f"{city}, {state}")
        return f"{self.BASE_URL}?search={query}&location={location}"
    
    def parse_job_card(self, card):
        """Extract data from a ZipRecruiter job listing card."""
        try:
            # Job title
            title_elem = card.select_one('h2.job_title, [class*="JobTitle"], .job-title a, a[class*="job_link"]')
            title = title_elem.text if title_elem else None
            
            # Company name
            company_elem = card.select_one('[class*="company"], .hiring-company, [class*="employer"]')
            company = company_elem.text if company_elem else None
            
            # Location
            location_elem = card.select_one('[class*="location"], .job-location')
            location = location_elem.text if location_elem else None
            
            # Salary/Pay
            salary_elem = card.select_one('[class*="salary"], [class*="compensation"], [class*="pay"]')
            salary = salary_elem.text if salary_elem else None
            
            # Job URL
            link_elem = card.select_one('a[href*="/job/"], a[href*="/jobs/"], a.job_link')
            job_url = None
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    job_url = f"https://www.ziprecruiter.com{href}"
                else:
                    job_url = href
            
            if title:
                return self.create_job_record(
                    title=title,
                    company=company,
                    location=location,
                    pay_raw=salary,
                    url=job_url
                )
            return None
            
        except Exception as e:
            print(f"Error parsing ZipRecruiter job card: {e}")
            return None
    
    def scrape(self, city, state, max_results=30):
        """Scrape ZipRecruiter for healthcare jobs in a specific city."""
        all_jobs = []
        
        for job_type in self.JOB_TYPES[:3]:  # Limit job types
            print(f"  Searching ZipRecruiter for: {job_type}")
            
            url = self.build_url(job_type, city, state)
            soup = self.get_page(url, wait_for_selector='.job_content, [class*="JobCard"]')
            
            if not soup:
                continue
            
            # Find job cards
            job_cards = soup.select('.job_content, [class*="JobCard"], article[class*="job"]')
            
            if not job_cards:
                job_cards = soup.select('[data-job-id], .job-listing')
            
            for card in job_cards[:max_results]:
                job = self.parse_job_card(card)
                if job:
                    job['search_query'] = job_type
                    all_jobs.append(job)
            
            print(f"    Found {len(job_cards)} listings")
            self.random_delay(3, 6)
        
        self.jobs = all_jobs
        return all_jobs
