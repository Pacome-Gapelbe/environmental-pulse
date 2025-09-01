# src/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import glob
import os

# Streamlit page configuration
st.set_page_config(
    page_title="🌍 Global Environmental Pulse", 
    page_icon="🌍",
    layout="wide"
)

def load_latest_data():
    """Load the most recent data files"""
    try:
        
        air_files = glob.glob('data/raw/air_quality_*.csv')
        if air_files:
            latest_air_file = max(air_files, key=os.path.getctime)
            air_df = pd.read_csv(latest_air_file)
        else:
            air_df = pd.DataFrame()
        
      
        fire_files = glob.glob('data/raw/fires_*.csv')
        if fire_files:
            latest_fire_file = max(fire_files, key=os.path.getctime)
            fire_df = pd.read_csv(latest_fire_file)
        else:
            fire_df = pd.DataFrame()
            
        return air_df, fire_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

def create_air_quality_map(df):
    """Create interactive map of air quality"""
    if df.empty:
        return None
        
    # Create color mapping for AQI levels
    color_map = {1: 'green', 2: 'yellow', 3: 'orange', 4: 'red', 5: 'purple'}
    df['color'] = df['aqi'].map(color_map)
    
    fig = px.scatter_mapbox(
        df,
        lat='lat',
        lon='lon',
        hover_name='city',
        hover_data={'aqi': True, 'pm2_5': True, 'pm10': True},
        color='aqi',
        color_continuous_scale=['green', 'yellow', 'orange', 'red', 'purple'],
        size_max=15,
        zoom=1,
        height=500
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    return fig

def create_fire_map(df):
    """Create interactive map of fire alerts"""
    if df.empty:
        return None
        
    
    if len(df) > 500:
        df = df.sample(500)
    
    fig = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        hover_data={'confidence': True, 'frp': True},
        color='confidence',
        color_continuous_scale='Reds',
        size='frp',
        size_max=10,
        zoom=1,
        height=500
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    return fig

def calculate_environmental_score(air_df):
    """Calculate simple environmental health score"""
    if air_df.empty:
        return None
        
  
    air_df['env_score'] = (6 - air_df['aqi']) * 20
    
    return air_df[['city', 'aqi', 'pm2_5', 'env_score']].sort_values('env_score', ascending=False)

# Main Dashboard
def main():
    st.title("🌍 Global Environmental Pulse")
    st.markdown("*Real-time environmental monitoring across the globe*")
    
    # Load data
    air_df, fire_df = load_latest_data()
    
    if air_df.empty and fire_df.empty:
        st.warning("No data available. Please run the data collection script first!")
        st.code("python src/data_ingestion.py")
        return
    
    # Sidebar with stats
    st.sidebar.header("📊 Current Statistics")
    
    if not air_df.empty:
        st.sidebar.metric("Cities Monitored", len(air_df))
        worst_air = air_df.loc[air_df['aqi'].idxmax()]
        st.sidebar.metric("Worst Air Quality", f"{worst_air['city']} (AQI: {worst_air['aqi']})")
    
    if not fire_df.empty:
        st.sidebar.metric("Active Fire Alerts", len(fire_df))
        avg_confidence = fire_df['confidence'].mean()
        st.sidebar.metric("Avg Fire Confidence", f"{avg_confidence:.1f}%")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🌬️ Air Quality", "🔥 Fire Alerts", "📈 Environmental Score"])
    
    with tab1:
        st.header("Global Air Quality Monitor")
        
        if not air_df.empty:
            # Show map
            air_map = create_air_quality_map(air_df)
            if air_map:
                st.plotly_chart(air_map, use_container_width=True)
            
            # Show data table
            st.subheader("Current Readings")
            display_df = air_df[['city', 'aqi', 'pm2_5', 'pm10', 'timestamp']].copy()
            st.dataframe(display_df, use_container_width=True)
            
            # AQI explanation
            st.info("""
            **Air Quality Index (AQI) Scale:**
            - 1: Good (Green)
            - 2: Fair (Yellow) 
            - 3: Moderate (Orange)
            - 4: Poor (Red)
            - 5: Very Poor (Purple)
            """)
        else:
            st.warning("No air quality data available")
    
    with tab2:
        st.header("Global Fire Alert System")
        
        if not fire_df.empty:
            # Show map
            fire_map = create_fire_map(fire_df)
            if fire_map:
                st.plotly_chart(fire_map, use_container_width=True)
            
            # Fire statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Alerts", len(fire_df))
            with col2:
                high_conf = len(fire_df[fire_df['confidence'] >= 90])
                st.metric("High Confidence", high_conf)
            with col3:
                avg_power = fire_df['frp'].mean() if 'frp' in fire_df.columns else 0
                st.metric("Avg Fire Power", f"{avg_power:.1f} MW")
                
        else:
            st.warning("No fire alert data available")
    
    with tab3:
        st.header("Environmental Health Score")
        
        if not air_df.empty:
            scores_df = calculate_environmental_score(air_df)
            
            if scores_df is not None:
                # Show top and bottom cities
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🏆 Best Air Quality")
                    top_5 = scores_df.head(5)
                    for _, row in top_5.iterrows():
                        st.success(f"{row['city']}: {row['env_score']:.0f}/100")
                
                with col2:
                    st.subheader("⚠️ Needs Attention") 
                    bottom_5 = scores_df.tail(5)
                    for _, row in bottom_5.iterrows():
                        st.error(f"{row['city']}: {row['env_score']:.0f}/100")
                
                # Bar chart of scores
                fig = px.bar(
                    scores_df,
                    x='city',
                    y='env_score',
                    title="Environmental Health Scores by City",
                    color='env_score',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No air quality data for scoring")
    
    # Footer
    st.markdown("---")
    st.markdown("*Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")

if __name__ == "__main__":
    main()