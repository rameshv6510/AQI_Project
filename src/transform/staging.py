import json
from pathlib import Path
import pandas as pd
from src.config import RAW_OPENAQ_DIR, RAW_WEATHER_DIR

def parse_iso_timestamp(value):
    if not value: return None
    return pd.to_datetime(value, utc=True).to_pydatetime()

def normalize_pollutant_unit(code, unit, value):
    code = str(code).lower().replace("pm2.5", "pm25").replace("pm10", "pm10")
    clean_unit = str(unit or "").lower().replace("μ", "u").replace("µ", "u")
    if code == "co" and clean_unit == "ppm": return "mg/m³", float(value) * 1.145
    return ("mg/m³" if code == "co" else "µg/m³"), float(value)

def stage_openaq_data():
    rows = []
    for path in RAW_OPENAQ_DIR.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8")); station_id = str(payload.get("station_id", path.stem.split("_")[2] if "_" in path.stem else ""))
            results = payload.get("results", payload.get("measurements", []))
            for item in results:
                parameter = item.get("parameter", item.get("parameterName", "")); value = item.get("value")
                if isinstance(parameter, dict): parameter = parameter.get("name")
                if value is None: continue
                code = str(parameter).lower().replace("pm2.5", "pm25").replace("pm10", "pm10")
                unit, value = normalize_pollutant_unit(code, item.get("unit", ""), value)
                timestamp = item.get("date", {}).get("utc") if isinstance(item.get("date"), dict) else item.get("datetime")
                rows.append({"station_id":station_id,"pollutant_code":code,"value":value,"unit":unit,"timestamp":parse_iso_timestamp(timestamp),"source":"OpenAQ","extracted_at":pd.Timestamp.now(tz="UTC")})
        except (ValueError, KeyError, OSError): continue
    return pd.DataFrame(rows, columns=["station_id","pollutant_code","value","unit","timestamp","source","extracted_at"])

def stage_weather_data():
    rows = []
    for path in RAW_WEATHER_DIR.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8")); station_id = str(payload.get("station_id", path.stem.split("_")[2] if "_" in path.stem else "")); hourly = payload.get("hourly", {})
            for i, timestamp in enumerate(hourly.get("time", [])):
                get = lambda key: hourly.get(key, [None]*len(hourly.get("time", [])))[i]
                rows.append({"station_id":station_id,"timestamp":parse_iso_timestamp(timestamp),"temperature":get("temperature_2m"),"relative_humidity":get("relative_humidity_2m"),"wind_speed":get("wind_speed_10m"),"wind_direction":get("wind_direction_10m"),"precipitation":get("precipitation"),"surface_pressure":get("surface_pressure")})
        except (ValueError, KeyError, OSError, IndexError): continue
    return pd.DataFrame(rows)
