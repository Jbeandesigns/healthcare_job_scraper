"""
CareRev Market Rates Dashboard
Compare your rates against market data from multiple job boards

To run locally: streamlit run dashboard.py
To deploy: Push to GitHub and connect to Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
import glob

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
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
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
    'market': '#3e8a93'
}


@st.cache_data
def load_market_data():
    """Load the most recent market data from scraped Excel files."""
    # Look for Excel files in the output directory
    excel_files = glob.glob('output/healthcare_jobs_*.xlsx')
    
    if not excel_files:
        # Try alternate locations
        excel_files = glob.glob('*.xlsx')
    
    if not excel_files:
        return None
    
    # Get the most recent file
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
    # Remove $ and commas, convert to float
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
    
    # Map variations to standard names
    mappings = {
        'ICU': ['ICU', 'INTENSIVE CARE', 'CRITICAL CARE', 'CCU'],
        'Med/Surg': ['MED/SURG', 'MED SURG', 'MEDICAL SURGICAL', 'MEDSURG', 'M/S'],
        'ER': ['ER', 'ED', 'EMERGENCY', 'EMERGENCY ROOM', 'EMERGENCY DEPARTMENT'],
        'Tele': ['TELE', 'TELEMETRY', 'CARDIAC', 'MED SURG/TELE'],
        'OR': ['OR', 'OPERATING ROOM', 'SURGICAL', 'PERIOPERATIVE', 'CIRCULATOR'],
        'L&D': ['L&D', 'LABOR', 'DELIVERY', 'OB', 'OBSTETRIC', 'MATERNITY'],
        'PACU': ['PACU', 'POST ANESTHESIA', 'RECOVERY'],
        'Stepdown': ['STEPDOWN', 'STEP DOWN', 'SDU', 'PCU', 'PROGRESSIVE'],
        'CNA': ['CNA', 'NURSING ASSISTANT', 'NURSE AIDE', 'HOSPITAL CNA'],
        'LPN': ['LPN', 'LVN', 'LICENSED PRACTICAL', 'LICENSED VOCATIONAL'],
        'RN': ['RN', 'REGISTERED NURSE'],
    }
    
    for standard, variations in mappings.items():
        for var in variations:
            if var in specialty:
                return standard
    
    return 'Other'


def process_carerev_data(df):
    """Process the uploaded CareRev CSV data."""
    df = df.copy()
    
    # Clean pay rate
    df['rate'] = df['AVERAGE Pay Rate'].apply(clean_pay_rate)
    
    # Normalize specialty
    df['specialty_normalized'] = df['Specialty'].apply(normalize_specialty)
    
    # Extract job type (RN, CNA, etc.)
    def get_job_type(specialty):
        specialty = str(specialty).upper()
        if 'CNA' in specialty or 'AIDE' in specialty or 'TECH' in specialty:
            return 'CNA/Tech'
        elif 'LPN' in specialty or 'LVN' in specialty:
            return 'LPN'
        else:
            return 'RN'
    
    df['job_type'] = df['Specialty'].apply(get_job_type)
    
    # Categorize shift
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
    
    return df


def create_comparison_chart(carerev_df, market_df, group_by='specialty_normalized'):
    """Create a comparison bar chart."""
    # Aggregate CareRev data
    carerev_agg = carerev_df.groupby(group_by)['rate'].agg(['mean', 'min', 'max', 'count']).reset_index()
    carerev_agg.columns = [group_by, 'carerev_avg', 'carerev_min', 'carerev_max', 'carerev_count']
    
    # Aggregate market data if available
    if market_df is not None and 'pay_rate_low' in market_df.columns:
        market_df['specialty_normalized'] = market_df['specialty'].apply(normalize_specialty) if 'specialty' in market_df.columns else 'Other'
        market_agg = market_df.groupby('specialty_normalized')['pay_rate_low'].agg(['mean', 'min', 'max', 'count']).reset_index()
        market_agg.columns = ['specialty_normalized', 'market_avg', 'market_min', 'market_max', 'market_count']
        
        # Merge
        comparison = carerev_agg.merge(market_agg, on=group_by, how='outer')
    else:
        comparison = carerev_agg.copy()
        comparison['market_avg'] = None
    
    return comparison


def main():
    # Header
    st.markdown('<p class="main-header">🏥 CareRev Market Rates Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Compare your rates against market data from Indeed, Vivian, Aya Healthcare & more</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/200x60/003e52/FFFFFF?text=CareRev", width=200)
    st.sidebar.markdown("---")
    
    # File upload
    st.sidebar.markdown("### 📤 Upload Your Rates")
    uploaded_file = st.sidebar.file_uploader(
        "Upload CareRev rates CSV",
        type=['csv'],
        help="Upload your Pay_Rates CSV file to compare against market data"
    )
    
    # Load market data
    market_data = None
    market_file = None
    
    st.sidebar.markdown("### 📊 Market Data")
    market_result = load_market_data()
    if market_result and market_result[0] is not None:
        market_data, market_file = market_result
        st.sidebar.success(f"✓ Loaded: {os.path.basename(market_file)}")
        st.sidebar.caption(f"{len(market_data)} jobs found")
    else:
        st.sidebar.warning("No market data found. Run the scraper first!")
        st.sidebar.caption("Run: `python main.py`")
    
    # Main content
    if uploaded_file is not None:
        # Load and process CareRev data
        carerev_df = pd.read_csv(uploaded_file)
        carerev_df = process_carerev_data(carerev_df)
        
        st.sidebar.success(f"✓ Loaded {len(carerev_df)} CareRev rates")
        
        # Filters
        st.sidebar.markdown("### 🔍 Filters")
        
        # Health System filter
        health_systems = ['All'] + sorted(carerev_df['Health System'].dropna().unique().tolist())
        selected_system = st.sidebar.selectbox("Health System", health_systems)
        
        # Specialty filter
        specialties = ['All'] + sorted(carerev_df['specialty_normalized'].dropna().unique().tolist())
        selected_specialty = st.sidebar.selectbox("Specialty", specialties)
        
        # Job Type filter
        job_types = ['All'] + sorted(carerev_df['job_type'].dropna().unique().tolist())
        selected_job_type = st.sidebar.selectbox("Job Type", job_types)
        
        # Apply filters
        filtered_df = carerev_df.copy()
        if selected_system != 'All':
            filtered_df = filtered_df[filtered_df['Health System'] == selected_system]
        if selected_specialty != 'All':
            filtered_df = filtered_df[filtered_df['specialty_normalized'] == selected_specialty]
        if selected_job_type != 'All':
            filtered_df = filtered_df[filtered_df['job_type'] == selected_job_type]
        
        # Key Metrics Row
        st.markdown("### 📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_rate = filtered_df['rate'].mean()
            st.metric(
                "Your Avg Rate",
                f"${avg_rate:.2f}/hr" if not pd.isna(avg_rate) else "N/A",
                help="Average hourly rate across all filtered CareRev data"
            )
        
        with col2:
            if market_data is not None and 'pay_rate_low' in market_data.columns:
                market_avg = market_data['pay_rate_low'].mean()
                st.metric(
                    "Market Avg Rate",
                    f"${market_avg:.2f}/hr" if not pd.isna(market_avg) else "N/A",
                    help="Average hourly rate from scraped market data"
                )
            else:
                st.metric("Market Avg Rate", "No data", help="Run the scraper to get market data")
        
        with col3:
            if market_data is not None and 'pay_rate_low' in market_data.columns:
                diff = avg_rate - market_avg
                pct_diff = (diff / market_avg * 100) if market_avg > 0 else 0
                st.metric(
                    "Difference",
                    f"${diff:+.2f}/hr",
                    delta=f"{pct_diff:+.1f}%",
                    delta_color="normal"
                )
            else:
                st.metric("Difference", "N/A")
        
        with col4:
            st.metric(
                "Records Analyzed",
                f"{len(filtered_df):,}",
                help="Number of rate records in filtered data"
            )
        
        st.markdown("---")
        
        # Charts Row
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 💰 Rates by Specialty")
            
            # Create specialty comparison chart
            specialty_data = filtered_df.groupby('specialty_normalized').agg({
                'rate': ['mean', 'min', 'max', 'count']
            }).reset_index()
            specialty_data.columns = ['Specialty', 'Avg Rate', 'Min Rate', 'Max Rate', 'Count']
            specialty_data = specialty_data.sort_values('Avg Rate', ascending=True)
            
            fig = go.Figure()
            
            # CareRev rates
            fig.add_trace(go.Bar(
                name='CareRev Rates',
                y=specialty_data['Specialty'],
                x=specialty_data['Avg Rate'],
                orientation='h',
                marker_color=COLORS['carerev'],
                text=[f"${x:.2f}" for x in specialty_data['Avg Rate']],
                textposition='outside'
            ))
            
            # Add market rates if available
            if market_data is not None and 'pay_rate_low' in market_data.columns and 'specialty' in market_data.columns:
                market_data['specialty_normalized'] = market_data['specialty'].apply(normalize_specialty)
                market_specialty = market_data.groupby('specialty_normalized')['pay_rate_low'].mean().reset_index()
                market_specialty.columns = ['Specialty', 'Market Rate']
                
                # Merge with specialty data
                merged = specialty_data.merge(market_specialty, on='Specialty', how='left')
                
                fig.add_trace(go.Bar(
                    name='Market Rates',
                    y=merged['Specialty'],
                    x=merged['Market Rate'],
                    orientation='h',
                    marker_color=COLORS['market'],
                    text=[f"${x:.2f}" if not pd.isna(x) else "" for x in merged['Market Rate']],
                    textposition='outside'
                ))
            
            fig.update_layout(
                barmode='group',
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                xaxis_title="Hourly Rate ($)",
                yaxis_title=""
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.markdown("### 🌙 Rates by Shift Type")
            
            # Shift type comparison
            shift_data = filtered_df.groupby('shift_category').agg({
                'rate': ['mean', 'count']
            }).reset_index()
            shift_data.columns = ['Shift', 'Avg Rate', 'Count']
            
            # Order shifts logically
            shift_order = ['Day', 'Night', 'Weekend', 'Night Weekend']
            shift_data['Shift'] = pd.Categorical(shift_data['Shift'], categories=shift_order, ordered=True)
            shift_data = shift_data.sort_values('Shift')
            
            fig2 = px.bar(
                shift_data,
                x='Shift',
                y='Avg Rate',
                color='Shift',
                color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['accent1'], COLORS['accent2']],
                text=[f"${x:.2f}" for x in shift_data['Avg Rate']]
            )
            
            fig2.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Hourly Rate ($)"
            )
            fig2.update_traces(textposition='outside')
            
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # Health System Analysis
        st.markdown("### 🏥 Rates by Health System")
        
        system_data = filtered_df.groupby('Health System').agg({
            'rate': ['mean', 'min', 'max', 'count']
        }).reset_index()
        system_data.columns = ['Health System', 'Avg Rate', 'Min Rate', 'Max Rate', 'Positions']
        system_data = system_data.sort_values('Avg Rate', ascending=False)
        
        fig3 = px.bar(
            system_data.head(15),  # Top 15
            x='Health System',
            y='Avg Rate',
            color='Avg Rate',
            color_continuous_scale=['#3e8a93', '#003e52'],
            text=[f"${x:.2f}" for x in system_data.head(15)['Avg Rate']]
        )
        
        fig3.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=20, b=100),
            xaxis_tickangle=-45,
            showlegend=False,
            coloraxis_showscale=False,
            yaxis_title="Hourly Rate ($)",
            xaxis_title=""
        )
        fig3.update_traces(textposition='outside')
        
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed Data Table
        st.markdown("### 📋 Detailed Rate Data")
        
        # Prepare display dataframe
        display_df = filtered_df[['Health System', 'Hospital', 'Specialty', 'Shift Type', 'AVERAGE Pay Rate', 'specialty_normalized', 'job_type']].copy()
        display_df.columns = ['Health System', 'Hospital', 'Specialty', 'Shift', 'Rate', 'Category', 'Job Type']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name=f"carerev_rates_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    else:
        # No file uploaded - show instructions
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 40px; background-color: #f8f9fa; border-radius: 10px;">
                <h2>👆 Upload Your CareRev Rates</h2>
                <p style="font-size: 1.1rem; color: #666;">
                    Use the sidebar to upload your <code>Pay_Rates_*.csv</code> file<br>
                    to see comparisons against market data.
                </p>
                <br>
                <p style="color: #888;">
                    <strong>Expected columns:</strong><br>
                    Health System, Hospital, Specialty, Shift Type, AVERAGE Pay Rate
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show market data preview if available
        if market_data is not None:
            st.markdown("---")
            st.markdown("### 📊 Market Data Preview")
            st.caption(f"Data from: {market_file}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Jobs", f"{len(market_data):,}")
            with col2:
                if 'pay_rate_low' in market_data.columns:
                    st.metric("Avg Market Rate", f"${market_data['pay_rate_low'].mean():.2f}/hr")
            with col3:
                if 'source' in market_data.columns:
                    st.metric("Sources", market_data['source'].nunique())
            
            st.dataframe(market_data.head(20), use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #888; font-size: 0.9rem;">
            CareRev Market Rates Dashboard | Last updated: {datetime.now().strftime('%B %d, %Y')}
            <br>Market data collected ethically from Indeed, Vivian Health, Aya Healthcare, IntelyCare
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
