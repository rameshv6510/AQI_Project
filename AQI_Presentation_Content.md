# AQI Project Presentation Content

## 1. Project Overview

**Air Quality Index Analysis and Prediction — Part 1**

- City: Bengaluru, Karnataka.
- Goal: collect pollution and weather data, apply quality checks, build AQI analytics, and present insights through Streamlit.
- Outcome: a repeatable data-engineering platform ready for a future Part 2 AQI forecasting model.

## 2. Dataset & Data Sources

- **OpenAQ API v3:** station-level PM2.5, PM10, NO2, SO2, CO, and O3 observations.
- **Open-Meteo API:** hourly temperature, humidity, wind, precipitation, and pressure.
- Primary station: BTM Layout (OpenAQ ID 594); additional Bengaluru stations support comparison.
- Raw responses are stored unchanged as timestamped JSON files.

## 3. Proposed Data Architecture

`OpenAQ + Open-Meteo → Python collectors → raw JSON → staging → cleaned QC → SQLite/PostgreSQL gold marts → Streamlit dashboard`

Airflow schedules: `extract_openaq → extract_weather → load_staging → load_clean → build_analytics`.

## 4. Data Ingestion Pipeline

- Python `requests` calls public APIs.
- Each response lands in `data/raw/` before transformation.
- `extraction_log` records run ID, source, status, row count, errors, and runtime.
- CLI run: `python run_pipeline.py --days 14`.
- Airflow supplies scheduled execution.

## 5. ETL & Data Quality

- Normalize timestamps, pollutant codes, and measurement units.
- Convert CO ppm to mg/m³ where required.
- Deduplicate station + pollutant + timestamp combinations.
- Validate physical pollutant and weather ranges.
- Store invalid rows and their reasons in `rejected_records_log`.

## 6. Database / Star Schema

- Dimensions: `dim_stations`, `dim_pollutants`, `dim_dates`.
- Facts: `fact_raw_readings`, `fact_weather`, `fact_hourly_aggregates`, `fact_daily_aqi`.
- Gold mart: daily AQI, category, dominant pollutant, pollutant averages, and weather summaries.
- Audit tables: `extraction_log`, `rejected_records_log`.

## 7. Feature Engineering — Part 2 Preview

Part 1 has no model training or deployment. Future features include lagged AQI, rolling averages, weather variables, and calendar attributes. The target is next-day AQI or AQI category.

## 8. Dashboard & Analytics

1. AQI trend by station and date.
2. Pollutant contribution analysis.
3. Cross-station comparison.
4. Hourly and diurnal patterns.
5. Weather impact on PM2.5.
6. Data marts and pipeline audit logs.

## 9. Pipeline Execution Evidence

```text
pytest -q
...... [100%]
6 passed
```

Tests cover AQI computation, category mapping, unit normalization, timestamp parsing, and rejection of out-of-range records.

## 10. MLOps Extension — Part 2

- Compare regression and classification models.
- Use chronological train/validation/test splits.
- Track experiments in MLflow.
- Register the best model.
- Serve predictions using FastAPI and Docker.
- Monitor data quality, drift, prediction error, latency, and retraining criteria.

## 11. Results & Key Insights

- Raw retention and logs make the pipeline traceable.
- Quality rules protect analytical results.
- Gold marts provide queryable AQI, pollutant, weather, and station insights.
- The architecture supports an MLOps forecasting extension.

## 12. Challenges & Learning Outcomes

- Stations can expose different pollutant subsets.
- Public APIs can return sparse data or fail temporarily.
- Unit, time-zone, and timestamp consistency require careful handling.
- The project demonstrates layered ETL, star-schema design, testing, orchestration, and dashboard development.

## 13. Conclusion & Future Scope

Part 1 delivers public API ingestion, immutable raw storage, cleaning, CPCB AQI calculation, analytical data marts, orchestration, and Streamlit analytics. Part 2 will add AQI prediction, experiment tracking, deployment, monitoring, and retraining.

## 14. References

- OpenAQ API v3: https://docs.openaq.org/
- Open-Meteo: https://open-meteo.com/en/docs
- Central Pollution Control Board National AQI framework.
- Apache Airflow: https://airflow.apache.org/
- Streamlit: https://streamlit.io/

## 15. Thank You

Questions & Discussion
