import logging, time
from src.db import get_engine, init_db
from src.ingestion.openaq_ingest import ingest_openaq
from src.ingestion.weather_ingest import ingest_weather
from src.transform.staging import stage_openaq_data, stage_weather_data
from src.transform.cleaning import clean_pollution_data, clean_weather_data
from src.transform.analytics import build_hourly_aggregates, build_daily_aqi_marts
logger=logging.getLogger(__name__)
def run_end_to_end_pipeline(past_days=14):
    start=time.time(); engine=get_engine(); init_db(engine)
    openaq=ingest_openaq(engine); weather=ingest_weather(engine,past_days)
    staged_pollution,staged_weather=stage_openaq_data(),stage_weather_data()
    pollution,rejected_p=clean_pollution_data(staged_pollution,engine); weather_df,rejected_w=clean_weather_data(staged_weather,engine)
    hourly=build_hourly_aggregates(pollution,weather_df,engine); daily=build_daily_aqi_marts(pollution,weather_df,engine)
    return {"status":"SUCCESS","total_execution_seconds":round(time.time()-start,2),"ingestion":{"openaq":openaq["status"],"weather":weather["status"]},"clean_pollution_records":len(pollution),"clean_weather_records":len(weather_df),"hourly_aggregates":len(hourly),"daily_aqi_records":len(daily),"rejected_records":len(rejected_p)+len(rejected_w)}
