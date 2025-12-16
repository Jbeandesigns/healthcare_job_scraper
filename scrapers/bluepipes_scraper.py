"""
BluePipes Job Scraper
Scrapes travel nursing jobs from BluePipes.com
BluePipes aggregates jobs from 100+ travel nursing agencies
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.robotparser import RobotFileParser


class BluePipesScraper:
    """Scraper for BluePipes travel nursing jobs."""
    
    BASE_URL = "https://www.bluepipes.com"
    JOBS_URL = "https://www.bluepipes.com/jobs"
    
    def __init__(self, respect_robots=True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        self.respect_robots = respect_robots
        self.robot_parser = None
        
    def check_robots_txt(self):
        """Check if scraping is allowed by robots.txt."""
        try:
            self.robot_parser = RobotFileParser()
            self.robot_parser.set_url(f"{self.BASE_URL}/robots.txt")
            self.robot_parser.read()
            
            can_fetch = self.robot_parser.can_fetch("*", self.JOBS_URL)
            print(f"  {'✓' if can_fetch else '⛔'} robots.txt {'ALLOWS' if can_fetch else 'DISALLOWS'}: {self.JOBS_URL}")
            return can_fetch
        except Exception as e:
            print(f"  ⚠️ Could not check robots.txt: {e}")
            return True  # Proceed with caution
    
    def rate_limit(self):
        """Add delay between requests."""
        delay = random.uniform(3, 6)
        print(f"  ⏱️ Rate limiting: waiting {delay:.1f}s...")
        time.sleep(delay)
    
    def scrape_jobs(self, specialty="registered-nurse", location=None, max_pages=3):
        """
        Scrape jobs from BluePipes.
        
        Args:
            specialty: Job specialty (registered-nurse, lpn, cna, etc.)
            location: City/state to filter by
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of job dictionaries
        """
        if self.respect_robots and not self.check_robots_txt():
            print("  Respecting robots.txt - skipping BluePipes")
            return []
        
        jobs = []
        
        # BluePipes job URLs follow pattern: /jobs/travel/nursing/registered-nurse/
        url = f"{self.BASE_URL}/jobs/travel/nursing/{specialty}/"
        
        if location:
            # Add location filter
            url += f"?location={location.replace(' ', '+')}"
        
        print(f"  Fetching: {url}")
        
        try:
            self.rate_limit()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job listings
            job_cards = soup.find_all('div', class_=re.compile(r'job|listing|card', re.I))
            
            if not job_cards:
                # Try alternate selectors
                job_cards = soup.find_all('tr', class_=re.compile(r'job|listing', re.I))
            
            if not job_cards:
                job_cards = soup.find_all('a', href=re.compile(r'/job/', re.I))
            
            print(f"  Found {len(job_cards)} potential job elements")
            
            for card in job_cards[:50]:  # Limit to first 50 per page
                job = self.parse_job_card(card)
                if job and job.get('job_title'):
                    jobs.append(job)
            
            print(f"  ✓ Parsed {len(jobs)} jobs from BluePipes")
            
        except requests.exceptions.Timeout:
            print(f"  ⚠️ Timeout fetching BluePipes")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ Error fetching BluePipes: {e}")
        except Exception as e:
            print(f"  ⚠️ Error parsing BluePipes: {e}")
        
        return jobs
    
    def parse_job_card(self, card):
        """Parse a job card element into a dictionary."""
        job = {
            'source': 'BluePipes',
            'pay_type': 'Travel'
        }
        
        try:
            # Get text content
            text = card.get_text(separator=' ', strip=True)
            
            # Extract job title
            title_elem = card.find(['h2', 'h3', 'h4', 'a', 'strong'])
            if title_elem:
                job['job_title'] = title_elem.get_text(strip=True)
            
            # Extract location
            location_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s*([A-Z]{2})\b',
                r'in\s+([^,]+),\s*([A-Z]{2})'
            ]
            for pattern in location_patterns:
                match = re.search(pattern, text)
                if match:
                    job['city'] = match.group(1).strip()
                    job['state'] = match.group(2).strip()
                    job['location'] = f"{job['city']}, {job['state']}"
                    break
            
            # Extract pay rate
            pay_patterns = [
                r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s*week|/week|weekly)',
                r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s*hour|/hour|/hr|hourly)',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:per\s*week|/week)',
            ]
            for pattern in pay_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    rate_str = match.group(1).replace(',', '')
                    rate = float(rate_str)
                    
                    # Convert weekly to hourly (assuming 36 hours/week)
                    if 'week' in pattern.lower() and rate > 500:
                        rate = rate / 36
                    
                    job['pay_rate_low'] = round(rate, 2)
                    job['pay_rate_high'] = round(rate * 1.1, 2)
                    break
            
            # Extract specialty
            specialties = ['ICU', 'Med/Surg', 'ER', 'Tele', 'OR', 'L&D', 'PACU', 'NICU', 'PICU', 'Psych', 'Oncology']
            for spec in specialties:
                if spec.lower() in text.lower():
                    job['specialty'] = spec
                    break
            
            # Extract facility name
            facility_patterns = [
                r'at\s+([A-Z][^,]+(?:Hospital|Medical Center|Health|Healthcare))',
                r'([A-Z][^,]+(?:Hospital|Medical Center|Health))'
            ]
            for pattern in facility_patterns:
                match = re.search(pattern, text)
                if match:
                    job['facility_name'] = match.group(1).strip()
                    break
            
            # Get job URL if available
            link = card.find('a', href=True)
            if link:
                href = link.get('href', '')
                if href.startswith('/'):
                    job['url'] = f"{self.BASE_URL}{href}"
                elif href.startswith('http'):
                    job['url'] = href
            
            job['employment_type'] = 'Travel'
            
        except Exception as e:
            pass
        
        return job


def main():
    """Test the BluePipes scraper."""
    print("=" * 60)
    print("BluePipes Travel Nursing Scraper")
    print("=" * 60)
    
    scraper = BluePipesScraper(respect_robots=True)
    
    # Test scraping RN jobs
    print("\n[BluePipes]")
    print("  Searching for: Travel RN jobs")
    
    jobs = scraper.scrape_jobs(specialty="registered-nurse", max_pages=1)
    
    print(f"\n  Total jobs found: {len(jobs)}")
    
    # Show sample jobs
    if jobs:
        print("\n  Sample jobs:")
        for job in jobs[:5]:
            title = job.get('job_title', 'Unknown')[:40]
            location = job.get('location', 'Unknown')
            pay = job.get('pay_rate_low', 'N/A')
            print(f"    - {title} | {location} | ${pay}/hr")
    
    return jobs


if __name__ == "__main__":
    main()
