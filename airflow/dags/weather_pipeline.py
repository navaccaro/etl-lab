from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, TaskGroup

from weather_etl.extract_weather import extract_weather, save_raw_weather
from weather_etl.load_weather import load_weather
from weather_etl.location_config import load_locations
from weather_etl.models import WeatherLocation
from weather_etl.transform_weather import transform_weather

logger = logging.getLogger(__name__)

RAW_DATA_DIRECTORY = Path("/opt/airflow/project/data/raw")


def extract_and_save_weather(
    location_data: dict[str, Any],
) -> dict[str, Any]:
    """Extract and preserve raw weather data for one location."""

    location = WeatherLocation.model_validate(location_data)

    logger.info(
        "Starting weather extraction for %s.",
        location.location_id,
    )

    payload = extract_weather(location)

    raw_file = save_raw_weather(
        payload,
        RAW_DATA_DIRECTORY,
    )

    logger.info(
        "Raw weather payload for %s saved to %s.",
        location.location_id,
        raw_file,
    )

    return payload


def transform_weather_task(
    payload: dict[str, Any],
    location_data: dict[str, Any],
) -> dict[str, Any]:
    """Transform one location's raw weather payload."""

    location = WeatherLocation.model_validate(location_data)

    logger.info(
        "Starting weather transformation for %s.",
        location.location_id,
    )

    record = transform_weather(
        payload,
        location,
    )

    logger.info(
        "Transformed observation for %s at %s.",
        location.location_id,
        record["observed_at"],
    )

    return record


def load_weather_task(record: dict[str, Any]) -> None:
    """Load one transformed weather observation."""

    logger.info(
        "Loading weather observation for %s at %s.",
        record["location_id"],
        record["observed_at"],
    )

    load_weather(record)

    logger.info("Weather observation loaded successfully.")


locations = load_locations()


with DAG(
    dag_id="weather_etl_pipeline",
    description="Extract, transform, and load configured weather locations.",
    start_date=pendulum.datetime(
        2026,
        7,
        1,
        tz="America/Chicago",
    ),
    schedule=None,
    catchup=False,
    tags=["weather", "etl", "learning"],
    default_args={
        "owner": "navaccaro",
        "retries": 2,
        "retry_delay": pendulum.duration(seconds=15),
    },
) as dag:
    for location in locations:
        location_data = location.model_dump()

        group_id = location.location_id.replace("-", "_")

        with TaskGroup(
            group_id=group_id,
            tooltip=location.display_name,
        ):
            extract_task = PythonOperator(
                task_id="extract",
                python_callable=extract_and_save_weather,
                op_kwargs={
                    "location_data": location_data,
                },
            )

            transform_task = PythonOperator(
                task_id="transform",
                python_callable=transform_weather_task,
                op_kwargs={
                    "payload": extract_task.output,
                    "location_data": location_data,
                },
            )

            load_task = PythonOperator(
                task_id="load",
                python_callable=load_weather_task,
                op_kwargs={
                    "record": transform_task.output,
                },
            )

            extract_task >> transform_task >> load_task
