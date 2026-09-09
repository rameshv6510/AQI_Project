# Validation Rules

- Deduplicate by station, pollutant, and timestamp.
- PM2.5: 0–1000 µg/m³; PM10: 0–1500 µg/m³; NO2/O3: 0–1000 µg/m³; SO2: 0–2000 µg/m³; CO: 0–100 mg/m³.
- Temperature: −10–60 °C; relative humidity: 0–100%; wind speed: 0–200 km/h.
- Reject records with missing timestamps or values outside these physical ranges.
