#!/usr/bin/env python3
"""
Healthcare Market Rate Scraper for CareRev
Pulls REAL-TIME nursing job data from Indeed, LinkedIn, Glassdoor & 16+ job boards
via TheirStack API.

SCHEDULE: Run on the 1st and 15th of each month (100 credits each = 200 free credits)

Usage:
    python3 run_healthcare_scraper.py                    # Full run (100 credits)
    python3 run_healthcare_scraper.py --test             # Quick test (5 credits)
    python3 run_healthcare_scraper.py --specialty icu    # Focus on ICU jobs

Output:
    Creates Excel file in output/ folder: healthcare_jobs_YYYY-MM-DD.xlsx
    Copy to your dashboard's data/ folder for visualization

RECOMMENDED SCHEDULE:
    - 1st of month: Full run (100 credits)
    - 15th of month: Full run (100 credits)
    - Total: 200 credits = FREE tier limit
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import argparse

# ============================================================================
# YOUR API KEY - Keep this private!
# ============================================================================
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqZXNzaWNhLmJlYW5AY2FyZXJldi5jb20iLCJwZXJtaXNzaW9ucyI6InVzZXIiLCJjcmVhdGVkX2F0IjoiMjAyNS0xMi0xNlQwMjo1NDozMy41NjA4NzYrMDA6MDAifQ.xjf9TYQce6JWbSIXedBVnm-LHs6uzrouZYCHJWM9jcc"

# ============================================================================
# CONFIGURATION
# ============================================================================

# Nursing specialties to search
SPECIALTIES = {
    "icu": ["ICU Nurse", "Intensive Care Nurse", "Critical Care Nurse", "ICU RN"],
    "er": ["ER Nurse", "Emergency Room Nurse", "Emergency Department Nurse", "ED RN"],
    "medsurg": ["Med Surg Nurse", "Medical Surgical Nurse", "Med/Surg RN"],
    "tele": ["Telemetry Nurse", "Tele RN", "Cardiac Telemetry"],
    "or": ["OR Nurse", "Operating Room Nurse", "Perioperative Nurse", "Surgical Nurse"],
    "ld": ["L&D Nurse", "Labor and Delivery Nurse", "OB Nurse", "Obstetric Nurse"],
    "pacu": ["PACU Nurse", "Post Anesthesia Nurse", "Recovery Room Nurse"],
    "nicu": ["NICU Nurse", "Neonatal ICU Nurse", "Neonatal Nurse"],
    "picu": ["PICU Nurse", "Pediatric ICU Nurse", "Pediatric Intensive Care"],
    "stepdown": ["Stepdown Nurse", "PCU Nurse", "Progressive Care Nurse"],
    "oncology": ["Oncology Nurse", "Cancer Nurse", "Chemo Nurse"],
    "dialysis": ["Dialysis Nurse", "Renal Nurse", "Nephrology Nurse"],
    "psych": ["Psych Nurse", "Psychiatric Nurse", "Behavioral Health Nurse", "Mental Health Nurse"],
    "rehab": ["Rehab Nurse", "Rehabilitation Nurse"],
    "cath": ["Cath Lab Nurse", "Cardiac Cath Nurse", "IR Nurse"],
    "travel": ["Travel Nurse", "Travel RN", "Traveling Nurse"],
    "lpn": ["LPN", "Licensed Practical Nurse", "LVN"],
    "cna": ["CNA", "Certified Nursing Assistant", "Nurse Aide"],
    "rn": ["Registered Nurse", "RN", "Staff Nurse"],
}


class HealthcareJobScraper:
    """Scrapes healthcare jobs from TheirStack API."""
    
    BASE_URL = "https://api.theirstack.com/v1/jobs/search"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
        self.all_jobs = []
        self.credits_used = 0
    
    def search(self, titles: list, days_back: int = 14, limit: int = 100) -> list:
        """
        Search for jobs by title.
        
        Args:
            titles: List of job titles to search (OR)
            days_back: How many days back to search
            limit: Max results (up to 100)
        
        Returns:
            List of job dicts
        """
        min_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        payload = {
            "job_title_pattern_or": titles,
            "job_country_code_or": ["US"],
            "min_date_posted": min_date,
            "limit": limit,
            "page": 0,
            "order_by": [{"desc": True, "field": "date_posted"}]
        }
        
        try:
            response = self.session.post(self.BASE_URL, json=payload, timeout=30)
            self.credits_used += 1
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                print(f"    ⚠️ API Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"    ⚠️ Request Error: {e}")
            return []
    
    def parse_job(self, job: dict, specialty: str) -> dict:
        """Parse raw job into standardized format."""
        
        # Extract hourly rate from annual salary
        pay_low = None
        pay_high = None
        
        min_annual = job.get("min_annual_salary")
        max_annual = job.get("max_annual_salary")
        
        if min_annual:
            pay_low = round(min_annual / 2080, 2)  # Annual to hourly
        if max_annual:
            pay_high = round(max_annual / 2080, 2)
        
        # Determine pay type
        title_lower = job.get("job_title", "").lower()
        if "travel" in title_lower:
            pay_type = "Travel"
        elif "per diem" in title_lower or "prn" in title_lower:
            pay_type = "Per Diem"
        elif "contract" in title_lower:
            pay_type = "Contract"
        else:
            pay_type = "Staff"
        
        return {
            "job_title": job.get("job_title", ""),
            "specialty": specialty,
            "facility_name": job.get("company_name", ""),
            "city": job.get("city", ""),
            "state": job.get("state", ""),
            "location": f"{job.get('city', '')}, {job.get('state', '')}".strip(", "),
            "pay_rate_low": pay_low,
            "pay_rate_high": pay_high,
            "salary_string": job.get("salary_string", ""),
            "pay_type": pay_type,
            "employment_type": job.get("employment_type", ""),
            "date_posted": job.get("date_posted", ""),
            "source": job.get("source", "TheirStack"),
            "url": job.get("final_url", ""),
            "scrape_date": datetime.now().strftime("%Y-%m-%d"),
        }
    
    def run(self, specialties: list = None, max_credits: int = 20, days_back: int = 14):
        """
        Run the full scraper.
        
        Args:
            specialties: List of specialty keys (e.g., ["icu", "er"]) or None for all
            max_credits: Maximum API credits to use
            days_back: How many days back to search
        
        Returns:
            List of all jobs
        """
        print("\n" + "=" * 70)
        print("🏥 HEALTHCARE MARKET RATE SCRAPER")
        print("    Data from: Indeed, LinkedIn, Glassdoor & 16+ job boards")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Max credits: {max_credits}")
        print(f"Days back: {days_back}")
        print()
        
        # Determine which specialties to search
        if specialties:
            search_specialties = {k: v for k, v in SPECIALTIES.items() if k in specialties}
        else:
            search_specialties = SPECIALTIES
        
        print(f"Searching {len(search_specialties)} specialty categories...")
        print()
        
        all_jobs = []
        seen_ids = set()
        
        for specialty_key, titles in search_specialties.items():
            if self.credits_used >= max_credits:
                print(f"\n⚠️ Reached max credits ({max_credits})")
                break
            
            specialty_name = specialty_key.upper()
            print(f"[{specialty_name}] Searching: {', '.join(titles[:2])}...")
            
            jobs = self.search(titles, days_back=days_back)
            
            new_count = 0
            for job in jobs:
                job_id = job.get("id")
                if job_id and job_id not in seen_ids:
                    seen_ids.add(job_id)
                    parsed = self.parse_job(job, specialty_name)
                    all_jobs.append(parsed)
                    new_count += 1
            
            print(f"    ✓ Found {new_count} new jobs")
            
            # Small delay between requests
            time.sleep(0.3)
        
        self.all_jobs = all_jobs
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"Total jobs collected: {len(all_jobs)}")
        print(f"API credits used: {self.credits_used}")
        print(f"Credits remaining: ~{200 - self.credits_used}")
        
        # Stats by specialty
        if all_jobs:
            print("\nJobs by Specialty:")
            df = pd.DataFrame(all_jobs)
            for spec, count in df["specialty"].value_counts().items():
                print(f"  {spec}: {count}")
            
            # Pay rate stats
            jobs_with_pay = df[df["pay_rate_low"].notna()]
            if len(jobs_with_pay) > 0:
                print(f"\nJobs with pay data: {len(jobs_with_pay)}")
                print(f"Average hourly rate: ${jobs_with_pay['pay_rate_low'].mean():.2f}")
                print(f"Rate range: ${jobs_with_pay['pay_rate_low'].min():.2f} - ${jobs_with_pay['pay_rate_high'].max():.2f}")
        
        return all_jobs
    
    def save_excel(self, filename: str = None) -> str:
        """Save results to Excel."""
        if not self.all_jobs:
            print("No jobs to save!")
            return None
        
        os.makedirs("output", exist_ok=True)
        
        if not filename:
            filename = f"output/healthcare_jobs_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
        
        df = pd.DataFrame(self.all_jobs)
        
        # Reorder columns
        cols = ["job_title", "specialty", "facility_name", "city", "state", "location",
                "pay_rate_low", "pay_rate_high", "salary_string", "pay_type",
                "employment_type", "date_posted", "source", "url", "scrape_date"]
        df = df[[c for c in cols if c in df.columns]]
        
        df.to_excel(filename, index=False)
        
        print(f"\n✅ Saved to: {filename}")
        return filename


def main():
    parser = argparse.ArgumentParser(description="Healthcare Market Rate Scraper for CareRev")
    parser.add_argument("--max-credits", type=int, default=100, 
                        help="Max API credits to use (default: 100 for full run)")
    parser.add_argument("--days", type=int, default=14,
                        help="Days back to search (default: 14)")
    parser.add_argument("--specialty", type=str,
                        help="Focus on specific specialty (icu, er, medsurg, etc.)")
    parser.add_argument("--test", action="store_true",
                        help="Quick test run with only 5 credits")
    args = parser.parse_args()
    
    # Determine credits
    if args.test:
        max_credits = 5
        print("🧪 TEST MODE - Using only 5 credits")
    else:
        max_credits = args.max_credits
        print(f"📅 FULL RUN - Run this on the 1st and 15th of each month")
        print(f"   Credits this run: {max_credits}")
        print(f"   Monthly budget: 200 (free tier)")
        print()
    
    # Determine specialties
    specialties = None
    if args.specialty:
        specialties = [args.specialty.lower()]
    
    # Run scraper
    scraper = HealthcareJobScraper(API_KEY)
    jobs = scraper.run(
        specialties=specialties,
        max_credits=max_credits,
        days_back=args.days
    )
    
    # Save results
    if jobs:
        scraper.save_excel()
        
        # Show sample
        print("\n" + "=" * 70)
        print("SAMPLE JOBS")
        print("=" * 70)
        
        for job in jobs[:10]:
            title = job["job_title"][:35]
            location = job["location"][:18]
            specialty = job["specialty"][:10]
            pay = f"${job['pay_rate_low']}-${job['pay_rate_high']}/hr" if job["pay_rate_low"] else "N/A"
            
            print(f"{title:35} | {location:18} | {specialty:10} | {pay}")


if __name__ == "__main__":
    main()
