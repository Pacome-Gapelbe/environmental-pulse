import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import sys  


sys.path.insert(0, "/app")

from dotenv import load_dotenv
from config.config import (
    MONITORED_CITIES, RAW_DATA_PATH, NASA_FIRE_URL,
    NASA_POWER_URL, NASA_POWER_PARAMS, AFRICAN_COUNTRIES,
    WORLD_BANK_API_URL, WORLD_BANK_INDICATORS, DB_CONFIG
)
from src.database import DatabaseManager

load_dotenv()


class EnvironmentalDataCollector:
    def __init__(self):
        self.openweather_key = os.getenv("OPENWEATHER_API_KEY")  
        self.gfw_api_key = os.getenv("GFW_API_KEY", "") 
        self.db_manager = DatabaseManager()  

    def get_air_quality_data(self, cities):
        """Fetch air quality data from OpenWeather for African cities"""
        air_quality_data = []

        for city in cities:
            try:
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={self.openweather_key}"
                geo_response = requests.get(geo_url)
                geo_data = geo_response.json()

                if geo_data:
                    lat = geo_data[0]["lat"]
                    lon = geo_data[0]["lon"]

                    aq_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.openweather_key}"
                    aq_response = requests.get(aq_url)
                    aq_data = aq_response.json()

                    if "list" in aq_data and len(aq_data["list"]) > 0:
                        pollution = aq_data["list"][0]
                        record = {
                            "city": city,
                            "timestamp": datetime.now().isoformat(),
                            "lat": lat,
                            "lon": lon,
                            "aqi": pollution["main"]["aqi"],
                            "co": pollution["components"]["co"],
                            "no": pollution["components"]["no"],
                            "no2": pollution["components"]["no2"],
                            "o3": pollution["components"]["o3"],
                            "so2": pollution["components"]["so2"],
                            "pm2_5": pollution["components"]["pm2_5"],
                            "pm10": pollution["components"]["pm10"],
                            "nh3": pollution["components"]["nh3"],
                        }
                        air_quality_data.append(record)
                        print(f"✅ Collected air quality for {city}")

            except Exception as e:
                print(f"❌ Error collecting air quality for {city}: {e}")

        return pd.DataFrame(air_quality_data)

    def get_nasa_fire_data(self):
        """Fetch high-confidence fires from NASA FIRMS (Africa only)"""
        try:
            fire_df = pd.read_csv(NASA_FIRE_URL)
            fire_df["timestamp"] = datetime.now().isoformat()
            fire_df = fire_df[fire_df["confidence"] >= 75]
            
            
            fire_df = fire_df.rename(columns={
                "latitude": "latitude",
                "longitude": "longitude",
                "confidence": "confidence",
                "frp": "frp"
            })
            
            africa_fires = fire_df[
                (fire_df["latitude"] >= -35) & (fire_df["latitude"] <= 37) &
                (fire_df["longitude"] >= -20) & (fire_df["longitude"] <= 52)
            ][["latitude", "longitude", "confidence", "frp", "timestamp"]].head(1000)
            
            print(f"✅ Collected {len(africa_fires)} African fire alerts")
            return africa_fires

        except Exception as e:
            print(f"❌ Error collecting fire data: {e}")
            return pd.DataFrame()

    def get_climate_data(self, cities):
        """Fetch climate data from NASA POWER API"""
        climate_data = []

        for city in cities:
            try:
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={self.openweather_key}"
                geo_response = requests.get(geo_url)
                geo_data = geo_response.json()

                if geo_data:
                    lat = geo_data[0]["lat"]
                    lon = geo_data[0]["lon"]

                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    start_str = start_date.strftime("%Y%m%d")
                    end_str = end_date.strftime("%Y%m%d")

                    api_url = (
                        f"{NASA_POWER_URL}?parameters={NASA_POWER_PARAMS['parameters']}"
                        f"&start={start_str}&end={end_str}"
                        f"&latitude={lat}&longitude={lon}"
                        f"&community={NASA_POWER_PARAMS['community']}"
                        f"&format={NASA_POWER_PARAMS['format']}"
                    )

                    response = requests.get(api_url)
                    data = response.json()

                    if "properties" in data:
                        latest_data = {}
                        for param in ['T2M', 'PRECTOT', 'ALLSKY_SFC_SW_DWN']:
                            if param in data["properties"]:
                                param_values = data["properties"][param]
                                latest_data[param] = list(param_values.values())[-1] if param_values else None

                        record = {
                            "city": city,
                            "lat": lat,
                            "lon": lon,
                            "timestamp": datetime.now().isoformat(),
                            "temperature_2m": latest_data.get('T2M'),
                            "precipitation": latest_data.get('PRECTOT'),
                            "solar_radiation": latest_data.get('ALLSKY_SFC_SW_DWN')
                        }
                        climate_data.append(record)
                        print(f"✅ Collected climate data for {city}")

            except Exception as e:
                print(f"❌ Error collecting climate data for {city}: {e}")

        return pd.DataFrame(climate_data)

    def get_economic_data(self):
        """Fetch economic indicators from World Bank for African countries"""
        economic_data = []

        try:
            for country_code, country_name in AFRICAN_COUNTRIES.items():
                for indicator_code, indicator_name in WORLD_BANK_INDICATORS.items():
                    api_url = f"{WORLD_BANK_API_URL}/{country_code}/indicator/{indicator_code}?format=json"
                    response = requests.get(api_url)
                    data = response.json()

                    if len(data) > 1 and data[1]:
                        for item in data[1]:
                            if item['value'] is not None:
                                record = {
                                    "country_code": country_code,
                                    "country_name": country_name,
                                    "indicator_code": indicator_code,
                                    "indicator_name": indicator_name,
                                    "value": item['value'],
                                    "year": item['date'],
                                    "timestamp": datetime.now().isoformat()
                                }
                                economic_data.append(record)
                                break  

            print(f"✅ Collected economic data for {len(economic_data)} records")

        except Exception as e:
            print(f"❌ Error collecting economic data: {e}")

        return pd.DataFrame(economic_data)

    def get_water_quality_data(self):
        """Simulated water quality data for demonstration"""
        water_data = []

        for city in MONITORED_CITIES[:5]:  
            try:
                record = {
                    "city": city,
                    "timestamp": datetime.now().isoformat(),
                    "ph": round(6.0 + (3.0 * (hash(city) % 100) / 100), 1),
                    "turbidity": round((hash(city) % 50) / 10, 1),
                    "dissolved_oxygen": round(5 + (3 * (hash(city) % 100) / 100), 1),
                    "water_quality_index": 70 + (hash(city) % 30)
                }
                water_data.append(record)
                print(f"✅ Collected simulated water quality for {city}")
            except Exception as e:
                print(f"❌ Error with water quality data for {city}: {e}")

        return pd.DataFrame(water_data)

    def save_all_data_to_db(self, air_df, fire_df, climate_df, economic_df, water_df):
        """Save all collected data to PostgreSQL database"""
        try:
            if not air_df.empty:
                self.db_manager.insert_air_quality_data(air_df)
            
            if not fire_df.empty:
                self.db_manager.insert_fire_data(fire_df)
            
            if not climate_df.empty:
                self.db_manager.insert_climate_data(climate_df)
            
            if not economic_df.empty:
                self.db_manager.insert_economic_data(economic_df)
            
            if not water_df.empty:
                self.db_manager.insert_water_quality_data(water_df)
                
            print("✅ All data successfully saved to PostgreSQL database")
            
        except Exception as e:
            print(f"❌ Error saving data to database: {e}")
            # Re-raise the exception to handle it in the main function
            raise

    def close_db_connection(self):
        """Close the database connection"""
        self.db_manager.close()


