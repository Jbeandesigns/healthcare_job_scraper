"""
CareRev Market Rates Dashboard - Enhanced Version
Features:
- Geographic heat maps for all major US cities
- Prospect research tool with city/specialty/pay type filters
- Trend analysis over time
- CareRev vs Market rate comparison

To run locally: streamlit run dashboard.py
To deploy: Push to GitHub and connect to Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import glob
import json

# Page configuration
st.set_page_config(
    page_title="CareRev Market Rates Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #003e52;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #00577f;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #eceeef;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #003e52;
        border-bottom: 3px solid #3e8a93;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .prospect-card {
        background: linear-gradient(135deg, #003e52 0%, #00577f 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Color scheme
COLORS = {
    'primary': '#003e52',
    'secondary': '#00577f',
    'accent1': '#3e8a93',
    'accent2': '#f4436c',
    'background': '#eceeef',
    'carerev': '#003e52',
    'market': '#3e8a93',
    'travel': '#f4436c',
    'staff': '#003e52',
    'perdiem': '#3e8a93'
}

# All major US cities with coordinates for heat map
MAJOR_CITIES = {
    # Northeast
    "New York, NY": {"lat": 40.7128, "lon": -74.0060, "state": "NY"},
    "Philadelphia, PA": {"lat": 39.9526, "lon": -75.1652, "state": "PA"},
    "Boston, MA": {"lat": 42.3601, "lon": -71.0589, "state": "MA"},
    "Pittsburgh, PA": {"lat": 40.4406, "lon": -79.9959, "state": "PA"},
    "Newark, NJ": {"lat": 40.7357, "lon": -74.1724, "state": "NJ"},
    "Hartford, CT": {"lat": 41.7658, "lon": -72.6734, "state": "CT"},
    "Providence, RI": {"lat": 41.8240, "lon": -71.4128, "state": "RI"},
    "Buffalo, NY": {"lat": 42.8864, "lon": -78.8784, "state": "NY"},
    "Albany, NY": {"lat": 42.6526, "lon": -73.7562, "state": "NY"},
    "Worcester, MA": {"lat": 42.2626, "lon": -71.8023, "state": "MA"},
    
    # Southeast
    "Atlanta, GA": {"lat": 33.7490, "lon": -84.3880, "state": "GA"},
    "Miami, FL": {"lat": 25.7617, "lon": -80.1918, "state": "FL"},
    "Tampa, FL": {"lat": 27.9506, "lon": -82.4572, "state": "FL"},
    "Orlando, FL": {"lat": 28.5383, "lon": -81.3792, "state": "FL"},
    "Charlotte, NC": {"lat": 35.2271, "lon": -80.8431, "state": "NC"},
    "Raleigh, NC": {"lat": 35.7796, "lon": -78.6382, "state": "NC"},
    "Nashville, TN": {"lat": 36.1627, "lon": -86.7816, "state": "TN"},
    "Jacksonville, FL": {"lat": 30.3322, "lon": -81.6557, "state": "FL"},
    "Memphis, TN": {"lat": 35.1495, "lon": -90.0490, "state": "TN"},
    "Louisville, KY": {"lat": 38.2527, "lon": -85.7585, "state": "KY"},
    "Richmond, VA": {"lat": 37.5407, "lon": -77.4360, "state": "VA"},
    "Birmingham, AL": {"lat": 33.5207, "lon": -86.8025, "state": "AL"},
    "New Orleans, LA": {"lat": 29.9511, "lon": -90.0715, "state": "LA"},
    "Charleston, SC": {"lat": 32.7765, "lon": -79.9311, "state": "SC"},
    
    # Midwest
    "Chicago, IL": {"lat": 41.8781, "lon": -87.6298, "state": "IL"},
    "Detroit, MI": {"lat": 42.3314, "lon": -83.0458, "state": "MI"},
    "Minneapolis, MN": {"lat": 44.9778, "lon": -93.2650, "state": "MN"},
    "Cleveland, OH": {"lat": 41.4993, "lon": -81.6944, "state": "OH"},
    "Columbus, OH": {"lat": 39.9612, "lon": -82.9988, "state": "OH"},
    "Cincinnati, OH": {"lat": 39.1031, "lon": -84.5120, "state": "OH"},
    "Indianapolis, IN": {"lat": 39.7684, "lon": -86.1581, "state": "IN"},
    "Milwaukee, WI": {"lat": 43.0389, "lon": -87.9065, "state": "WI"},
    "Kansas City, MO": {"lat": 39.0997, "lon": -94.5786, "state": "MO"},
    "St. Louis, MO": {"lat": 38.6270, "lon": -90.1994, "state": "MO"},
    "Omaha, NE": {"lat": 41.2565, "lon": -95.9345, "state": "NE"},
    "Madison, WI": {"lat": 43.0731, "lon": -89.4012, "state": "WI"},
    "Green Bay, WI": {"lat": 44.5133, "lon": -88.0133, "state": "WI"},
    
    # Southwest
    "Dallas, TX": {"lat": 32.7767, "lon": -96.7970, "state": "TX"},
    "Houston, TX": {"lat": 29.7604, "lon": -95.3698, "state": "TX"},
    "San Antonio, TX": {"lat": 29.4241, "lon": -98.4936, "state": "TX"},
    "Austin, TX": {"lat": 30.2672, "lon": -97.7431, "state": "TX"},
    "Phoenix, AZ": {"lat": 33.4484, "lon": -112.0740, "state": "AZ"},
    "Tucson, AZ": {"lat": 32.2226, "lon": -110.9747, "state": "AZ"},
    "Albuquerque, NM": {"lat": 35.0844, "lon": -106.6504, "state": "NM"},
    "El Paso, TX": {"lat": 31.7619, "lon": -106.4850, "state": "TX"},
    "Oklahoma City, OK": {"lat": 35.4676, "lon": -97.5164, "state": "OK"},
    "Tulsa, OK": {"lat": 36.1540, "lon": -95.9928, "state": "OK"},
    "Fort Worth, TX": {"lat": 32.7555, "lon": -97.3308, "state": "TX"},
    
    # West Coast
    "Los Angeles, CA": {"lat": 34.0522, "lon": -118.2437, "state": "CA"},
    "San Francisco, CA": {"lat": 37.7749, "lon": -122.4194, "state": "CA"},
    "San Diego, CA": {"lat": 32.7157, "lon": -117.1611, "state": "CA"},
    "San Jose, CA": {"lat": 37.3382, "lon": -121.8863, "state": "CA"},
    "Sacramento, CA": {"lat": 38.5816, "lon": -121.4944, "state": "CA"},
    "Seattle, WA": {"lat": 47.6062, "lon": -122.3321, "state": "WA"},
    "Portland, OR": {"lat": 45.5152, "lon": -122.6784, "state": "OR"},
    "Las Vegas, NV": {"lat": 36.1699, "lon": -115.1398, "state": "NV"},
    "Denver, CO": {"lat": 39.7392, "lon": -104.9903, "state": "CO"},
    "Salt Lake City, UT": {"lat": 40.7608, "lon": -111.8910, "state": "UT"},
    "Fresno, CA": {"lat": 36.7378, "lon": -119.7871, "state": "CA"},
    "Long Beach, CA": {"lat": 33.7701, "lon": -118.1937, "state": "CA"},
    
    # Other Major Markets
    "Washington, DC": {"lat": 38.9072, "lon": -77.0369, "state": "DC"},
    "Baltimore, MD": {"lat": 39.2904, "lon": -76.6122, "state": "MD"},
    "Honolulu, HI": {"lat": 21.3069, "lon": -157.8583, "state": "HI"},
    "Anchorage, AK": {"lat": 61.2181, "lon": -149.9003, "state": "AK"},
}

# Standard specialties for filtering
SPECIALTIES = [
    "ICU RN", "Med/Surg RN", "ER RN", "Tele RN", "Stepdown RN", 
    "OR RN", "L&D RN", "PACU RN", "NICU RN", "PICU RN",
    "Oncology RN", "Dialysis RN", "Rehab RN", "Psych RN",
    "LPN", "CNA", "Surgical Tech", "Respiratory Therapist",
    "Medical Assistant", "Phlebotomist"
]

# Pay types
PAY_TYPES = ["All", "Staff", "Travel", "Per Diem", "Crisis"]


@st.cache_data(ttl=3600)
def load_all_market_data():
    """Load all historical market data from scraped Excel files."""
    # Check multiple possible locations (handles both root and subfolder deployment)
    excel_files = (
        glob.glob('output/healthcare_jobs_*.xlsx') +
        glob.glob('../output/healthcare_jobs_*.xlsx') +
        glob.glob('healthcare_job_scraper/output/healthcare_jobs_*.xlsx')
    )
    
    if not excel_files:
        excel_files = glob.glob('*.xlsx') + glob.glob('../*.xlsx')
    
    all_data = []
    for file in excel_files:
        try:
            df = pd.read_excel(file)
            # Extract date from filename
            filename = os.path.basename(file)
            date_str = filename.replace('healthcare_jobs_', '').replace('.xlsx', '').split('_')[0]
            df['file_date'] = date_str
            all_data.append(df)
        except Exception as e:
            continue
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        return combined
    return None


@st.cache_data
def load_market_data():
    """Load the most recent market data from scraped Excel files."""
    # Check multiple possible locations (handles both root and subfolder deployment)
    excel_files = (
        glob.glob('output/healthcare_jobs_*.xlsx') +
        glob.glob('../output/healthcare_jobs_*.xlsx') +
        glob.glob('healthcare_job_scraper/output/healthcare_jobs_*.xlsx')
    )
    
    if not excel_files:
        excel_files = glob.glob('*.xlsx') + glob.glob('../*.xlsx')
    
    if not excel_files:
        return None, None
    
    latest_file = max(excel_files, key=os.path.getctime)
    
    try:
        df = pd.read_excel(latest_file)
        return df, latest_file
    except Exception as e:
        st.error(f"Error loading market data: {e}")
        return None, None


def clean_pay_rate(value):
    """Convert pay rate string to float."""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        return float(cleaned)
    except:
        return None


def normalize_specialty(specialty):
    """Normalize specialty names for matching."""
    if pd.isna(specialty):
        return 'Other'
    
    specialty = str(specialty).upper()
    
    mappings = {
        'ICU': ['ICU', 'INTENSIVE CARE', 'CRITICAL CARE', 'CCU', 'MICU', 'SICU'],
        'Med/Surg': ['MED/SURG', 'MED SURG', 'MEDICAL SURGICAL', 'MEDSURG', 'M/S'],
        'ER': ['ER', 'ED', 'EMERGENCY', 'EMERGENCY ROOM', 'EMERGENCY DEPARTMENT'],
        'Tele': ['TELE', 'TELEMETRY', 'CARDIAC', 'MED SURG/TELE', 'PCU'],
        'OR': ['OR', 'OPERATING ROOM', 'SURGICAL', 'PERIOPERATIVE', 'CIRCULATOR'],
        'L&D': ['L&D', 'LABOR', 'DELIVERY', 'OB', 'OBSTETRIC', 'MATERNITY', 'WOMEN'],
        'PACU': ['PACU', 'POST ANESTHESIA', 'RECOVERY'],
        'Stepdown': ['STEPDOWN', 'STEP DOWN', 'SDU', 'PROGRESSIVE'],
        'NICU': ['NICU', 'NEONATAL'],
        'PICU': ['PICU', 'PEDIATRIC ICU', 'PEDIATRIC INTENSIVE'],
        'Psych': ['PSYCH', 'PSYCHIATRIC', 'BEHAVIORAL', 'MENTAL HEALTH', 'BH'],
        'Oncology': ['ONCOLOGY', 'CANCER', 'CHEMO'],
        'Dialysis': ['DIALYSIS', 'RENAL', 'NEPHROLOGY'],
        'Rehab': ['REHAB', 'REHABILITATION', 'PHYSICAL THERAPY'],
        'CNA': ['CNA', 'NURSING ASSISTANT', 'NURSE AIDE', 'HOSPITAL CNA', 'TECH'],
        'LPN': ['LPN', 'LVN', 'LICENSED PRACTICAL', 'LICENSED VOCATIONAL'],
    }
    
    for standard, variations in mappings.items():
        for var in variations:
            if var in specialty:
                return standard
    
    return 'Other'


def classify_pay_type(row):
    """Classify the pay type based on job data."""
    source = str(row.get('source', '')).lower()
    employment = str(row.get('employment_type', '')).lower()
    title = str(row.get('job_title', '')).lower()
    
    if 'travel' in employment or 'travel' in title or source in ['vivian', 'aya']:
        return 'Travel'
    elif 'per diem' in employment or 'prn' in employment or 'prn' in title or source == 'intelycare':
        return 'Per Diem'
    elif 'crisis' in title or 'rapid' in title:
        return 'Crisis'
    else:
        return 'Staff'


def process_carerev_data(df):
    """Process the uploaded CareRev CSV data."""
    df = df.copy()
    df['rate'] = df['AVERAGE Pay Rate'].apply(clean_pay_rate)
    df['specialty_normalized'] = df['Specialty'].apply(normalize_specialty)
    
    def get_job_type(specialty):
        specialty = str(specialty).upper()
        if 'CNA' in specialty or 'AIDE' in specialty or 'TECH' in specialty:
            return 'CNA/Tech'
        elif 'LPN' in specialty or 'LVN' in specialty:
            return 'LPN'
        else:
            return 'RN'
    
    df['job_type'] = df['Specialty'].apply(get_job_type)
    
    def categorize_shift(shift):
        shift = str(shift).upper()
        if 'NIGHT' in shift and 'WEEKEND' in shift:
            return 'Night Weekend'
        elif 'WEEKEND' in shift:
            return 'Weekend'
        elif 'NIGHT' in shift:
            return 'Night'
        else:
            return 'Day'
    
    df['shift_category'] = df['Shift Type'].apply(categorize_shift)
    df['pay_type'] = 'Staff'  # CareRev is typically staff rates
    
    return df


def process_market_data(df):
    """Process market data with additional classifications."""
    df = df.copy()
    
    if 'specialty' in df.columns:
        df['specialty_normalized'] = df['specialty'].apply(normalize_specialty)
    else:
        df['specialty_normalized'] = 'Other'
    
    # Classify pay type
    df['pay_type'] = df.apply(classify_pay_type, axis=1)
    
    # Ensure we have rate columns
    if 'pay_rate_low' not in df.columns:
        df['pay_rate_low'] = None
    if 'pay_rate_high' not in df.columns:
        df['pay_rate_high'] = df['pay_rate_low']
    
    # Calculate midpoint rate
    df['rate_mid'] = df.apply(
        lambda x: (x['pay_rate_low'] + x['pay_rate_high']) / 2 
        if pd.notna(x['pay_rate_low']) and pd.notna(x['pay_rate_high']) 
        else x['pay_rate_low'], 
        axis=1
    )
    
    return df


def create_us_heatmap(market_df, carerev_df=None, specialty_filter='All', pay_type_filter='All'):
    """Create a US heat map showing rates by city."""
    
    # Build city data
    city_data = []
    
    for city_name, coords in MAJOR_CITIES.items():
        city_rates = {'city': city_name, 'lat': coords['lat'], 'lon': coords['lon'], 'state': coords['state']}
        
        # Get market rates for this city
        market_rate = None
        carerev_rate = None
        job_count = 0
        
        # Extract city short name (used for both market and CareRev matching)
        city_short = city_name.split(',')[0].strip()
        
        if market_df is not None and len(market_df) > 0:
            city_market = market_df.copy()
            
            # Filter by city name (partial match)
            if 'city' in city_market.columns:
                city_market = city_market[city_market['city'].str.contains(city_short, case=False, na=False)]
            elif 'location' in city_market.columns:
                city_market = city_market[city_market['location'].str.contains(city_short, case=False, na=False)]
            
            # Apply filters
            if specialty_filter != 'All' and 'specialty_normalized' in city_market.columns:
                city_market = city_market[city_market['specialty_normalized'] == specialty_filter]
            
            if pay_type_filter != 'All' and 'pay_type' in city_market.columns:
                city_market = city_market[city_market['pay_type'] == pay_type_filter]
            
            if len(city_market) > 0 and 'pay_rate_low' in city_market.columns:
                market_rate = city_market['pay_rate_low'].mean()
                job_count = len(city_market)
        
        # Get CareRev rates for this city/state
        if carerev_df is not None and len(carerev_df) > 0:
            # Match by state from health system names or hospital names
            state_abbr = coords['state']
            carerev_city = carerev_df[
                carerev_df['Health System'].str.contains(state_abbr, case=False, na=False) |
                carerev_df['Hospital'].str.contains(city_short, case=False, na=False)
            ]
            
            if specialty_filter != 'All':
                carerev_city = carerev_city[carerev_city['specialty_normalized'] == specialty_filter]
            
            if len(carerev_city) > 0:
                carerev_rate = carerev_city['rate'].mean()
        
        city_rates['market_rate'] = market_rate
        city_rates['carerev_rate'] = carerev_rate
        city_rates['job_count'] = job_count
        city_rates['display_rate'] = market_rate if market_rate else carerev_rate
        
        # Calculate difference if both exist
        if market_rate and carerev_rate:
            city_rates['difference'] = carerev_rate - market_rate
            city_rates['diff_pct'] = ((carerev_rate - market_rate) / market_rate) * 100
        else:
            city_rates['difference'] = None
            city_rates['diff_pct'] = None
        
        city_data.append(city_rates)
    
    city_df = pd.DataFrame(city_data)
    
    # Create the map
    fig = go.Figure()
    
    # Add scatter points for cities with data
    cities_with_data = city_df[city_df['display_rate'].notna()]
    cities_without_data = city_df[city_df['display_rate'].isna()]
    
    if len(cities_with_data) > 0:
        # Color scale based on rate
        fig.add_trace(go.Scattergeo(
            lon=cities_with_data['lon'],
            lat=cities_with_data['lat'],
            text=cities_with_data.apply(
                lambda x: f"<b>{x['city']}</b><br>" + 
                         f"Market Rate: ${x['market_rate']:.2f}/hr<br>" if pd.notna(x['market_rate']) else f"<b>{x['city']}</b><br>" +
                         f"CareRev Rate: ${x['carerev_rate']:.2f}/hr<br>" if pd.notna(x['carerev_rate']) else "" +
                         f"Jobs Found: {x['job_count']}" if x['job_count'] > 0 else "No data",
                axis=1
            ),
            mode='markers',
            marker=dict(
                size=cities_with_data['display_rate'].fillna(0) / 3 + 8,
                color=cities_with_data['display_rate'],
                colorscale='Teal',
                showscale=True,
                colorbar=dict(title="$/hr"),
                line=dict(width=1, color='white')
            ),
            hoverinfo='text',
            name='Cities with Rate Data'
        ))
    
    # Add gray points for cities without data
    if len(cities_without_data) > 0:
        fig.add_trace(go.Scattergeo(
            lon=cities_without_data['lon'],
            lat=cities_without_data['lat'],
            text=cities_without_data['city'],
            mode='markers',
            marker=dict(
                size=8,
                color='lightgray',
                line=dict(width=1, color='gray')
            ),
            hoverinfo='text',
            name='No Data Available'
        ))
    
    fig.update_layout(
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            subunitcolor='rgb(204, 204, 204)',
            showsubunits=True
        ),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig, city_df


def create_trend_chart(historical_df, city=None, specialty=None, pay_type=None):
    """Create a trend chart showing rate changes over time."""
    if historical_df is None or len(historical_df) == 0:
        return None
    
    df = historical_df.copy()
    
    # Apply filters
    if city and city != 'All':
        city_short = city.split(',')[0].strip() if ',' in city else city
        if 'city' in df.columns:
            df = df[df['city'].str.contains(city_short, case=False, na=False)]
        elif 'location' in df.columns:
            df = df[df['location'].str.contains(city_short, case=False, na=False)]
    
    if specialty and specialty != 'All' and 'specialty_normalized' in df.columns:
        df = df[df['specialty_normalized'] == specialty]
    
    if pay_type and pay_type != 'All' and 'pay_type' in df.columns:
        df = df[df['pay_type'] == pay_type]
    
    if len(df) == 0 or 'file_date' not in df.columns:
        return None
    
    # Group by date
    trend_data = df.groupby('file_date').agg({
        'pay_rate_low': ['mean', 'min', 'max', 'count']
    }).reset_index()
    trend_data.columns = ['date', 'avg_rate', 'min_rate', 'max_rate', 'count']
    trend_data = trend_data.sort_values('date')
    
    if len(trend_data) < 2:
        return None
    
    fig = go.Figure()
    
    # Add range area
    fig.add_trace(go.Scatter(
        x=trend_data['date'],
        y=trend_data['max_rate'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=trend_data['date'],
        y=trend_data['min_rate'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(62, 138, 147, 0.2)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add average line
    fig.add_trace(go.Scatter(
        x=trend_data['date'],
        y=trend_data['avg_rate'],
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8),
        name='Average Rate',
        hovertemplate='%{x}<br>Avg: $%{y:.2f}/hr<extra></extra>'
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Date",
        yaxis_title="Hourly Rate ($)",
        hovermode='x unified'
    )
    
    return fig


def main():
    # Header
    st.markdown('<p class="main-header">🏥 CareRev Market Rates Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Compare your rates against market data • Research new markets • Track trends</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("## 📁 Data Sources")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload CareRev rates CSV",
        type=['csv'],
        help="Upload your Pay_Rates CSV file"
    )
    
    # Load data
    carerev_df = None
    if uploaded_file is not None:
        carerev_df = pd.read_csv(uploaded_file)
        carerev_df = process_carerev_data(carerev_df)
        st.sidebar.success(f"✓ Loaded {len(carerev_df)} CareRev rates")
    
    market_data, market_file = load_market_data()
    historical_data = load_all_market_data()
    
    if market_data is not None:
        market_data = process_market_data(market_data)
        st.sidebar.success(f"✓ Market data: {len(market_data)} jobs")
    else:
        st.sidebar.warning("No market data found")
    
    if historical_data is not None:
        historical_data = process_market_data(historical_data)
        st.sidebar.info(f"📈 Historical: {len(historical_data)} records")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Geographic Heat Map", 
        "🔍 Prospect Research", 
        "📊 Rate Comparison",
        "📈 Trends & Analysis"
    ])
    
    # ==================== TAB 1: GEOGRAPHIC HEAT MAP ====================
    with tab1:
        st.markdown('<p class="section-header">🗺️ Market Rates Heat Map - All Major US Cities</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            map_specialty = st.selectbox(
                "Filter by Specialty",
                ['All'] + sorted(set([normalize_specialty(s) for s in SPECIALTIES])),
                key='map_specialty'
            )
        with col2:
            map_pay_type = st.selectbox(
                "Filter by Pay Type",
                PAY_TYPES,
                key='map_pay_type'
            )
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("Bubble size = rate level • Color = rate value")
        
        # Create and display heat map
        heatmap_fig, city_df = create_us_heatmap(
            market_data, 
            carerev_df, 
            map_specialty if map_specialty != 'All' else 'All',
            map_pay_type if map_pay_type != 'All' else 'All'
        )
        st.plotly_chart(heatmap_fig, use_container_width=True)
        
        # City data table
        st.markdown("### 📋 City Rate Details")
        display_cities = city_df[['city', 'state', 'market_rate', 'carerev_rate', 'job_count']].copy()
        display_cities.columns = ['City', 'State', 'Market Rate', 'CareRev Rate', 'Jobs Found']
        display_cities = display_cities.sort_values('Market Rate', ascending=False, na_position='last')
        
        # Format rates
        display_cities['Market Rate'] = display_cities['Market Rate'].apply(
            lambda x: f"${x:.2f}" if pd.notna(x) else "No data"
        )
        display_cities['CareRev Rate'] = display_cities['CareRev Rate'].apply(
            lambda x: f"${x:.2f}" if pd.notna(x) else "—"
        )
        
        st.dataframe(display_cities, use_container_width=True, height=400)
    
    # ==================== TAB 2: PROSPECT RESEARCH ====================
    with tab2:
        st.markdown('<p class="section-header">🔍 Prospect Research Tool</p>', unsafe_allow_html=True)
        st.markdown("Research market rates for potential new clients")
        
        # Prospect search card
        st.markdown("""
        <div class="prospect-card">
            <h3 style="margin:0; color:white;">🎯 Find Market Rates</h3>
            <p style="margin:5px 0 0 0; opacity:0.9;">Select location, specialty, and pay type to see current market rates</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_city = st.selectbox(
                "📍 City & State",
                ['All Cities'] + sorted(MAJOR_CITIES.keys()),
                key='search_city'
            )
        
        with col2:
            search_specialty = st.selectbox(
                "🏥 Specialty",
                ['All Specialties'] + sorted(set([normalize_specialty(s) for s in SPECIALTIES])),
                key='search_specialty'
            )
        
        with col3:
            search_pay_type = st.selectbox(
                "💰 Pay Type",
                PAY_TYPES,
                key='search_pay_type'
            )
        
        st.markdown("---")
        
        # Filter and display results
        if market_data is not None:
            filtered_market = market_data.copy()
            
            # Apply city filter
            if search_city != 'All Cities':
                city_short = search_city.split(',')[0].strip()
                if 'city' in filtered_market.columns:
                    filtered_market = filtered_market[
                        filtered_market['city'].str.contains(city_short, case=False, na=False)
                    ]
                elif 'location' in filtered_market.columns:
                    filtered_market = filtered_market[
                        filtered_market['location'].str.contains(city_short, case=False, na=False)
                    ]
            
            # Apply specialty filter
            if search_specialty != 'All Specialties':
                filtered_market = filtered_market[
                    filtered_market['specialty_normalized'] == search_specialty
                ]
            
            # Apply pay type filter
            if search_pay_type != 'All':
                filtered_market = filtered_market[
                    filtered_market['pay_type'] == search_pay_type
                ]
            
            if len(filtered_market) > 0 and 'pay_rate_low' in filtered_market.columns:
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_rate = filtered_market['pay_rate_low'].mean()
                    st.metric("Average Rate", f"${avg_rate:.2f}/hr")
                
                with col2:
                    min_rate = filtered_market['pay_rate_low'].min()
                    st.metric("Minimum Rate", f"${min_rate:.2f}/hr")
                
                with col3:
                    max_rate = filtered_market['pay_rate_low'].max()
                    st.metric("Maximum Rate", f"${max_rate:.2f}/hr")
                
                with col4:
                    st.metric("Jobs Found", f"{len(filtered_market)}")
                
                # Recommendation box
                st.markdown("---")
                col_left, col_right = st.columns([2, 1])
                
                with col_left:
                    st.markdown("### 💡 Rate Recommendation")
                    percentile_25 = filtered_market['pay_rate_low'].quantile(0.25)
                    percentile_75 = filtered_market['pay_rate_low'].quantile(0.75)
                    
                    st.info(f"""
                    **Competitive Rate Range:** ${percentile_25:.2f} - ${percentile_75:.2f}/hr
                    
                    - **Budget Option:** ${min_rate:.2f} - ${percentile_25:.2f}/hr (bottom 25%)
                    - **Competitive:** ${percentile_25:.2f} - ${avg_rate:.2f}/hr (25th-50th percentile)  
                    - **Premium:** ${avg_rate:.2f} - ${percentile_75:.2f}/hr (50th-75th percentile)
                    - **Top Market:** ${percentile_75:.2f}+ /hr (top 25%)
                    """)
                
                with col_right:
                    # Distribution chart
                    fig = px.histogram(
                        filtered_market,
                        x='pay_rate_low',
                        nbins=15,
                        title="Rate Distribution",
                        color_discrete_sequence=[COLORS['accent1']]
                    )
                    fig.update_layout(
                        height=250,
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis_title="$/hr",
                        yaxis_title="Count"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Trend chart for this search
                st.markdown("### 📈 Rate Trend")
                trend_fig = create_trend_chart(
                    historical_data,
                    search_city if search_city != 'All Cities' else None,
                    search_specialty if search_specialty != 'All Specialties' else None,
                    search_pay_type if search_pay_type != 'All' else None
                )
                
                if trend_fig:
                    st.plotly_chart(trend_fig, use_container_width=True)
                else:
                    st.caption("📊 Trend data will appear after multiple scraper runs")
                
                # Detailed data
                st.markdown("### 📋 Job Listings")
                display_cols = ['job_title', 'facility_name', 'location', 'pay_rate_low', 'pay_type', 'source']
                display_cols = [c for c in display_cols if c in filtered_market.columns]
                st.dataframe(filtered_market[display_cols].head(50), use_container_width=True)
                
            else:
                st.warning("No jobs found matching your criteria. Try broadening your search.")
        else:
            st.info("📊 Run the scraper to populate market data: `python main.py`")
    
    # ==================== TAB 3: RATE COMPARISON ====================
    with tab3:
        st.markdown('<p class="section-header">📊 CareRev vs Market Rate Comparison</p>', unsafe_allow_html=True)
        
        if carerev_df is not None:
            # Filters
            st.sidebar.markdown("### 🔍 Comparison Filters")
            
            health_systems = ['All'] + sorted(carerev_df['Health System'].dropna().unique().tolist())
            selected_system = st.sidebar.selectbox("Health System", health_systems)
            
            specialties = ['All'] + sorted(carerev_df['specialty_normalized'].dropna().unique().tolist())
            selected_specialty = st.sidebar.selectbox("Specialty", specialties, key='comp_specialty')
            
            # Apply filters
            filtered_df = carerev_df.copy()
            if selected_system != 'All':
                filtered_df = filtered_df[filtered_df['Health System'] == selected_system]
            if selected_specialty != 'All':
                filtered_df = filtered_df[filtered_df['specialty_normalized'] == selected_specialty]
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_rate = filtered_df['rate'].mean()
                st.metric("Your Avg Rate", f"${avg_rate:.2f}/hr")
            
            with col2:
                if market_data is not None and 'pay_rate_low' in market_data.columns:
                    market_avg = market_data['pay_rate_low'].mean()
                    st.metric("Market Avg Rate", f"${market_avg:.2f}/hr")
                else:
                    st.metric("Market Avg Rate", "No data")
                    market_avg = 0
            
            with col3:
                if market_avg > 0:
                    diff = avg_rate - market_avg
                    pct_diff = (diff / market_avg * 100)
                    st.metric("Difference", f"${diff:+.2f}", delta=f"{pct_diff:+.1f}%")
                else:
                    st.metric("Difference", "N/A")
            
            with col4:
                st.metric("Records", f"{len(filtered_df):,}")
            
            st.markdown("---")
            
            # Charts
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("### 💰 Rates by Specialty")
                specialty_data = filtered_df.groupby('specialty_normalized').agg({
                    'rate': ['mean', 'min', 'max', 'count']
                }).reset_index()
                specialty_data.columns = ['Specialty', 'Avg Rate', 'Min Rate', 'Max Rate', 'Count']
                specialty_data = specialty_data.sort_values('Avg Rate', ascending=True)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='CareRev Rates',
                    y=specialty_data['Specialty'],
                    x=specialty_data['Avg Rate'],
                    orientation='h',
                    marker_color=COLORS['carerev'],
                    text=[f"${x:.2f}" for x in specialty_data['Avg Rate']],
                    textposition='outside'
                ))
                
                fig.update_layout(height=400, margin=dict(l=20, r=80, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_right:
                st.markdown("### 🌙 Rates by Shift Type")
                shift_data = filtered_df.groupby('shift_category')['rate'].mean().reset_index()
                shift_order = ['Day', 'Night', 'Weekend', 'Night Weekend']
                shift_data['shift_category'] = pd.Categorical(shift_data['shift_category'], categories=shift_order, ordered=True)
                shift_data = shift_data.sort_values('shift_category')
                
                fig2 = px.bar(
                    shift_data,
                    x='shift_category',
                    y='rate',
                    color='shift_category',
                    color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['accent1'], COLORS['accent2']],
                    text=[f"${x:.2f}" for x in shift_data['rate']]
                )
                fig2.update_layout(height=400, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
                fig2.update_traces(textposition='outside')
                st.plotly_chart(fig2, use_container_width=True)
            
            # Health System chart
            st.markdown("### 🏥 Rates by Health System")
            system_data = filtered_df.groupby('Health System')['rate'].mean().reset_index()
            system_data = system_data.sort_values('rate', ascending=False).head(15)
            
            fig3 = px.bar(
                system_data,
                x='Health System',
                y='rate',
                color='rate',
                color_continuous_scale='Teal',
                text=[f"${x:.2f}" for x in system_data['rate']]
            )
            fig3.update_layout(height=400, xaxis_tickangle=-45, coloraxis_showscale=False)
            fig3.update_traces(textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)
            
            # Data table
            st.markdown("### 📋 Detailed Data")
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
        else:
            st.info("👆 Upload your CareRev rates CSV in the sidebar to see comparisons")
    
    # ==================== TAB 4: TRENDS & ANALYSIS ====================
    with tab4:
        st.markdown('<p class="section-header">📈 Market Trends & Analysis</p>', unsafe_allow_html=True)
        
        if historical_data is not None and len(historical_data) > 0:
            # Trend filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                trend_city = st.selectbox(
                    "City",
                    ['All Cities'] + sorted(MAJOR_CITIES.keys()),
                    key='trend_city'
                )
            
            with col2:
                trend_specialty = st.selectbox(
                    "Specialty",
                    ['All'] + sorted(set([normalize_specialty(s) for s in SPECIALTIES])),
                    key='trend_specialty'
                )
            
            with col3:
                trend_pay_type = st.selectbox(
                    "Pay Type",
                    PAY_TYPES,
                    key='trend_pay_type'
                )
            
            # Create trend chart
            trend_fig = create_trend_chart(
                historical_data,
                trend_city if trend_city != 'All Cities' else None,
                trend_specialty if trend_specialty != 'All' else None,
                trend_pay_type if trend_pay_type != 'All' else None
            )
            
            if trend_fig:
                st.plotly_chart(trend_fig, use_container_width=True)
            else:
                st.info("📊 More historical data needed. Run the scraper multiple times to build trend data.")
            
            # Pay type comparison
            st.markdown("### 💰 Rate Comparison by Pay Type")
            pay_type_data = historical_data.groupby('pay_type')['pay_rate_low'].agg(['mean', 'count']).reset_index()
            pay_type_data.columns = ['Pay Type', 'Avg Rate', 'Count']
            pay_type_data = pay_type_data.sort_values('Avg Rate', ascending=False)
            
            if len(pay_type_data) > 0:
                fig = px.bar(
                    pay_type_data,
                    x='Pay Type',
                    y='Avg Rate',
                    color='Pay Type',
                    color_discrete_map={
                        'Travel': COLORS['travel'],
                        'Staff': COLORS['staff'],
                        'Per Diem': COLORS['perdiem'],
                        'Crisis': COLORS['accent2']
                    },
                    text=[f"${x:.2f}" for x in pay_type_data['Avg Rate']]
                )
                fig.update_layout(height=350, showlegend=False)
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            # Source comparison
            if 'source' in historical_data.columns:
                st.markdown("### 📊 Rates by Source")
                source_data = historical_data.groupby('source')['pay_rate_low'].agg(['mean', 'count']).reset_index()
                source_data.columns = ['Source', 'Avg Rate', 'Jobs']
                source_data = source_data.sort_values('Avg Rate', ascending=False)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.bar(
                        source_data,
                        x='Source',
                        y='Avg Rate',
                        color='Avg Rate',
                        color_continuous_scale='Teal',
                        text=[f"${x:.2f}" for x in source_data['Avg Rate']]
                    )
                    fig.update_layout(height=300, coloraxis_showscale=False)
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig2 = px.pie(
                        source_data,
                        values='Jobs',
                        names='Source',
                        title='Jobs by Source',
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig2.update_layout(height=300)
                    st.plotly_chart(fig2, use_container_width=True)
            
        else:
            st.info("📊 Run the scraper multiple times to build trend data. Each run adds a data point.")
            st.markdown("""
            **To build trend data:**
            1. Run `python main.py` today
            2. Run again tomorrow (or let GitHub Actions run daily)
            3. After 3+ runs, trends will appear here
            """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #888; font-size: 0.9rem;">
            CareRev Market Rates Dashboard | Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            <br>Market data collected ethically from Indeed, Vivian Health, Aya Healthcare, IntelyCare
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
