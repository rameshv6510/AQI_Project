import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_OPENAQ_DIR = RAW_DIR / "openaq"
RAW_WEATHER_DIR = RAW_DIR / "weather"
LOGS_DIR = DATA_DIR / "extraction_logs"
for directory in (RAW_OPENAQ_DIR, RAW_WEATHER_DIR, LOGS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "")
OPENAQ_BASE_URL = "https://api.openaq.org/v3"
OPENAQ_HEADERS = {"X-API-Key": OPENAQ_API_KEY, "Accept": "application/json"}
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "aqi_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
POSTGRES_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLITE_URL = f"sqlite:///{PROJECT_ROOT / 'aqi_pipeline.db'}"

STATIONS = [
    {"station_id": "594", "name": "BTM Layout, Bengaluru - KSPCB", "city": "Bengaluru", "latitude": 12.9135, "longitude": 77.5959, "is_primary": True},
    {"station_id": "412", "name": "Peenya, Bengaluru - KSPCB", "city": "Bengaluru", "latitude": 13.0285, "longitude": 77.5197, "is_primary": False},
    {"station_id": "797", "name": "City Railway Station, Bengaluru - KSPCB", "city": "Bengaluru", "latitude": 12.9774, "longitude": 77.5708, "is_primary": False},
    {"station_id": "2589", "name": "SaneguravaHalli, Bengaluru - KSPCB", "city": "Bengaluru", "latitude": 12.9902, "longitude": 77.5459, "is_primary": False},
    {"station_id": "2592", "name": "BWSSB Kadabesanahalli, Bengaluru - KSPCB", "city": "Bengaluru", "latitude": 12.9348, "longitude": 77.6896, "is_primary": False},
    {"station_id": "6975", "name": "Silk Board, Bengaluru - KSPCB", "city": "Bengaluru", "latitude": 12.9176, "longitude": 77.6233, "is_primary": False},
]
POLLUTANTS = [
    {"pollutant_code": "pm25", "display_name": "Particulate Matter 2.5", "unit": "µg/m³", "cpcb_standard_24hr": 60.0},
    {"pollutant_code": "pm10", "display_name": "Particulate Matter 10", "unit": "µg/m³", "cpcb_standard_24hr": 100.0},
    {"pollutant_code": "no2", "display_name": "Nitrogen Dioxide", "unit": "µg/m³", "cpcb_standard_24hr": 80.0},
    {"pollutant_code": "so2", "display_name": "Sulfur Dioxide", "unit": "µg/m³", "cpcb_standard_24hr": 80.0},
    {"pollutant_code": "co", "display_name": "Carbon Monoxide", "unit": "mg/m³", "cpcb_standard_24hr": 2.0},
    {"pollutant_code": "o3", "display_name": "Ozone", "unit": "µg/m³", "cpcb_standard_24hr": 100.0},
]
