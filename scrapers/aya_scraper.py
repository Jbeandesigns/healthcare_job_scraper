"""
Aya Healthcare Job Scraper
Scrapes travel nursing and allied health jobs from AyaHealthcare.com
Aya is one of the largest travel nursing agencies
"""

from .base_scraper import BaseScraper
from urllib.parse import quote


class AyaHealthcareScraper(BaseScraper):
    """Scraper for Aya Healthcare job listings."""
    
    BASE_URL = "https://www.ayahealthcare.com/healthcare-jobs"
    
    def __init__(self, headless=True):
        super().__init__(headless)
        self.source_name = "Aya Healthcare"
    
    def build_url(self, city, state, specialty=None):
        """Build Aya Healthcare search URL."""
        # Aya uses location-based URL structure
        location = quote(f"{city}, {state}")
        base = f"{self.BASE_URL}?location={location}"
        if specialty:
            base += f"&specialty={quote(specialty)}"
        return base
    
    def parse_job_card(self, card):
        """Extract data from an Aya Healthcare job listing card."""
        try:
            # Job title / Specialty
            title_elem = card.select_one('h2, h3, [class*="title"], [class*="specialty"]')
            title = title_elem.text if title_elem else None
            
            # Facility name
            facility_elem = card.select_one('[class*="facility"], [class*="hospital"], [class*="client"]')
            facility = facility_elem.text if facility_elem else "Aya Healthcare"
            
            # Location
            location_elem = card.select_one('[class*="location"], [class*="city"], [class*="state"]')
            location = location_elem.text if location_elem else None
            
            # Pay rate (Aya typically shows weekly pay)
            pay_elem = card.select_one('[class*="pay"], [class*="rate"], [class*="salary"], [class*="weekly"]')
            pay = pay_elem.text if pay_elem else None
            
            # Shift information
            shift_elem = card.select_one('[class*="shift"], [class*="schedule"]')
            shift = shift_elem.text if shift_elem else None
            
            # Job URL
            link_elem = card.select_one('a[href*="job"], a[href*="position"]')
            job_url = None
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    job_url = f"https://www.ayahealthcare.com{href}"
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
                    employment_type='Travel'
                )
            return None
            
        except Exception as e:
            print(f"Error parsing Aya Healthcare job card: {e}")
            return None
    
    def scrape(self, city, state, max_results=50):
        """Scrape Aya Healthcare for jobs in a specific city."""
        all_jobs = []
        
        specialties = ['RN', 'LPN', 'Allied Health', 'OR', 'ICU', 'ER']
        
        for specialty in specialties[:3]:  # Limit for speed
            print(f"  Searching Aya Healthcare for: {specialty}")
            
            url = self.build_url(city, state, specialty)
            soup = self.get_page(url, wait_for_selector='[class*="job"], [class*="card"]')
            
            if not soup:
                continue
            
            # Find job cards - try various selectors
            job_cards = soup.select('[class*="job-card"], [class*="JobCard"], [class*="listing-card"]')
            
            if not job_cards:
                job_cards = soup.select('article, .card, [class*="result"]')
            
            for card in job_cards[:max_results]:
                job = self.parse_job_card(card)
                if job:
                    job['search_query'] = specialty
                    all_jobs.append(job)
            
            print(f"    Found {len(job_cards)} listings")
            self.random_delay(3, 5)
        
        self.jobs = all_jobs
        return all_jobs
