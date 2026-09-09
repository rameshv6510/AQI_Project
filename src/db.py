import json
import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from src.config import DB_TYPE, POSTGRES_URL, SQLITE_URL, STATIONS, POLLUTANTS

logger = logging.getLogger(__name__)

def get_engine():
    if DB_TYPE.lower() == "postgresql":
        try:
            engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
            with engine.connect() as conn: conn.execute(text("SELECT 1"))
            return engine
        except SQLAlchemyError as exc:
            logger.warning("PostgreSQL unavailable (%s); using SQLite.", exc)
    return create_engine(SQLITE_URL, future=True)

DDL = [
"CREATE TABLE IF NOT EXISTS dim_stations (station_id VARCHAR(50) PRIMARY KEY, name VARCHAR(255) NOT NULL, city VARCHAR(100) NOT NULL, latitude FLOAT NOT NULL, longitude FLOAT NOT NULL, source VARCHAR(50) DEFAULT 'OpenAQ')",
"CREATE TABLE IF NOT EXISTS dim_pollutants (pollutant_code VARCHAR(20) PRIMARY KEY, display_name VARCHAR(100) NOT NULL, unit VARCHAR(20) NOT NULL, cpcb_standard_24hr FLOAT)",
"CREATE TABLE IF NOT EXISTS dim_dates (date DATE PRIMARY KEY, day_of_week INTEGER, day_name VARCHAR(20), month INTEGER, month_name VARCHAR(20), quarter INTEGER, year INTEGER, is_weekend BOOLEAN)",
"CREATE TABLE IF NOT EXISTS fact_raw_readings (reading_id INTEGER PRIMARY KEY, station_id VARCHAR(50), pollutant_code VARCHAR(20), value FLOAT NOT NULL, unit VARCHAR(20), timestamp TIMESTAMP, source VARCHAR(50), extracted_at TIMESTAMP, UNIQUE(station_id,pollutant_code,timestamp))",
"CREATE TABLE IF NOT EXISTS fact_weather (weather_id INTEGER PRIMARY KEY, station_id VARCHAR(50), timestamp TIMESTAMP, temperature FLOAT, relative_humidity FLOAT, wind_speed FLOAT, wind_direction FLOAT, precipitation FLOAT, surface_pressure FLOAT, UNIQUE(station_id,timestamp))",
"CREATE TABLE IF NOT EXISTS fact_hourly_aggregates (id INTEGER PRIMARY KEY, station_id VARCHAR(50), pollutant_code VARCHAR(20), hour_timestamp TIMESTAMP, avg_value FLOAT, min_value FLOAT, max_value FLOAT, reading_count INTEGER, temperature FLOAT, relative_humidity FLOAT, wind_speed FLOAT, precipitation FLOAT, UNIQUE(station_id,pollutant_code,hour_timestamp))",
"CREATE TABLE IF NOT EXISTS fact_daily_aqi (id INTEGER PRIMARY KEY, station_id VARCHAR(50), date DATE, aqi_value FLOAT, aqi_category VARCHAR(50), dominant_pollutant VARCHAR(20), pm25_avg FLOAT, pm10_avg FLOAT, no2_avg FLOAT, so2_avg FLOAT, co_avg FLOAT, o3_avg FLOAT, avg_temperature FLOAT, avg_humidity FLOAT, avg_wind_speed FLOAT, total_precipitation FLOAT, UNIQUE(station_id,date))",
"CREATE TABLE IF NOT EXISTS extraction_log (run_id VARCHAR(100) PRIMARY KEY, source VARCHAR(50), timestamp TIMESTAMP, status VARCHAR(20), row_count INTEGER, error_message TEXT, execution_time_seconds FLOAT)",
"CREATE TABLE IF NOT EXISTS rejected_records_log (record_id INTEGER PRIMARY KEY, source_table VARCHAR(50), reason VARCHAR(255), raw_value TEXT, timestamp TIMESTAMP)"
]

def init_db(engine):
    with engine.begin() as conn:
        for statement in DDL: conn.execute(text(statement))
        for station in STATIONS:
            conn.execute(text("INSERT INTO dim_stations(station_id,name,city,latitude,longitude) VALUES (:station_id,:name,:city,:latitude,:longitude) ON CONFLICT(station_id) DO UPDATE SET name=excluded.name"), station)
        for pollutant in POLLUTANTS:
            conn.execute(text("INSERT INTO dim_pollutants(pollutant_code,display_name,unit,cpcb_standard_24hr) VALUES (:pollutant_code,:display_name,:unit,:cpcb_standard_24hr) ON CONFLICT(pollutant_code) DO UPDATE SET display_name=excluded.display_name"), pollutant)

def log_extraction(engine, run_id, source, status, row_count=0, error_message=None, execution_time_seconds=None):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO extraction_log(run_id,source,timestamp,status,row_count,error_message,execution_time_seconds) VALUES (:run_id,:source,:timestamp,:status,:row_count,:error_message,:execution_time_seconds) ON CONFLICT(run_id) DO UPDATE SET status=excluded.status,row_count=excluded.row_count,error_message=excluded.error_message"), {"run_id":run_id,"source":source,"timestamp":datetime.now(timezone.utc),"status":status,"row_count":row_count,"error_message":error_message,"execution_time_seconds":execution_time_seconds})

def log_rejection(engine, source_table, reason, raw_value):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO rejected_records_log(record_id,source_table,reason,raw_value,timestamp) VALUES ((SELECT COALESCE(MAX(record_id),0)+1 FROM rejected_records_log),:source_table,:reason,:raw_value,:timestamp)"), {"source_table":source_table,"reason":reason,"raw_value":json.dumps(raw_value, default=str),"timestamp":datetime.now(timezone.utc)})
