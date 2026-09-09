# Architecture

`OpenAQ + Open-Meteo → Python collectors → immutable raw JSON → staging → cleaned QC → fact tables / AQI gold marts → Streamlit`

Apache Airflow schedules the same ETL workflow daily. Failed validations are recorded in `rejected_records_log`; extraction outcomes are stored in `extraction_log`.
