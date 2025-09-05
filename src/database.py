import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from config.config import DB_CONFIG
import logging
from datetime import datetime
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            logger.info("✅ Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:  # If it's a SELECT query
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                    return pd.DataFrame(results, columns=columns)
                else:  # For INSERT, UPDATE, DELETE
                    self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Error executing query: {e}")
            self.connection.rollback()
            raise
    
    def create_tables(self):
        tables = {
            'air_quality': """
                CREATE TABLE IF NOT EXISTS air_quality (
                    id SERIAL PRIMARY KEY,
                    city VARCHAR(100) NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    lat FLOAT,
                    lon FLOAT,
                    aqi INTEGER,
                    co FLOAT,
                    no FLOAT,
                    no2 FLOAT,
                    o3 FLOAT,
                    so2 FLOAT,
                    pm2_5 FLOAT,
                    pm10 FLOAT,
                    nh3 FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city, timestamp)
                )
            """,
            'fire_alerts': """
                CREATE TABLE IF NOT EXISTS fire_alerts (
                    id SERIAL PRIMARY KEY,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    confidence FLOAT,
                    frp FLOAT,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(latitude, longitude, timestamp)
                )
            """,
            'climate_data': """
                CREATE TABLE IF NOT EXISTS climate_data (
                    id SERIAL PRIMARY KEY,
                    city VARCHAR(100) NOT NULL,
                    lat FLOAT,
                    lon FLOAT,
                    timestamp TIMESTAMP NOT NULL,
                    temperature_2m FLOAT,
                    precipitation FLOAT,
                    solar_radiation FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city, timestamp)
                )
            """,
            'economic_data': """
                CREATE TABLE IF NOT EXISTS economic_data (
                    id SERIAL PRIMARY KEY,
                    country_code VARCHAR(10) NOT NULL,
                    country_name VARCHAR(100) NOT NULL,
                    indicator_code VARCHAR(50) NOT NULL,
                    indicator_name VARCHAR(200) NOT NULL,
                    value FLOAT,
                    year INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(country_code, indicator_code, year)
                )
            """,
            'water_quality': """
                CREATE TABLE IF NOT EXISTS water_quality (
                    id SERIAL PRIMARY KEY,
                    city VARCHAR(100) NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    ph FLOAT,
                    turbidity FLOAT,
                    dissolved_oxygen FLOAT,
                    water_quality_index FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city, timestamp)
                )
            """
        }
        
        success_count = 0
        for table_name, table_sql in tables.items():
            try:
                # First check if table already exists
                check_query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """
                table_exists = self.execute_query(check_query, (table_name,))
                
                if table_exists.iloc[0, 0]:
                    logger.info(f"✅ Table already exists: {table_name}")
                    success_count += 1
                else:
                    # Try to create the table
                    self.execute_query(table_sql)
                    logger.info(f"✅ Created table: {table_name}")
                    success_count += 1
                    
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"✅ Table already exists: {table_name}")
                    success_count += 1
                elif "permission denied" in str(e).lower():
                    logger.warning(f"⚠️ No CREATE permission for {table_name}, but table may already exist")
                    # Check if we can at least access the table
                    try:
                        access_test = self.execute_query(f"SELECT 1 FROM {table_name} LIMIT 1")
                        logger.info(f"✅ Can access existing table: {table_name}")
                        success_count += 1
                    except:
                        logger.error(f"❌ Cannot access table: {table_name}")
                else:
                    logger.error(f"❌ Error with table {table_name}: {e}")
        
        if success_count == len(tables):
            logger.info("✅ All tables are accessible")
        else:
            logger.warning(f"⚠️ Only {success_count} out of {len(tables)} tables are accessible")
    
    def insert_air_quality_data(self, df):
        """Insert air quality data into database"""
        if df.empty:
            logger.warning("⚠️ No air quality data to insert")
            return 0
        
        try:
            # Prepare data for insertion
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            
            # Ensure all required columns exist
            expected_columns = ['city', 'timestamp', 'lat', 'lon', 'aqi', 'co', 'no', 
                              'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert to list of tuples
            records = []
            for _, row in df.iterrows():
                record = (
                    row['city'], row['timestamp'], row['lat'], row['lon'],
                    row['aqi'], row['co'], row['no'], row['no2'], row['o3'],
                    row['so2'], row['pm2_5'], row['pm10'], row['nh3']
                )
                records.append(record)
            
            # Use ON CONFLICT DO NOTHING to avoid duplicates
            query = """
                INSERT INTO air_quality 
                (city, timestamp, lat, lon, aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3)
                VALUES %s
                ON CONFLICT (city, timestamp) DO NOTHING
            """
            
            with self.connection.cursor() as cursor:
                execute_values(cursor, query, records)
                self.connection.commit()
                inserted_count = cursor.rowcount
                logger.info(f"✅ Inserted {inserted_count} air quality records")
                return inserted_count
                
        except Exception as e:
            logger.error(f"❌ Error inserting air quality data: {e}")
            self.connection.rollback()
            return 0
    
    def insert_fire_data(self, df):
        """Insert fire alert data into database"""
        if df.empty:
            logger.warning("⚠️ No fire data to insert")
            return 0
        
        try:
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            
            # Ensure all required columns exist
            expected_columns = ['latitude', 'longitude', 'confidence', 'frp', 'timestamp']
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert to list of tuples
            records = []
            for _, row in df.iterrows():
                record = (
                    row['latitude'], row['longitude'], row['confidence'], 
                    row['frp'], row['timestamp']
                )
                records.append(record)
            
            # Use ON CONFLICT DO NOTHING to avoid duplicates
            query = """
                INSERT INTO fire_alerts 
                (latitude, longitude, confidence, frp, timestamp)
                VALUES %s
                ON CONFLICT (latitude, longitude, timestamp) DO NOTHING
            """
            
            with self.connection.cursor() as cursor:
                execute_values(cursor, query, records)
                self.connection.commit()
                inserted_count = cursor.rowcount
                logger.info(f"✅ Inserted {inserted_count} fire alert records")
                return inserted_count
                
        except Exception as e:
            logger.error(f"❌ Error inserting fire data: {e}")
            self.connection.rollback()
            return 0
    
    def insert_climate_data(self, df):
        """Insert climate data into database"""
        if df.empty:
            logger.warning("⚠️ No climate data to insert")
            return 0
        
        try:
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            
            # Ensure all required columns exist
            expected_columns = ['city', 'lat', 'lon', 'timestamp', 'temperature_2m', 'precipitation', 'solar_radiation']
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert to list of tuples
            records = []
            for _, row in df.iterrows():
                record = (
                    row['city'], row['lat'], row['lon'], row['timestamp'],
                    row['temperature_2m'], row['precipitation'], row['solar_radiation']
                )
                records.append(record)
            
            # Use ON CONFLICT DO NOTHING to avoid duplicates
            query = """
                INSERT INTO climate_data 
                (city, lat, lon, timestamp, temperature_2m, precipitation, solar_radiation)
                VALUES %s
                ON CONFLICT (city, timestamp) DO NOTHING
            """
            
            with self.connection.cursor() as cursor:
                execute_values(cursor, query, records)
                self.connection.commit()
                inserted_count = cursor.rowcount
                logger.info(f"✅ Inserted {inserted_count} climate records")
                return inserted_count
                
        except Exception as e:
            logger.error(f"❌ Error inserting climate data: {e}")
            self.connection.rollback()
            return 0
    
    def insert_economic_data(self, df):
        """Insert economic data into database"""
        if df.empty:
            logger.warning("⚠️ No economic data to insert")
            return 0
        
        try:
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            
            # Ensure all required columns exist
            expected_columns = ['country_code', 'country_name', 'indicator_code', 
                              'indicator_name', 'value', 'year', 'timestamp']
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert year to integer
            df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
            
            # Convert to list of tuples
            records = []
            for _, row in df.iterrows():
                record = (
                    row['country_code'], row['country_name'], row['indicator_code'],
                    row['indicator_name'], row['value'], row['year'], row['timestamp']
                )
                records.append(record)
            
            # Use ON CONFLICT DO NOTHING to avoid duplicates
            query = """
                INSERT INTO economic_data 
                (country_code, country_name, indicator_code, indicator_name, value, year, timestamp)
                VALUES %s
                ON CONFLICT (country_code, indicator_code, year) DO NOTHING
            """
            
            with self.connection.cursor() as cursor:
                execute_values(cursor, query, records)
                self.connection.commit()
                inserted_count = cursor.rowcount
                logger.info(f"✅ Inserted {inserted_count} economic records")
                return inserted_count
                
        except Exception as e:
            logger.error(f"❌ Error inserting economic data: {e}")
            self.connection.rollback()
            return 0
    
    def insert_water_quality_data(self, df):
        """Insert water quality data into database"""
        if df.empty:
            logger.warning("⚠️ No water quality data to insert")
            return 0
        
        try:
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            
            # Ensure all required columns exist
            expected_columns = ['city', 'timestamp', 'ph', 'turbidity', 'dissolved_oxygen', 'water_quality_index']
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert to list of tuples
            records = []
            for _, row in df.iterrows():
                record = (
                    row['city'], row['timestamp'], row['ph'], row['turbidity'],
                    row['dissolved_oxygen'], row['water_quality_index']
                )
                records.append(record)
            
            # Use ON CONFLICT DO NOTHING to avoid duplicates
            query = """
                INSERT INTO water_quality 
                (city, timestamp, ph, turbidity, dissolved_oxygen, water_quality_index)
                VALUES %s
                ON CONFLICT (city, timestamp) DO NOTHING
            """
            
            with self.connection.cursor() as cursor:
                execute_values(cursor, query, records)
                self.connection.commit()
                inserted_count = cursor.rowcount
                logger.info(f"✅ Inserted {inserted_count} water quality records")
                return inserted_count
                
        except Exception as e:
            logger.error(f"❌ Error inserting water quality data: {e}")
            self.connection.rollback()
            return 0
    
    def get_latest_data(self, table_name, limit=1000):
        """Get latest data from specified table"""
        try:
            query = f"""
                SELECT * FROM {table_name} 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            return self.execute_query(query, (limit,))
        except Exception as e:
            logger.error(f"❌ Error fetching data from {table_name}: {e}")
            return pd.DataFrame()
    
    def get_table_stats(self):
        """Get statistics about each table"""
        tables = ['air_quality', 'fire_alerts', 'climate_data', 'economic_data', 'water_quality']
        stats = {}
        
        for table in tables:
            try:
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                latest_query = f"SELECT MAX(timestamp) as latest FROM {table}"
                
                count_result = self.execute_query(count_query)
                latest_result = self.execute_query(latest_query)
                
                stats[table] = {
                    'count': count_result['count'].iloc[0] if not count_result.empty else 0,
                    'latest': latest_result['latest'].iloc[0] if not latest_result.empty else None
                }
            except Exception as e:
                logger.error(f"❌ Error getting stats for {table}: {e}")
                stats[table] = {'count': 0, 'latest': None}
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("✅ Database connection closed")


# Utility function for testing
def test_database_connection():
    """Test database connection and basic operations"""
    try:
        db = DatabaseManager()
        
        # Test connection
        version = db.execute_query("SELECT version();")
        print("✅ PostgreSQL Version:", version.iloc[0, 0] if not version.empty else "Unknown")
        
        # Test table stats
        stats = db.get_table_stats()
        print("📊 Table Statistics:")
        for table, stat in stats.items():
            print(f"   {table}: {stat['count']} records, latest: {stat['latest']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the database connection when run directly
    print("🧪 Testing Database Connection...")
    success = test_database_connection()
    if success:
        print("🎉 Database test completed successfully!")
    else:
        print("💥 Database test failed!")