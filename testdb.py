#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.database import DatabaseManager
    print("✅ Successfully imported DatabaseManager")
    
    # Test database connection
    db = DatabaseManager()
    print("✅ Database connection successful")
    
    # Test data retrieval
    air_data = db.get_latest_data('air_quality', 5)
    print(f"✅ Retrieved {len(air_data)} air quality records")
    
    db.close()
    print("🎉 All database tests passed!")
    
except Exception as e:
    print(f"❌ Database test failed: {e}")
    print("💡 Make sure you're running from the project root directory")