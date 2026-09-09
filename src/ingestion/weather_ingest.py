import json, time, uuid
from datetime import datetime
import requests
from src.config import STATIONS, OPEN_METEO_BASE_URL, RAW_WEATHER_DIR
from src.db import log_extraction

def ingest_weather(engine=None, past_days=14):
    run_id=f"weather_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"; start=time.time(); count=0; errors=[]
    variables="temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,surface_pressure"
    for station in STATIONS:
        try:
            params={"latitude":station["latitude"],"longitude":station["longitude"],"hourly":variables,"timezone":"Asia/Kolkata","past_days":past_days,"forecast_days":1}
            response=requests.get(OPEN_METEO_BASE_URL,params=params,timeout=20); response.raise_for_status(); payload=response.json(); payload["station_id"]=station["station_id"]
            path=RAW_WEATHER_DIR/f"weather_station_{station['station_id']}_{int(time.time())}.json"; path.write_text(json.dumps(payload,indent=2),encoding="utf-8")
            count += len(payload.get("hourly",{}).get("time",[]))
        except requests.RequestException as exc: errors.append(f"{station['station_id']}: {exc}")
    status="SUCCESS" if not errors else ("PARTIAL" if count else "FAILED")
    if engine: log_extraction(engine,run_id,"Open-Meteo",status,count,"; ".join(errors)[:2000] or None,time.time()-start)
    return {"status":status,"total_records":count,"errors":errors}
