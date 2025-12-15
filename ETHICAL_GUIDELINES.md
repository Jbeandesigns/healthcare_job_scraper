# Ethical & Legal Guidelines for Healthcare Job Scraper

## Overview

This scraper is designed with ethical web scraping practices built-in. Before using this tool, please read and understand the following guidelines.

---

## 1. Robots.txt Compliance ✓

### What is robots.txt?
Every website can publish a `robots.txt` file that specifies which parts of their site can be accessed by automated tools (bots/scrapers). This is the website owner's way of communicating their preferences.

### How this scraper respects robots.txt:
- **Automatic checking**: Before accessing any URL, the scraper checks the site's robots.txt
- **Disallow compliance**: If robots.txt disallows a URL, the scraper skips it automatically
- **Crawl-delay respect**: If a site specifies a crawl delay, we use at least that delay

### Example robots.txt check:
```
✓ Checked robots.txt for indeed.com
✓ Checked robots.txt for vivian.com
⛔ robots.txt DISALLOWS: https://example.com/api/internal
   Respecting site owner's wishes - skipping this URL
```

### How to view a site's robots.txt:
Simply add `/robots.txt` to any website's base URL:
- https://www.indeed.com/robots.txt
- https://www.vivian.com/robots.txt
- https://www.ziprecruiter.com/robots.txt
- https://www.ayahealthcare.com/robots.txt
- https://www.intelycare.com/robots.txt

---

## 2. Rate Limiting ✓

### Why rate limiting matters:
Sending too many requests too quickly can:
- Overwhelm the website's servers
- Degrade service for other users
- Get your IP address blocked
- Potentially violate terms of service

### How this scraper implements rate limiting:

| Feature | Implementation |
|---------|---------------|
| Minimum delay | 3 seconds between requests |
| Maximum delay | 7 seconds between requests |
| Random delays | Prevents predictable patterns |
| Crawl-delay respect | Uses site's specified delay if higher |
| Auto-slowdown | Adds extra delays if request rate exceeds 15/min |

### Example output:
```
⏱️ Rate limiting: waiting 4.2s...
⏱️ Rate limiting: waiting 5.8s...
⚠️ High request rate detected: 16.2/min
   Adding extra delay to be respectful...
```

---

## 3. Terms of Service ⚠️

### IMPORTANT: You must review each site's Terms of Service

Before using this scraper, review the Terms of Service for each job board:

| Job Board | Terms of Service URL |
|-----------|---------------------|
| Indeed | https://www.indeed.com/legal |
| Vivian Health | https://www.vivian.com/terms |
| ZipRecruiter | https://www.ziprecruiter.com/terms |
| Aya Healthcare | https://www.ayahealthcare.com/terms-and-conditions |
| IntelyCare | https://www.intelycare.com/terms-of-service |

### Acceptable Use Cases:

✅ **Allowed:**
- Personal career research and job hunting
- Understanding healthcare job market trends
- Academic research (with proper attribution)
- Internal competitive analysis for your own career
- Market rate research for salary negotiations

❌ **Not Allowed:**
- Commercial redistribution of job data
- Building competing job aggregation services
- Selling or licensing scraped data
- Scraping at rates that could harm site performance
- Bypassing authentication or access controls
- Any use that violates the sites' Terms of Service

---

## 4. Configuration Options

### Enabling/Disabling Ethical Features

```python
# In your code:
scraper = IndeedScraper(
    headless=True,
    respect_robots=True  # Always keep this True!
)

# In main.py:
run_scraper(
    respect_robots=True,  # Checks robots.txt (recommended)
    # ... other options
)
```

### Adjusting Rate Limits

If you need to be even more conservative (recommended for production):

```python
# In base_scraper.py, you can adjust:
MIN_DELAY = 5   # Increase minimum delay
MAX_DELAY = 10  # Increase maximum delay
```

---

## 5. Legal Disclaimer

### Your Responsibility

By using this tool, you acknowledge and agree that:

1. **You are responsible** for ensuring your use complies with all applicable laws and Terms of Service
2. **You have reviewed** the Terms of Service for each job board you scrape
3. **You will not use** this tool for any prohibited purposes
4. **You understand** that websites may change their Terms of Service at any time
5. **The authors of this tool** are not responsible for how you use it

### Applicable Laws

Depending on your jurisdiction, relevant laws may include:
- Computer Fraud and Abuse Act (CFAA) - United States
- General Data Protection Regulation (GDPR) - European Union
- Various state and local computer access laws

### When in Doubt

If you're unsure whether your intended use is permitted:
1. Contact the website's legal department
2. Consult with a lawyer familiar with technology law
3. Err on the side of caution and don't scrape

---

## 6. Best Practices Checklist

Before running the scraper:

- [ ] I have read the Terms of Service for each job board
- [ ] I understand my use case is for personal/research purposes
- [ ] I have kept `respect_robots=True` enabled
- [ ] I have not modified the rate limiting to be more aggressive
- [ ] I understand I am responsible for my use of this tool

During scraping:

- [ ] Monitor the console for any robots.txt warnings
- [ ] Watch for rate limiting messages
- [ ] Stop immediately if you see unexpected errors or blocks

After scraping:

- [ ] Use the data only for permitted purposes
- [ ] Do not redistribute the data commercially
- [ ] Delete data you no longer need

---

## 7. Reporting Issues

If you discover that this scraper is not properly respecting a site's robots.txt or rate limits, please:

1. Stop using the scraper immediately
2. Document the issue
3. Report it so it can be fixed

---

## Summary

This scraper is built with ethics in mind, but **you are ultimately responsible** for how you use it. When in doubt:

1. **Be respectful** - These sites provide a valuable service
2. **Be conservative** - Use longer delays rather than shorter ones
3. **Be legal** - Follow all applicable laws and Terms of Service
4. **Be honest** - Don't misrepresent your use of the data

Happy (ethical) scraping! 🏥
