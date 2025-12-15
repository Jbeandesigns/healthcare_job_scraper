"""
Healthcare Job Scraper - Main Entry Point
Runs all scrapers and saves results to database/Excel
"""

from scrapers.indeed_scraper import IndeedScraper
from parsers.pay_normalizer import PayNormalizer
from config.cities import MAJOR_CITIES
import pandas as pd
from datetime import datetime

def run_scraper():
    """Main function to run all scrapers."""
    print(f"Starting healthcare job scrape at {datetime.now()}")
    
    all_jobs = []
    normalizer = PayNormalizer()
    
    # Initialize scrapers
    indeed = IndeedScraper()
    
    # Scrape a few test cities first
    test_cities = MAJOR_CITIES[:3]  # Start with just 3 cities for testing
    
    for city, state in test_cities:
        print(f"Scraping jobs in {city}, {state}...")
        try:
            jobs = indeed.scrape(city, state)
            
            # Normalize pay rates
            for job in jobs:
                if job.get('pay_raw'):
                    job['pay_normalized'] = normalizer.normalize(job['pay_raw'])
                    
            all_jobs.extend(jobs)
            print(f"  Found {len(jobs)} jobs")
        except Exception as e:
            print(f"  Error scraping {city}: {e}")
    
    # Export to Excel
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        filename = f"healthcare_jobs_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Saved {len(all_jobs)} jobs to {filename}")
    else:
        print("No jobs found")
    
    return all_jobs

if __name__ == "__main__":
    run_scraper()