# 🌍 Global Environmental Pulse Platform

A real-time environmental monitoring system that aggregates air quality data, wildfire alerts, climate data, economic indicators, and water quality information across Africa, providing comprehensive environmental insights through an interactive dashboard.

![alt text](/images/image-1.png)

![alt text](/images/image-2.png)

![alt text](/images/image-3.png)

## 🚀 Project Overview

This data engineering project demonstrates:
- **Real-time data ingestion** from multiple environmental APIs
- **Data processing and transformation** of heterogeneous environmental datasets
- **Interactive visualization** with geographic mapping and analytics
- **Automated data pipeline** architecture
- **African-focused environmental monitoring** covering multiple cities and regions

### Why This Project Matters
This platform creates a **comprehensive environmental monitoring system** that combines multiple data sources to provide holistic environmental insights for African cities, enabling better decision-making and awareness.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │ -> │  Data Pipeline   │ -> │   Dashboard     │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ OpenWeatherMap  │    │ data_ingestion.py│    │ Streamlit UI    │
│ NASA FIRMS      │    │ data_processing  │    │ Plotly Maps     │
│ Climate APIs    │    │ Error Handling   │    │ Real-time Stats │
│ Economic Data   │    │ Data Validation  │    │ Multi-tab       │
│ Water Quality   │    │                  │    │ Visualization   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Features

### Current Implementation
- ✅ **Multi-source data ingestion**: Air quality, fire alerts, climate data, economic indicators, and water quality
- ✅ **Geographic focus**: African cities and regions
- ✅ **Interactive maps**: Real-time environmental data visualization
- ✅ **Automated data collection**: Programmatic API calls with error handling
- ✅ **Data persistence**: CSV-based data storage with timestamps

### Dashboard Components
1. **Air Quality Monitor**: Global AQI mapping with PM2.5, PM10, and pollutant breakdowns
2. **Fire Alert System**: NASA satellite fire detection with confidence ratings
3. **Climate Analysis**: Temperature and precipitation monitoring across cities
4. **Economic Indicators**: GDP and economic trends visualization
5. **Water Quality**: Water quality index tracking and analysis

## 🛠️ Tech Stack

**Data Pipeline:**
- **Python 3.9+**: Core processing language
- **Pandas**: Data manipulation and analysis
- **Requests**: API data retrieval
- **python-dotenv**: Environment variable management

**Visualization:**
- **Streamlit**: Web application framework
- **Plotly**: Interactive maps and charts
- **Plotly Express**: Simplified plotting interface

**Data Sources:**
- **OpenWeatherMap API**: Air quality data
- **NASA FIRMS**: Real-time satellite fire detection data
- **Climate Data APIs**: Temperature and precipitation data
- **Economic Data Sources**: GDP and economic indicators
- **Water Quality APIs**: Water quality measurements

## 📦 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Required API keys for data sources

### 1. Clone and Setup
```bash
git clone https://github.com/Pacome-Gapelbe/environmental-pulse.git
cd environmental-pulse
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory with your API keys:
```
OPENWEATHER_API_KEY=your_api_key_here
NASA_FIRMS_API_KEY=your_api_key_here
# Add other API keys as needed
```

### 3. Create Directory Structure
```bash
mkdir -p data/raw data/processed
```

### 4. Run Data Collection
```bash
python src/data_ingestion.py
```

### 5. Launch Dashboard
```bash
streamlit run src/dashboard.py
```

## 🗂️ Project Structure

```
environmental-pulse/
├── data/
│   ├── raw/                     # Raw API data (CSV files)
│   └── processed/               # Cleaned, transformed data
├── src/
│   ├── data_ingestion.py        # API data collection pipeline
│   ├── data_processing.py       # Data cleaning & transformation
│   └── dashboard.py             # Streamlit dashboard application
├── config/
│   └── config.py                # Configuration settings
├── .env                         # Environment variables (API keys)
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## 📊 Data Pipeline Details

### Data Sources
1. **Air Quality Data**
   - Sources: OpenWeatherMap and other air quality APIs
   - Data: AQI, PM2.5, PM10, and other pollutants
   - Coverage: Multiple African cities

2. **Fire Alert Data**
   - Source: NASA FIRMS and other fire detection systems
   - Data: Fire coordinates, confidence levels, radiative power
   - Coverage: African regions

3. **Climate Data**
   - Sources: Various climate APIs
   - Data: Temperature, precipitation, solar radiation
   - Coverage: Multiple cities

4. **Economic Data**
   - Sources: World Bank, IMF, and other economic databases
   - Data: GDP, economic indicators, development metrics
   - Coverage: African countries

5. **Water Quality Data**
   - Sources: Water quality monitoring APIs and databases
   - Data: Water quality indices, contamination levels
   - Coverage: African cities and regions

### Data Processing
- **Geographic filtering**: Africa-focused data extraction
- **Quality filtering**: Data validation and error handling
- **Data validation**: Error handling for API failures
- **Timestamp management**: ISO format timestamps for all data

## 🚀 Usage Examples

### Manual Data Collection
```python
from src.data_ingestion import EnvironmentalDataCollector

collector = EnvironmentalDataCollector()
air_data = collector.get_air_quality_data(cities)
fire_data = collector.get_fire_data()
climate_data = collector.get_climate_data()
economic_data = collector.get_economic_data()
water_data = collector.get_water_quality_data()
```

### Dashboard Navigation
1. **🌬️ Air Quality Tab**: Interactive map + city rankings + pollutant details
2. **🔥 Fire Alerts Tab**: Real-time fire locations + statistics + confidence levels
3. **🌤️ Climate Tab**: Temperature and precipitation monitoring + trends
4. **💰 Economic Tab**: GDP and economic indicators visualization
5. **💧 Water Tab**: Water quality indices and analysis

## 📈 Future Enhancements (Roadmap)

### Phase 2: Advanced Data Engineering
- [ ] **Apache Airflow**: Automated scheduling and workflow management
- [ ] **Apache Kafka**: Real-time streaming data pipeline
- [ ] **DuckDB/PostgreSQL**: Proper database implementation
- [ ] **Data quality monitoring**: Automated data validation and alerting

### Phase 3: Additional Data Sources
- [ ] **Satellite imagery**: Land use change detection
- [ ] **Seismic data**: USGS earthquake monitoring
- [ ] **Biodiversity data**: Wildlife and ecosystem monitoring
- [ ] **Social indicators**: Population health and wellbeing metrics

### Phase 4: Production Deployment
- [ ] **Cloud deployment**: AWS/GCP free tier hosting
- [ ] **RESTful API**: Public API endpoints for data access
- [ ] **Docker containerization**: Portable deployment
- [ ] **CI/CD pipeline**: Automated testing and deployment

## 🤝 Contributing

This is a portfolio project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Pacome License.

## 🙏 Acknowledgments

- **OpenWeatherMap**: Air quality data API
- **NASA FIRMS**: Fire Information for Resource Management System
- **Streamlit**: Open-source app framework
- **Plotly**: Interactive visualization library
- **Various data providers**: For climate, economic, and water quality data

## 📞 Contact

**Your Name** - [gapelbep@gmail.com]   
**LinkedIn**: [www.linkedin.com/in/pacome-gapelbe-86516137b]  

---