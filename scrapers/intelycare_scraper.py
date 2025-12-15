"""
IntelyCare Job Scraper
Scrapes nursing jobs from IntelyCare.com
IntelyCare specializes in per-diem and PRN nursing shifts
"""

from .base_scraper import BaseScraper
from urllib.parse import quote


class IntelyCareScraper(BaseScraper):
    """Scraper for IntelyCare job listings."""
    
    BASE_URL = "https://www.intelycare.com/nursing-jobs"
    
    def __init__(self, headless=True):
        super().__init__(headless)
        self.source_name = "IntelyCare"
    
    def build_url(self, city, state):
        """Build IntelyCare search URL."""
        # IntelyCare URL structure - they focus on specific markets
        location = f"{city.lower().replace(' ', '-')}-{state.lower()}"
        return f"{self.BASE_URL}/{location}"
    
    def build_search_url(self, city, state):
        """Alternative search URL format."""
        location = quote(f"{city}, {state}")
        return f"https://www.intelycare.com/jobs?location={location}"
    
    def parse_job_card(self, card):
        """Extract data from an IntelyCare job listing card."""
        try:
            # Job title / Role
            title_elem = card.select_one('h2, h3, [class*="title"], [class*="role"], [class*="position"]')
            title = title_elem.text if title_elem else None
            
            # Facility name
            facility_elem = card.select_one('[class*="facility"], [class*="location-name"], [class*="employer"]')
            facility = facility_elem.text if facility_elem else "IntelyCare Partner Facility"
            
            # Location
            location_elem = card.select_one('[class*="location"], [class*="address"], [class*="city"]')
            location = location_elem.text if location_elem else None
            
            # Pay rate (IntelyCare shows hourly rates)
            pay_elem = card.select_one('[class*="pay"], [class*="rate"], [class*="hourly"], [class*="salary"]')
            pay = pay_elem.text if pay_elem else None
            
            # Shift type
            shift_elem = card.select_one('[class*="shift"], [class*="schedule"], [class*="hours"]')
            shift = shift_elem.text if shift_elem else None
            
            # Job URL
            link_elem = card.select_one('a[href*="job"], a[href*="shift"], a[href*="position"]')
            job_url = None
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    job_url = f"https://www.intelycare.com{href}"
                else:
                    job_url = href
            
            if title:
                return self.create_job_record(
                    title=title,
                    company=facility,
                    location=location,
                    pay_raw=pay,
                    url=job_url,
                    shift_type=shift,
                    employment_type='Per Diem'
                )
            return None
            
        except Exception as e:
            print(f"Error parsing IntelyCare job card: {e}")
            return None
    
    def scrape(self, city, state, max_results=50):
        """Scrape IntelyCare for jobs in a specific city."""
        all_jobs = []
        
        print(f"  Searching IntelyCare...")
        
        # Try primary URL format
        url = self.build_url(city, state)
        soup = self.get_page(url, wait_for_selector='[class*="job"], [class*="shift"]')
        
        if not soup:
            # Try alternative search URL
            url = self.build_search_url(city, state)
            soup = self.get_page(url, wait_for_selector='[class*="job"], [class*="shift"]')
        
        if not soup:
            print("    Could not load IntelyCare page")
            return all_jobs
        
        # Find job/shift cards
        job_cards = soup.select('[class*="job-card"], [class*="shift-card"], [class*="listing"]')
        
        if not job_cards:
            job_cards = soup.select('article, .card, [class*="result"], [class*="opportunity"]')
        
        for card in job_cards[:max_results]:
            job = self.parse_job_card(card)
            if job:
                all_jobs.append(job)
        
        print(f"    Found {len(job_cards)} listings")
        
        self.jobs = all_jobs
        return all_jobs
