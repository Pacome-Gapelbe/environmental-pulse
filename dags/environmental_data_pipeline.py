from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import sys
import os

# Add your project to Python path
sys.path.insert(0, '/opt/airflow/environmental-pulse')

default_args = {
    'owner': 'environmental_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_data_ingestion():
    """Run your data ingestion script"""
    try:
        from src.data_ingestion import main as collect_data
        print("Starting data collection...")
        air_df, fire_df, climate_df, economic_df, water_df = collect_data()
        
        print(f"✅ Data collection successful!")
        print(f"   Air Quality: {len(air_df)} records")
        print(f"   Fire Alerts: {len(fire_df)} records") 
        print(f"   Climate Data: {len(climate_df)} records")
        print(f"   Economic Data: {len(economic_df)} records")
        print(f"   Water Quality: {len(water_df)} records")
        
        return True
    except Exception as e:
        print(f"❌ Data collection failed: {e}")
        raise

def check_database_connection():
    """Verify database is accessible"""
    try:
        from src.database import DatabaseManager
        db = DatabaseManager()
        
        # Test connection by getting table stats
        stats = db.get_table_stats()
        print("✅ Database connection successful!")
        for table, stat in stats.items():
            print(f"   {table}: {stat['count']} records")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

with DAG(
    'environmental_data_pipeline',
    default_args=default_args,
    description='Collect and store environmental data for Africa',
    schedule_interval=timedelta(hours=1),  # Run every hour
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['environment', 'africa', 'data-pipeline'],
) as dag:

    start = EmptyOperator(task_id='start')
    
    check_db_task = PythonOperator(
        task_id='check_database_connection',
        python_callable=check_database_connection,
    )
    
    collect_data_task = PythonOperator(
        task_id='collect_environmental_data',
        python_callable=run_data_ingestion,
    )
    
    end = EmptyOperator(task_id='end')
    
    # Set up dependencies
    start >> check_db_task >> collect_data_task >> end