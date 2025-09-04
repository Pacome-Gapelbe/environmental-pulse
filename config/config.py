# OpenWeather API (requires free API key)
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
OPENWEATHER_GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"

# NASA FIRMS Fire Data URLs (free)
NASA_FIRE_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv"

# NASA POWER API for climate data (free)
NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_POWER_PARAMS = {
    "parameters": "T2M,PRECTOT,ALLSKY_SFC_SW_DWN",
    "community": "AG",
    "format": "JSON"
}

# Global Forest Watch API (optional, requires authentication)
GFW_API_URL = "https://data-api.globalforestwatch.org"

# World Bank API for economic indicators (free)
WORLD_BANK_API_URL = "https://api.worldbank.org/v2/country"
WORLD_BANK_INDICATORS = {
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "SP.POP.TOTL": "Population, total",
    "SH.XPD.CHEX.GD.ZS": "Current health expenditure (% of GDP)",
    "AG.LND.FRST.ZS": "Forest area (% of land area)"
}

# WHO GEMS Water Data (sample, may need scraping or simulation)
WHO_WATER_URL = "https://www.who.int/health-topics/water-sanitation-and-health"

# African cities to monitor
MONITORED_CITIES = [
    "Lagos", "Abuja", "Port Harcourt",
    "Accra", "Kumasi", "Lomé",
    "Yaoundé", "Douala", "N'Djamena",
    "Kinshasa", "Lubumbashi", "Goma",
    "Kigali", "Nairobi", "Addis Ababa",
    "Cape Town", "Johannesburg", "Dakar",
    "Cairo"
]

# African countries for economic data
AFRICAN_COUNTRIES = {
    "NG": "Nigeria", "GH": "Ghana", "TG": "Togo",
    "CM": "Cameroon", "TD": "Chad", "CD": "DR Congo",
    "RW": "Rwanda", "KE": "Kenya", "ET": "Ethiopia",
    "ZA": "South Africa", "SN": "Senegal", "EG": "Egypt"
}

# Data storage paths
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"

# Dashboard settings
MAP_DEFAULT_ZOOM = 3
MAX_FIRE_POINTS = 500  # Limit for performance

# Data refresh intervals (in minutes)
AIR_QUALITY_REFRESH = 30
FIRE_DATA_REFRESH = 60
CLIMATE_DATA_REFRESH = 1440  # 24 hours
ECONOMIC_DATA_REFRESH = 10080  # 7 days
WATER_QUALITY_REFRESH = 1440  # 24 hours
