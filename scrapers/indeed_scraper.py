"""
Indeed Healthcare Job Scraper
Scrapes nursing and healthcare jobs from Indeed.com

Note: Always check Indeed's robots.txt and Terms of Service before use.
https://www.indeed.com/robots.txt
https://www.indeed.com/legal
"""

from .base_scraper import BaseScraper
from urllib.parse import quote


class IndeedScraper(BaseScraper):
    """Scraper for Indeed healthcare job listings."""
    
    BASE_URL = "https://www.indeed.com/jobs"
    
    # Healthcare job types to search for
    JOB_TYPES = [
        'RN Registered Nurse',
        'LPN Licensed Practical Nurse', 
        'CNA Certified Nursing Assistant',
        'Nurse Practitioner',
        'Travel Nurse',
        'ICU Nurse',
        'Emergency Room Nurse'
    ]
    
    def __init__(self, headless=True, respect_robots=True):
        super().__init__(headless, respect_robots)
        self.source_name = "Indeed"
        self.base_url = "https://www.indeed.com"
    
    def build_url(self, job_type, city, state, start=0):
        """Build Indeed search URL."""
        query = quote(job_type)
        location = quote(f"{city}, {state}")
        return f"{self.BASE_URL}?q={query}&l={location}&start={start}"
    
    def parse_job_card(self, card):
        """Extract data from a single job listing card."""
        try:
            # Job title
            title_elem = card.select_one('h2.jobTitle span[title]')
            if not title_elem:
                title_elem = card.select_one('h2.jobTitle a')
            title = title_elem.get('title') or title_elem.text if title_elem else None
            
            # Company name
            company_elem = card.select_one('[data-testid="company-name"]')
            if not company_elem:
                company_elem = card.select_one('.companyName')
            company = company_elem.text if company_elem else None
            
            # Location
            location_elem = card.select_one('[data-testid="text-location"]')
            if not location_elem:
                location_elem = card.select_one('.companyLocation')
            location = location_elem.text if location_elem else None
            
            # Salary/Pay
            salary_elem = card.select_one('[data-testid="attribute_snippet_testid"]')
            if not salary_elem:
                salary_elem = card.select_one('.salary-snippet-container')
            if not salary_elem:
                salary_elem = card.select_one('.estimated-salary')
            salary = salary_elem.text if salary_elem else None
            
            # Job URL
            link_elem = card.select_one('a[data-jk]')
            if not link_elem:
                link_elem = card.select_one('h2.jobTitle a')
            job_id = link_elem.get('data-jk') if link_elem else None
            job_url = f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else None
            
            if title:  # Only return if we found a title
                return self.create_job_record(
                    title=title,
                    company=company,
                    location=location,
                    pay_raw=salary,
                    url=job_url
                )
            return None
            
        except Exception as e:
            print(f"Error parsing Indeed job card: {e}")
            return None
    
    def scrape(self, city, state, max_pages=2):
        """Scrape Indeed for healthcare jobs in a specific city."""
        all_jobs = []
        
        for job_type in self.JOB_TYPES[:3]:  # Limit job types for speed
            print(f"  Searching Indeed for: {job_type}")
            
            for page in range(max_pages):
                start = page * 10
                url = self.build_url(job_type, city, state, start)
                
                soup = self.get_page(url, wait_for_selector='.jobsearch-ResultsList')
                
                if not soup:
                    continue
                
                # Find job cards
                job_cards = soup.select('.job_seen_beacon')
                if not job_cards:
                    job_cards = soup.select('.jobsearch-ResultsList > li')
                
                if not job_cards:
                    print(f"    No job cards found on page {page + 1}")
                    break
                
                for card in job_cards:
                    job = self.parse_job_card(card)
                    if job:
                        job['search_query'] = job_type
                        all_jobs.append(job)
                
                print(f"    Page {page + 1}: Found {len(job_cards)} listings")
        
        # Remove duplicates based on job URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['source_url'] and job['source_url'] not in seen_urls:
                seen_urls.add(job['source_url'])
                unique_jobs.append(job)
            elif not job['source_url']:
                unique_jobs.append(job)
        
        self.jobs = unique_jobs
        return unique_jobs
