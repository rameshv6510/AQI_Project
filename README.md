# Bengaluru AQI Analytics

An end-to-end data engineering project for Bengaluru air-quality analysis. It ingests station-level pollution observations from OpenAQ and weather history from Open-Meteo, validates and aggregates the data, calculates CPCB AQI, and presents the results in a Streamlit dashboard.

## Features

- OpenAQ pollution ingestion for configured Bengaluru monitoring stations
- Open-Meteo weather ingestion and station-level joins
- Unit normalization, validation, deduplication, and rejected-record tracking
- Hourly aggregates and daily CPCB AQI marts
- Interactive AQI trends, pollutant distribution, station comparison, hourly patterns, and weather analysis
- SQLite by default, with PostgreSQL configuration available
- Optional Apache Airflow Docker setup

## Requirements

- Python 3.10 or newer
- An OpenAQ API key for live pollution data
- Docker Desktop only if you want to run Airflow

## Installation

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace `your_openaq_api_key_here` with your API key. `.env` is intentionally ignored by Git. SQLite is the default and stores its local database as `aqi_pipeline.db`, which is also ignored.

## Run With Demo Data

Demo mode creates clearly labelled synthetic data without calling external APIs:

```powershell
python run_pipeline.py --demo --days 14
streamlit run dashboard/app.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`.

## Run With Live Data

After configuring `OPENAQ_API_KEY`:

```powershell
python run_pipeline.py --days 14
streamlit run dashboard/app.py
```

## Tests

```powershell
pytest -q
```

The tests cover AQI calculations, category mapping, timestamp parsing, unit normalization, and validation of outlier records.

## Airflow

To run the optional Airflow environment:

```powershell
docker compose -f docker/docker-compose.yaml up
```

## Project Structure

```text
dashboard/       Streamlit dashboard
dags/            Airflow DAG
docs/            Architecture, data dictionary, and validation notes
sql/             Schema and sample queries
src/             Configuration, ingestion, transformation, and database code
tests/           Automated tests
run_pipeline.py  Pipeline entry point
```

Generated raw data, local databases, logs, virtual environments, caches, and secret environment files are excluded through `.gitignore`. Commit `.env.example`, never `.env`.

## Data Sources

- [OpenAQ](https://openaq.org/) for air-quality observations
- [Open-Meteo](https://open-meteo.com/) for historical weather data
- CPCB breakpoints for AQI calculation
