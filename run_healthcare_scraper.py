#!/usr/bin/env python3
"""
Healthcare Market Rate Scraper for CareRev
Pulls REAL-TIME nursing job data from Indeed, LinkedIn, Glassdoor & 16+ job boards

SETUP: 
    1. Create a file called .env in this folder with:
       THEIRSTACK_API_KEY=your_api_key_here
    
    2. Make sure .env is in your .gitignore (it should be already)

SCHEDULE: Run on the 1st and 15th of each month

Usage:
    python3 run_healthcare_scraper.py                    # Full run
    python3 run_healthcare_scraper.py --test             # Quick test (1 API call)
"""

import requests
import pandas as pd
from datetime import datetime
import os
import time
import argparse

# ============================================================================
# API KEY - Loaded from .env file (NEVER commit your API key to GitHub!)
# ============================================================================
def load_api_key():
    """Load API key from .env file or environment variable."""
    
    # First try environment variable
    api_key = os.environ.get("THEIRSTACK_API_KEY")
    
    # If not found, try loading from .env file
    if not api_key:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("THEIRSTACK_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    
    if not api_key:
        print("=" * 60)
        print("❌ ERROR: No API key found!")
        print("=" * 60)
        print()
        print("Please create a .env file in this folder with:")
        print()
        print('    THEIRSTACK_API_KEY=your_api_key_here')
        print()
        print("Your API key from TheirStack:")
        print("    https://app.theirstack.com/")
        print()
        print("⚠️  NEVER commit your .env file to GitHub!")
        print("    (It should already be in .gitignore)")
        print()
        exit(1)
    
    return api_key


# ============================================================================
# CONFIGURATION - Nursing job titles to search
# ============================================================================
NURSING_SEARCHES = [
    ["Registered Nurse", "RN"],
    ["ICU Nurse", "Intensive Care Nurse", "Critical Care Nurse"],
    ["ER Nurse", "Emergency Room Nurse", "Emergency Nurse"],
    ["Med Surg Nurse", "Medical Surgical Nurse"],
    ["Telemetry Nurse", "Tele Nurse"],
    ["OR Nurse", "Operating Room Nurse", "Perioperative Nurse"],
    ["Labor and Delivery Nurse", "L&D Nurse", "OB Nurse"],
    ["PACU Nurse", "Post Anesthesia Nurse"],
    ["NICU Nurse", "Neonatal Nurse"],
    ["PICU Nurse", "Pediatric ICU Nurse"],
    ["Stepdown Nurse", "PCU Nurse", "Progressive Care Nurse"],
    ["Oncology Nurse"],
    ["Dialysis Nurse", "Renal Nurse"],
    ["Psych Nurse", "Psychiatric Nurse", "Behavioral Health Nurse"],
    ["Cath Lab Nurse", "Cardiac Cath Nurse"],
    ["Travel Nurse", "Travel RN"],
    ["LPN", "Licensed Practical Nurse", "LVN"],
    ["CNA", "Certified Nursing Assistant", "Nurse Aide"],
    ["Surgical Tech", "Surgical Technologist"],
    ["Respiratory Therapist"],
]


class HealthcareJobScraper:
    """Scrapes healthcare jobs from TheirStack API."""
    
    BASE_URL = "https://api.theirstack.com/v1/jobs/search"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self.all_jobs = []
        self.api_calls = 0
    
    def search(self, job_titles: list, limit: int = 500) -> list:
        """Search for jobs using TheirStack API."""
        
        payload = {
            "job_title_or": job_titles,
            "job_country_code_or": ["US"],
            "posted_at_max_age_days": 14,
            "limit": limit,
            "offset": 0,
        }
        
        try:
            response = self.session.post(self.BASE_URL, json=payload, timeout=60)
            self.api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("data", [])
                total = data.get("total", 0)
                print(f"    ✓ Found {len(jobs)} jobs (total: {total})")
                return jobs
            elif response.status_code == 422:
                print(f"    ⚠️ Invalid request: {response.text[:100]}")
                return []
            elif response.status_code == 429:
                print(f"    ⚠️ Rate limit - waiting 60 seconds...")
                time.sleep(60)
                return []
            elif response.status_code == 401:
                print(f"    ❌ Invalid API key - check your .env file")
                return []
            else:
                print(f"    ⚠️ API Error {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            print(f"    ⚠️ Request timeout")
            return []
        except Exception as e:
            print(f"    ⚠️ Error: {e}")
            return []
    
    def parse_job(self, job: dict, search_category: str) -> dict:
        """Parse raw job into standardized format."""
        
        pay_low = None
        pay_high = None
        
        min_annual = job.get("min_annual_salary")
        max_annual = job.get("max_annual_salary")
        
        if min_annual:
            pay_low = round(min_annual / 2080, 2)
        if max_annual:
            pay_high = round(max_annual / 2080, 2)
        
        title = job.get("job_title", "")
        title_lower = title.lower()
        
        if "travel" in title_lower:
            pay_type = "Travel"
        elif "per diem" in title_lower or "prn" in title_lower:
            pay_type = "Per Diem"
        elif "contract" in title_lower:
            pay_type = "Contract"
        else:
            pay_type = "Staff"
        
        specialty = self.determine_specialty(title, search_category)
        
        return {
            "job_title": title,
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
            "url": job.get("final_url", "") or job.get("url", ""),
            "scrape_date": datetime.now().strftime("%Y-%m-%d"),
        }
    
    def determine_specialty(self, title: str, search_category: str) -> str:
        """Determine specialty from job title."""
        title_lower = title.lower()
        
        specialty_map = {
            "icu": "ICU RN", "intensive care": "ICU RN", "critical care": "ICU RN",
            "emergency": "ER RN", "er ": "ER RN", " ed ": "ER RN",
            "med surg": "Med/Surg RN", "medical surgical": "Med/Surg RN",
            "telemetry": "Tele RN", "tele ": "Tele RN",
            "stepdown": "Stepdown RN", "pcu": "Stepdown RN",
            "operating room": "OR RN", "perioperative": "OR RN",
            "labor": "L&D RN", "l&d": "L&D RN", "delivery": "L&D RN",
            "pacu": "PACU RN", "post anesthesia": "PACU RN",
            "nicu": "NICU RN", "neonatal": "NICU RN",
            "picu": "PICU RN", "pediatric intensive": "PICU RN",
            "oncology": "Oncology RN",
            "dialysis": "Dialysis RN", "renal": "Dialysis RN",
            "psych": "Psych RN", "behavioral": "Psych RN",
            "cath lab": "Cath Lab RN",
            "travel": "Travel RN",
            "lpn": "LPN", "lvn": "LPN",
            "cna": "CNA", "nursing assistant": "CNA",
            "surgical tech": "Surgical Tech",
            "respiratory": "Respiratory Therapist",
        }
        
        for keyword, specialty in specialty_map.items():
            if keyword in title_lower:
                return specialty
        
        if "rn" in title_lower or "nurse" in title_lower:
            return "RN"
        
        return "Other"
    
    def run(self, test_mode: bool = False):
        """Run the full scraper."""
        
        print("\n" + "=" * 70)
        print("🏥 CAREREV HEALTHCARE MARKET RATE SCRAPER")
        print("    Data from: Indeed, LinkedIn, Glassdoor & 16+ job boards")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'TEST (1 search)' if test_mode else 'FULL (all specialties)'}")
        print()
        
        searches = NURSING_SEARCHES[:1] if test_mode else NURSING_SEARCHES
        
        all_jobs = []
        seen_ids = set()
        
        for i, job_titles in enumerate(searches, 1):
            search_name = job_titles[0]
            print(f"[{i}/{len(searches)}] {search_name}...")
            
            jobs = self.search(job_titles)
            
            new_count = 0
            for job in jobs:
                job_id = job.get("id")
                if job_id and job_id not in seen_ids:
                    seen_ids.add(job_id)
                    parsed = self.parse_job(job, search_name)
                    all_jobs.append(parsed)
                    new_count += 1
            
            if not test_mode:
                time.sleep(1)
        
        self.all_jobs = all_jobs
        
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"Total jobs collected: {len(all_jobs)}")
        print(f"API calls made: {self.api_calls}")
        
        if all_jobs:
            df = pd.DataFrame(all_jobs)
            
            jobs_with_pay = df[df["pay_rate_low"].notna()]
            print(f"Jobs with pay rates: {len(jobs_with_pay)}")
            
            if len(jobs_with_pay) > 0:
                avg_rate = jobs_with_pay["pay_rate_low"].mean()
                print(f"Average hourly rate: ${avg_rate:.2f}")
            
            print("\nBy Specialty:")
            for spec, count in df["specialty"].value_counts().head(10).items():
                print(f"  {spec}: {count}")
        
        return all_jobs
    
    def save_excel(self, filename: str = None) -> str:
        """Save results to Excel."""
        if not self.all_jobs:
            print("No jobs to save!")
            return None
        
        os.makedirs("output", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        if not filename:
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"output/healthcare_jobs_{date_str}.xlsx"
        
        df = pd.DataFrame(self.all_jobs)
        
        cols = ["job_title", "specialty", "facility_name", "city", "state", "location",
                "pay_rate_low", "pay_rate_high", "salary_string", "pay_type",
                "employment_type", "date_posted", "source", "url", "scrape_date"]
        df = df[[c for c in cols if c in df.columns]]
        
        df.to_excel(filename, index=False)
        print(f"\n✅ Saved to: {filename}")
        
        data_filename = f"data/healthcare_jobs_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        df.to_excel(data_filename, index=False)
        print(f"✅ Also saved to: {data_filename} (for dashboard)")
        
        return filename


def main():
    parser = argparse.ArgumentParser(description="CareRev Healthcare Market Rate Scraper")
    parser.add_argument("--test", action="store_true", help="Quick test (1 API call)")
    args = parser.parse_args()
    
    # Load API key from .env file
    api_key = load_api_key()
    
    print()
    if args.test:
        print("🧪 TEST MODE - Single search to verify API works")
    else:
        print("📅 FULL RUN - Run this on the 1st and 15th of each month")
    print()
    
    scraper = HealthcareJobScraper(api_key)
    jobs = scraper.run(test_mode=args.test)
    
    if jobs:
        scraper.save_excel()
        
        print("\n" + "=" * 70)
        print("SAMPLE JOBS")
        print("=" * 70)
        
        for job in jobs[:10]:
            title = job["job_title"][:35]
            location = job["location"][:18] if job["location"] else "N/A"
            specialty = job["specialty"][:12]
            
            if job["pay_rate_low"]:
                pay = f"${job['pay_rate_low']:.0f}-${job['pay_rate_high']:.0f}/hr"
            else:
                pay = "Not listed"
            
            print(f"{title:35} | {location:18} | {specialty:12} | {pay}")
    else:
        print("\n❌ No jobs found. Check the error messages above.")


if __name__ == "__main__":
    main()
