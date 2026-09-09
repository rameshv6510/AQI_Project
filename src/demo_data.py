"""Create deterministic, clearly non-live sample data for dashboard demonstrations."""
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

from src.config import STATIONS
from src.db import get_engine, init_db, log_extraction
from src.transform.analytics import build_daily_aqi_marts, build_hourly_aggregates
from src.transform.cleaning import clean_pollution_data, clean_weather_data


def seed_demo_data(days=14):
    """Populate local marts with synthetic demonstration observations.

    This is only for dashboard demonstration when live API history is unavailable.
    It never writes to the raw landing zone or claims to be live data.
    """
    engine = get_engine()
    init_db(engine)
    rng = np.random.default_rng(42)
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    hours = pd.date_range(end=end, periods=days * 24, freq="h", tz="UTC")
    pollution_rows, weather_rows = [], []
    baselines = {"pm25": 48, "pm10": 85, "no2": 35, "so2": 14, "co": 1.1, "o3": 42}
    for station_index, station in enumerate(STATIONS):
        station_factor = 1 + station_index * 0.07
        for hour_index, timestamp in enumerate(hours):
            hour = timestamp.hour
            traffic_factor = 1.35 if hour in (8, 9, 10, 18, 19, 20) else 0.85
            # Rotate plausible dominant conditions across station-days so the
            # dashboard's pollutant comparison is meaningful in demo mode.
            dominant = ("pm25", "pm10", "no2", "o3", "pm25", "co")[(hour_index // 24 + station_index) % 6]
            temperature = 23 + 5 * np.sin((hour - 7) * np.pi / 12) + rng.normal(0, .7)
            humidity = max(35, min(95, 72 - 10 * np.sin((hour - 7) * np.pi / 12) + rng.normal(0, 3)))
            wind = max(.5, 10 + 3 * np.sin(hour * np.pi / 12) + rng.normal(0, 1.5))
            weather_rows.append({"station_id": station["station_id"], "timestamp": timestamp, "temperature": temperature, "relative_humidity": humidity, "wind_speed": wind, "wind_direction": rng.uniform(0, 360), "precipitation": max(0, rng.normal(.1, .25)), "surface_pressure": 1012 + rng.normal(0, 2)})
            for pollutant, baseline in baselines.items():
                dominance_multiplier = {
                    "pm25": 1.0,
                    "pm10": 2.1 if pollutant == "pm10" else 1.0,
                    "no2": 4.2 if pollutant == "no2" else 1.0,
                    "o3": 3.3 if pollutant == "o3" else 1.0,
                    "co": 3.8 if pollutant == "co" else 1.0,
                }[dominant]
                concentration = max(0.01, baseline * station_factor * traffic_factor * dominance_multiplier * (1.12 - wind / 100) + rng.normal(0, baseline * .08))
                pollution_rows.append({"station_id": station["station_id"], "pollutant_code": pollutant, "value": concentration, "unit": "mg/m³" if pollutant == "co" else "µg/m³", "timestamp": timestamp, "source": "Demo data — not live", "extracted_at": datetime.now(timezone.utc)})
    pollution, _ = clean_pollution_data(pd.DataFrame(pollution_rows), engine)
    weather, _ = clean_weather_data(pd.DataFrame(weather_rows), engine)
    hourly = build_hourly_aggregates(pollution, weather, engine)
    daily = build_daily_aqi_marts(pollution, weather, engine)
    log_extraction(
        engine,
        f"demo_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}",
        "Demo data",
        "SUCCESS",
        len(pollution) + len(weather),
        "Synthetic data - not live",
    )
    return {"pollution_records": len(pollution), "weather_records": len(weather), "hourly_aggregates": len(hourly), "daily_aqi_records": len(daily)}
