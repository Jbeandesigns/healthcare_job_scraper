from .base_scraper import BaseScraper
from urllib.parse import quote

class IndeedScraper(BaseScraper):
    """Scraper for Indeed healthcare job listings."""
    
    BASE_URL = 'https://www.indeed.com/jobs'
    
    # Healthcare job types to search for
    JOB_TYPES = ['RN', 'LPN', 'CNA', 'Nurse Practitioner',
                 'Physician Assistant', 'Respiratory Therapist']
    
    def build_url(self, job_type, city, state):
        """Build Indeed search URL."""
        query = quote(job_type)
        location = quote(f'{city}, {state}')
        return f'{self.BASE_URL}?q={query}&l={location}'
    
    def parse_job_card(self, card):
        """Extract data from a single job listing card."""
        try:
            title = card.select_one('[data-testid="title"]')
            company = card.select_one('[data-testid="company-name"]')
            location = card.select_one('[data-testid="text-location"]')
            salary = card.select_one('[data-testid="salary-info"]')
            
            return {
                'title': title.text.strip() if title else None,
                'company': company.text.strip() if company else None,
                'location': location.text.strip() if location else None,
                'pay_raw': salary.text.strip() if salary else None,
                'source': 'Indeed'
            }
        except Exception as e:
            print(f'Error parsing card: {e}')
            return None
