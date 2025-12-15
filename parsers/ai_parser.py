import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

class AIJobParser:
    """Use Claude to extract structured data from job postings."""
    
    SYSTEM_PROMPT = '''You are a healthcare job data extraction expert.
    Extract the following from job postings and return valid JSON:
    - job_title: Standardized title (RN, LPN, CNA, NP, etc.)
    - specialty: Unit/department (ICU, ED, Med/Surg, etc.)
    - pay_rate_low: Minimum hourly rate as number
    - pay_rate_high: Maximum hourly rate as number
    - pay_type: 'base', 'per_diem', 'travel', 'crisis'
    - shift_type: 'day', 'night', 'rotating', 'prn'
    - employment_type: 'full_time', 'part_time', 'prn', 'contract'
    Convert weekly rates to hourly (assume 36-hr week).
    Convert annual rates to hourly (assume 2080 hrs/yr).'''
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def parse(self, job_text):
        """Send job text to Claude and get structured data."""
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"Extract job data as JSON: {job_text}"}
            ]
        )
        return json.loads(message.content[0].text)
