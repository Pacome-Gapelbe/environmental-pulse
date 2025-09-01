# src/data_ingestion.py
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from config.config import MONITORED_CITIES, RAW_DATA_PATH, NASA_FIRE_URL

load_dotenv()


class EnvironmentalDataCollector:
    def __init__(self):
        self.openweather_key = os.getenv("OPENWEATHER_API_KEY")

    def get_air_quality_data(self, cities):
        """
        Fetch air quality data for multiple African cities from OpenWeatherMap
        """
        air_quality_data = []

        for city in cities:
            try:
                
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={self.openweather_key}"
                geo_response = requests.get(geo_url)
                geo_data = geo_response.json()

                if geo_data:
                    lat = geo_data[0]["lat"]
                    lon = geo_data[0]["lon"]

                    # Get air quality data
                    aq_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.openweather_key}"
                    aq_response = requests.get(aq_url)
                    aq_data = aq_response.json()

                    # Parse the data
                    if "list" in aq_data and len(aq_data["list"]) > 0:
                        pollution_data = aq_data["list"][0]

                        record = {
                            "city": city,
                            "timestamp": datetime.now().isoformat(),
                            "lat": lat,
                            "lon": lon,
                            "aqi": pollution_data["main"]["aqi"],  
                            "co": pollution_data["components"]["co"],
                            "no": pollution_data["components"]["no"],
                            "no2": pollution_data["components"]["no2"],
                            "o3": pollution_data["components"]["o3"],
                            "so2": pollution_data["components"]["so2"],
                            "pm2_5": pollution_data["components"]["pm2_5"],
                            "pm10": pollution_data["components"]["pm10"],
                            "nh3": pollution_data["components"]["nh3"],
                        }
                        air_quality_data.append(record)
                        print(f"✅ Collected data for {city}")

            except Exception as e:
                print(f"❌ Error collecting data for {city}: {e}")

        return pd.DataFrame(air_quality_data)

    def get_nasa_fire_data(self):
        """
        Fetch current wildfire data from NASA FIRMS (Africa only)
        """
        try:
            fire_df = pd.read_csv(NASA_FIRE_URL)
            fire_df["timestamp"] = datetime.now().isoformat()


            recent_fires = fire_df[fire_df["confidence"] >= 75].copy()


            africa_fires = recent_fires[
                (recent_fires["latitude"] >= -35)
                & (recent_fires["latitude"] <= 37)
                & (recent_fires["longitude"] >= -20)
                & (recent_fires["longitude"] <= 52)
            ]

            africa_fires = africa_fires[
                ["latitude", "longitude", "confidence", "frp", "timestamp"]
            ].head(1000)

            print(f"✅ Collected {len(africa_fires)} African fire alerts")
            return africa_fires

        except Exception as e:
            print(f"❌ Error collecting fire data: {e}")
            return pd.DataFrame()


def main():
    collector = EnvironmentalDataCollector()

    print("🌍 Starting Environmental Data Collection...")

    # Collect air quality data
    print("\n📊 Collecting Air Quality Data...")
    air_quality_df = collector.get_air_quality_data(MONITORED_CITIES)

    # Collect fire data
    print("\n🔥 Collecting Fire Alert Data...")
    fire_df = collector.get_nasa_fire_data()

    # Save data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(RAW_DATA_PATH, exist_ok=True)

    if not air_quality_df.empty:
        air_quality_df.to_csv(
            f"{RAW_DATA_PATH}/air_quality_{timestamp}.csv", index=False
        )
        print(f"💾 Saved air quality data: {len(air_quality_df)} records")

    if not fire_df.empty:
        fire_df.to_csv(f"{RAW_DATA_PATH}/fires_{timestamp}.csv", index=False)
        print(f"💾 Saved fire data: {len(fire_df)} records")

    print("\n✅ Data collection complete!")
    return air_quality_df, fire_df


if __name__ == "__main__":
    main()
