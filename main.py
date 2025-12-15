"""
Healthcare Job Scraper - Main Entry Point
Orchestrates all scrapers, parsing, storage, and notifications

================================================================================
ETHICAL SCRAPING NOTICE
================================================================================
This scraper is designed with ethical considerations in mind:
- Respects robots.txt directives
- Implements rate limiting (3-7 second delays between requests)
- Does not bypass authentication or access restricted areas
- Intended for personal research and market analysis only

Please review each job board's Terms of Service before use.
================================================================================
"""

import os
import sys
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import scrapers
from scrapers.indeed_scraper import IndeedScraper
from scrapers.vivian_scraper import VivianScraper
from scrapers.ziprecruiter_scraper import ZipRecruiterScraper
from scrapers.aya_scraper import AyaHealthcareScraper
from scrapers.intelycare_scraper import IntelyCareScraper
from scrapers.base_scraper import print_tos_notice, TOS_NOTICE

# Import parsers
from parsers.pay_normalizer import PayNormalizer
from parsers.ai_parser import AIJobParser

# Import config
from config.cities import MAJOR_CITIES, TEST_CITIES

# Import notifications
from notifications.email_notifier import EmailNotifier

# Import database
from database.connection import DatabaseManager


def run_scraper(
    cities=None,
    scrapers_to_use=None,
    use_ai_parsing=True,
    save_to_db=True,
    send_email=True,
    output_dir='./output',
    respect_robots=True,  # Always respect robots.txt by default
    skip_tos_notice=False  # Set True for automated runs (GitHub Actions)
):
    """
    Main function to run all healthcare job scrapers.
    
    Args:
        cities: List of (city, state) tuples to scrape
        scrapers_to_use: List of scraper names to use
        use_ai_parsing: Whether to use AI for enhanced parsing
        save_to_db: Whether to save results to database
        send_email: Whether to send email notification
        output_dir: Directory to save Excel exports
        respect_robots: Whether to check robots.txt (recommended: True)
        skip_tos_notice: Skip TOS notice (for automated/CI runs)
    
    Returns:
        List of all scraped jobs
    """
    start_time = datetime.now()
    
    # Print ethical notice
    if not skip_tos_notice:
        print("\n" + "="*70)
        print("HEALTHCARE JOB SCRAPER - ETHICAL SCRAPING MODE")
        print("="*70)
        print("""
This scraper follows ethical web scraping practices:
  ✓ Checks robots.txt before accessing each site
  ✓ Respects Crawl-delay directives  
  ✓ Rate limits requests (3-7 second delays)
  ✓ Does not access restricted or authenticated areas

For Terms of Service links, run: python main.py --tos
        """)
    
    print(f"\n{'='*60}")
    print(f"Healthcare Job Scraper")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Default to test cities for safety
    if cities is None:
        cities = TEST_CITIES
        print(f"Using TEST mode with {len(cities)} cities")
    
    # Default scrapers
    if scrapers_to_use is None:
        scrapers_to_use = ['indeed', 'vivian', 'aya', 'intelycare']
    
    # Initialize components
    normalizer = PayNormalizer()
    all_jobs = []
    
    # Initialize scrapers with robots.txt checking enabled
    scrapers = {}
    if 'indeed' in scrapers_to_use:
        scrapers['Indeed'] = IndeedScraper(respect_robots=respect_robots)
    if 'vivian' in scrapers_to_use:
        scrapers['Vivian'] = VivianScraper(respect_robots=respect_robots)
    if 'ziprecruiter' in scrapers_to_use:
        scrapers['ZipRecruiter'] = ZipRecruiterScraper(respect_robots=respect_robots)
    if 'aya' in scrapers_to_use:
        scrapers['Aya Healthcare'] = AyaHealthcareScraper(respect_robots=respect_robots)
    if 'intelycare' in scrapers_to_use:
        scrapers['IntelyCare'] = IntelyCareScraper(respect_robots=respect_robots)
    
    print(f"Active scrapers: {', '.join(scrapers.keys())}")
    print(f"Cities to scrape: {len(cities)}")
    print(f"Robots.txt checking: {'ENABLED ✓' if respect_robots else 'DISABLED ⚠️'}")
    print()
    
    # Scrape each city
    for city, state in cities:
        print(f"\n{'─'*60}")
        print(f"📍 Scraping {city}, {state}")
        print(f"{'─'*60}")
        
        for name, scraper in scrapers.items():
            try:
                print(f"\n[{name}]")
                jobs = scraper.scrape(city, state)
                
                # Add city/state to each job
                for job in jobs:
                    job['city'] = city
                    job['state'] = state
                
                all_jobs.extend(jobs)
                
                # Print session stats for this scraper
                stats = scraper.get_session_stats()
                print(f"  ✓ Found {len(jobs)} jobs")
                print(f"  ℹ️ Session: {stats['requests']} requests, {stats['requests_per_minute']:.1f}/min")
                
            except Exception as e:
                print(f"  ✗ Error with {name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Scraping complete! Total raw jobs: {len(all_jobs)}")
    print(f"{'='*60}\n")
    
    # Normalize pay rates
    print("Normalizing pay rates...")
    jobs_with_pay = 0
    for job in all_jobs:
        if job.get('pay_raw'):
            normalized = normalizer.normalize(job['pay_raw'])
            if normalized:
                job['pay_rate_low'] = normalized['low']
                job['pay_rate_high'] = normalized['high']
                job['pay_type'] = normalized['type']
                jobs_with_pay += 1
    
    print(f"  Jobs with normalized pay: {jobs_with_pay}")
    
    # AI parsing (optional)
    if use_ai_parsing and os.getenv('ANTHROPIC_API_KEY'):
        print("\nEnhancing data with AI parsing...")
        try:
            ai_parser = AIJobParser()
            # Only parse jobs that need it (have pay but no specialty)
            jobs_to_parse = [j for j in all_jobs if j.get('pay_raw') and not j.get('specialty')][:20]
            if jobs_to_parse:
                ai_parser.parse_batch(jobs_to_parse)
                print(f"  AI parsed {len(jobs_to_parse)} jobs")
        except Exception as e:
            print(f"  AI parsing error (continuing without): {e}")
    
    # Save to database
    if save_to_db:
        print("\nSaving to database...")
        try:
            db = DatabaseManager()
            db.create_tables()
            new_count, updated_count = db.add_jobs(all_jobs)
            print(f"  New jobs: {new_count}")
            print(f"  Updated jobs: {updated_count}")
        except Exception as e:
            print(f"  Database error: {e}")
    
    # Export to Excel
    print("\nExporting to Excel...")
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(
        output_dir,
        f"healthcare_jobs_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
    )
    
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        
        # Reorder columns for better readability
        column_order = [
            'job_title', 'specialty', 'facility_name', 'city', 'state', 'location',
            'pay_raw', 'pay_rate_low', 'pay_rate_high', 'pay_type',
            'shift_type', 'employment_type', 'source', 'source_url', 'scraped_at'
        ]
        # Only include columns that exist
        columns = [c for c in column_order if c in df.columns]
        df = df[columns]
        
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"  Saved to: {filename}")
    else:
        print("  No jobs to export")
    
    # Send email notification
    if send_email:
        print("\nSending email notification...")
        notifier = EmailNotifier()
        notifier.send_report(all_jobs, filename)
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total jobs scraped: {len(all_jobs)}")
    print(f"Jobs with pay data: {jobs_with_pay}")
    print(f"Duration: {duration}")
    print(f"Output file: {filename}")
    print(f"{'='*60}\n")
    
    return all_jobs


