from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from weather_etl.models import WeatherLocation

import requests

logger = logging.getLogger(__name__)


API_URL = "https://api.open-meteo.com/v1/forecast"


def extract_weather(
    location: WeatherLocation,
) -> dict[str, Any]:
    """Retrieve current weather data for one configured location."""

    params: dict[str, str | float | list[str]] = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
        ],
        "timezone": location.timezone,
    }

    logger.info("Requesting weather data from Open-Meteo for %s.", location.location_id)

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    logger.info("Weather data retrieved successfully.")

    payload = response.json()

    if not isinstance(payload, dict):
        raise ValueError("Weather API response must contain a JSON object.")

    return cast(dict[str, Any], payload)


def save_raw_weather(
    payload: dict[str, Any],
    output_directory: Path,
) -> Path:
    """Save the unmodified API response to a timestamped JSON file."""

    output_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_path = output_directory / f"weather_{timestamp}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    logger.info("Saved raw weather data to %s", output_path)

    return output_path
