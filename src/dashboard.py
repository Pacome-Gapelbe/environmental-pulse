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



current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)


for path in [current_dir, project_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import glob
import numpy as np


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
</style>
""", unsafe_allow_html=True)

def load_latest_data():
    """Load data from PostgreSQL database with CSV fallback"""
    data_files = {}
    data_source = "csv"  # Default to CSV
    

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
                    # Mark as fallback data
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

def create_air_quality_map(df):
    if df.empty:
        return None
    color_map = {1: 'green', 2: 'yellow', 3: 'orange', 4: 'red', 5: 'purple'}
    df['color'] = df['aqi'].map(color_map)
    
    fig = px.scatter_map(
        df, lat='lat', lon='lon', hover_name='city',
        hover_data={'aqi': True, 'pm2_5': True, 'pm10': True},
        color='aqi', color_continuous_scale=['green', 'yellow', 'orange', 'red', 'purple'],
        size_max=15, zoom=1, height=500,
        title="🌬️ Air Quality Index Across Cities"
    )
    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        title_font_size=20,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_air_quality_charts(df):
    """Create comprehensive air quality visualizations"""
    if df.empty:
        return None, None, None
    
    df_clean = df.copy()
    
    # Handle missing values
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
    
    # PM2.5 vs PM10 Scatter - ensure positive values
    df_clean['pm2_5'] = df_clean['pm2_5'].clip(lower=0.1)
    df_clean['pm10'] = df_clean['pm10'].clip(lower=0.1)
    df_clean['aqi_size'] = df_clean['aqi'].clip(lower=1)  # Ensure positive values for size
    
    fig2 = px.scatter(
        df_clean, x='pm2_5', y='pm10', 
        size='aqi_size', color='city',
        title="💨 PM2.5 vs PM10 Levels",
        labels={'pm2_5': 'PM2.5 (μg/m³)', 'pm10': 'PM10 (μg/m³)'}
    )
    fig2.update_layout(height=400)
    
    # AQI Distribution
    fig3 = px.histogram(
        df_clean, x='aqi', nbins=20,
        title="📊 AQI Distribution",
        color_discrete_sequence=['#3498db']
    )
    fig3.update_layout(height=300)
    
    return fig1, fig2, fig3

def create_fire_map(df):
    if df.empty:
        return None
    if len(df) > 500:
        df = df.sample(500)
    

    df_clean = df.copy()
    df_clean['confidence'] = pd.to_numeric(df_clean['confidence'], errors='coerce').fillna(50)
    df_clean['frp'] = pd.to_numeric(df_clean['frp'], errors='coerce').fillna(1)
    df_clean = df_clean.dropna(subset=['confidence', 'frp'])
    
    fig = px.scatter_map(
        df_clean, lat='latitude', lon='longitude',
        hover_data={'confidence': True, 'frp': True},
        color='confidence', color_continuous_scale='Reds',
        size='frp', size_max=10, zoom=1, height=500,
        title="🔥 Active Fire Alerts"
    )
    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        title_font_size=20
    )
    return fig

def create_fire_charts(df):
    """Create fire analytics charts"""
    if df.empty:
        return None, None
    
    # Create a clean copy
    df_clean = df.copy()
    
    # Clean numerical columns
    for col in ['confidence', 'frp']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
  
    df_clean = df_clean.dropna(subset=['confidence', 'frp'])
    

    df_clean['confidence'] = df_clean['confidence'].clip(0, 100)
    df_clean['frp'] = df_clean['frp'].clip(0.1, 1000)  # Ensure positive values
    
    if df_clean.empty:
        return None, None
    

    fig1 = px.histogram(
        df_clean, x='confidence', nbins=20,
        title="🎯 Fire Detection Confidence Distribution",
        color_discrete_sequence=['#e74c3c']
    )
    fig1.update_layout(height=300)
    
    fig2 = px.scatter(
        df_clean, x='confidence', y='frp',
        title="🔥 Fire Radiative Power vs Detection Confidence",
        labels={'frp': 'Fire Radiative Power (MW)', 'confidence': 'Detection Confidence (%)'}
    )
    fig2.update_layout(height=400)
    
    return fig1, fig2

def create_climate_map(df):
    """Create interactive map of climate data"""
    if df.empty:
        return None
    
    df_clean = df.copy()
    df_clean['precipitation'] = df_clean['precipitation'].fillna(0)
    df_clean['temperature_2m'] = df_clean['temperature_2m'].fillna(df_clean['temperature_2m'].mean())
    

    df_clean['precipitation_size'] = df_clean['precipitation'] + 0.1
    

    fig = px.scatter_map(
        df_clean,
        lat='lat',
        lon='lon',
        hover_name='city',
        hover_data={'temperature_2m': ':.1f', 'precipitation': ':.1f'},
        color='temperature_2m',
        color_continuous_scale='RdYlBu_r',
        size='precipitation_size',
        size_max=15,
        zoom=1,
        height=500,
        title="🌤️ Temperature and Precipitation"
    )
    
    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        title_font_size=20
    )
    
    return fig

def create_climate_charts(df):
    """Create climate visualization charts"""
    if df.empty:
        return None, None, None
    
 
    df_clean = df.copy()
    
    df_clean['temperature_2m'] = df_clean['temperature_2m'].fillna(df_clean['temperature_2m'].mean())
    df_clean['precipitation'] = df_clean['precipitation'].fillna(0)
    
    # Temperature bar chart
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
    
    # Precipitation chart
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
        # Fill NaN values with mean or 0, then ensure all values are positive
        df_clean['solar_radiation'] = df_clean['solar_radiation'].fillna(df_clean['solar_radiation'].mean())
        df_clean['solar_radiation'] = df_clean['solar_radiation'].clip(lower=0.1)  # Ensure positive values
        
        # Check if we have valid solar radiation data after cleaning
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
            # Fallback if no valid solar radiation data
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
        # Create scatter plot without size parameter if solar radiation data is missing
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
    """Create economic indicator visualizations"""
    if df.empty:
        return None, None
    
    # Pivot the data
    pivot_df = df.pivot_table(
        index=['country_name', 'year'],
        columns='indicator_name',
        values='value',
        aggfunc='first'
    ).reset_index()
    
    # GDP trend
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
    
    # Latest economic indicators by country
    latest_year = df['year'].max() if 'year' in df.columns else None
    if latest_year:
        latest_data = df[df['year'] == latest_year]
        fig2 = px.bar(
            latest_data, x='country_name', y='value', color='indicator_name',
            title=f"📊 Economic Indicators ({latest_year})",
            labels={'value': 'Indicator Value', 'country_name': 'Country'}
        )
        fig2.update_layout(height=400, xaxis_tickangle=-45)
    else:
        fig2 = None
    
    return fig1, fig2

def create_water_charts(df):
    """Create water quality visualizations"""
    if df.empty:
        return None, None
    
    if 'water_quality_index' in df.columns:
        # Water quality by city
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
        
        # Water quality distribution
        fig2 = px.histogram(
            df, x='water_quality_index',
            title="📊 Water Quality Distribution",
            color_discrete_sequence=['#3498db']
        )
        fig2.update_layout(height=300)
        
        return fig1, fig2
    
    return None, None

def main():

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
        
        # Data source badge
        if data_source == "database":
            st.markdown('<div class="data-source-badge db-badge">📊 PostgreSQL Database</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-source-badge csv-badge">📁 CSV Files (Fallback)</div>', unsafe_allow_html=True)
        
        if not air_df.empty:
            st.metric("🏙️ Cities Monitored", len(air_df), delta=None)
            worst_air = air_df.loc[air_df['aqi'].idxmax()]
            st.metric("⚠️ Worst AQI", f"{worst_air['city']}", delta=f"AQI: {worst_air['aqi']}")
            
        if not fire_df.empty:
            st.metric("🔥 Active Fires", len(fire_df), delta=None)
            avg_confidence = fire_df['confidence'].mean()
            st.metric("🎯 Avg Confidence", f"{avg_confidence:.1f}%", delta=None)
            
        if not climate_df.empty:
            avg_temp = climate_df['temperature_2m'].mean()
            st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C", delta=None)
            
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
            # Map
            air_map = create_air_quality_map(air_df)
            if air_map:
                st.plotly_chart(air_map, use_container_width=True)
            
            # Charts
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
            # Map
            fire_map = create_fire_map(fire_df)
            if fire_map:
                st.plotly_chart(fire_map, use_container_width=True)
            
            # Charts
            col1, col2 = st.columns(2)
            fire_charts = create_fire_charts(fire_df)
            
            if fire_charts[0] and fire_charts[1]:
                with col1:
                    st.plotly_chart(fire_charts[0], use_container_width=True)
                with col2:
                    st.plotly_chart(fire_charts[1], use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔥 Total Alerts", len(fire_df))
            with col2:
                st.metric("🎯 Avg Confidence", f"{fire_df['confidence'].mean():.1f}%")
            with col3:
                st.metric("⚡ Avg FRP", f"{fire_df['frp'].mean():.1f} MW")
                
            with st.expander("📋 View Raw Data"):
                st.dataframe(fire_df.head(100), use_container_width=True)
        else:
            st.warning("⚠️ No fire alert data available")

    with tab3:
        st.header("🌤️ Climate Analysis")
        
        if not climate_df.empty:
            # Map
            climate_map = create_climate_map(climate_df)
            if climate_map:
                st.plotly_chart(climate_map, use_container_width=True)
            
            # Charts
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

    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #7f8c8d;'>"
        f"🌍 Global Environmental Pulse Dashboard | "
        f"Data Source: {'PostgreSQL Database' if data_source == 'database' else 'CSV Files'} | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()