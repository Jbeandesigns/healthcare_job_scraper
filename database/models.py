"""
Database Models
SQLAlchemy models for storing healthcare job data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class HealthcareJob(Base):
    """Model for healthcare job listings."""
    
    __tablename__ = 'healthcare_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic job info
    job_title = Column(String(255))
    specialty = Column(String(100))
    facility_name = Column(String(255))
    
    # Location
    city = Column(String(100))
    state = Column(String(50))
    location = Column(String(255))  # Full location string
    
    # Pay information
    pay_raw = Column(String(255))  # Original pay text
    pay_rate_low = Column(Float)  # Normalized hourly rate (low)
    pay_rate_high = Column(Float)  # Normalized hourly rate (high)
    pay_type = Column(String(50))  # base, per_diem, travel, crisis
    
    # Job details
    shift_type = Column(String(50))  # day, night, rotating, prn
    employment_type = Column(String(50))  # full_time, part_time, prn, contract, travel
    
    # Source tracking
    source = Column(String(100))  # Indeed, Vivian, etc.
    source_url = Column(Text)  # Link to original posting
    search_query = Column(String(255))  # What search query found this job
    
    # Metadata
    scraped_at = Column(DateTime, default=func.now())
    posted_date = Column(DateTime)  # When the job was posted (if available)
    is_active = Column(Boolean, default=True)
    
    # For tracking changes
    first_seen = Column(DateTime, default=func.now())
    last_seen = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<HealthcareJob(title='{self.job_title}', facility='{self.facility_name}', location='{self.location}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'job_title': self.job_title,
            'specialty': self.specialty,
            'facility_name': self.facility_name,
            'city': self.city,
            'state': self.state,
            'location': self.location,
            'pay_raw': self.pay_raw,
            'pay_rate_low': self.pay_rate_low,
            'pay_rate_high': self.pay_rate_high,
            'pay_type': self.pay_type,
            'shift_type': self.shift_type,
            'employment_type': self.employment_type,
            'source': self.source,
            'source_url': self.source_url,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
        }


class ScrapeRun(Base):
    """Model for tracking scrape runs."""
    
    __tablename__ = 'scrape_runs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    status = Column(String(50))  # running, completed, failed
    jobs_found = Column(Integer, default=0)
    jobs_new = Column(Integer, default=0)
    jobs_updated = Column(Integer, default=0)
    error_message = Column(Text)
    cities_scraped = Column(Integer, default=0)
    sources_used = Column(String(500))  # Comma-separated list
    
    def __repr__(self):
        return f"<ScrapeRun(id={self.id}, status='{self.status}', jobs={self.jobs_found})>"


class PayRateHistory(Base):
    """Model for tracking pay rate changes over time."""
    
    __tablename__ = 'pay_rate_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(100))
    state = Column(String(50))
    specialty = Column(String(100))
    job_type = Column(String(50))  # RN, LPN, CNA, etc.
    
    avg_rate = Column(Float)
    min_rate = Column(Float)
    max_rate = Column(Float)
    sample_size = Column(Integer)
    
    recorded_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<PayRateHistory(city='{self.city}', specialty='{self.specialty}', avg=${self.avg_rate:.2f})>"
