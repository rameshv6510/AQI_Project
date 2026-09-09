"""Airflow DAG. Mount this project in the Airflow container before enabling."""
from datetime import datetime, timedelta
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from src.pipeline import run_end_to_end_pipeline
    with DAG("aqi_weather_etl_pipeline",start_date=datetime(2026,9,1),schedule="@daily",catchup=False,default_args={"retries":2,"retry_delay":timedelta(minutes=5)}) as dag:
        run_pipeline=PythonOperator(task_id="run_end_to_end_pipeline",python_callable=run_end_to_end_pipeline)
except ImportError:
    dag = None
