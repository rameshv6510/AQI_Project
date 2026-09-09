# Data Dictionary

- `dim_stations`: monitoring location metadata.
- `dim_pollutants`: pollutant codes, units, and CPCB reference limits.
- `dim_dates`: calendar attributes for analytical joins.
- `fact_raw_readings`: atomic pollutant observations.
- `fact_weather`: hourly weather observations.
- `fact_hourly_aggregates`: hourly pollutant summaries with weather.
- `fact_daily_aqi`: daily CPCB AQI, category, dominant pollutant, averages, and weather summary.
