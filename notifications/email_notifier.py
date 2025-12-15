"""
Email Notification Module
Sends daily scrape reports via email using SMTP
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class EmailNotifier:
    """Send email notifications with scrape results."""
    
    def __init__(self):
        """Initialize email settings from environment variables."""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')  # App password for Gmail
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        # Check if email is configured
        self.is_configured = all([
            self.sender_email,
            self.sender_password,
            self.recipient_email
        ])
    
    def send_report(self, jobs, filename=None, subject=None):
        """
        Send a daily report email with job scrape results.
        
        Args:
            jobs: List of job dictionaries
            filename: Optional Excel file to attach
            subject: Custom email subject
        """
        if not self.is_configured:
            print("Email not configured. Skipping notification.")
            print("To enable email, add these to your .env file:")
            print("  SENDER_EMAIL=your-email@gmail.com")
            print("  SENDER_PASSWORD=your-app-password")
            print("  RECIPIENT_EMAIL=recipient@email.com")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject or f"Healthcare Job Scraper Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Build email body
            body = self._build_report_body(jobs)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach Excel file if provided
            if filename and os.path.exists(filename):
                self._attach_file(msg, filename)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Report email sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _build_report_body(self, jobs):
        """Build HTML email body with job statistics."""
        total_jobs = len(jobs)
        
        # Calculate statistics
        jobs_with_pay = [j for j in jobs if j.get('pay_raw')]
        pay_rates = []
        for job in jobs:
            if job.get('pay_rate_low'):
                pay_rates.append(job['pay_rate_low'])
            if job.get('pay_rate_high'):
                pay_rates.append(job['pay_rate_high'])
        
        avg_pay = sum(pay_rates) / len(pay_rates) if pay_rates else 0
        min_pay = min(pay_rates) if pay_rates else 0
        max_pay = max(pay_rates) if pay_rates else 0
        
        # Count by source
        sources = {}
        for job in jobs:
            source = job.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        # Build HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background-color: #003e52; color: white; padding: 20px; }}
                .stats {{ background-color: #eceeef; padding: 15px; margin: 20px 0; }}
                .stat-box {{ display: inline-block; margin: 10px 20px; text-align: center; }}
                .stat-number {{ font-size: 28px; font-weight: bold; color: #003e52; }}
                .stat-label {{ font-size: 12px; color: #666; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th {{ background-color: #003e52; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Healthcare Job Scraper Report</h1>
                <p>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{total_jobs}</div>
                    <div class="stat-label">Total Jobs Found</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(jobs_with_pay)}</div>
                    <div class="stat-label">Jobs with Pay Data</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">${avg_pay:.2f}</div>
                    <div class="stat-label">Avg Hourly Rate</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">${min_pay:.2f} - ${max_pay:.2f}</div>
                    <div class="stat-label">Pay Range</div>
                </div>
            </div>
            
            <h3>Jobs by Source</h3>
            <table>
                <tr>
                    <th>Source</th>
                    <th>Jobs Found</th>
                </tr>
        """
        
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            html += f"""
                <tr>
                    <td>{source}</td>
                    <td>{count}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h3>Sample Jobs (Top 10)</h3>
            <table>
                <tr>
                    <th>Title</th>
                    <th>Facility</th>
                    <th>Location</th>
                    <th>Pay</th>
                    <th>Source</th>
                </tr>
        """
        
        for job in jobs[:10]:
            html += f"""
                <tr>
                    <td>{job.get('job_title', 'N/A')}</td>
                    <td>{job.get('facility_name', 'N/A')}</td>
                    <td>{job.get('location', 'N/A')}</td>
                    <td>{job.get('pay_raw', 'N/A')}</td>
                    <td>{job.get('source', 'N/A')}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <div class="footer">
                <p>This report was automatically generated by your Healthcare Job Scraper.</p>
                <p>Full data is available in the attached Excel file.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _attach_file(self, msg, filename):
        """Attach a file to the email message."""
        with open(filename, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(filename)}"'
            )
            msg.attach(part)
    
    def send_alert(self, message, subject="Healthcare Job Scraper Alert"):
        """Send a simple alert email."""
        if not self.is_configured:
            print(f"Alert (email not configured): {message}")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending alert: {e}")
            return False
