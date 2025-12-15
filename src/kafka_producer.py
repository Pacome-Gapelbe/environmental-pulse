#!/usr/bin/env python3
"""
Kafka producer for air quality (OpenWeatherMap) and fire alerts.
- Polls OpenWeatherMap Air Pollution API for configured cities.
- For fire alerts, tries to fetch from FIRE_API_URL (if provided), otherwise simulates events.
Sends JSON events to Kafka topics: air_quality and fire_alerts.

Requires:
  pip install kafka-python requests python-dotenv
Configure via .env (see .env.example)
"""

import os
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kafka_producer")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
AIR_TOPIC = os.getenv("KAFKA_TOPIC_AIR", "air_quality")
FIRE_TOPIC = os.getenv("KAFKA_TOPIC_FIRE", "fire_alerts")

OWM_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
# Example cities list with lat/lon. Update or load from config.
# CITIES = json.loads(os.getenv("CITIES_JSON", '[{"name":"Lagos","lat":6.5244,"lon":3.3792},{"name":"Nairobi","lat":-1.2921,"lon":36.8219},{"name":"Accra","lat":5.6037,"lon":-0.1870}]'))
# # Example cities list with lat/lon (African cities)
CITIES = [
    {"name": "Lagos", "lat": 6.5244, "lon": 3.3792},
    {"name": "Abuja", "lat": 9.0579, "lon": 7.4951},
    {"name": "Port Harcourt", "lat": 4.8156, "lon": 7.0498},
    {"name": "Accra", "lat": 5.6037, "lon": -0.1870},
    {"name": "Kumasi", "lat": 6.6885, "lon": -1.6244},
    {"name": "Lomé", "lat": 6.1725, "lon": 1.2314},
    {"name": "Yaoundé", "lat": 3.8480, "lon": 11.5021},
    {"name": "Douala", "lat": 4.0511, "lon": 9.7679},
    {"name": "N'Djamena", "lat": 12.1348, "lon": 15.0557},
    {"name": "Kinshasa", "lat": -4.4419, "lon": 15.2663},
    {"name": "Lubumbashi", "lat": -11.6879, "lon": 27.4682},
    {"name": "Goma", "lat": -1.6819, "lon": 29.2200},
    {"name": "Kigali", "lat": -1.9706, "lon": 30.1044},
    {"name": "Nairobi", "lat": -1.2921, "lon": 36.8219},
    {"name": "Addis Ababa", "lat": 9.0304, "lon": 38.7400},
    {"name": "Cape Town", "lat": -33.9249, "lon": 18.4241},
    {"name": "Johannesburg", "lat": -26.2041, "lon": 28.0473},
    {"name": "Dakar", "lat": 14.6928, "lon": -17.4467},
    {"name": "Cairo", "lat": 30.0444, "lon": 31.2357}
]


FIRE_API_URL = os.getenv("FIRE_API_URL", "")  # optional: your NASA FIRMS or other fire feed URL
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))

producer = KafkaProducer(
    bootstrap_servers=[s.strip() for s in KAFKA_BOOTSTRAP.split(",")],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
)

def make_event(source: str, city: Optional[str], payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "event_id": str(uuid.uuid4()),
        "source": source,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "city": city,
        "payload": payload,
    }

def fetch_air_quality_for_city(city: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not OWM_API_KEY:
        logger.warning("OPENWEATHER_API_KEY not set — skipping real API call for air quality")
        return None
    lat = city["lat"]
    lon = city["lon"]
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OWM_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        logger.exception("Failed to fetch OWM air pollution: %s", e)
        return None

def fetch_fire_alerts() -> List[Dict[str, Any]]:
    """
    Try to fetch fire alerts from FIRE_API_URL if provided.
    If not provided, we simulate a small random event for demo.
    """
    if FIRE_API_URL:
        try:
            resp = requests.get(FIRE_API_URL, timeout=15)
            resp.raise_for_status()
            # Assume JSON/GeoJSON or CSV. We'll try to parse JSON features if present.
            content_type = resp.headers.get("Content-Type", "")
            if "json" in content_type:
                j = resp.json()
                # If GeoJSON features
                if isinstance(j, dict) and "features" in j:
                    return j["features"]
                # If it's a list of records
                if isinstance(j, list):
                    return j
                # Unknown JSON shape
                return [{"raw": j}]
            else:
                # Non-JSON content — return raw text as single event
                return [{"raw_text": resp.text}]
        except Exception as e:
            logger.exception("Failed to fetch fire alerts from FIRE_API_URL: %s", e)
            return []
    # Simulated event for demo
    logger.info("No FIRE_API_URL provided — generating simulated fire event")
    sample = {
        "properties": {"confidence": 75, "brightness": 300.2},
        "geometry": {"coordinates": [3.3792, 6.5244]},  # lon, lat
        "id": str(uuid.uuid4()),
        "source": "simulated",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    return [sample]

def send_air_event(city_name: str, payload: Dict[str, Any]):
    event = make_event("openweathermap", city_name, payload)
    producer.send(AIR_TOPIC, value=event)
    producer.flush()
    logger.info("Sent air event for %s to %s", city_name, AIR_TOPIC)

def send_fire_event(fire_record: Dict[str, Any]):
    # extract coords if feature-like
    lat = None
    lon = None
    properties = {}
    if "geometry" in fire_record and "coordinates" in fire_record["geometry"]:
        coords = fire_record["geometry"]["coordinates"]
        # GeoJSON: [lon, lat]
        lon, lat = coords[0], coords[1]
    if "properties" in fire_record:
        properties = fire_record["properties"]
    event_payload = {
        "raw": fire_record,
        "latitude": lat,
        "longitude": lon,
        "properties": properties,
    }
    event = make_event(fire_record.get("source", "nasa_firms"), None, event_payload)
    producer.send(FIRE_TOPIC, value=event)
    producer.flush()
    logger.info("Sent fire event to %s (lat=%s lon=%s)", FIRE_TOPIC, lat, lon)

def run_loop():
    logger.info("Starting producer loop: polling every %s seconds", POLL_INTERVAL_SECONDS)
    try:
        while True:
            # Air quality for each city
            for c in CITIES:
                data = fetch_air_quality_for_city(c)
                # If no API key or fetch failed, build a sample payload
                if data is None:
                    sample_payload = {
                        "pm2_5": 10.0,
                        "pm10": 20.0,
                        "aqi": 42,
                        "note": "simulated"
                    }
                    send_air_event(c["name"], sample_payload)
                else:
                    send_air_event(c["name"], data)

            # Fire alerts
            fires = fetch_fire_alerts()
            for f in fires:
                try:
                    send_fire_event(f)
                except Exception:
                    logger.exception("Failed to send one fire event")

            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Producer interrupted by user")
    finally:
        try:
            producer.close()
        except Exception:
            pass

if __name__ == "__main__":
    run_loop()