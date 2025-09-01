# config/config.py

# API Configuration
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
OPENWEATHER_GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"

# NASA FIRMS Fire Data URLs
NASA_FIRE_URL = (
    "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv"
)

# Data refresh intervals (in minutes)
AIR_QUALITY_REFRESH = 30
FIRE_DATA_REFRESH = 60

# African cities to monitor
MONITORED_CITIES = [
    # Nigeria
    "Lagos",
    "Abuja",
    "Port Harcourt",
    # Ghana
    "Accra",
    "Kumasi",
    # Togo
    "Lomé",
    # Cameroon
    "Yaoundé",
    "Douala",
    # Chad
    "N'Djamena",
    # DRC
    "Kinshasa",
    "Lubumbashi",
    "Goma",
    # Rwanda
    "Kigali",
    # Other African hubs (optional)
    "Nairobi",
    "Addis Ababa",
    "Cape Town",
    "Johannesburg",
    "Dakar",
    "Cairo",
]

# Data storage paths
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"

# Dashboard settings
MAP_DEFAULT_ZOOM = 3
MAX_FIRE_POINTS = 500  # Limit for performance
