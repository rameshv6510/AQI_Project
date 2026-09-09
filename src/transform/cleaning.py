import pandas as pd
from sqlalchemy import text
from src.db import log_rejection

RANGES = {"pm25":(0,1000),"pm10":(0,1500),"no2":(0,1000),"so2":(0,2000),"co":(0,100),"o3":(0,1000)}
WEATHER_RANGES = {"temperature":(-10,60),"relative_humidity":(0,100),"wind_speed":(0,200),"precipitation":(0,1000)}

def _upsert(engine, table, df, keys):
    if df.empty: return
    with engine.begin() as conn:
        for row in df.to_dict("records"):
            # SQLite's DB-API cannot bind pandas Timestamp/NA objects directly.
            row = {
                key: (value.to_pydatetime() if isinstance(value, pd.Timestamp)
                      else None if pd.isna(value) else value)
                for key, value in row.items()
            }
            columns = list(row); values = ",".join(f":{c}" for c in columns); updates = ",".join(f"{c}=excluded.{c}" for c in columns if c not in keys)
            conn.execute(text(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({values}) ON CONFLICT({','.join(keys)}) DO UPDATE SET {updates}"), row)

def clean_pollution_data(df, engine=None):
    if df.empty: return df.copy(), []
    rejected=[]; good=[]
    for row in df.drop_duplicates(subset=["station_id","pollutant_code","timestamp"]).to_dict("records"):
        low, high = RANGES.get(row["pollutant_code"], (0, float("inf")))
        if row["timestamp"] is None or not low <= float(row["value"]) <= high:
            reason = "missing timestamp" if row["timestamp"] is None else "value out of physical range"
            rejected.append({"reason":reason, "raw_value":row})
            if engine: log_rejection(engine, "fact_raw_readings", reason, row)
        else: good.append(row)
    clean = pd.DataFrame(good, columns=df.columns)
    if engine and not clean.empty: _upsert(engine, "fact_raw_readings", clean, ["station_id","pollutant_code","timestamp"])
    return clean, rejected

def clean_weather_data(df, engine=None):
    if df.empty: return df.copy(), []
    rejected=[]; good=[]
    for row in df.drop_duplicates(subset=["station_id","timestamp"]).to_dict("records"):
        failures=[key for key,(low,high) in WEATHER_RANGES.items() if row.get(key) is not None and not low <= float(row[key]) <= high]
        if row.get("timestamp") is None or failures:
            reason="missing timestamp" if row.get("timestamp") is None else f"weather out of physical range: {', '.join(failures)}"; rejected.append({"reason":reason,"raw_value":row})
            if engine: log_rejection(engine,"fact_weather",reason,row)
        else: good.append(row)
    clean=pd.DataFrame(good,columns=df.columns)
    if engine and not clean.empty: _upsert(engine,"fact_weather",clean,["station_id","timestamp"])
    return clean,rejected
