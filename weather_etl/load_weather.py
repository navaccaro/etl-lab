from __future__ import annotations

import logging
import os
from typing import Any

import psycopg


logger = logging.getLogger(__name__)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location_name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    temperature_c DOUBLE PRECISION,
    apparent_temperature_c DOUBLE PRECISION,
    relative_humidity_pct INTEGER,
    precipitation_mm DOUBLE PRECISION,
    weather_code INTEGER,
    wind_speed_kmh DOUBLE PRECISION,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (location_name, observed_at)
);
"""


INSERT_WEATHER_SQL = """
INSERT INTO weather_observations (
    location_name,
    latitude,
    longitude,
    observed_at,
    temperature_c,
    apparent_temperature_c,
    relative_humidity_pct,
    precipitation_mm,
    weather_code,
    wind_speed_kmh
)
VALUES (
    %(location_name)s,
    %(latitude)s,
    %(longitude)s,
    %(observed_at)s,
    %(temperature_c)s,
    %(apparent_temperature_c)s,
    %(relative_humidity_pct)s,
    %(precipitation_mm)s,
    %(weather_code)s,
    %(wind_speed_kmh)s
)
ON CONFLICT (location_name, observed_at)
DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    temperature_c = EXCLUDED.temperature_c,
    apparent_temperature_c = EXCLUDED.apparent_temperature_c,
    relative_humidity_pct = EXCLUDED.relative_humidity_pct,
    precipitation_mm = EXCLUDED.precipitation_mm,
    weather_code = EXCLUDED.weather_code,
    wind_speed_kmh = EXCLUDED.wind_speed_kmh,
    loaded_at = CURRENT_TIMESTAMP;
"""


def get_connection_string() -> str:
    """Build a PostgreSQL connection string from environment variables."""

    required_variables = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing_variables = [
        name for name in required_variables if not os.getenv(name)
    ]

    if missing_variables:
        raise RuntimeError(
            f"Missing database environment variables: {missing_variables}"
        )

    return (
        f"host={os.environ['POSTGRES_HOST']} "
        f"port={os.environ['POSTGRES_PORT']} "
        f"dbname={os.environ['POSTGRES_DB']} "
        f"user={os.environ['POSTGRES_USER']} "
        f"password={os.environ['POSTGRES_PASSWORD']}"
    )


def load_weather(record: dict[str, Any]) -> None:
    """Create the destination table and load one weather observation."""

    logger.info("Connecting to PostgreSQL.")

    connection_string = get_connection_string()

    with psycopg.connect(connection_string) as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TABLE_SQL)
            logger.info("Verified weather_observations table exists.")
            cursor.execute(INSERT_WEATHER_SQL, record)
            logger.info(
                "Loaded weather observation for %s",
                record["observed_at"],
            )