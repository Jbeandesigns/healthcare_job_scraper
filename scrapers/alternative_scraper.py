"""
Alternative Healthcare Job Scraper
Uses job boards that allow scraping (unlike Indeed/Vivian which block it)

Included Sources:
- BluePipes (aggregates from 100+ agencies - 60,000+ jobs)
- Fastaff (Rapid Response travel nursing)
- HealthTrust Workforce Solutions (HCA Healthcare)
- Gypsy Nurse (travel nursing community)

Usage:
    python alternative_scraper.py
    python alternative_scraper.py --specialty icu
    python alternative_scraper.py --state CA
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import os
from datetime import datetime
from urllib.robotparser import RobotFileParser
import argparse


class AlternativeScraper:
    """Combined scraper for alternative healthcare job boards."""
    
    def __init__(self, respect_robots=True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.respect_robots = respect_robots
        self.all_jobs = []
    
    def check_robots(self, url):
        """Check if a URL is allowed by robots.txt."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            allowed = rp.can_fetch("*", url)
            return allowed
        except:
            return True  # Proceed if can't check
    
    def rate_limit(self, min_delay=3, max_delay=6):
        """Add random delay between requests."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def scrape_bluepipes(self):
        """Scrape jobs from BluePipes."""
        print("\n" + "=" * 50)
        print("[BluePipes] - Travel Nursing Job Aggregator")
        print("=" * 50)
        
        jobs = []
        base_url = "https://www.bluepipes.com"
        
        # BluePipes job pages
        urls = [
            f"{base_url}/jobs/travel/nursing/registered-nurse/",
            f"{base_url}/jobs/travel/nursing/lpn/",
        ]
        
        for url in urls:
            if self.respect_robots and not self.check_robots(url):
                print(f"  ⛔ robots.txt DISALLOWS: {url}")
                continue
            
            print(f"  Checking: {url}")
            
            try:
                self.rate_limit()
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for job count info
                    text = soup.get_text()
                    count_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:jobs?|positions?|listings?)', text, re.I)
                    if count_match:
                        print(f"  ✓ BluePipes reports {count_match.group(1)} jobs available")
                    
                    # Find job data
                    job_elements = soup.find_all(['tr', 'div', 'li'], class_=re.compile(r'job|listing', re.I))
                    
                    for elem in job_elements[:50]:
                        job = self.parse_generic_job(elem, "BluePipes")
                        if job.get('job_title'):
                            job['pay_type'] = 'Travel'
                            jobs.append(job)
                    
                    print(f"  ✓ Parsed {len(jobs)} job listings")
                else:
                    print(f"  ⚠️ Status {response.status_code}")
                    
            except Exception as e:
                print(f"  ⚠️ Error: {str(e)[:50]}")
        
        return jobs
    
    def scrape_fastaff(self):
        """Scrape jobs from Fastaff."""
        print("\n" + "=" * 50)
        print("[Fastaff] - Rapid Response Travel Nursing")
        print("=" * 50)
        
        jobs = []
        base_url = "https://www.fastaff.com"
        url = f"{base_url}/jobs"
        
        if self.respect_robots and not self.check_robots(url):
            print(f"  ⛔ robots.txt DISALLOWS: {url}")
            return jobs
        
        print(f"  Checking: {url}")
        
        try:
            self.rate_limit()
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_links = soup.find_all('a', href=re.compile(r'/jobs?/|/position|/specialty', re.I))
                
                seen = set()
                for link in job_links:
                    href = link.get('href', '')
                    if href in seen:
                        continue
                    seen.add(href)
                    
                    text = link.get_text(strip=True)
                    if len(text) > 5 and 'menu' not in text.lower():
                        job = {
                            'source': 'Fastaff',
                            'job_title': text,
                            'pay_type': 'Travel',
                            'url': f"{base_url}{href}" if href.startswith('/') else href
                        }
                        
                        # Extract specialty from title
                        specialty_map = {
                            'icu': 'ICU RN', 'er ': 'ER RN', 'emergency': 'ER RN',
                            'med surg': 'Med/Surg RN', 'telemetry': 'Tele RN',
                            'operating': 'OR RN', 'labor': 'L&D RN', 'l&d': 'L&D RN'
                        }
                        for key, val in specialty_map.items():
                            if key in text.lower():
                                job['specialty'] = val
                                break
                        
                        jobs.append(job)
                
                print(f"  ✓ Found {len(jobs)} job links")
            else:
                print(f"  ⚠️ Status {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️ Error: {str(e)[:50]}")
        
        return jobs
    
    def scrape_healthtrust(self):
        """Scrape jobs from HealthTrust Workforce Solutions."""
        print("\n" + "=" * 50)
        print("[HealthTrust] - HCA Healthcare Staffing")
        print("=" * 50)
        
        jobs = []
        url = "https://healthtrustws.com/jobs/search"
        
        if self.respect_robots and not self.check_robots(url):
            print(f"  ⛔ robots.txt DISALLOWS: {url}")
            return jobs
        
        print(f"  Checking: {url}")
        
        try:
            self.rate_limit()
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job elements
                job_cards = soup.find_all(['div', 'article', 'li'], 
                    class_=re.compile(r'job|posting|listing|result|card', re.I))
                
                for card in job_cards[:100]:
                    job = self.parse_generic_job(card, "HealthTrust")
                    if job.get('job_title'):
                        jobs.append(job)
                
                print(f"  ✓ Found {len(jobs)} jobs")
            else:
                print(f"  ⚠️ Status {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️ Error: {str(e)[:50]}")
        
        return jobs
    
    def scrape_gypsynurse(self):
        """Scrape jobs from The Gypsy Nurse."""
        print("\n" + "=" * 50)
        print("[Gypsy Nurse] - Travel Nursing Community")
        print("=" * 50)
        
        jobs = []
        url = "https://www.thegypsynurse.com/jobs/"
        
        if self.respect_robots and not self.check_robots(url):
            print(f"  ⛔ robots.txt DISALLOWS: {url}")
            return jobs
        
        print(f"  Checking: {url}")
        
        try:
            self.rate_limit()
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_elements = soup.find_all(['div', 'article', 'li'], 
                    class_=re.compile(r'job|listing|post', re.I))
                
                for elem in job_elements[:50]:
                    job = self.parse_generic_job(elem, "Gypsy Nurse")
                    if job.get('job_title'):
                        job['pay_type'] = 'Travel'
                        jobs.append(job)
                
                print(f"  ✓ Found {len(jobs)} jobs")
            else:
                print(f"  ⚠️ Status {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️ Error: {str(e)[:50]}")
        
        return jobs
    
    def parse_generic_job(self, element, source):
        """Parse a generic job element."""
        job = {'source': source}
        
        try:
            text = element.get_text(separator=' ', strip=True)
            
            # Skip short elements
            if len(text) < 10:
                return job
            
            # Title
            title_elem = element.find(['h2', 'h3', 'h4', 'a', 'strong'])
            if title_elem:
                job['job_title'] = title_elem.get_text(strip=True)[:100]
            
            # Location
            loc_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s*([A-Z]{2})\b', text)
            if loc_match:
                job['city'] = loc_match.group(1)
                job['state'] = loc_match.group(2)
                job['location'] = f"{job['city']}, {job['state']}"
            
            # Pay rate
            pay_match = re.search(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
            if pay_match:
                rate = float(pay_match.group(1).replace(',', ''))
                if rate > 500:  # Weekly rate
                    rate = rate / 36
                job['pay_rate_low'] = round(rate, 2)
                job['pay_rate_high'] = round(rate * 1.1, 2)
            
            # Specialty
            specialty_keywords = {
                'icu': 'ICU RN', 'intensive care': 'ICU RN',
                'med surg': 'Med/Surg RN', 'medical surgical': 'Med/Surg RN',
                'emergency': 'ER RN', 'er ': 'ER RN',
                'telemetry': 'Tele RN', 'tele ': 'Tele RN',
                'operating room': 'OR RN', 'or ': 'OR RN',
                'labor': 'L&D RN', 'l&d': 'L&D RN',
                'pacu': 'PACU RN', 'nicu': 'NICU RN',
                'stepdown': 'Stepdown RN', 'pcu': 'Stepdown RN'
            }
            text_lower = text.lower()
            for keyword, specialty in specialty_keywords.items():
                if keyword in text_lower:
                    job['specialty'] = specialty
                    break
            
            # URL
            link = element.find('a', href=True)
            if link:
                job['url'] = link.get('href', '')
            
            job['employment_type'] = 'Travel'
            job['scrape_date'] = datetime.now().strftime('%Y-%m-%d')
            
        except:
            pass
        
        return job
    
    def run_all(self):
        """Run all scrapers and combine results."""
        print("\n" + "=" * 60)
        print("ALTERNATIVE HEALTHCARE JOB SCRAPER")
        print("Sources: BluePipes, Fastaff, HealthTrust, Gypsy Nurse")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Robots.txt checking: {'ENABLED' if self.respect_robots else 'DISABLED'}")
        
        all_jobs = []
        
        # Run each scraper
        all_jobs.extend(self.scrape_bluepipes())
        all_jobs.extend(self.scrape_fastaff())
        all_jobs.extend(self.scrape_healthtrust())
        all_jobs.extend(self.scrape_gypsynurse())
        
        self.all_jobs = all_jobs
        
        return all_jobs
    
    def save_to_excel(self, filepath=None):
        """Save results to Excel file."""
        if not self.all_jobs:
            print("\n⚠️ No jobs to save")
            return None
        
        if not filepath:
            os.makedirs('output', exist_ok=True)
            filepath = f"output/healthcare_jobs_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
        
        df = pd.DataFrame(self.all_jobs)
        
        # Reorder columns
        col_order = ['job_title', 'specialty', 'facility_name', 'city', 'state', 'location',
                     'pay_rate_low', 'pay_rate_high', 'pay_type', 'employment_type', 
                     'source', 'url', 'scrape_date']
        cols = [c for c in col_order if c in df.columns]
        df = df[cols]
        
        df.to_excel(filepath, index=False)
        print(f"\n✓ Saved {len(df)} jobs to: {filepath}")
        
        return filepath


def main():
    parser = argparse.ArgumentParser(description='Alternative Healthcare Job Scraper')
    parser.add_argument('--specialty', help='Filter by specialty (icu, er, medsurg, etc.)')
    parser.add_argument('--state', help='Filter by state (CA, TX, NY, etc.)')
    parser.add_argument('--no-robots', action='store_true', help='Skip robots.txt checking')
    args = parser.parse_args()
    
    scraper = AlternativeScraper(respect_robots=not args.no_robots)
    jobs = scraper.run_all()
    
    # Apply filters
    if args.specialty:
        jobs = [j for j in jobs if args.specialty.lower() in j.get('specialty', '').lower() 
                or args.specialty.lower() in j.get('job_title', '').lower()]
    
    if args.state:
        jobs = [j for j in jobs if args.state.upper() == j.get('state', '').upper()]
    
    scraper.all_jobs = jobs
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total jobs scraped: {len(jobs)}")
    
    if jobs:
        # Count by source
        sources = {}
        for job in jobs:
            src = job.get('source', 'Unknown')
            sources[src] = sources.get(src, 0) + 1
        
        print("\nBy source:")
        for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {src}: {count}")
        
        # Save results
        filepath = scraper.save_to_excel()
        
        # Show sample
        print("\nSample jobs:")
        for job in jobs[:5]:
            print(f"  - {job.get('job_title', 'Unknown')[:40]} | {job.get('location', 'Unknown')} | {job.get('source', '')}")
    
    return jobs


if __name__ == "__main__":
    main()
