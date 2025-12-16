"""
HealthTrust Workforce Solutions Scraper
Scrapes healthcare jobs from healthtrustws.com
HealthTrust is part of HCA Healthcare, a major hospital network
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json
from urllib.robotparser import RobotFileParser


class HealthTrustScraper:
    """Scraper for HealthTrust Workforce Solutions jobs."""
    
    BASE_URL = "https://healthtrustws.com"
    JOBS_URL = "https://healthtrustws.com/jobs/search"
    
    def __init__(self, respect_robots=True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        self.respect_robots = respect_robots
        
    def check_robots_txt(self):
        """Check if scraping is allowed by robots.txt."""
        try:
            robot_parser = RobotFileParser()
            robot_parser.set_url(f"{self.BASE_URL}/robots.txt")
            robot_parser.read()
            
            can_fetch = robot_parser.can_fetch("*", self.JOBS_URL)
            print(f"  {'✓' if can_fetch else '⛔'} robots.txt {'ALLOWS' if can_fetch else 'DISALLOWS'}: {self.JOBS_URL}")
            return can_fetch
        except Exception as e:
            print(f"  ⚠️ Could not check robots.txt: {e}")
            return True
    
    def rate_limit(self):
        """Add delay between requests."""
        delay = random.uniform(3, 6)
        print(f"  ⏱️ Rate limiting: waiting {delay:.1f}s...")
        time.sleep(delay)
    
    def scrape_jobs(self, specialty=None, location=None, max_results=100):
        """
        Scrape jobs from HealthTrust.
        
        Args:
            specialty: Job specialty filter
            location: Location filter
            max_results: Maximum jobs to return
        
        Returns:
            List of job dictionaries
        """
        if self.respect_robots and not self.check_robots_txt():
            print("  Respecting robots.txt - skipping HealthTrust")
            return []
        
        jobs = []
        
        # Build search URL
        url = self.JOBS_URL
        params = {}
        if specialty:
            params['specialty'] = specialty
        if location:
            params['location'] = location
        
        print(f"  Fetching: {url}")
        
        try:
            self.rate_limit()
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find job data in JSON format (many modern sites embed this)
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'JobPosting':
                                job = self.parse_json_job(item)
                                if job:
                                    jobs.append(job)
                    elif data.get('@type') == 'JobPosting':
                        job = self.parse_json_job(data)
                        if job:
                            jobs.append(job)
                except:
                    pass
            
            # If no JSON, parse HTML
            if not jobs:
                job_cards = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'job|posting|listing|result', re.I))
                
                for card in job_cards[:max_results]:
                    job = self.parse_job_card(card)
                    if job and job.get('job_title'):
                        jobs.append(job)
            
            print(f"  ✓ Found {len(jobs)} jobs from HealthTrust")
            
        except requests.exceptions.Timeout:
            print(f"  ⚠️ Timeout fetching HealthTrust")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ Error fetching HealthTrust: {e}")
        except Exception as e:
            print(f"  ⚠️ Error parsing HealthTrust: {e}")
        
        return jobs
    
    def parse_json_job(self, data):
        """Parse a JSON-LD JobPosting into a dictionary."""
        try:
            job = {
                'source': 'HealthTrust',
                'job_title': data.get('title', ''),
                'facility_name': data.get('hiringOrganization', {}).get('name', 'HealthTrust Partner'),
                'employment_type': data.get('employmentType', 'Contract'),
                'pay_type': 'Travel'
            }
            
            # Location
            location = data.get('jobLocation', {})
            if isinstance(location, dict):
                address = location.get('address', {})
                job['city'] = address.get('addressLocality', '')
                job['state'] = address.get('addressRegion', '')
                job['location'] = f"{job['city']}, {job['state']}"
            
            # Salary
            salary = data.get('baseSalary', {})
            if isinstance(salary, dict):
                value = salary.get('value', {})
                if isinstance(value, dict):
                    job['pay_rate_low'] = value.get('minValue', 0)
                    job['pay_rate_high'] = value.get('maxValue', 0)
                else:
                    job['pay_rate_low'] = value
                    job['pay_rate_high'] = value
            
            # URL
            job['url'] = data.get('url', '')
            
            return job
        except:
            return None
    
    def parse_job_card(self, card):
        """Parse an HTML job card into a dictionary."""
        job = {
            'source': 'HealthTrust',
            'pay_type': 'Travel'
        }
        
        try:
            text = card.get_text(separator=' ', strip=True)
            
            # Title
            title_elem = card.find(['h2', 'h3', 'h4', 'a'])
            if title_elem:
                job['job_title'] = title_elem.get_text(strip=True)
            
            # Location
            match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s*([A-Z]{2})\b', text)
            if match:
                job['city'] = match.group(1)
                job['state'] = match.group(2)
                job['location'] = f"{job['city']}, {job['state']}"
            
            # Pay
            pay_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
            if pay_match:
                rate = float(pay_match.group(1).replace(',', ''))
                if rate > 500:  # Weekly
                    rate = rate / 36
                job['pay_rate_low'] = round(rate, 2)
                job['pay_rate_high'] = round(rate * 1.1, 2)
            
            # URL
            link = card.find('a', href=True)
            if link:
                href = link.get('href', '')
                if href.startswith('/'):
                    job['url'] = f"{self.BASE_URL}{href}"
                elif href.startswith('http'):
                    job['url'] = href
            
            job['employment_type'] = 'Travel'
            
        except:
            pass
        
        return job


def main():
    """Test the HealthTrust scraper."""
    print("=" * 60)
    print("HealthTrust Workforce Solutions Scraper")
    print("=" * 60)
    
    scraper = HealthTrustScraper(respect_robots=True)
    
    print("\n[HealthTrust]")
    jobs = scraper.scrape_jobs()
    
    print(f"\n  Total jobs found: {len(jobs)}")
    
    if jobs:
        print("\n  Sample jobs:")
        for job in jobs[:5]:
            title = job.get('job_title', 'Unknown')[:40]
            location = job.get('location', 'Unknown')
            print(f"    - {title} | {location}")
    
    return jobs


if __name__ == "__main__":
    main()
