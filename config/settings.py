"""
Application Settings
Central configuration for the healthcare job scraper
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Scraper Settings
SCRAPER_CONFIG = {
    'headless': True,  # Run browser in headless mode (no GUI)
    'max_pages_per_search': 2,  # Pages to scrape per search query
    'max_results_per_source': 50,  # Max jobs per source per city
    'delay_min': 2,  # Minimum delay between requests (seconds)
    'delay_max': 5,  # Maximum delay between requests (seconds)
    'timeout': 60000,  # Page load timeout (milliseconds)
}

# Which scrapers to run
ACTIVE_SCRAPERS = [
    'indeed',
    'vivian',
    'ziprecruiter',
    'aya',
    'intelycare',
]

# API Settings
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
USE_AI_PARSING = True  # Set to False to disable AI parsing (saves API costs)
AI_BATCH_SIZE = 10  # Number of jobs to parse before pausing

# Database Settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///healthcare_jobs.db')

# Email Settings
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('SENDER_PASSWORD'),
    'recipient_email': os.getenv('RECIPIENT_EMAIL'),
}

# Export Settings
EXPORT_CONFIG = {
    'output_dir': os.getenv('OUTPUT_DIR', './output'),
    'filename_prefix': 'healthcare_jobs',
    'formats': ['xlsx', 'csv'],  # Export formats
}

# Scheduling Settings
SCHEDULE_CONFIG = {
    'daily_run_time': '06:00',  # 6 AM local time
    'timezone': 'America/New_York',
}

# Pay Rate Conversion Assumptions
PAY_CONVERSION = {
    'weekly_hours': 36,  # Standard travel nursing week
    'annual_hours': 2080,  # Standard work year
}

# Specialty Categories for Analysis
SPECIALTIES = [
    'ICU',
    'ER/ED',
    'Med/Surg',
    'OR',
    'L&D',
    'NICU',
    'PICU',
    'Tele',
    'PACU',
    'Cath Lab',
    'Oncology',
    'Dialysis',
    'Home Health',
    'Long Term Care',
    'Rehab',
]

# Job Types
JOB_TYPES = [
    'RN',
    'LPN/LVN',
    'CNA',
    'NP',
    'PA',
    'RT',
    'PT',
    'OT',
    'Medical Assistant',
    'Phlebotomist',
]
