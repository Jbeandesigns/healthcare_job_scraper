from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class JobPosting(Base):
    __tablename__ = 'job_postings'
    
    id = Column(Integer, primary_key=True)
    job_title = Column(String(100))
    specialty = Column(String(50))
    facility_name = Column(String(200))
    city = Column(String(100))
    state = Column(String(2))
    pay_rate_low = Column(Float)
    pay_rate_high = Column(Float)
    pay_type = Column(String(20))  # base, per_diem, travel, crisis
    shift_type = Column(String(20))
    employment_type = Column(String(20))
    source = Column(String(50))  # Indeed, Vivian, etc.
    source_url = Column(String(500))
    posted_date = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
