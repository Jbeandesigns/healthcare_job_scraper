"""
TheirStack Healthcare Job API Integration
Pulls real-time nursing job data from Indeed, LinkedIn, Glassdoor & 16+ job boards
via the TheirStack aggregation API.

Data freshness: Updated hourly
Free tier: 200 API credits/month (~20,000 jobs)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import time


class TheirStackScraper:
    """
    TheirStack API client for healthcare job data.
    Aggregates from Indeed, LinkedIn, Glassdoor, and 16+ other job boards.
    """
    
    BASE_URL = "https://api.theirstack.com/v1/jobs/search"
    
    # Healthcare job titles to search
    HEALTHCARE_TITLES = [
        "Registered Nurse",
        "RN",
        "ICU Nurse",
        "Emergency Room Nurse",
        "ER Nurse",
        "Med Surg Nurse",
        "Telemetry Nurse",
        "OR Nurse",
        "Operating Room Nurse",
        "Labor and Delivery Nurse",
        "L&D Nurse",
        "PACU Nurse",
        "NICU Nurse",
        "PICU Nurse",
        "Oncology Nurse",
        "Dialysis Nurse",
        "Psych Nurse",
        "Travel Nurse",
        "LPN",
        "Licensed Practical Nurse",
        "CNA",
        "Certified Nursing Assistant",
        "Surgical Tech",
        "Respiratory Therapist",
    ]
    
    # Major US cities for healthcare jobs
    MAJOR_CITIES = [
        "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
        "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA",
        "Dallas, TX", "San Jose, CA", "Austin, TX", "Jacksonville, FL",
        "San Francisco, CA", "Seattle, WA", "Denver, CO", "Boston, MA",
        "Atlanta, GA", "Miami, FL", "Minneapolis, MN", "Portland, OR",
        "Detroit, MI", "Las Vegas, NV", "Nashville, TN", "Cleveland, OH",
        "Indianapolis, IN", "Charlotte, NC", "Tampa, FL", "Orlando, FL",
    ]
    
    def __init__(self, api_key: str = None):
        """
        Initialize the TheirStack client.
        
        Args:
            api_key: TheirStack API key. If not provided, looks for THEIRSTACK_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("THEIRSTACK_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Pass api_key or set THEIRSTACK_API_KEY env var.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        self.all_jobs = []
        self.credits_used = 0
    
    def search_jobs(
        self,
        job_title: str = None,
        job_title_or: list = None,
        location: str = None,
        country_code: str = "US",
        posted_after: str = None,
        min_salary: int = None,
        max_salary: int = None,
        keywords: list = None,
        limit: int = 100,
        page: int = 0,
    ) -> dict:
        """
        Search for jobs using the TheirStack API.
        
        Args:
            job_title: Exact job title to search
            job_title_or: List of job titles (OR search)
            location: City, state or region
            country_code: Country code (default: US)
            posted_after: ISO date string for jobs posted after this date
            min_salary: Minimum salary filter
            max_salary: Maximum salary filter
            keywords: Keywords to search in job description
            limit: Max results per request (up to 100)
            page: Page number for pagination
        
        Returns:
            API response dict with job listings
        """
        # Build request payload
        payload = {
            "page": page,
            "limit": limit,
            "order_by": [{"desc": True, "field": "date_posted"}],
        }
        
        # Job title filter
        if job_title:
            payload["job_title_pattern_or"] = [job_title]
        elif job_title_or:
            payload["job_title_pattern_or"] = job_title_or
        
        # Location filter
        if location:
            payload["job_location_pattern_or"] = [location]
        
        # Country filter
        if country_code:
            payload["job_country_code_or"] = [country_code]
        
        # Date filter (default to last 30 days)
        if posted_after:
            payload["min_date_posted"] = posted_after
        else:
            # Default: last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            payload["min_date_posted"] = thirty_days_ago
        
        # Salary filters
        if min_salary:
            payload["min_salary_usd"] = min_salary
        if max_salary:
            payload["max_salary_usd"] = max_salary
        
        # Keyword search in job description
        if keywords:
            payload["job_description_pattern_or"] = keywords
        
        print(f"  🔍 Searching: {job_title or job_title_or} | {location or 'US'}")
        
        try:
            response = self.session.post(self.BASE_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.credits_used += 1
            
            total = data.get("total", 0)
            jobs = data.get("data", [])
            
            print(f"  ✓ Found {len(jobs)} jobs (total available: {total})")
            
            return data
            
        except requests.exceptions.HTTPError as e:
            print(f"  ⚠️ HTTP Error: {e}")
            if response.status_code == 401:
                print("  → Check your API key")
            elif response.status_code == 429:
                print("  → Rate limit reached, waiting...")
                time.sleep(60)
            return {"data": [], "total": 0}
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ Request Error: {e}")
            return {"data": [], "total": 0}
    
    def search_healthcare_jobs(
        self,
        specialties: list = None,
        cities: list = None,
        include_travel: bool = True,
        days_back: int = 30,
        max_credits: int = 50,
    ) -> list:
        """
        Search for healthcare/nursing jobs across multiple specialties and cities.
        
        Args:
            specialties: List of nursing specialties to search (default: common RN types)
            cities: List of cities to search (default: major US cities)
            include_travel: Include "Travel Nurse" in searches
            days_back: How many days back to search
            max_credits: Maximum API credits to use
        
        Returns:
            List of job dictionaries
        """
        print("\n" + "=" * 60)
        print("TheirStack Healthcare Job Search")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Max credits to use: {max_credits}")
        
        # Default specialties
        if not specialties:
            specialties = [
                "Registered Nurse",
                "ICU Nurse", 
                "ER Nurse",
                "Med Surg Nurse",
                "Telemetry Nurse",
                "OR Nurse",
                "Travel Nurse",
                "LPN",
                "CNA",
            ]
        
        # Default cities (subset of major cities to conserve credits)
        if not cities:
            cities = [
                "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
                "Philadelphia", "Dallas", "San Francisco", "Seattle", "Boston",
                "Atlanta", "Miami", "Denver", "Minneapolis", "Nashville",
            ]
        
        posted_after = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        all_jobs = []
        seen_ids = set()
        
        # Strategy: Search by specialty (more efficient than city-by-city)
        for specialty in specialties:
            if self.credits_used >= max_credits:
                print(f"\n⚠️ Reached max credits ({max_credits}). Stopping.")
                break
            
            print(f"\n[Searching: {specialty}]")
            
            # Search nationwide for this specialty
            result = self.search_jobs(
                job_title=specialty,
                country_code="US",
                posted_after=posted_after,
                limit=100,
            )
            
            jobs = result.get("data", [])
            
            for job in jobs:
                job_id = job.get("id")
                if job_id and job_id not in seen_ids:
                    seen_ids.add(job_id)
                    parsed = self.parse_job(job)
                    if parsed:
                        all_jobs.append(parsed)
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        self.all_jobs = all_jobs
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total jobs found: {len(all_jobs)}")
        print(f"API credits used: {self.credits_used}")
        print(f"Credits remaining: ~{200 - self.credits_used}")
        
        return all_jobs
    
    def parse_job(self, job: dict) -> dict:
        """
        Parse a TheirStack job object into a standardized format.
        
        Args:
            job: Raw job dict from TheirStack API
        
        Returns:
            Standardized job dict for our dashboard
        """
        try:
            parsed = {
                "job_id": job.get("id"),
                "job_title": job.get("job_title", ""),
                "facility_name": job.get("company_name", ""),
                "company_domain": job.get("company_domain", ""),
                "city": job.get("city", ""),
                "state": job.get("state", ""),
                "country": job.get("country", ""),
                "location": f"{job.get('city', '')}, {job.get('state', '')}".strip(", "),
                "date_posted": job.get("date_posted", ""),
                "discovered_at": job.get("discovered_at", ""),
                "url": job.get("final_url", "") or job.get("url", ""),
                "source": job.get("source", "TheirStack"),
                "scrape_date": datetime.now().strftime("%Y-%m-%d"),
            }
            
            # Parse salary
            salary_string = job.get("salary_string", "")
            min_salary = job.get("min_annual_salary")
            max_salary = job.get("max_annual_salary")
            
            if min_salary:
                # Convert annual to hourly (assuming 2080 hours/year)
                parsed["pay_rate_low"] = round(min_salary / 2080, 2)
            if max_salary:
                parsed["pay_rate_high"] = round(max_salary / 2080, 2)
            
            parsed["salary_string"] = salary_string
            
            # Determine pay type from title
            title_lower = parsed["job_title"].lower()
            if "travel" in title_lower:
                parsed["pay_type"] = "Travel"
            elif "per diem" in title_lower or "prn" in title_lower:
                parsed["pay_type"] = "Per Diem"
            elif "contract" in title_lower:
                parsed["pay_type"] = "Contract"
            else:
                parsed["pay_type"] = "Staff"
            
            # Determine specialty
            parsed["specialty"] = self.extract_specialty(parsed["job_title"])
            
            # Employment type
            parsed["employment_type"] = job.get("employment_type", "")
            
            return parsed
            
        except Exception as e:
            print(f"  ⚠️ Error parsing job: {e}")
            return None
    
    def extract_specialty(self, title: str) -> str:
        """Extract nursing specialty from job title."""
        title_lower = title.lower()
        
        specialty_map = {
            "icu": "ICU RN",
            "intensive care": "ICU RN",
            "critical care": "ICU RN",
            "med surg": "Med/Surg RN",
            "medical surgical": "Med/Surg RN",
            "medsurg": "Med/Surg RN",
            "emergency": "ER RN",
            "er ": "ER RN",
            "ed ": "ER RN",
            "telemetry": "Tele RN",
            "tele ": "Tele RN",
            "stepdown": "Stepdown RN",
            "step down": "Stepdown RN",
            "pcu": "Stepdown RN",
            "operating room": "OR RN",
            "or ": "OR RN",
            "perioperative": "OR RN",
            "labor": "L&D RN",
            "l&d": "L&D RN",
            "delivery": "L&D RN",
            "ob ": "L&D RN",
            "pacu": "PACU RN",
            "post anesthesia": "PACU RN",
            "nicu": "NICU RN",
            "neonatal": "NICU RN",
            "picu": "PICU RN",
            "pediatric intensive": "PICU RN",
            "oncology": "Oncology RN",
            "onc ": "Oncology RN",
            "dialysis": "Dialysis RN",
            "renal": "Dialysis RN",
            "psych": "Psych RN",
            "behavioral": "Psych RN",
            "mental health": "Psych RN",
            "rehab": "Rehab RN",
            "rehabilitation": "Rehab RN",
            "cath lab": "Cath Lab RN",
            "cardiac cath": "Cath Lab RN",
            "lpn": "LPN",
            "licensed practical": "LPN",
            "lvn": "LPN",
            "cna": "CNA",
            "nursing assistant": "CNA",
            "nurse aide": "CNA",
            "surgical tech": "Surgical Tech",
            "surg tech": "Surgical Tech",
            "respiratory": "Respiratory Therapist",
        }
        
        for keyword, specialty in specialty_map.items():
            if keyword in title_lower:
                return specialty
        
        # Default for general RN
        if "rn" in title_lower or "nurse" in title_lower:
            return "RN"
        
        return "Other"
    
    def save_to_excel(self, filepath: str = None) -> str:
        """
        Save collected jobs to Excel file.
        
        Args:
            filepath: Output file path (default: auto-generated)
        
        Returns:
            Path to saved file
        """
        if not self.all_jobs:
            print("⚠️ No jobs to save")
            return None
        
        if not filepath:
            os.makedirs("output", exist_ok=True)
            filepath = f"output/healthcare_jobs_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
        
        df = pd.DataFrame(self.all_jobs)
        
        # Reorder columns
        col_order = [
            "job_title", "specialty", "facility_name", "city", "state", "location",
            "pay_rate_low", "pay_rate_high", "salary_string", "pay_type",
            "employment_type", "date_posted", "source", "url", "scrape_date"
        ]
        cols = [c for c in col_order if c in df.columns]
        df = df[cols]
        
        df.to_excel(filepath, index=False)
        print(f"\n✓ Saved {len(df)} jobs to: {filepath}")
        
        return filepath
    
    def save_to_csv(self, filepath: str = None) -> str:
        """Save collected jobs to CSV file."""
        if not self.all_jobs:
            print("⚠️ No jobs to save")
            return None
        
        if not filepath:
            os.makedirs("output", exist_ok=True)
            filepath = f"output/healthcare_jobs_{datetime.now().strftime('%Y-%m-%d_%H%M')}.csv"
        
        df = pd.DataFrame(self.all_jobs)
        df.to_csv(filepath, index=False)
        print(f"\n✓ Saved {len(df)} jobs to: {filepath}")
        
        return filepath


def main():
    """Test the TheirStack integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="TheirStack Healthcare Job Scraper")
    parser.add_argument("--api-key", help="TheirStack API key")
    parser.add_argument("--max-credits", type=int, default=20, help="Max API credits to use")
    parser.add_argument("--days", type=int, default=14, help="Days back to search")
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("THEIRSTACK_API_KEY")
    
    if not api_key:
        print("Error: API key required")
        print("Usage: python theirstack_scraper.py --api-key YOUR_KEY")
        print("   Or: export THEIRSTACK_API_KEY=YOUR_KEY")
        return
    
    # Initialize scraper
    scraper = TheirStackScraper(api_key=api_key)
    
    # Search for healthcare jobs
    jobs = scraper.search_healthcare_jobs(
        days_back=args.days,
        max_credits=args.max_credits,
    )
    
    # Save results
    if jobs:
        scraper.save_to_excel()
        
        # Show sample
        print("\nSample jobs:")
        for job in jobs[:10]:
            title = job.get("job_title", "")[:35]
            location = job.get("location", "")[:20]
            pay_low = job.get("pay_rate_low", "N/A")
            pay_high = job.get("pay_rate_high", "N/A")
            specialty = job.get("specialty", "")
            
            if pay_low and pay_low != "N/A":
                pay = f"${pay_low}-${pay_high}/hr"
            else:
                pay = job.get("salary_string", "N/A")[:20]
            
            print(f"  {title:35} | {location:20} | {specialty:12} | {pay}")
    
    return jobs


if __name__ == "__main__":
    main()
