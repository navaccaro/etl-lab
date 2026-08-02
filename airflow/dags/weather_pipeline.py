from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pendulum
from airflow.providers.standard.operators.python import PythonOperator

from airflow import DAG
from weather_etl.extract_weather import extract_weather, save_raw_weather
from weather_etl.load_weather import load_weather
from weather_etl.transform_weather import transform_weather

logger = logging.getLogger(__name__)

RAW_DATA_DIRECTORY = Path("/opt/airflow/project/data/raw")


def extract_and_save_weather() -> dict[str, Any]:
    """Extract weather data, preserve the raw response, and return the payload."""

    logger.info("Starting weather extraction.")

    payload = extract_weather()
    raw_file = save_raw_weather(payload, RAW_DATA_DIRECTORY)

    logger.info("Raw weather payload saved to %s", raw_file)

    return payload


def transform_weather_task(payload: dict[str, Any]) -> dict[str, Any]:
    """Transform and validate the extracted weather payload."""

    logger.info("Starting weather transformation.")

    record = transform_weather(payload)

    logger.info(
        "Transformed observation for %s at %s.",
        record["location_name"],
        record["observed_at"],
    )

    return record


def load_weather_task(record: dict[str, Any]) -> None:
    """Load the transformed weather observation into PostgreSQL."""

    logger.info(
        "Loading weather observation for %s at %s.",
        record["location_name"],
        record["observed_at"],
    )

    load_weather(record)

    logger.info("Weather observation loaded successfully.")


with DAG(
    dag_id="weather_etl_pipeline",
    description="Extract, transform, and load current Forest Park weather data.",
    start_date=pendulum.datetime(2026, 7, 1, tz="America/Chicago"),
    schedule=None,
    catchup=False,
    tags=["weather", "etl", "learning"],
    default_args={
        "owner": "navaccaro",
        "retries": 2,
        "retry_delay": pendulum.duration(seconds=15),
    },
) as dag:
    extract_task = PythonOperator(
        task_id="extract_weather",
        python_callable=extract_and_save_weather,
    )

    transform_task = PythonOperator(
        task_id="transform_weather",
        python_callable=transform_weather_task,
        op_args=[extract_task.output],
    )

    load_task = PythonOperator(
        task_id="load_weather",
        python_callable=load_weather_task,
        op_args=[transform_task.output],
    )

    extract_task >> transform_task >> load_task