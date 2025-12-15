#!/usr/bin/env python3
"""
Kafka consumer that listens to air_quality and fire_alerts topics
and writes FLATTENED analytics-ready data to Postgres.
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict

import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kafka_consumer")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPICS = [t.strip() for t in os.getenv("KAFKA_TOPICS", "air_quality,fire_alerts").split(",")]

DB_DSN = os.getenv(
    "DATABASE_DSN",
    "postgresql://postgres:postgres@localhost:5432/envpulse"
)
GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP", "env-pulse-consumer")

consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=[s.strip() for s in KAFKA_BOOTSTRAP.split(",")],
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id=GROUP_ID,
)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def parse_iso_ts(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.utcnow()

# ------------------------------------------------------------------
# AIR QUALITY
# ------------------------------------------------------------------
def upsert_air_event(conn, event: Dict[str, Any]):
    payload = event.get("payload", {})

    lat = lon = aqi = pm2_5 = pm10 = None
    ts = parse_iso_ts(event.get("timestamp"))

    if "list" in payload and payload["list"]:
        item = payload["list"][0]
        aqi = item.get("main", {}).get("aqi")
        pm2_5 = item.get("components", {}).get("pm2_5")
        pm10 = item.get("components", {}).get("pm10")
        coord = payload.get("coord", {})
        lat = coord.get("lat")
        lon = coord.get("lon")
    else:
        aqi = payload.get("aqi")
        pm2_5 = payload.get("pm2_5")
        pm10 = payload.get("pm10")

    with conn.cursor() as cur:
        # 1️⃣ Insert
        cur.execute(
            """
            INSERT INTO air_quality (
                event_id, source, city, lat, lon,
                aqi, pm2_5, pm10, timestamp
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (event_id) DO NOTHING;
            """,
            (
                event.get("event_id"),
                event.get("source"),
                event.get("city"),
                lat,
                lon,
                aqi,
                pm2_5,
                pm10,
                ts,
            ),
        )

        # 2️⃣ Keep only latest 100
        cur.execute(
            """
            DELETE FROM air_quality
            WHERE event_id NOT IN (
                SELECT event_id
                FROM air_quality
                ORDER BY timestamp DESC
                LIMIT 100
            );
            """
        )

    conn.commit()


    logger.info(
        "🌍 Air event stored | city=%s aqi=%s pm2_5=%s",
        event.get("city"),
        aqi,
        pm2_5,
    )


# ------------------------------------------------------------------
# FIRE ALERTS
# ------------------------------------------------------------------
def upsert_fire_event(conn, event: Dict[str, Any]):
    payload = event.get("payload", {})
    properties = payload.get("properties", {})

    with conn.cursor() as cur:
        # 1️⃣ Insert
        cur.execute(
            """
            INSERT INTO fire_alerts (
                event_id, source, latitude, longitude,
                confidence, frp, timestamp
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (event_id) DO NOTHING;
            """,
            (
                event.get("event_id"),
                event.get("source"),
                payload.get("latitude"),
                payload.get("longitude"),
                properties.get("confidence"),
                properties.get("brightness"),
                parse_iso_ts(event.get("timestamp")),
            ),
        )

        # 2️⃣ Keep only latest 100
        cur.execute(
            """
            DELETE FROM fire_alerts
            WHERE event_id NOT IN (
                SELECT event_id
                FROM fire_alerts
                ORDER BY timestamp DESC
                LIMIT 100
            );
            """
        )

    conn.commit()


    logger.info(
        "🔥 Fire event stored | lat=%s lon=%s conf=%s",
        payload.get("latitude"),
        payload.get("longitude"),
        properties.get("confidence"),
    )

# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------
def main_loop():
    logger.info("🔌 Connecting to Postgres...")
    conn = psycopg2.connect(DB_DSN)
    logger.info("✅ Connected to Postgres")

    try:
        logger.info("🚀 Kafka consumer started for topics: %s", TOPICS)

        for msg in consumer:
            event = msg.value
            topic = msg.topic

            try:
                if topic == "air_quality":
                    upsert_air_event(conn, event)

                elif topic == "fire_alerts":
                    upsert_fire_event(conn, event)

                else:
                    logger.warning("⚠️ Unhandled topic: %s", topic)

            except Exception:
                logger.exception("❌ Failed processing event from %s", topic)

    except KeyboardInterrupt:
        logger.info("🛑 Consumer stopped by user")

    finally:
        consumer.close()
        conn.close()
        logger.info("🔒 Connections closed")

# ------------------------------------------------------------------
if __name__ == "__main__":
    main_loop()