def save_data_to_csv(air_df, fire_df, climate_df, economic_df, water_df):
    """Save data to CSV files for backward compatibility"""
    os.makedirs(RAW_DATA_PATH, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not air_df.empty:
        air_df.to_csv(f"{RAW_DATA_PATH}/air_quality_{timestamp}.csv", index=False)
        print(f"💾 Saved air quality data to CSV: {len(air_df)} records")
    
    if not fire_df.empty:
        fire_df.to_csv(f"{RAW_DATA_PATH}/fires_{timestamp}.csv", index=False)
        print(f"💾 Saved fire data to CSV: {len(fire_df)} records")
    
    if not climate_df.empty:
        climate_df.to_csv(f"{RAW_DATA_PATH}/climate_{timestamp}.csv", index=False)
        print(f"💾 Saved climate data to CSV: {len(climate_df)} records")
    
    if not economic_df.empty:
        economic_df.to_csv(f"{RAW_DATA_PATH}/economic_{timestamp}.csv", index=False)
        print(f"💾 Saved economic data to CSV: {len(economic_df)} records")
    
    if not water_df.empty:
        water_df.to_csv(f"{RAW_DATA_PATH}/water_{timestamp}.csv", index=False)
        print(f"💾 Saved water quality data to CSV: {len(water_df)} records")


def main():
    collector = EnvironmentalDataCollector()
    print("🌍 Starting Environmental Data Collection...")

    try:
        air_quality_df = collector.get_air_quality_data(MONITORED_CITIES)
        fire_df = collector.get_nasa_fire_data()
        climate_df = collector.get_climate_data(MONITORED_CITIES)
        economic_df = collector.get_economic_data()
        water_df = collector.get_water_quality_data()

        collector.save_all_data_to_db(air_quality_df, fire_df, climate_df, economic_df, water_df)

        save_data_to_csv(air_quality_df, fire_df, climate_df, economic_df, water_df)

        print("\n✅ Data collection and storage complete!")
        print("📊 Data Summary:")
        print(f"   Air Quality Records: {len(air_quality_df)}")
        print(f"   Fire Alert Records: {len(fire_df)}")
        print(f"   Climate Records: {len(climate_df)}")
        print(f"   Economic Records: {len(economic_df)}")
        print(f"   Water Quality Records: {len(water_df)}")

    except Exception as e:
        try:
            save_data_to_csv(air_quality_df, fire_df, climate_df, economic_df, water_df)
            print("💾 Data saved to CSV as fallback")
        except Exception as csv_error:
            print(f"❌ CSV fallback also failed: {csv_error}")

    finally:
        collector.close_db_connection()
    return air_quality_df, fire_df, climate_df, economic_df, water_df


if __name__ == "__main__":
    main()