def main():
    """Entry point when running as script."""
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--tos':
            # Print Terms of Service notice
            print_tos_notice()
            return
        
        elif sys.argv[1] == '--full':
            # Full run with all cities
            print("Running FULL scrape with all cities...")
            run_scraper(
                cities=MAJOR_CITIES,
                use_ai_parsing=True,
                send_email=True,
                respect_robots=True
            )
        
        elif sys.argv[1] == '--test':
            # Test run with 3 cities
            print("Running TEST scrape...")
            run_scraper(
                cities=TEST_CITIES,
                use_ai_parsing=False,
                send_email=False,
                respect_robots=True
            )
        
        elif sys.argv[1] == '--help':
            print("""
Healthcare Job Scraper - Usage

Commands:
  python main.py           Run test scrape (3 cities)
  python main.py --test    Run test scrape (3 cities)
  python main.py --full    Run full scrape (all cities)
  python main.py --tos     Show Terms of Service notice
  python main.py --help    Show this help message

Ethical Features:
  - Respects robots.txt directives
  - Rate limits requests (3-7 second delays)
  - Monitors request rate and slows down automatically

Environment Variables (.env file):
  ANTHROPIC_API_KEY    - Required for AI parsing
  SENDER_EMAIL         - Gmail address for sending reports
  SENDER_PASSWORD      - Gmail App Password
  RECIPIENT_EMAIL      - Where to send reports
            """)
            return
        
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python main.py [--test|--full|--tos|--help]")
    
    else:
        # Default: test run (for GitHub Actions, skip TOS notice)
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        run_scraper(
            cities=TEST_CITIES,
            use_ai_parsing=True,
            send_email=True,
            respect_robots=True,
            skip_tos_notice=is_github_actions
        )


if __name__ == "__main__":
    main()
