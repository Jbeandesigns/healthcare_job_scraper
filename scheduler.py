"""
Local Scheduler for Healthcare Job Scraper
Runs the scraper daily at a specified time
"""

import schedule
import time
from datetime import datetime
from main import run_scraper
from config.cities import MAJOR_CITIES, TEST_CITIES


def daily_scrape():
    """Run the daily scrape job."""
    print(f"\n[{datetime.now()}] Starting scheduled scrape...")
    try:
        run_scraper(
            cities=MAJOR_CITIES[:10],  # First 10 cities for daily runs
            use_ai_parsing=True,
            send_email=True
        )
        print(f"[{datetime.now()}] Scheduled scrape completed successfully!")
    except Exception as e:
        print(f"[{datetime.now()}] Scheduled scrape failed: {e}")


def test_scrape():
    """Run a quick test scrape."""
    print(f"\n[{datetime.now()}] Running test scrape...")
    run_scraper(
        cities=TEST_CITIES,
        use_ai_parsing=False,
        send_email=False
    )


if __name__ == "__main__":
    print("Healthcare Job Scraper - Local Scheduler")
    print("=" * 50)
    print("Scheduled to run daily at 6:00 AM")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    # Schedule the daily job
    schedule.every().day.at("06:00").do(daily_scrape)
    
    # Also run a test immediately to verify everything works
    print("\nRunning initial test scrape...")
    test_scrape()
    
    # Keep the scheduler running
    print("\nScheduler is running. Waiting for next scheduled run...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
