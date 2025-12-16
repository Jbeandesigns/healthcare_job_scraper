#!/usr/bin/env python3
"""
TheirStack API Quick Test
Run this first to verify your API key works and see sample data.

Usage:
    python3 test_theirstack.py
"""

import requests
import json
from datetime import datetime, timedelta

# Your TheirStack API Key
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqZXNzaWNhLmJlYW5AY2FyZXJldi5jb20iLCJwZXJtaXNzaW9ucyI6InVzZXIiLCJjcmVhdGVkX2F0IjoiMjAyNS0xMi0xNlQwMjo1NDozMy41NjA4NzYrMDA6MDAifQ.xjf9TYQce6JWbSIXedBVnm-LHs6uzrouZYCHJWM9jcc"

def test_api():
    """Test the TheirStack API with a simple nursing job search."""
    
    print("=" * 60)
    print("TheirStack API Test")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    url = "https://api.theirstack.com/v1/jobs/search"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Search for RN jobs posted in last 14 days
    fourteen_days_ago = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    
    payload = {
        "job_title_pattern_or": ["Registered Nurse", "RN", "ICU Nurse", "Travel Nurse"],
        "job_country_code_or": ["US"],
        "min_date_posted": fourteen_days_ago,
        "limit": 50,
        "page": 0,
        "order_by": [{"desc": True, "field": "date_posted"}]
    }
    
    print(f"Searching for: RN / ICU Nurse / Travel Nurse jobs")
    print(f"Posted after: {fourteen_days_ago}")
    print(f"Country: US")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"API Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            jobs = data.get("data", [])
            
            print(f"✅ SUCCESS!")
            print(f"Total jobs matching query: {total:,}")
            print(f"Jobs returned in this request: {len(jobs)}")
            print(f"API credits used: 1")
            print()
            
            if jobs:
                print("=" * 100)
                print("SAMPLE JOBS (First 15)")
                print("=" * 100)
                print(f"{'Title':<40} | {'Company':<25} | {'Location':<20} | {'Salary':<25}")
                print("-" * 100)
                
                for job in jobs[:15]:
                    title = job.get("job_title", "N/A")[:38]
                    company = job.get("company_name", "N/A")[:23]
                    city = job.get("city", "")
                    state = job.get("state", "")
                    location = f"{city}, {state}"[:18] if city else "N/A"
                    salary = job.get("salary_string", "")[:23] if job.get("salary_string") else "Not listed"
                    
                    print(f"{title:<40} | {company:<25} | {location:<20} | {salary:<25}")
                
                print()
                print("=" * 100)
                print("DETAILED VIEW - First Job")
                print("=" * 100)
                
                first_job = jobs[0]
                print(f"Title:       {first_job.get('job_title', 'N/A')}")
                print(f"Company:     {first_job.get('company_name', 'N/A')}")
                print(f"Location:    {first_job.get('city', '')}, {first_job.get('state', '')} {first_job.get('country', '')}")
                print(f"Salary:      {first_job.get('salary_string', 'Not listed')}")
                print(f"Date Posted: {first_job.get('date_posted', 'N/A')}")
                print(f"Source:      {first_job.get('source', 'N/A')}")
                print(f"URL:         {first_job.get('final_url', 'N/A')[:80]}")
                
                # Show salary breakdown if available
                min_sal = first_job.get("min_annual_salary")
                max_sal = first_job.get("max_annual_salary")
                if min_sal or max_sal:
                    print(f"\nSalary Details:")
                    if min_sal:
                        hourly = min_sal / 2080
                        print(f"  Min Annual: ${min_sal:,} (${hourly:.2f}/hr)")
                    if max_sal:
                        hourly = max_sal / 2080
                        print(f"  Max Annual: ${max_sal:,} (${hourly:.2f}/hr)")
            
            print()
            print("✅ API is working! You can now run the full scraper.")
            return True
            
        elif response.status_code == 401:
            print("❌ Authentication failed - check your API key")
            print(response.text)
            return False
            
        elif response.status_code == 429:
            print("❌ Rate limit exceeded - wait a bit and try again")
            return False
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text[:500])
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - try again")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


if __name__ == "__main__":
    test_api()
