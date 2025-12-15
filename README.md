# CareRev Market Rates Dashboard - Enhanced Version

An interactive dashboard for comparing CareRev rates against market data, with geographic heat maps, prospect research tools, and trend analysis.

## 🌟 Key Features

### 🗺️ Tab 1: Geographic Heat Map
- **60+ Major US Cities** displayed on interactive US map
- Bubble size indicates rate level
- Color scale shows rate values
- Filter by Specialty and Pay Type
- See all markets at a glance - not just CareRev locations

### 🔍 Tab 2: Prospect Research Tool
- **Search by City & State** - dropdown with 60+ cities
- **Filter by Specialty** - ICU, Med/Surg, ER, Tele, OR, L&D, etc.
- **Filter by Pay Type** - Staff, Travel, Per Diem, Crisis
- **Rate Recommendations** - competitive range, budget, premium tiers
- **Rate Distribution** - histogram showing market spread
- **Trend Chart** - see how rates have changed over time

### 📊 Tab 3: Rate Comparison
- Upload CareRev CSV to compare against market
- Your rates vs Market rates side-by-side
- By Specialty comparison
- By Shift Type (Day/Night/Weekend differentials)
- By Health System ranking

### 📈 Tab 4: Trends & Analysis
- Historical rate trends over time
- Pay Type comparison (Travel vs Staff vs Per Diem)
- Source comparison (Indeed vs Vivian vs Aya, etc.)
- Build trend data with each scraper run

---

## 🚀 Quick Start

### Local Development
```bash
pip3 install -r requirements.txt
streamlit run dashboard.py
```

### Deploy to Streamlit Cloud (Get Shareable Link)
1. Add files to your GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Deploy → Get URL like `carerev-rates.streamlit.app`

---

## 📁 Files Included

```
dashboard.py           # Main dashboard application
requirements.txt       # Python dependencies
.streamlit/
  └── config.toml      # Theme & settings
README.md              # This file
```

---

## 🗺️ Cities Included in Heat Map

### Northeast
- New York, NY
- Philadelphia, PA
- Boston, MA
- Pittsburgh, PA
- Newark, NJ
- Hartford, CT
- Providence, RI
- Buffalo, NY
- Albany, NY
- Worcester, MA

### Southeast
- Atlanta, GA
- Miami, FL
- Tampa, FL
- Orlando, FL
- Charlotte, NC
- Raleigh, NC
- Nashville, TN
- Jacksonville, FL
- Memphis, TN
- Louisville, KY
- Richmond, VA
- Birmingham, AL
- New Orleans, LA
- Charleston, SC

### Midwest
- Chicago, IL
- Detroit, MI
- Minneapolis, MN
- Cleveland, OH
- Columbus, OH
- Cincinnati, OH
- Indianapolis, IN
- Milwaukee, WI
- Kansas City, MO
- St. Louis, MO
- Omaha, NE
- Madison, WI
- Green Bay, WI

### Southwest
- Dallas, TX
- Houston, TX
- San Antonio, TX
- Austin, TX
- Phoenix, AZ
- Tucson, AZ
- Albuquerque, NM
- El Paso, TX
- Oklahoma City, OK
- Tulsa, OK
- Fort Worth, TX

### West Coast
- Los Angeles, CA
- San Francisco, CA
- San Diego, CA
- San Jose, CA
- Sacramento, CA
- Seattle, WA
- Portland, OR
- Las Vegas, NV
- Denver, CO
- Salt Lake City, UT
- Fresno, CA
- Long Beach, CA

### Other Major Markets
- Washington, DC
- Baltimore, MD
- Honolulu, HI
- Anchorage, AK

---

## 💰 Pay Types Tracked

| Pay Type | Description | Typical Sources |
|----------|-------------|-----------------|
| **Staff** | Permanent/FTE positions | Indeed, ZipRecruiter |
| **Travel** | Travel nursing contracts | Vivian, Aya Healthcare |
| **Per Diem** | PRN/as-needed shifts | IntelyCare |
| **Crisis** | Emergency/rapid response | Various |

---

## 🏥 Specialties Tracked

- ICU RN
- Med/Surg RN
- ER RN
- Tele RN
- Stepdown RN
- OR RN
- L&D RN
- PACU RN
- NICU RN
- PICU RN
- Oncology RN
- Dialysis RN
- Rehab RN
- Psych RN
- LPN
- CNA
- Surgical Tech
- Respiratory Therapist
- Medical Assistant
- Phlebotomist

---

## 📊 Using the Prospect Research Tool

### Scenario: New Client in Phoenix, AZ wants ICU Travel Nurses

1. Go to **🔍 Prospect Research** tab
2. Select:
   - City: `Phoenix, AZ`
   - Specialty: `ICU`
   - Pay Type: `Travel`
3. View results:
   - **Average Rate**: $72.50/hr
   - **Competitive Range**: $65-$80/hr
   - **Rate Distribution**: histogram
   - **Trend**: 3-month rate history

### Rate Recommendation Output

```
💡 Rate Recommendation

Competitive Rate Range: $65.00 - $80.00/hr

- Budget Option: $58.00 - $65.00/hr (bottom 25%)
- Competitive: $65.00 - $72.50/hr (25th-50th percentile)
- Premium: $72.50 - $80.00/hr (50th-75th percentile)
- Top Market: $80.00+/hr (top 25%)
```

---

## 📈 Building Trend Data

Trends require multiple data points. Each time the scraper runs, it adds a new data point.

**Recommended Schedule:**
- Run scraper daily via GitHub Actions
- After 7 days: weekly trends visible
- After 30 days: monthly trends visible

**Manual Runs:**
```bash
python main.py --test   # Quick test (3 cities)
python main.py --full   # Full run (all cities)
```

---

## 🎨 Color Scheme

| Element | Color | Hex |
|---------|-------|-----|
| Primary | Dark Teal | #003e52 |
| Secondary | Blue | #00577f |
| Accent 1 | Teal | #3e8a93 |
| Accent 2 | Pink | #f4436c |
| Background | Light Gray | #eceeef |

---

## 🔧 Customization

### Add More Cities

Edit `MAJOR_CITIES` dictionary in `dashboard.py`:

```python
MAJOR_CITIES = {
    "Your City, ST": {"lat": 40.0000, "lon": -75.0000, "state": "ST"},
    # ... existing cities
}
```

### Add More Specialties

Edit `SPECIALTIES` list in `dashboard.py`:

```python
SPECIALTIES = [
    "ICU RN", "Med/Surg RN", "Your New Specialty",
    # ... existing specialties
]
```

---

## 🐛 Troubleshooting

### "No market data found"
Run the scraper first: `python main.py`

### Heat map shows gray dots
No rate data available for those cities yet. Run scraper with more cities.

### Trends not showing
Need 2+ data points. Run scraper multiple times.

### CSV upload fails
Ensure columns match: `Health System`, `Hospital`, `Specialty`, `Shift Type`, `AVERAGE Pay Rate`

---

## 📞 Support

For questions or feature requests, contact the CareRev Analytics team.
