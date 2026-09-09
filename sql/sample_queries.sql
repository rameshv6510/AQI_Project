-- Daily AQI by station
SELECT station_id, date, aqi_value, aqi_category, dominant_pollutant
FROM fact_daily_aqi ORDER BY date DESC;

-- Recent pipeline runs
SELECT * FROM extraction_log ORDER BY timestamp DESC;

-- Quality failures
SELECT source_table, reason, COUNT(*) AS rejected_count
FROM rejected_records_log GROUP BY source_table, reason;
