from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from weather_etl.models import WeatherLocation

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCATIONS_DIRECTORY = PROJECT_ROOT / "config" / "locations"
SCHEMA_PATH = PROJECT_ROOT / "config" / "schemas" / "weather-location.schema.json"


def _load_schema(path: Path) -> dict[str, Any]:
    """Load and return the location schema from disk."""

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
        

def _load_location_file(path: Path) -> dict[str, Any]:
    """Load a single YAML location file and return its parsed data."""

    with path.open("r", encoding="utf-8") as handle:
        location = yaml.safe_load(handle)

    if not isinstance(location, dict):
        raise ValueError(f"Location file {path} must contain a mapping.")

    return location


def _validate_location(
    location: dict[str, Any],
    validator: Draft202012Validator,
    source_path: Path,
) -> None:
    """Validate a location mapping against the JSON schema."""

    errors = sorted(validator.iter_errors(location), key=lambda error: error.path)

    if errors:
        message = "; ".join(
            f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ValueError(
            f"Location validation failed for {source_path.name}: {message}"
        )


def _validate_unique_locations(
    locations: list[WeatherLocation],
) -> None:
    """Reject duplicate IDs and coordinates."""

    seen_ids: set[str] = set()
    seen_coordinates: set[tuple[float, float]] = set()

    for location in locations:
        if location.location_id in seen_ids:
            raise ValueError(
                f"Duplicate location ID: {location.location_id}"
            )

        coordinates = (
            location.latitude,
            location.longitude,
        )

        if coordinates in seen_coordinates:
            raise ValueError(
                "Duplicate location coordinates: "
                f"{location.latitude}, {location.longitude}"
            )

        seen_ids.add(location.location_id)
        seen_coordinates.add(coordinates)


def _validate_unique_locations(
    locations: list[WeatherLocation],
) -> None:
    """Reject duplicate location IDs and coordinates."""

    seen_ids: set[str] = set()
    seen_coordinates: set[tuple[float, float]] = set()

    for location in locations:
        if location.location_id in seen_ids:
            raise ValueError(
                f"Duplicate location ID: {location.location_id}"
            )

        coordinates = (
            location.latitude,
            location.longitude,
        )

        if coordinates in seen_coordinates:
            raise ValueError(
                "Duplicate location coordinates: "
                f"{location.latitude}, {location.longitude}"
            )

        seen_ids.add(location.location_id)
        seen_coordinates.add(coordinates)


def load_locations(
    locations_directory: Path = LOCATIONS_DIRECTORY,
    schema_path: Path = SCHEMA_PATH,
) -> list[WeatherLocation]:
    """Load all enabled weather location definitions from config/locations."""

    if not locations_directory.is_dir():
        raise FileNotFoundError(
            f"Locations directory not found: {locations_directory}"
        )

    yaml_files = sorted(locations_directory.glob("*.yaml"))

    if not yaml_files:
        raise FileNotFoundError(
            f"No YAML location files found in: {locations_directory}"
        )

    schema = _load_schema(schema_path)
    validator = Draft202012Validator(schema)
    all_locations: list[WeatherLocation] = []

    for path in yaml_files:
        location_data = _load_location_file(path)
        _validate_location(location_data, validator, path)

        location = WeatherLocation.model_validate(location_data)

        if location.location_id != path.stem:
            raise ValueError(
                f"Location ID '{location.location_id}' does not match "
                f"filename '{path.name}'."
            )

        all_locations.append(location)

    _validate_unique_locations(all_locations)

    return [
        location
        for location in all_locations
        if location.enabled
    ]
