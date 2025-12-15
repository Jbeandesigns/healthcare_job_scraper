# CareRev Market Rates Dashboard

A Streamlit dashboard for comparing CareRev rates against market data from Indeed, Vivian Health, Aya Healthcare, and IntelyCare.

## Features

- 📤 **CSV Upload**: Upload your CareRev rates to compare against market data
- 📊 **Interactive Charts**: Visualize rates by specialty, shift type, and health system
- 🔍 **Filters**: Filter by health system, specialty, and job type
- 📥 **Data Export**: Download filtered data as CSV
- 🔗 **Shareable Link**: Deploy to Streamlit Cloud for team access

## Quick Start (Local)

### 1. Install dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run the dashboard
```bash
streamlit run dashboard.py
```

### 3. Open in browser
Navigate to `http://localhost:8501`

---

## Deploy to Streamlit Cloud (Free - Get a Shareable Link)

### Step 1: Add dashboard to your GitHub repo

Copy these files to your `healthcare_job_scraper` repository:
```
healthcare_job_scraper/
├── dashboard.py           # Main dashboard
├── requirements.txt       # Update existing or create new
└── .streamlit/
    └── config.toml        # Theme configuration
```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add market rates dashboard"
git push
```

### Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub account (if not already)
4. Select your repository: `healthcare_job_scraper`
5. Set the main file: `dashboard.py`
6. Click **"Deploy"**

### Step 4: Share with your team!

You'll get a URL like: `https://carerev-market-rates.streamlit.app`

Share this link with anyone on your team - they can:
- View market rate comparisons
- Upload their own CareRev CSV files
- Filter and analyze the data
- Download filtered results

---

## CSV Format

Your CareRev rates CSV should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Health System | Parent organization | Advocate Aurora Health WI |
| Hospital | Facility name | Aurora BayCare Medical Center |
| Specialty | Job specialty | ICU RN, Med/Surg RN, ER RN |
| Shift Type | Shift category | Day Shift, Night Shift, Weekend |
| AVERAGE Pay Rate | Hourly rate | $68.36 |

---

## Dashboard Sections

### 📈 Key Metrics
- Your average rate vs market average
- Difference ($ and %)
- Total records analyzed

### 💰 Rates by Specialty
- Side-by-side comparison: CareRev vs Market
- Specialties: ICU, Med/Surg, ER, Tele, OR, PACU, CNA

### 🌙 Rates by Shift Type
- Day, Night, Weekend, Night Weekend
- See shift differentials

### 🏥 Rates by Health System
- Top 15 health systems by average rate
- Identify high and low paying systems

### 📋 Detailed Data Table
- Full filterable data
- Download as CSV

---

## Connecting to Market Data

The dashboard automatically loads market data from your scraper's output files.

Make sure your scraper exports to the `output/` folder:
```
output/healthcare_jobs_2024-12-15.xlsx
```

The dashboard will find and load the most recent file.

---

## Customization

### Change Colors

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#003e52"      # Main accent color
backgroundColor = "#ffffff"    # Page background
secondaryBackgroundColor = "#eceeef"  # Sidebar, cards
textColor = "#003e52"         # Text color
```

### Add More Charts

Edit `dashboard.py` to add additional visualizations using Plotly.

---

## Troubleshooting

### "No market data found"
Run your scraper first: `python main.py --test`

### Charts not showing
Make sure your CSV has the correct column names (case-sensitive)

### Deployment fails
Check that `requirements.txt` is in your repo root

---

## Support

For issues or feature requests, contact the CareRev Analytics team.
