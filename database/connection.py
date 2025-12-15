"""
Database Connection Manager
Handles SQLAlchemy engine and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

from .models import Base

load_dotenv()


class DatabaseManager:
    """Manage database connections and sessions."""
    
    def __init__(self, database_url=None):
        """Initialize database connection."""
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///healthcare_jobs.db')
        self.engine = create_engine(self.database_url, echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)
        print("Database tables created/verified.")
    
    def get_session(self):
        """Get a new database session."""
        return self.Session()
    
    def close_session(self, session):
        """Close a database session."""
        session.close()
    
    def add_jobs(self, jobs, session=None):
        """
        Add jobs to the database, avoiding duplicates.
        
        Args:
            jobs: List of job dictionaries
            session: Optional existing session
            
        Returns:
            Tuple of (new_count, updated_count)
        """
        from .models import HealthcareJob
        from datetime import datetime
        
        own_session = session is None
        if own_session:
            session = self.get_session()
        
        new_count = 0
        updated_count = 0
        
        try:
            for job_data in jobs:
                # Check if job already exists (by source URL)
                existing = None
                if job_data.get('source_url'):
                    existing = session.query(HealthcareJob).filter_by(
                        source_url=job_data['source_url']
                    ).first()
                
                if existing:
                    # Update last_seen
                    existing.last_seen = datetime.now()
                    updated_count += 1
                else:
                    # Parse location into city/state if possible
                    city, state = self._parse_location(job_data.get('location', ''))
                    
                    # Create new job record
                    new_job = HealthcareJob(
                        job_title=job_data.get('job_title'),
                        specialty=job_data.get('specialty'),
                        facility_name=job_data.get('facility_name'),
                        city=city,
                        state=state,
                        location=job_data.get('location'),
                        pay_raw=job_data.get('pay_raw'),
                        pay_rate_low=job_data.get('pay_rate_low'),
                        pay_rate_high=job_data.get('pay_rate_high'),
                        pay_type=job_data.get('pay_type'),
                        shift_type=job_data.get('shift_type'),
                        employment_type=job_data.get('employment_type'),
                        source=job_data.get('source'),
                        source_url=job_data.get('source_url'),
                        search_query=job_data.get('search_query'),
                    )
                    session.add(new_job)
                    new_count += 1
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"Error adding jobs to database: {e}")
            raise
        
        finally:
            if own_session:
                self.close_session(session)
        
        return new_count, updated_count
    
    def _parse_location(self, location):
        """Parse location string into city and state."""
        if not location:
            return None, None
        
        # Common formats: "City, ST", "City, State", "City, ST 12345"
        parts = location.split(',')
        if len(parts) >= 2:
            city = parts[0].strip()
            state_part = parts[1].strip().split()[0]  # Get first word after comma
            return city, state_part
        
        return location, None
    
    def get_jobs(self, filters=None, limit=100):
        """
        Retrieve jobs from database with optional filters.
        
        Args:
            filters: Dict of filter conditions
            limit: Maximum number of jobs to return
            
        Returns:
            List of HealthcareJob objects
        """
        from .models import HealthcareJob
        
        session = self.get_session()
        try:
            query = session.query(HealthcareJob)
            
            if filters:
                if filters.get('city'):
                    query = query.filter(HealthcareJob.city == filters['city'])
                if filters.get('state'):
                    query = query.filter(HealthcareJob.state == filters['state'])
                if filters.get('source'):
                    query = query.filter(HealthcareJob.source == filters['source'])
                if filters.get('specialty'):
                    query = query.filter(HealthcareJob.specialty.contains(filters['specialty']))
                if filters.get('min_pay'):
                    query = query.filter(HealthcareJob.pay_rate_low >= filters['min_pay'])
            
            jobs = query.order_by(HealthcareJob.scraped_at.desc()).limit(limit).all()
            return jobs
            
        finally:
            self.close_session(session)
    
    def get_statistics(self):
        """Get summary statistics from the database."""
        from .models import HealthcareJob
        from sqlalchemy import func
        
        session = self.get_session()
        try:
            total_jobs = session.query(func.count(HealthcareJob.id)).scalar()
            jobs_with_pay = session.query(func.count(HealthcareJob.id)).filter(
                HealthcareJob.pay_rate_low.isnot(None)
            ).scalar()
            avg_pay = session.query(func.avg(HealthcareJob.pay_rate_low)).filter(
                HealthcareJob.pay_rate_low.isnot(None)
            ).scalar()
            
            sources = session.query(
                HealthcareJob.source,
                func.count(HealthcareJob.id)
            ).group_by(HealthcareJob.source).all()
            
            return {
                'total_jobs': total_jobs,
                'jobs_with_pay': jobs_with_pay,
                'avg_pay': round(avg_pay, 2) if avg_pay else 0,
                'sources': dict(sources)
            }
            
        finally:
            self.close_session(session)
