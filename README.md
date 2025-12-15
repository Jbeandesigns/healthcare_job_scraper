# Healthcare Job Scraper

An AI-powered web scraper that collects healthcare job listings from multiple job boards, normalizes pay rates, and generates daily reports.

---

## ⚠️ IMPORTANT: Ethical & Legal Considerations

**Before using this tool, you MUST read [ETHICAL_GUIDELINES.md](ETHICAL_GUIDELINES.md)**

This scraper is designed with ethical web scraping practices:

| Principle | How It's Implemented |
|-----------|---------------------|
| **1. Respect robots.txt** | ✅ Automatically checks each site's robots.txt before scraping |
| **2. Rate Limiting** | ✅ 3-7 second delays between requests; auto-slowdown if too fast |
| **3. Terms of Service** | ⚠️ YOU must review each site's ToS before using |

### Terms of Service Links (Review Before Use!)

- [Indeed Terms](https://www.indeed.com/legal)
- [Vivian Health Terms](https://www.vivian.com/terms)
- [ZipRecruiter Terms](https://www.ziprecruiter.com/terms)
- [Aya Healthcare Terms](https://www.ayahealthcare.com/terms-and-conditions)
- [IntelyCare Terms](https://www.intelycare.com/terms-of-service)

---

## Features

- **Multi-source scraping**: Indeed, Vivian Health, ZipRecruiter, Aya Healthcare, IntelyCare
- **Ethical by default**: robots.txt compliance, rate limiting, ToS awareness
- **AI-powered parsing**: Uses Claude (Anthropic) to intelligently extract job details
- **Pay rate normalization**: Converts hourly/weekly/annual rates to standardized hourly format
- **50+ US cities**: Comprehensive geographic coverage
- **Daily automation**: GitHub Actions runs the scraper daily at 6 AM EST
- **Email reports**: Receive daily summaries with Excel attachments
- **Database storage**: SQLite for tracking jobs over time

---

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

### 4. Review Terms of Service
```bash
# View the Terms of Service notice
python3 main.py --tos
```

### 5. Run the scraper
```bash
# Test run (3 cities, quick)
python3 main.py --test

# Full run (all cities)
python3 main.py --full
```

---

## Ethical Scraping Features

### robots.txt Compliance
```
✓ Checked robots.txt for indeed.com
✓ Checked robots.txt for vivian.com
⛔ robots.txt DISALLOWS: https://example.com/restricted
   Respecting site owner's wishes - skipping this URL
```

### Rate Limiting
```
⏱️ Rate limiting: waiting 4.2s...
⏱️ Rate limiting: waiting 5.8s...
ℹ️ Site requests 10s crawl delay - respecting
```

### Auto-Slowdown
```
⚠️ High request rate detected: 16.2/min
   Adding extra delay to be respectful...
```

---

## Configuration

### Environment Variables (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| ANTHROPIC_API_KEY | Your Anthropic API key for AI parsing | Yes |
| SENDER_EMAIL | Gmail address for sending reports | No |
| SENDER_PASSWORD | Gmail App Password | No |
| RECIPIENT_EMAIL | Where to send reports | No |

### Ethical Settings (in code)

```python
# Always recommended: keep robots.txt checking enabled
scraper = IndeedScraper(respect_robots=True)

# Rate limiting is built-in and cannot be disabled
# Minimum 3-7 second delays between all requests
```

---

## Project Structure

```
healthcare_job_scraper/
├── .github/workflows/     # GitHub Actions automation
│   └── daily-scrape.yml
├── config/                # Configuration files
│   ├── cities.py          # City list
│   └── settings.py        # App settings
├── scrapers/              # Job board scrapers
│   ├── base_scraper.py    # Ethical scraping base class
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
├── requirements.txt      # Python dependencies
├── ETHICAL_GUIDELINES.md # ⚠️ READ THIS FIRST
└── README.md
```

---

## Job Sources

| Source | URL | Specialty | robots.txt |
|--------|-----|-----------|------------|
| Indeed | indeed.com | General healthcare jobs | [View](https://www.indeed.com/robots.txt) |
| Vivian Health | vivian.com | Travel nursing | [View](https://www.vivian.com/robots.txt) |
| ZipRecruiter | ziprecruiter.com | General healthcare | [View](https://www.ziprecruiter.com/robots.txt) |
| Aya Healthcare | ayahealthcare.com | Travel nursing/allied | [View](https://www.ayahealthcare.com/robots.txt) |
| IntelyCare | intelycare.com | Per diem nursing | [View](https://www.intelycare.com/robots.txt) |

---

## Output

The scraper generates:
- **Excel files**: `output/healthcare_jobs_YYYY-MM-DD.xlsx`
- **SQLite database**: `healthcare_jobs.db`
- **Email reports**: Daily summaries with statistics

---

## GitHub Actions

The workflow runs automatically at 6 AM EST daily. To set up:

1. Go to your repository Settings → Secrets → Actions
2. Add these secrets:
   - `ANTHROPIC_API_KEY`
   - `SENDER_EMAIL` (optional)
   - `SENDER_PASSWORD` (optional)
   - `RECIPIENT_EMAIL` (optional)

---

## Command Line Options

```bash
python3 main.py           # Default test run
python3 main.py --test    # Test run (3 cities)
python3 main.py --full    # Full run (all cities)
python3 main.py --tos     # Show Terms of Service notice
python3 main.py --help    # Show help
```

---

## Acceptable Use

✅ **Allowed:**
- Personal career research
- Market rate analysis for salary negotiations
- Academic research
- Understanding job market trends

❌ **Not Allowed:**
- Commercial redistribution of data
- Building competing job boards
- Selling scraped data
- Any use violating site Terms of Service

---

## License

MIT License - See [ETHICAL_GUIDELINES.md](ETHICAL_GUIDELINES.md) for usage restrictions.

---

## Disclaimer

This tool is provided for educational and personal research purposes. **You are responsible** for ensuring your use complies with all applicable laws and Terms of Service. The authors are not responsible for misuse of this tool.
