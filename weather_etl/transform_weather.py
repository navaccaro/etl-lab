from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def transform_weather(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert the raw API payload into our destination-table structure."""

    logger.info("Transforming weather payload.")

    if "current" not in payload:
        raise ValueError("Weather payload does not contain a 'current' section.")

    current = payload["current"]

    required_fields = [
        "time",
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "weather_code",
        "wind_speed_10m",
    ]

    missing_fields = [field for field in required_fields if field not in current]

    if missing_fields:
        raise ValueError(
            f"Weather payload is missing required fields: {missing_fields}"
        )

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    latitude = payload["latitude"]
    longitude = payload["longitude"]

    if not -100 <= temperature <= 60:
        logger.error("Temperature out of range: %s", temperature)
        raise ValueError(f"Temperature out of range: {temperature}")

    if not 0 <= humidity <= 100:
        raise ValueError(f"Humidity out of range: {humidity}")

    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude out of range: {latitude}")

    if not -180 <= longitude <= 180:
        logger.error("Longitude out of range: %s", longitude)
        raise ValueError(f"Longitude out of range: {longitude}")

    logger.info(
        "Transformation complete for observation at %s",
        current["time"],
    )

    return {
        "location_name": "Forest Park, IL",
        "latitude": payload["latitude"],
        "longitude": payload["longitude"],
        "observed_at": current["time"],
        "temperature_c": current["temperature_2m"],
        "apparent_temperature_c": current["apparent_temperature"],
        "relative_humidity_pct": current["relative_humidity_2m"],
        "precipitation_mm": current["precipitation"],
        "weather_code": current["weather_code"],
        "wind_speed_kmh": current["wind_speed_10m"],
    }
