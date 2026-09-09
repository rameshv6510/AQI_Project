from datetime import datetime, timezone, timedelta
import pandas as pd
from src.transform.aqi_calculator import calculate_sub_index,get_aqi_category,compute_daily_aqi
from src.transform.staging import normalize_pollutant_unit,parse_iso_timestamp
from src.transform.cleaning import clean_pollution_data
def test_aqi_sub_index_pm25(): assert round(calculate_sub_index("pm25",15)) == 25
def test_aqi_categories(): assert get_aqi_category(150) == "Moderate"
def test_compute_daily_aqi():
    result=compute_daily_aqi({"pm25":45,"pm10":150,"no2":25,"so2":15}); assert result["dominant_pollutant"] == "pm10" and result["aqi_category"] == "Moderate"
def test_unit_normalization():
    unit,value=normalize_pollutant_unit("co","ppm",2); assert unit == "mg/m³" and round(value,2) == 2.29
def test_timestamp_parser(): assert parse_iso_timestamp("2026-09-09T10:00:00Z").hour == 10 and parse_iso_timestamp(None) is None
def test_cleaning_rejects_outlier():
    now=datetime.now(timezone.utc); df=pd.DataFrame([{"station_id":"594","pollutant_code":"pm25","value":55,"unit":"µg/m³","timestamp":now,"source":"OpenAQ","extracted_at":now},{"station_id":"594","pollutant_code":"pm25","value":9999,"unit":"µg/m³","timestamp":now+timedelta(hours=1),"source":"OpenAQ","extracted_at":now}]); clean,rejected=clean_pollution_data(df); assert len(clean)==1 and len(rejected)==1
