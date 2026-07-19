from __future__ import annotations

import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


logger = logging.getLogger(__name__)


API_URL = "https://api.open-meteo.com/v1/forecast"

# Approximate coordinates for Forest Park, Illinois.
LATITUDE = 41.88
LONGITUDE = -87.81


def extract_weather() -> dict[str, Any]:
    """Retrieve current weather data from the API without modifying it."""

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
        ],
        "timezone": "America/Chicago",
    }

    logger.info("Requesting weather data from Open-Meteo.")

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    logger.info("Weather data retrieved successfully.")

    return response.json()


def save_raw_weather(
    payload: dict[str, Any],
    output_directory: Path,
) -> Path:
    """Save the unmodified API response to a timestamped JSON file."""

    output_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = output_directory / f"weather_{timestamp}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    logger.info("Saved raw weather data to %s", output_path)

    return output_path