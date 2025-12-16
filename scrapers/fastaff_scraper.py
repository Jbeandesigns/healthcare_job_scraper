"""
Fastaff Travel Nursing Scraper
Scrapes travel nursing jobs from Fastaff.com
Fastaff is the leading Rapid Response travel nursing agency
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.robotparser import RobotFileParser


class FastaffScraper:
    """Scraper for Fastaff travel nursing jobs."""
    
    BASE_URL = "https://www.fastaff.com"
    JOBS_URL = "https://www.fastaff.com/jobs"
    
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
    
    def scrape_jobs(self, specialty=None, state=None, max_pages=3):
        """
        Scrape jobs from Fastaff.
        
        Args:
            specialty: Job specialty (rn, lpn, etc.)
            state: State abbreviation to filter by
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of job dictionaries
        """
        if self.respect_robots and not self.check_robots_txt():
            print("  Respecting robots.txt - skipping Fastaff")
            return []
        
        jobs = []
        
        # Fastaff jobs page
        url = self.JOBS_URL
        
        print(f"  Fetching: {url}")
        
        try:
            self.rate_limit()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job listings - Fastaff uses various card layouts
            job_cards = soup.find_all('div', class_=re.compile(r'job|card|listing|position', re.I))
            
            if not job_cards:
                # Try finding links to job detail pages
                job_links = soup.find_all('a', href=re.compile(r'/jobs?/|/position|/career', re.I))
                job_cards = job_links
            
            print(f"  Found {len(job_cards)} potential job elements")
            
            for card in job_cards[:100]:
                job = self.parse_job_card(card)
                if job and job.get('job_title'):
                    # Filter by specialty if provided
                    if specialty and specialty.lower() not in job.get('job_title', '').lower():
                        continue
                    # Filter by state if provided
                    if state and state.upper() != job.get('state', '').upper():
                        continue
                    jobs.append(job)
            
            # Remove duplicates based on title and location
            seen = set()
            unique_jobs = []
            for job in jobs:
                key = (job.get('job_title', ''), job.get('location', ''))
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)
            
            jobs = unique_jobs
            print(f"  ✓ Parsed {len(jobs)} unique jobs from Fastaff")
            
        except requests.exceptions.Timeout:
            print(f"  ⚠️ Timeout fetching Fastaff")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ Error fetching Fastaff: {e}")
        except Exception as e:
            print(f"  ⚠️ Error parsing Fastaff: {e}")
        
        return jobs
    
    def scrape_specialty_page(self, specialty_slug):
        """Scrape a specific specialty page like /nurses/specialty/rn"""
        url = f"{self.BASE_URL}/nurses/specialty/{specialty_slug}"
        
        print(f"  Fetching specialty page: {url}")
        
        jobs = []
        
        try:
            self.rate_limit()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse the page content
            text = soup.get_text()
            
            # Fastaff pages often have job counts and general info
            # rather than individual listings
            
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
        
        return jobs
    
    def parse_job_card(self, card):
        """Parse a job card element into a dictionary."""
        job = {
            'source': 'Fastaff',
            'pay_type': 'Travel'
        }
        
        try:
            # Get text content
            text = card.get_text(separator=' ', strip=True)
            
            # Skip if too short
            if len(text) < 10:
                return None
            
            # Skip navigation/menu items
            skip_words = ['login', 'sign up', 'apply now', 'contact', 'about', 'menu', 'navigation']
            if any(word in text.lower() for word in skip_words) and len(text) < 50:
                return None
            
            # Extract job title
            title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'strong'])
            if title_elem:
                job['job_title'] = title_elem.get_text(strip=True)
            else:
                # Try to get title from link text
                if hasattr(card, 'get_text'):
                    potential_title = card.get_text(strip=True)[:60]
                    if len(potential_title) > 5:
                        job['job_title'] = potential_title
            
            # Extract location
            location_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s*([A-Z]{2})\b',
                r'in\s+([^,]+),\s*([A-Z]{2})',
                r'Location:\s*([^,]+),\s*([A-Z]{2})'
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
                r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s*hour|/hour|/hr)',
                r'pay[:\s]+\$?(\d{1,3}(?:,\d{3})*)',
            ]
            for pattern in pay_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    rate_str = match.group(1).replace(',', '')
                    rate = float(rate_str)
                    
                    # Convert weekly to hourly
                    if 'week' in pattern.lower() and rate > 500:
                        rate = rate / 36
                    
                    job['pay_rate_low'] = round(rate, 2)
                    job['pay_rate_high'] = round(rate * 1.1, 2)
                    break
            
            # Extract specialty from title or content
            specialty_map = {
                'icu': 'ICU RN',
                'intensive care': 'ICU RN',
                'med surg': 'Med/Surg RN',
                'medical surgical': 'Med/Surg RN',
                'emergency': 'ER RN',
                'er ': 'ER RN',
                'telemetry': 'Tele RN',
                'tele ': 'Tele RN',
                'operating room': 'OR RN',
                'or ': 'OR RN',
                'labor': 'L&D RN',
                'l&d': 'L&D RN',
                'pacu': 'PACU RN',
                'nicu': 'NICU RN',
                'picu': 'PICU RN',
                'psych': 'Psych RN',
                'behavioral': 'Psych RN',
                'oncology': 'Oncology RN',
                'cath lab': 'Cath Lab RN',
                'stepdown': 'Stepdown RN',
            }
            
            text_lower = text.lower()
            for keyword, spec in specialty_map.items():
                if keyword in text_lower:
                    job['specialty'] = spec
                    break
            
            # Get job URL
            link = card if card.name == 'a' else card.find('a', href=True)
            if link and link.get('href'):
                href = link.get('href', '')
                if href.startswith('/'):
                    job['url'] = f"{self.BASE_URL}{href}"
                elif href.startswith('http'):
                    job['url'] = href
            
            job['employment_type'] = 'Travel'
            job['facility_name'] = 'Fastaff Partner Facility'
            
        except Exception as e:
            pass
        
        return job


def main():
    """Test the Fastaff scraper."""
    print("=" * 60)
    print("Fastaff Travel Nursing Scraper")
    print("=" * 60)
    
    scraper = FastaffScraper(respect_robots=True)
    
    print("\n[Fastaff]")
    print("  Searching for: Travel RN jobs")
    
    jobs = scraper.scrape_jobs()
    
    print(f"\n  Total jobs found: {len(jobs)}")
    
    if jobs:
        print("\n  Sample jobs:")
        for job in jobs[:5]:
            title = job.get('job_title', 'Unknown')[:40]
            location = job.get('location', 'Unknown')
            specialty = job.get('specialty', 'RN')
            print(f"    - {title} | {location} | {specialty}")
    
    return jobs


if __name__ == "__main__":
    main()
