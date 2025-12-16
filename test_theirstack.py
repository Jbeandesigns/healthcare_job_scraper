#!/usr/bin/env python3
"""
Quick API Test for TheirStack
Run this first to verify your API key works.

SETUP:
    Create a .env file in this folder with:
    THEIRSTACK_API_KEY=your_api_key_here

Usage:
    python3 test_theirstack.py
"""

import requests
from datetime import datetime
import os


def load_api_key():
    """Load API key from .env file."""
    
    api_key = os.environ.get("THEIRSTACK_API_KEY")
    
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
        print("Create a .env file in this folder with:")
        print()
        print('    THEIRSTACK_API_KEY=your_api_key_here')
        print()
        exit(1)
    
    return api_key


def test():
    print("=" * 60)
    print("TheirStack API Test")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print()
    
    api_key = load_api_key()
    print("✓ API key loaded from .env file")
    print()
    
    url = "https://api.theirstack.com/v1/jobs/search"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "job_title_or": ["Registered Nurse", "RN", "ICU Nurse"],
        "job_country_code_or": ["US"],
        "posted_at_max_age_days": 14,
        "limit": 25,
        "offset": 0
    }
    
    print("Searching for: Registered Nurse / RN / ICU Nurse")
    print("Location: US")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            jobs = data.get("data", [])
            
            print(f"✅ SUCCESS!")
            print(f"Total matching jobs: {total:,}")
            print(f"Jobs returned: {len(jobs)}")
            print()
            
            if jobs:
                print("-" * 80)
                print(f"{'Title':<40} | {'Location':<20} | {'Salary':<20}")
                print("-" * 80)
                
                for job in jobs[:10]:
                    title = job.get("job_title", "N/A")[:38]
                    city = job.get("city", "")
                    state = job.get("state", "")
                    location = f"{city}, {state}"[:18] if city else "N/A"
                    salary = job.get("salary_string", "Not listed")[:18] if job.get("salary_string") else "Not listed"
                    
                    print(f"{title:<40} | {location:<20} | {salary:<20}")
                
                print()
                print("✅ API is working! Run: python3 run_healthcare_scraper.py")
                
        elif response.status_code == 401:
            print("❌ INVALID API KEY")
            print("Check your .env file")
            
        elif response.status_code == 422:
            print("❌ INVALID REQUEST")
            print(response.text[:200])
            
        elif response.status_code == 429:
            print("❌ RATE LIMIT - wait a few minutes")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    test()
