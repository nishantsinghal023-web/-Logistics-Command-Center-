import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIGURATION & HIGH-VISIBILITY CSS
# ==========================================
st.set_page_config(
    page_title="Nassau Logistics Command", 
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode, High Contrast, Neon Accents
st.markdown("""
    <style>
        /* Deep dark background for maximum contrast */
        .stApp { background-color: #0e1117; }
        
        /* Bright white text for headers */
        h1, h2, h3 { color: #f8fafc !important; font-family: 'Inter', sans-serif; font-weight: 800 !important; }
        p, .subtitle { color: #94a3b8 !important; font-size: 1.2rem; }
        
        /* MASSIVE KPI Metric Cards with Neon Borders */
        div[data-testid="stMetricSimpleValue"] {
            font-size: 3rem !important; /* Huge numbers */
            font-weight: 900 !important;
            color: #ffffff !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1.1rem !important;
            color: #cbd5e1 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        div.element-container:has(div.stMetric) {
            background-color: #1e293b;
            padding: 25px !important;
            border-radius: 12px !important;
            border-left: 6px solid #00f2fe; /* Bright Cyan Accent */
            box-shadow: 0 8px 16px rgba(0,0,0,0.6);
            transition: transform 0.2s ease-in-out;
        }
        div.element-container:has(div.stMetric):hover {
            transform: scale(1.02);
            border-left: 6px solid #fe0979; /* Neon Pink Hover */
        }
        
        /* Darker table styling */
        .stDataFrame { background-color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# Main Headers
st.title("⚡ Logistics Command Center")
st.markdown('<p class="subtitle">High-Visibility Route & Bottleneck Tracking</p>', unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv('Final_Nassau_Route_Data.csv')
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
    
    us_state_to_abbrev = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
        "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
        "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
        "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
        "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
        "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "District Of Columbia": "DC"
    }
    df['State_Code'] = df['State/Province'].map(us_state_to_abbrev)
    return df

df = load_data()
global_avg_lead_time = df['Lead Time (Days)'].mean()

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.header("🎛️ Network Filters")
    min_date, max_date = df['Order Date'].min().date(), df['Order Date'].max().date()
    date_selection = st.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    threshold = st.slider("SLA Target (Flag Delayed >)", 1, 15, 5)
    selected_states = st.multiselect("Select Destination States", sorted(df['State/Province'].dropna().unique()))
    selected_modes = st.multiselect("Select Ship Modes", df['Ship Mode'].unique(), default=list(df['Ship Mode'].unique()))

filtered_df = df.copy()
if len(date_selection) == 2:
    start_date, end_date = date_selection
    filtered_df = filtered_df[(filtered_df['Order Date'].dt.date >= start_date) & (filtered_df['Order Date'].dt.date <= end_date)]
if selected_states:
    filtered_df = filtered_df[filtered_df['State/Province'].isin(selected_states)]
if selected_modes:
    filtered_df = filtered_df[filtered_df['Ship Mode'].isin(selected_modes)]

filtered_df['Is_Delayed'] = filtered_df['Lead Time (Days)'] > threshold

# ==========================================
# 4. HUGE KPI METRICS
# ==========================================
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    volume_diff = len(filtered_df) - len(df)
    st.metric("Total Shipments", f"{len(filtered_df):,}", delta=f"{volume_diff} vs base")
with kpi2:
    current_avg = filtered_df['Lead Time (Days)'].mean()
    st.metric("Network Avg Lead Time", f"{current_avg:.2f} Days", delta=f"{current_avg - global_avg_lead_time:.2f} Days", delta_color="inverse")
with kpi3:
    delay_rate = (filtered_df['Is_Delayed'].mean() * 100) if len(filtered_df) > 0 else 0
    st.metric("SLA Breach Rate", f"{delay_rate:.1f}%")

st.markdown("---")

# ==========================================
# 5. HIGH-CONTRAST VISUALIZATIONS
# ==========================================
col_map, col_chart = st.columns([6, 4])

with col_map:
    st.subheader("🗺️ Regional Bottleneck Heatmap")
    map_data = filtered_df.groupby(['State_Code', 'State/Province'])['Lead Time (Days)'].mean().reset_index()
    fig_map = px.choropleth(
        map_data, locations='State_Code', locationmode="USA-states", 
        color='Lead Time (Days)', scope="usa",
        color_continuous_scale="Inferno", # High contrast dark-to-bright scale
        hover_name='State/Province'
    )
    # Applied Plotly Dark theme
    fig_map.update_layout(
        template="plotly_dark",
        geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#1f2937'),
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_chart:
    st.subheader("📦 Delivery Speed by Method")
    mode_data = filtered_df.groupby('Ship Mode')['Lead Time (Days)'].mean().reset_index().sort_values('Lead Time (Days)')
    fig_mode = px.bar(
        mode_data, x='Lead Time (Days)', y='Ship Mode', orientation='h',
        color='Lead Time (Days)', color_continuous_scale="Viridis" # Bright green/yellow pops on dark
    )
    fig_mode.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        margin=dict(l=0, r=0, t=20, b=0), showlegend=False
    )
    st.plotly_chart(fig_mode, use_container_width=True)

# ==========================================
# 6. ROUTE PERFORMANCE LEADERBOARDS
# ==========================================
st.subheader("⚡ Route Analytics")

route_kpis = filtered_df.groupby('Route').agg(
    Total_Orders=('Order ID', 'count'), 
    Avg_Lead_Time=('Lead Time (Days)', 'mean')
).reset_index()

valid_routes = route_kpis[route_kpis['Total_Orders'] > 5]

col_best, col_worst = st.columns(2)

with col_best:
    st.success("🟢 Highest Efficiency Routes")
    best_routes = valid_routes.sort_values(by='Avg_Lead_Time', ascending=True).head(5)
    st.dataframe(best_routes.style.format({'Avg_Lead_Time': '{:.2f} days'}), width='stretch', hide_index=True)

with col_worst:
    st.error("🔴 Critical Bottleneck Routes")
    worst_routes = valid_routes.sort_values(by='Avg_Lead_Time', ascending=False).head(5)
    st.dataframe(worst_routes.style.format({'Avg_Lead_Time': '{:.2f} days'}), width='stretch', hide_index=True)

with st.expander("🔍 Investigate Order-Level Shipment Timelines"):
    raw_timeline = filtered_df[['Order ID', 'Order Date', 'Ship Date', 'Route', 'Ship Mode', 'Lead Time (Days)', 'Is_Delayed']]
    st.dataframe(raw_timeline.sort_values(by='Lead Time (Days)', ascending=False).head(50), width='stretch', hide_index=True)