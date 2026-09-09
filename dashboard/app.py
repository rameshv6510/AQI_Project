import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text
from src.db import get_engine
from src.config import STATIONS

st.set_page_config(page_title="Bengaluru AQI Analytics",page_icon="🌿",layout="wide")
st.title("🌿 Bengaluru Air Quality & Weather Analytics")
st.caption("Part 1 Data Engineering Pipeline | OpenAQ + Open-Meteo + CPCB AQI")
@st.cache_data(ttl=60)
def load(table):
    try:
        with get_engine().connect() as conn: return pd.read_sql(text(f"SELECT * FROM {table}"),conn)
    except Exception: return pd.DataFrame()
daily,hourly,weather,logs,rejections=map(load,["fact_daily_aqi","fact_hourly_aggregates","fact_weather","extraction_log","rejected_records_log"])
options={s["name"]:s["station_id"] for s in STATIONS}; selected=st.sidebar.selectbox("Monitoring station",list(options)); station=options[selected]
if not daily.empty: daily["date"]=pd.to_datetime(daily["date"]); filtered=daily[daily.station_id.astype(str)==station]
else: filtered=pd.DataFrame()
if not daily.empty and "source" not in daily.columns:
    st.info("Data shown in this dashboard may include locally seeded demonstration data. Run the live pipeline after configuring OPENAQ_API_KEY for live observations.")
k1,k2,k3=st.columns(3)
if not filtered.empty:
    last=filtered.sort_values("date").iloc[-1]; k1.metric("Latest AQI",round(last.aqi_value,1)); k2.metric("Category",last.aqi_category); k3.metric("Dominant pollutant",str(last.dominant_pollutant).upper())
else: st.info("No analytical records yet. Configure .env and run `python run_pipeline.py --days 14`.")
tabs=st.tabs(["AQI Trend","Pollutants","Station Comparison","Hourly Patterns","Weather Impact","Data & Logs"])
with tabs[0]:
    if not filtered.empty: st.plotly_chart(px.line(filtered,x="date",y="aqi_value",markers=True,title=f"AQI Trend — {selected}"),use_container_width=True)
with tabs[1]:
    if not filtered.empty:
        dominant = filtered["dominant_pollutant"].dropna().value_counts().rename_axis("pollutant").reset_index(name="days_dominant")
        if not dominant.empty:
            pie = px.pie(
                dominant,
                names="pollutant",
                values="days_dominant",
                hole=0.42,
                title="Dominant Pollutant Distribution",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            pie.update_traces(textinfo="label+percent", textposition="outside", automargin=True)
            pie.update_layout(
                height=600,
                margin={"t": 70, "b": 70, "l": 20, "r": 20},
                legend={"orientation": "h", "y": -0.08, "x": 0.5, "xanchor": "center"},
            )
            st.plotly_chart(
                pie,
                use_container_width=True,
            )
with tabs[2]:
    if not daily.empty:
        station_names = {str(s["station_id"]): s["name"] for s in STATIONS}
        comparison = daily.groupby("station_id", as_index=False)["aqi_value"].mean()
        comparison["station"] = comparison["station_id"].astype(str).map(station_names).fillna(comparison["station_id"].astype(str))
        comparison = comparison.sort_values("aqi_value", ascending=True)
        chart = px.bar(
            comparison,
            x="aqi_value",
            y="station",
            orientation="h",
            text="aqi_value",
            title="Average AQI by Monitoring Station",
            labels={"aqi_value": "Average AQI", "station": "Monitoring station"},
            color="aqi_value",
            color_continuous_scale="YlOrRd",
        )
        chart.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
        chart.update_layout(showlegend=False, coloraxis_showscale=False, margin={"r": 80})
        st.plotly_chart(chart, use_container_width=True)
with tabs[3]:
    if not hourly.empty:
        hourly["hour_timestamp"]=pd.to_datetime(hourly.hour_timestamp); h=hourly[hourly.station_id.astype(str)==station].copy(); h["hour"]=h.hour_timestamp.dt.hour; st.plotly_chart(px.line(h.groupby(["hour","pollutant_code"],as_index=False).avg_value.mean(),x="hour",y="avg_value",color="pollutant_code"),use_container_width=True)
with tabs[4]:
    if not hourly.empty and "wind_speed" in hourly: st.plotly_chart(px.scatter(hourly[hourly.pollutant_code=="pm25"],x="wind_speed",y="avg_value",title="PM2.5 vs wind speed"),use_container_width=True)
with tabs[5]:
    st.subheader("Available data")
    data_counts = pd.DataFrame({"table": ["Daily AQI", "Hourly aggregates", "Weather"], "rows": [len(daily), len(hourly), len(weather)]})
    st.dataframe(data_counts, hide_index=True, use_container_width=True)
    st.dataframe(daily.head(20), hide_index=True, use_container_width=True)
    st.subheader("Pipeline audit trail")
    if logs.empty:
        st.info("No extraction runs have been recorded. Live pipeline runs write here; demo data is recorded after the next `python run_pipeline.py --demo` run.")
    else:
        st.dataframe(logs, hide_index=True, use_container_width=True)
    st.subheader("Rejected records")
    if rejections.empty:
        st.success("No rejected records were recorded.")
    else:
        st.dataframe(rejections, hide_index=True, use_container_width=True)
