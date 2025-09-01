# 🌍 Global Environmental Pulse Platform

A real-time environmental monitoring system that aggregates air quality data and wildfire alerts across Africa, providing unified environmental health insights through an interactive dashboard.

![alt text](/images/image-1.png)

![alt text](/images/image-2.png)

![alt text](/images/image-3.png)


## 🚀 Project Overview

This data engineering project demonstrates:
- **Real-time data ingestion** from multiple environmental APIs
- **Data processing and transformation** of heterogeneous environmental datasets
- **Interactive visualization** with geographic mapping and analytics
- **Automated data pipeline** architecture
- **African-focused environmental monitoring** covering 18+ major cities

### Why This Project Matters
Most environmental dashboards focus on individual metrics (air quality OR fires OR weather). This platform creates a **unified environmental health index** that combines multiple data sources to provide comprehensive environmental insights for African cities.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │ -> │  Data Pipeline   │ -> │   Dashboard     │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ OpenWeatherMap  │    │ data_ingestion.py│    │ Streamlit UI    │
│ NASA FIRMS      │    │ data_processing  │    │ Plotly Maps     │
│ (Future: EPA,   │    │ Error Handling   │    │ Real-time Stats │
│  WHO, etc.)     │    │ Data Validation  │    │ Environmental   │
└─────────────────┘    └──────────────────┘    │ Health Score    │
                                               └─────────────────┘
```

## 📋 Features

### Current Implementation
- ✅ **Multi-source data ingestion**: Air quality (OpenWeatherMap) + Fire alerts (NASA FIRMS)
- ✅ **Geographic focus**: 18 African cities from Nigeria to South Africa
- ✅ **Interactive maps**: Real-time air quality and fire alert visualization
- ✅ **Environmental scoring**: Custom algorithm ranking cities by environmental health
- ✅ **Automated data collection**: Programmatic API calls with error handling
- ✅ **Data persistence**: CSV-based data storage with timestamps

### Dashboard Components
1. **Air Quality Monitor**: Global AQI mapping with PM2.5, PM10, and pollutant breakdowns
2. **Fire Alert System**: NASA satellite fire detection with confidence ratings
3. **Environmental Health Score**: Composite scoring system ranking cities (0-100 scale)

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
- **OpenWeatherMap API**: Air quality data for 18 African cities
- **NASA FIRMS**: Real-time satellite fire detection data

## 📦 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- OpenWeatherMap API key (free tier: 1000 calls/day)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd environmental-pulse
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```
OPENWEATHER_API_KEY=your_api_key_here
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
1. **OpenWeatherMap Air Pollution API**
   - Endpoint: Air Pollution Current Data
   - Coverage: 18 African cities
   - Refresh: Every 30 minutes
   - Data: AQI, PM2.5, PM10, CO, NO₂, O₃, SO₂, NH₃

2. **NASA FIRMS Fire Data**
   - Source: MODIS satellite fire detection
   - Coverage: Africa (lat: -35 to 37, lon: -20 to 52)
   - Refresh: Every 60 minutes
   - Data: Fire coordinates, confidence, radiative power

### Data Processing
- **Geographic filtering**: Africa-focused fire data extraction
- **Quality filtering**: High-confidence fire alerts (≥75% confidence)
- **Data validation**: Error handling for API failures
- **Timestamp management**: ISO format timestamps for all data

### Environmental Health Score Algorithm
```python
# Simple scoring: AQI inverse scale (1=excellent, 5=hazardous)
env_score = (6 - aqi) * 20  # Converts to 0-100 scale
```

## 🚀 Usage Examples

### Manual Data Collection
```python
from src.data_ingestion import EnvironmentalDataCollector

collector = EnvironmentalDataCollector()
air_data, fire_data = collector.get_air_quality_data(cities), collector.get_nasa_fire_data()
```

### Dashboard Navigation
1. **🌬️ Air Quality Tab**: Interactive map + city rankings + pollutant details
2. **🔥 Fire Alerts Tab**: Real-time fire locations + statistics + confidence levels
3. **📈 Environmental Score Tab**: City rankings + composite health scores

## 📈 Future Enhancements (Roadmap)

### Phase 2: Advanced Data Engineering
- [ ] **Apache Airflow**: Automated scheduling and workflow management
- [ ] **Apache Kafka**: Real-time streaming data pipeline
- [ ] **DuckDB/PostgreSQL**: Proper database implementation
- [ ] **Data quality monitoring**: Automated data validation and alerting

### Phase 3: Additional Data Sources
- [ ] **Water quality**: WHO/EPA water monitoring APIs
- [ ] **Weather integration**: Temperature, humidity, precipitation
- [ ] **Satellite imagery**: Land use change detection
- [ ] **Seismic data**: USGS earthquake monitoring

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

This project is licensed under the Pacome License .

## 🙏 Acknowledgments

- **OpenWeatherMap**: Air quality data API
- **NASA FIRMS**: Fire Information for Resource Management System
- **Streamlit**: Open-source app framework
- **Plotly**: Interactive visualization library

## 📞 Contact

**Your Name** - [gapelbep@gmail.com]   
**LinkedIn**: [www.linkedin.com/in/pacome-gapelbe-86516137b]  

---

