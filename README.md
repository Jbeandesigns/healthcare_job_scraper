# Healthcare Job Scraper

An AI-powered web scraper that collects healthcare job listings from multiple job boards, normalizes pay rates, and generates daily reports.

## Features

- **Multi-source scraping**: Indeed, Vivian Health, ZipRecruiter, Aya Healthcare, IntelyCare
- **AI-powered parsing**: Uses Claude (Anthropic) to intelligently extract job details
- **Pay rate normalization**: Converts hourly/weekly/annual rates to standardized hourly format
- **50+ US cities**: Comprehensive geographic coverage
- **Daily automation**: GitHub Actions runs the scraper daily at 6 AM EST
- **Email reports**: Receive daily summaries with Excel attachments
- **Database storage**: SQLite for tracking jobs over time

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/healthcare_job_scraper.git
cd healthcare_job_scraper
```

### 2. Install dependencies
```bash
pip3 install -r requirements.txt
playwright install chromium
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run the scraper
```bash
# Test run (3 cities, no email)
python3 main.py --test

# Full run (all cities)
python3 main.py --full
```

## Configuration

### Environment Variables (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| ANTHROPIC_API_KEY | Your Anthropic API key for AI parsing | Yes |
| SENDER_EMAIL | Gmail address for sending reports | No |
| SENDER_PASSWORD | Gmail App Password | No |
| RECIPIENT_EMAIL | Where to send reports | No |

### Cities

Edit `config/cities.py` to customize which cities to scrape.

## Project Structure

```
healthcare_job_scraper/
├── .github/workflows/     # GitHub Actions automation
│   └── daily-scrape.yml
├── config/                # Configuration files
│   ├── cities.py          # City list
│   └── settings.py        # App settings
├── scrapers/              # Job board scrapers
│   ├── indeed_scraper.py
│   ├── vivian_scraper.py
│   ├── ziprecruiter_scraper.py
│   ├── aya_scraper.py
│   └── intelycare_scraper.py
├── parsers/               # Data processing
│   ├── ai_parser.py       # Claude AI integration
│   └── pay_normalizer.py  # Pay rate standardization
├── database/              # Data storage
│   ├── models.py          # SQLAlchemy models
│   └── connection.py      # Database manager
├── notifications/         # Email reports
│   └── email_notifier.py
├── main.py               # Main entry point
├── scheduler.py          # Local scheduling
└── requirements.txt      # Python dependencies
```

## Job Sources

| Source | URL | Specialty |
|--------|-----|-----------|
| Indeed | indeed.com | General healthcare jobs |
| Vivian Health | vivian.com | Travel nursing |
| ZipRecruiter | ziprecruiter.com | General healthcare |
| Aya Healthcare | ayahealthcare.com | Travel nursing/allied |
| IntelyCare | intelycare.com | Per diem nursing |

## Output

The scraper generates:
- **Excel files**: `output/healthcare_jobs_YYYY-MM-DD.xlsx`
- **SQLite database**: `healthcare_jobs.db`
- **Email reports**: Daily summaries with statistics

## GitHub Actions

The workflow runs automatically at 6 AM EST daily. To set up:

1. Go to your repository Settings → Secrets → Actions
2. Add these secrets:
   - `ANTHROPIC_API_KEY`
   - `SENDER_EMAIL` (optional)
   - `SENDER_PASSWORD` (optional)
   - `RECIPIENT_EMAIL` (optional)

## License

MIT License
