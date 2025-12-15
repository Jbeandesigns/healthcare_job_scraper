"""
AI-Powered Job Parser
Uses Claude (Anthropic) to intelligently extract and normalize job data
"""

import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()


class AIJobParser:
    """Use Claude to extract structured data from job postings."""
    
    SYSTEM_PROMPT = """You are a healthcare job data extraction expert. 
    Extract the following from job postings and return ONLY valid JSON (no markdown, no explanation):
    
    {
        "job_title": "Standardized title (RN, LPN, CNA, NP, PA, RT, etc.)",
        "specialty": "Unit/department (ICU, ED, Med/Surg, OR, L&D, Tele, PACU, etc.)",
        "pay_rate_low": minimum hourly rate as number only (convert weekly/annual to hourly),
        "pay_rate_high": maximum hourly rate as number only,
        "pay_type": "base, per_diem, travel, or crisis",
        "shift_type": "day, night, rotating, or prn",
        "employment_type": "full_time, part_time, prn, contract, or travel"
    }
    
    Conversion rules:
    - Weekly rates: divide by 36 (standard travel nursing hours)
    - Annual rates: divide by 2080
    - If only one rate given, use it for both low and high
    - If no pay info, use null for pay fields
    """
    
    def __init__(self):
        """Initialize the Anthropic client."""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def parse(self, job_text):
        """Send job text to Claude and get structured data."""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {
                        "role": "user", 
                        "content": f"Extract job data as JSON from this posting:\n\n{job_text}"
                    }
                ],
                system=self.SYSTEM_PROMPT
            )
            
            # Extract the text response
            response_text = message.content[0].text
            
            # Clean up response (remove any markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return None
    
    def parse_batch(self, jobs, batch_size=5):
        """Parse multiple jobs, adding AI-extracted fields to each."""
        parsed_jobs = []
        
        for i, job in enumerate(jobs):
            # Create a text representation of the job for parsing
            job_text = f"""
            Title: {job.get('job_title', 'Unknown')}
            Company: {job.get('facility_name', 'Unknown')}
            Location: {job.get('location', 'Unknown')}
            Pay: {job.get('pay_raw', 'Not specified')}
            """
            
            # Only parse if we have pay info to extract
            if job.get('pay_raw'):
                parsed = self.parse(job_text)
                if parsed:
                    job.update({
                        'pay_rate_low': parsed.get('pay_rate_low'),
                        'pay_rate_high': parsed.get('pay_rate_high'),
                        'pay_type': parsed.get('pay_type'),
                        'specialty': parsed.get('specialty') or job.get('specialty'),
                        'shift_type': parsed.get('shift_type') or job.get('shift_type'),
                        'employment_type': parsed.get('employment_type') or job.get('employment_type')
                    })
            
            parsed_jobs.append(job)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"    Parsed {i + 1}/{len(jobs)} jobs with AI")
        
        return parsed_jobs
