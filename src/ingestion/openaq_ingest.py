import json, time, uuid
from datetime import datetime, timezone
import requests
from src.config import STATIONS, OPENAQ_BASE_URL, OPENAQ_HEADERS, RAW_OPENAQ_DIR
from src.db import log_extraction

def ingest_openaq(engine=None):
    run_id=f"openaq_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"; start=time.time(); count=0; errors=[]
    if not OPENAQ_HEADERS["X-API-Key"]:
        message="OPENAQ_API_KEY is not configured"; 
        if engine: log_extraction(engine,run_id,"OpenAQ","FAILED",0,message,time.time()-start)
        return {"status":"FAILED","total_records":0,"error":message}
    for station in STATIONS:
        try:
            response=requests.get(f"{OPENAQ_BASE_URL}/locations/{station['station_id']}/latest",headers=OPENAQ_HEADERS,timeout=20); response.raise_for_status(); payload=response.json(); payload["station_id"]=station["station_id"]
            path=RAW_OPENAQ_DIR/f"openaq_station_{station['station_id']}_{int(time.time())}.json"; path.write_text(json.dumps(payload,indent=2),encoding="utf-8")
            count += len(payload.get("results",[]))
        except requests.RequestException as exc: errors.append(f"{station['station_id']}: {exc}")
    status="SUCCESS" if not errors else ("PARTIAL" if count else "FAILED")
    if engine: log_extraction(engine,run_id,"OpenAQ",status,count,"; ".join(errors)[:2000] or None,time.time()-start)
    return {"status":status,"total_records":count,"errors":errors}
