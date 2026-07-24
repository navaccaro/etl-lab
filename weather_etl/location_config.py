from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCATIONS_DIRECTORY = PROJECT_ROOT / "config" / "locations"
SCHEMA_PATH = PROJECT_ROOT / "config" / "schemas" / "weather-location.schema.json"


def _load_schema() -> dict[str, Any]:
    """Load and return the location schema from disk."""

    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
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


def load_locations() -> list[dict[str, Any]]:
    """Load all enabled weather location definitions from config/locations."""

    if not LOCATIONS_DIRECTORY.is_dir():
        raise FileNotFoundError(
            f"Locations directory not found: {LOCATIONS_DIRECTORY}"
        )

    yaml_files = sorted(LOCATIONS_DIRECTORY.glob("*.yaml"))
    if not yaml_files:
        raise FileNotFoundError(
            f"No YAML location files found in: {LOCATIONS_DIRECTORY}"
        )

    schema = _load_schema()
    validator = Draft202012Validator(schema)
    locations: list[dict[str, Any]] = []

    for path in yaml_files:
        location = _load_location_file(path)
        _validate_location(location, validator, path)

        if location["enabled"]:
            locations.append(location)

    return locations


