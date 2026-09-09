import pandas as pd
from sqlalchemy import text
from src.transform.aqi_calculator import compute_daily_aqi
from src.transform.cleaning import _upsert

def build_hourly_aggregates(pollution, weather, engine=None):
    if pollution.empty: return pd.DataFrame()
    df=pollution.copy(); df["hour_timestamp"]=pd.to_datetime(df["timestamp"],utc=True).dt.floor("h")
    hourly=df.groupby(["station_id","pollutant_code","hour_timestamp"],as_index=False).agg(avg_value=("value","mean"),min_value=("value","min"),max_value=("value","max"),reading_count=("value","count"))
    if not weather.empty:
        weather=weather.copy(); weather["hour_timestamp"]=pd.to_datetime(weather["timestamp"],utc=True).dt.floor("h"); weather=weather.drop(columns=["timestamp"])
        weather=weather[[column for column in ["station_id","hour_timestamp","temperature","relative_humidity","wind_speed","precipitation"] if column in weather.columns]]
        hourly=hourly.merge(weather,on=["station_id","hour_timestamp"],how="left")
    for col in ["temperature","relative_humidity","wind_speed","precipitation"]:
        if col not in hourly: hourly[col]=None
    if engine: _upsert(engine,"fact_hourly_aggregates",hourly,["station_id","pollutant_code","hour_timestamp"])
    return hourly

def build_daily_aqi_marts(pollution, weather, engine=None):
    if pollution.empty: return pd.DataFrame()
    df=pollution.copy(); df["date"]=pd.to_datetime(df["timestamp"],utc=True).dt.date
    rows=[]
    for (station,date), group in df.groupby(["station_id","date"]):
        averages=group.groupby("pollutant_code")["value"].mean().to_dict(); aqi=compute_daily_aqi(averages)
        row={"station_id":station,"date":date,**aqi,**{f"{p}_avg":averages.get(p) for p in ["pm25","pm10","no2","so2","co","o3"]}}
        rows.append(row)
    result=pd.DataFrame(rows)
    if not weather.empty:
        w=weather.copy(); w["date"]=pd.to_datetime(w["timestamp"],utc=True).dt.date
        summary=w.groupby(["station_id","date"],as_index=False).agg(avg_temperature=("temperature","mean"),avg_humidity=("relative_humidity","mean"),avg_wind_speed=("wind_speed","mean"),total_precipitation=("precipitation","sum"))
        result=result.merge(summary,on=["station_id","date"],how="left")
    for col in ["avg_temperature","avg_humidity","avg_wind_speed","total_precipitation"]:
        if col not in result: result[col]=None
    if engine:
        with engine.begin() as conn:
            for date in result["date"].unique(): conn.execute(text("INSERT INTO dim_dates(date,day_of_week,day_name,month,month_name,quarter,year,is_weekend) VALUES (:date,:dow,:day,:month,:month_name,:quarter,:year,:weekend) ON CONFLICT(date) DO NOTHING"), {"date":date,"dow":date.isoweekday(),"day":date.strftime("%A"),"month":date.month,"month_name":date.strftime("%B"),"quarter":(date.month-1)//3+1,"year":date.year,"weekend":date.weekday()>=5})
        _upsert(engine,"fact_daily_aqi",result,["station_id","date"])
    return result
