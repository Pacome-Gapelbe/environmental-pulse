import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import glob
import os
import numpy as np
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

for path in [current_dir, project_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from database import DatabaseManager
    DB_AVAILABLE = True
    print("✅ Database module imported successfully")
except ImportError:
    try:
        from src.database import DatabaseManager
        DB_AVAILABLE = True
        print("✅ Database module imported from src")
    except ImportError as e:
        DB_AVAILABLE = False
        print(f"⚠️ Database module not available: {e}")
except Exception as e:
    DB_AVAILABLE = False
    print(f"⚠️ Database error: {e}")

st.set_page_config(
    page_title="Global Environmental Pulse",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with refresh indicator
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .gradient-text {
        background: linear-gradient(90deg, #1f4037, #99f2c8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .stTab {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50, #34495e);
    }
    .data-source-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .db-badge {
        background-color: #10b981;
        color: white;
    }
    .csv-badge {
        background-color: #f59e0b;
        color: white;
    }
    .refresh-indicator {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        text-align: center;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

def load_latest_data():
    """Load data from PostgreSQL database with CSV fallback"""
    data_files = {}
    data_source = "csv"
    
    if DB_AVAILABLE:
        try:
            db_manager = DatabaseManager()
            
            data_files['air'] = db_manager.get_latest_data('air_quality', 1000)
            data_files['fire'] = db_manager.get_latest_data('fire_alerts', 1000)
            data_files['climate'] = db_manager.get_latest_data('climate_data', 1000)
            data_files['economic'] = db_manager.get_latest_data('economic_data', 1000)
            data_files['water'] = db_manager.get_latest_data('water_quality', 1000)
            
            db_manager.close()
            
            if any(not df.empty for df in data_files.values()):
                data_source = "database"
                print("✅ Loaded data from PostgreSQL database")
            else:
                print("⚠️ Database is empty, falling back to CSV")
                
        except Exception as e:
            print(f"❌ Database load failed: {e}")
    
    if data_source == "csv" or all(df.empty for df in data_files.values() if data_files):
        try:
            for key in ['air', 'fire', 'climate', 'economic', 'water']:
                files = glob.glob(f'data/raw/{key}_*.csv')
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    data_files[key] = pd.read_csv(latest_file)
                    data_files[key]._is_fallback = True
                    print(f"✅ Loaded {key} data from CSV")
                else:
                    data_files[key] = pd.DataFrame()
        except Exception as e:
            print(f"❌ Error loading CSV data: {e}")
    
    for key in data_files:
        if not data_files[key].empty:
            data_files[key].attrs['data_source'] = data_source
    
    return data_files, data_source

# --- UPDATED FUNCTION FOR 3D INTERACTIVE MAP (AIR QUALITY) ---
# --- UPDATED FUNCTION FOR 3D INTERACTIVE MAP (AIR QUALITY) ---
def create_air_quality_map(df):
    if df.empty:
        return None
    df_clean = df.copy()
    if 'aqi' in df_clean.columns:
        df_clean['aqi'] = pd.to_numeric(df_clean['aqi'], errors='coerce').fillna(0)
    else:
        df_clean['aqi'] = 0
    df_clean['aqi_size'] = (df_clean['aqi'] - df_clean['aqi'].min()).clip(lower=1)
    fig = px.scatter_geo(
        df_clean, lat='lat', lon='lon', hover_name='city',
        hover_data={'aqi': True, 'pm2_5': True, 'pm10': True},
        color='aqi',
        color_continuous_scale=['green', 'yellow', 'orange', 'red', 'purple'],
        size='aqi_size', size_max=20,
        projection="orthographic",
        height=520,
        title="  "
    )
    fig.update_geos(
        showland=True, landcolor="lightgray",
        showocean=True, oceancolor="lightblue",
        showcountries=True, countrycolor="darkgray", # Changed color to be more prominent
        projection_rotation=dict(lon=-20, lat=10, roll=0),
        bgcolor='rgba(0,0,0,0)'
    )
    fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0}, title_font_size=18,
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig
# -----------------------------------------------------------------

def create_air_quality_charts(df):
    if df.empty:
        return None, None, None
    
    df_clean = df.copy()
    
    for col in ['aqi', 'pm2_5', 'pm10']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
    
    fig1 = px.bar(
        df_clean.sort_values('aqi', ascending=True), 
        x='aqi', y='city', 
        orientation='h',
        color='aqi',
        color_continuous_scale=['green', 'yellow', 'orange', 'red', 'purple'],
        title="🏙️ Air Quality Index by City",
        labels={'aqi': 'Air Quality Index', 'city': 'City'}
    )
    fig1.update_layout(height=400, showlegend=False)
    
    df_clean['pm2_5'] = df_clean['pm2_5'].clip(lower=0.1)
    df_clean['pm10'] = df_clean['pm10'].clip(lower=0.1)
    df_clean['aqi_size'] = df_clean['aqi'].clip(lower=1)
    
    fig2 = px.scatter(
        df_clean, x='pm2_5', y='pm10', 
        size='aqi_size', color='city',
        title="💨 PM2.5 vs PM10 Levels",
        labels={'pm2_5': 'PM2.5 (μg/m³)', 'pm10': 'PM10 (μg/m³)'}
    )
    fig2.update_layout(height=400)
    
    fig3 = px.histogram(
        df_clean, x='aqi', nbins=20,
        title="📊 AQI Distribution",
        color_discrete_sequence=['#3498db']
    )
    fig3.update_layout(height=300)
    
    return fig1, fig2, fig3

# --- UPDATED FUNCTION FOR 3D INTERACTIVE MAP (FIRE ALERTS) ---
# --- UPDATED FUNCTION FOR 3D INTERACTIVE MAP (FIRE ALERTS) ---
def create_fire_map(df):
    if df.empty:
        return None
    df_clean = df.copy()
    if 'confidence' in df_clean.columns:
        df_clean['confidence'] = pd.to_numeric(df_clean['confidence'], errors='coerce').fillna(50)
    else:
        df_clean['confidence'] = 50
    if 'frp' in df_clean.columns:
        df_clean['frp'] = pd.to_numeric(df_clean['frp'], errors='coerce').fillna(1)
    else:
        df_clean['frp'] = 1
    fig = px.scatter_geo(df_clean, lat='latitude', lon='longitude',
                         hover_data={'confidence': True, 'frp': True},
                         color='confidence', color_continuous_scale='Reds',
                         size='frp', size_max=15,
                         projection="orthographic",
                         height=520,
                         title="  ")
    fig.update_geos(showland=True, landcolor="lightgray", showocean=True, oceancolor="lightblue",
                    showcountries=True, countrycolor="darkgray", projection_rotation=dict(lon=-20, lat=10, roll=0), # Changed color to be more prominent
                    bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0}, title_font_size=18,
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig
# -----------------------------------------------------------------

def create_fire_charts(df):
    if df.empty:
        return None, None

    df_clean = df.copy()

    # Ensure numeric columns
    for col in ['confidence', 'frp']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    # Drop rows without required fields
    df_clean = df_clean.dropna(
        subset=['latitude', 'longitude', 'confidence', 'frp']
    )

    # 🔑 DISTINCT fires by location (same logic as your metric)
    df_clean = df_clean.drop_duplicates(
        subset=['latitude', 'longitude']
    )

    if df_clean.empty:
        return None, None

    # Clip values for visualization
    df_clean['confidence'] = df_clean['confidence'].clip(0, 100)
    df_clean['frp'] = df_clean['frp'].clip(0.1, 1000)

    # 🎯 Confidence distribution (counts DISTINCT fires)
    fig1 = px.histogram(
        df_clean,
        x='confidence',
        nbins=20,
        title="🎯 Fire Detection Confidence Distribution (Distinct Fires)",
        color_discrete_sequence=['#e74c3c']
    )
    fig1.update_layout(height=300)

    # 🔥 FRP vs Confidence (one point per fire)
    fig2 = px.scatter(
        df_clean,
        x='confidence',
        y='frp',
        title="🔥 Fire Radiative Power vs Detection Confidence (Distinct Fires)",
        labels={
            'frp': 'Fire Radiative Power (MW)',
            'confidence': 'Detection Confidence (%)'
        }
    )
    fig2.update_layout(height=400)

    return fig1, fig2


# --- UPDATED FUNCTION FOR 3D INTERACTIVE MAP (CLIMATE DATA) ---
def create_climate_map(df):
    if df.empty:
        return None
    df_clean = df.copy()
    if 'temperature_2m' in df_clean.columns:
        df_clean['temperature_2m'] = pd.to_numeric(df_clean['temperature_2m'], errors='coerce').fillna(df_clean['temperature_2m'].mean())
    else:
        df_clean['temperature_2m'] = 0
    if 'precipitation' in df_clean.columns:
        df_clean['precipitation'] = pd.to_numeric(df_clean['precipitation'], errors='coerce').fillna(0)
    else:
        df_clean['precipitation'] = 0
    df_clean['precipitation_size'] = df_clean['precipitation'] + 0.1
    fig = px.scatter_geo(df_clean, lat='lat', lon='lon', hover_name='city',
                         hover_data={'temperature_2m': ':.1f', 'precipitation': ':.1f'},
                         color='temperature_2m', color_continuous_scale='RdYlBu_r',
                         size='precipitation_size', size_max=15,
                         projection="orthographic", height=520,
                         title="   ")
    fig.update_geos(showland=True, landcolor="lightgray", showocean=True, oceancolor="lightblue",
                    showcountries=True, countrycolor="gray", projection_rotation=dict(lon=-20, lat=10, roll=0),
                    bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0}, title_font_size=18,
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig
# -----------------------------------------------------------------

def create_climate_charts(df):
    if df.empty:
        return None, None, None
    
    df_clean = df.copy()
    
    df_clean['temperature_2m'] = df_clean['temperature_2m'].fillna(df_clean['temperature_2m'].mean())
    df_clean['precipitation'] = df_clean['precipitation'].fillna(0)
    
    fig1 = px.bar(
        df_clean.sort_values('temperature_2m', ascending=True),
        x='temperature_2m', y='city',
        orientation='h',
        color='temperature_2m',
        color_continuous_scale='RdYlBu_r',
        title="🌡️ Temperature by City",
        labels={'temperature_2m': 'Temperature (°C)', 'city': 'City'}
    )
    fig1.update_layout(height=400)
    
    fig2 = px.bar(
        df_clean.sort_values('precipitation', ascending=True),
        x='precipitation', y='city',
        orientation='h',
        color='precipitation',
        color_continuous_scale='Blues',
        title="🌧️ Precipitation by City",
        labels={'precipitation': 'Precipitation (mm)', 'city': 'City'}
    )
    fig2.update_layout(height=400)
    
    if 'solar_radiation' in df_clean.columns:
        df_clean['solar_radiation'] = df_clean['solar_radiation'].fillna(df_clean['solar_radiation'].mean())
        df_clean['solar_radiation'] = df_clean['solar_radiation'].clip(lower=0.1)
        
        if df_clean['solar_radiation'].notna().any():
            fig3 = px.scatter(
                df_clean, 
                x='temperature_2m', 
                y='precipitation',
                size='solar_radiation',
                color='city',
                title="🌡️ Temperature vs Precipitation (Size: Solar Radiation)",
                labels={
                    'temperature_2m': 'Temperature (°C)', 
                    'precipitation': 'Precipitation (mm)',
                    'solar_radiation': 'Solar Radiation (W/m²)'
                }
            )
        else:
            fig3 = px.scatter(
                df_clean, 
                x='temperature_2m', 
                y='precipitation',
                color='city',
                title="🌡️ Temperature vs Precipitation",
                labels={
                    'temperature_2m': 'Temperature (°C)', 
                    'precipitation': 'Precipitation (mm)'
                }
            )
    else:
        fig3 = px.scatter(
            df_clean, 
            x='temperature_2m', 
            y='precipitation',
            color='city',
            title="🌡️ Temperature vs Precipitation",
            labels={
                'temperature_2m': 'Temperature (°C)', 
                'precipitation': 'Precipitation (mm)'
            }
        )
    
    fig3.update_layout(height=400)
    
    return fig1, fig2, fig3

def create_economic_charts(df):
    if df.empty:
        return None, None
    
    pivot_df = df.pivot_table(
        index=['country_name', 'year'],
        columns='indicator_name',
        values='value',
        aggfunc='first'
    ).reset_index()
    
    gdp_data = df[df['indicator_name'].str.contains('GDP', case=False, na=False)]
    if not gdp_data.empty:
        fig1 = px.line(
            gdp_data, x='year', y='value', color='country_name',
            title="💰 GDP Trends by Country",
            labels={'value': 'GDP Value', 'year': 'Year'}
        )
        fig1.update_layout(height=400)
    else:
        fig1 = None
    
    latest_year = df['year'].max() if 'year' in df.columns else None
    if latest_year:
        latest_data = df[df['year'] == latest_year]
        
        # --- MODIFICATION START ---
        fig2 = px.bar(
            latest_data, 
            x='country_name', 
            y='value', 
            color='country_name', # Changed from 'indicator_name' to 'country_name'
            title=f"📊 Economic Indicators ({latest_year}) (Colored by Country)", # Updated title for clarity
            labels={'value': 'Indicator Value', 'country_name': 'Country'}
        )
        # --- MODIFICATION END ---
        
        fig2.update_layout(height=400, xaxis_tickangle=-45)
    else:
        fig2 = None
    
    return fig1, fig2

def create_water_charts(df):
    if df.empty:
        return None, None
    
    if 'water_quality_index' in df.columns:
        fig1 = px.bar(
            df.sort_values('water_quality_index', ascending=True),
            x='water_quality_index', y='city',
            orientation='h',
            color='water_quality_index',
            color_continuous_scale='Blues',
            title="💧 Water Quality Index by City",
            labels={'water_quality_index': 'Water Quality Index', 'city': 'City'}
        )
        fig1.update_layout(height=400)
        
        fig2 = px.histogram(
            df, x='water_quality_index',
            title="📊 Water Quality Distribution",
            color_discrete_sequence=['#3498db']
        )
        fig2.update_layout(height=300)
        
        return fig1, fig2
    
    return None, None

def main():
    # Initialize session state for refresh tracking
    if 'refresh_count' not in st.session_state:
        st.session_state.refresh_count = 0
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    st.markdown(
        '''
        <h1 class="main-header">
            <span style="font-size: 3rem;">🌍</span>
            <span class="gradient-text">Global Environmental Pulse</span>
        </h1>
        ''', 
        unsafe_allow_html=True
    )
    st.markdown("*Real-time environmental monitoring across Africa*")
    
    # Auto-refresh controls in sidebar
    with st.sidebar:
        st.header("🔄 Auto-Refresh Settings")
        
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        
        if auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh Interval",
                options=[5, 10, 30, 60, 120, 300, 600],
                format_func=lambda x: f"{x} seconds ({x//60} min)" if x >= 60 else f"{x} seconds",
                index=2  # Default to 120 seconds
            )
            
            st.markdown(
                f'<div class="refresh-indicator">🔄 Auto-refreshing every {refresh_interval}s</div>',
                unsafe_allow_html=True
            )
            
            # Display refresh stats
            # st.metric("Refresh Count", st.session_state.refresh_count)
            # st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            st.session_state.refresh_count += 1
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # Load data with progress indicator
    with st.spinner("🌍 Loading environmental data..."):
        data, data_source = load_latest_data()
    
    air_df = data.get('air', pd.DataFrame())
    fire_df = data.get('fire', pd.DataFrame())
    climate_df = data.get('climate', pd.DataFrame())
    economic_df = data.get('economic', pd.DataFrame())
    water_df = data.get('water', pd.DataFrame())

    if all(df.empty for df in [air_df, fire_df, climate_df, economic_df, water_df]):
        st.warning("⚠️ No data available. Run the data collection script first!")
        st.code("python src/data_ingestion.py")
        return

    with st.sidebar:
        st.header("📊 Dashboard Stats")
        
        if data_source == "database":
            st.markdown('<div class="data-source-badge db-badge">📊 PostgreSQL Database</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-source-badge csv-badge">📁 CSV Files (Fallback)</div>', unsafe_allow_html=True)
        
        if not air_df.empty:
            distinct_cities = air_df['city'].dropna().nunique()
            st.metric("🏙️ Cities Monitored", distinct_cities)
            worst_air = air_df.loc[air_df['aqi'].idxmax()]
            st.metric("⚠️ Worst AQI", f"{worst_air['city']}", delta=f"AQI: {worst_air['aqi']}")
            
        if not fire_df.empty:
            # Added a try/except to handle potential non-numeric data in sidebar metrics gracefully
            try:
                numeric_confidence = pd.to_numeric(fire_df['confidence'], errors='coerce').dropna()
                avg_confidence = numeric_confidence.mean() if not numeric_confidence.empty else 0
                distinct_fire_locations = (
                    fire_df[['latitude', 'longitude']]
                    .dropna()
                    .drop_duplicates()
                    .shape[0]
                )

                st.metric("🔥 Active Fires", distinct_fire_locations)
                st.metric("🎯 Avg Confidence", f"{avg_confidence:.1f}%", delta=None)
            except:
                st.metric("🔥 Active Fires", len(fire_df), delta=None)
                st.caption("Avg Confidence N/A")

        if not climate_df.empty:
            try:
                # Clean temperature column
                temp_col = climate_df['temperature_2m'].astype(str).str.replace('°C', '', regex=False)
                numeric_temp = pd.to_numeric(temp_col, errors='coerce').dropna()
                
                # Fill missing with mean (optional)
                numeric_temp = numeric_temp.fillna(numeric_temp.mean())
                
                avg_temp = numeric_temp.mean() if not numeric_temp.empty else 0
                st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C", delta=None)
            except Exception as e:
                st.caption("Avg Temperature N/A")

            
        st.markdown("---")
        st.markdown("### 🔄 Last Updated")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌬️ Air Quality", "🔥 Fire Alerts", "🌤️ Climate", 
        "💰 Economic", "💧 Water"
    ])

    with tab1:
        st.header("🌬️ Air Quality Analysis")
        
        if not air_df.empty:
            # The map here is now 3D interactive!
            air_map = create_air_quality_map(air_df)
            if air_map:
                st.plotly_chart(air_map, use_container_width=True)
            
            col1, col2 = st.columns(2)
            air_charts = create_air_quality_charts(air_df)
            
            if air_charts[0]:
                with col1:
                    st.plotly_chart(air_charts[0], use_container_width=True)
                with col2:
                    st.plotly_chart(air_charts[1], use_container_width=True)
                
                st.plotly_chart(air_charts[2], use_container_width=True)
            
            with st.expander("📋 View Raw Data"):
                st.dataframe(air_df[['city','aqi','pm2_5','pm10','timestamp']], use_container_width=True)
        else:
            st.warning("⚠️ No air quality data available")

    with tab2:
        st.header("🔥 Fire Alert Analysis")
        
        if not fire_df.empty:
            # The map here is now 3D interactive!
            fire_map = create_fire_map(fire_df)
            if fire_map:
                st.plotly_chart(fire_map, use_container_width=True)
            
            col1, col2 = st.columns(2)
            fire_charts = create_fire_charts(fire_df)
            
            if fire_charts[0] and fire_charts[1]:
                with col1:
                    st.plotly_chart(fire_charts[0], use_container_width=True)
                with col2:
                    st.plotly_chart(fire_charts[1], use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            # Ensure fire data metrics are safe if not numeric
            try:
                with col1:
                    distinct_fire_locations = (
                    fire_df[['latitude', 'longitude']]
                    .dropna()
                    .drop_duplicates()
                    .shape[0]
                    )
                    st.metric("🔥 Total Alerts", distinct_fire_locations)
                
                numeric_confidence = pd.to_numeric(fire_df['confidence'], errors='coerce').dropna()
                avg_confidence = numeric_confidence.mean() if not numeric_confidence.empty else 0
                with col2:
                    st.metric("🎯 Avg Confidence", f"{avg_confidence:.1f}%")

                numeric_frp = pd.to_numeric(fire_df['frp'], errors='coerce').dropna()
                avg_frp = numeric_frp.mean() if not numeric_frp.empty else 0
                with col3:
                    st.metric("⚡ Avg FRP", f"{avg_frp:.1f} MW")
            except Exception as e:
                st.error(f"Error displaying fire metrics: {e}")
                
            with st.expander("📋 View Raw Data"):
                st.dataframe(fire_df.head(100), use_container_width=True)
        else:
            st.warning("⚠️ No fire alert data available")

    with tab3:
        st.header("🌤️ Climate Analysis")
        
        if not climate_df.empty:
            # The map here is now 3D interactive!
            climate_map = create_climate_map(climate_df)
            if climate_map:
                st.plotly_chart(climate_map, use_container_width=True)
            
            climate_charts = create_climate_charts(climate_df)
            
            if climate_charts[0] and climate_charts[1]:
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(climate_charts[0], use_container_width=True)
                with col2:
                    st.plotly_chart(climate_charts[1], use_container_width=True)
                
                st.plotly_chart(climate_charts[2], use_container_width=True)
            
            with st.expander("📋 View Raw Data"):
                st.dataframe(climate_df[['city','temperature_2m','precipitation','solar_radiation','timestamp']], use_container_width=True)
        else:
            st.warning("⚠️ No climate data available")

    with tab4:
        st.header("💰 Economic Indicators")
        
        if not economic_df.empty:
            econ_charts = create_economic_charts(economic_df)
            
            if econ_charts[0]:
                st.plotly_chart(econ_charts[0], use_container_width=True)
            if econ_charts[1]:
                st.plotly_chart(econ_charts[1], use_container_width=True)
            
            with st.expander("📋 View Raw Data"):
                pivot_df = economic_df.pivot_table(
                    index=['country_name', 'year'],
                    columns='indicator_name',
                    values='value',
                    aggfunc='first'
                ).reset_index()
                st.dataframe(pivot_df, use_container_width=True)
        else:
            st.warning("⚠️ No economic data available")

    with tab5:
        st.header("💧 Water Quality Analysis")
        
        if not water_df.empty:
            water_charts = create_water_charts(water_df)
            
            if water_charts[0] and water_charts[1]:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.plotly_chart(water_charts[0], use_container_width=True)
                with col2:
                    st.plotly_chart(water_charts[1], use_container_width=True)
            
            with st.expander("📋 View Raw Data"):
                st.dataframe(water_df, use_container_width=True)
        else:
            st.warning("⚠️ No water quality data available")

    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #7f8c8d;'>"
        f"🌍 Global Environmental Pulse Dashboard | "
        f"Data Source: {'PostgreSQL Database' if data_source == 'database' else 'CSV Files'} | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    # Auto-refresh mechanism
    if auto_refresh:
        time.sleep(refresh_interval)
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = datetime.now()
        st.rerun()

if __name__ == "__main__":
    main()  