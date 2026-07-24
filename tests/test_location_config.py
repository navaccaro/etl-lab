import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from weather_etl.location_config import load_locations


def test_load_locations_returns_forest_park() -> None:
    locations = load_locations()

    assert len(locations) == 1

    location = locations[0]

    assert location.location_id == "forest-park-il"
    assert location.display_name == "Forest Park, Illinois"
    assert location.latitude == 41.8795
    assert location.longitude == -87.8137
    assert location.timezone == "America/Chicago"
    assert location.enabled is True


def test_loaded_location_serializes_expected_fields() -> None:
    location = load_locations()[0]

    assert set(location.model_dump()) == {
        "version",
        "location_id",
        "display_name",
        "latitude",
        "longitude",
        "timezone",
        "enabled",
    }


def test_location_is_immutable() -> None:
    location = load_locations()[0]

    with pytest.raises(ValidationError):
        location.latitude = 0

def write_schema(path: Path) -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "version",
            "location_id",
            "display_name",
            "latitude",
            "longitude",
            "timezone",
            "enabled",
        ],
        "properties": {
            "version": {"const": 1},
            "location_id": {
                "type": "string",
                "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$",
            },
            "display_name": {
                "type": "string",
                "minLength": 3,
                "maxLength": 100,
            },
            "latitude": {
                "type": "number",
                "minimum": -90,
                "maximum": 90,
            },
            "longitude": {
                "type": "number",
                "minimum": -180,
                "maximum": 180,
            },
            "timezone": {
                "type": "string",
                "minLength": 1,
            },
            "enabled": {"type": "boolean"},
        },
    }

    path.write_text(json.dumps(schema), encoding="utf-8")


def write_location(
    path: Path,
    **overrides: Any,
) -> None:
    location = {
        "version": 1,
        "location_id": path.stem,
        "display_name": "Test Location",
        "latitude": 41.0,
        "longitude": -87.0,
        "timezone": "America/Chicago",
        "enabled": True,
    }

    location.update(overrides)

    path.write_text(
        yaml.safe_dump(location, sort_keys=False),
        encoding="utf-8",
    )

def test_missing_locations_directory_raises(
    tmp_path: Path,
) -> None:
    schema_path = tmp_path / "schema.json"
    write_schema(schema_path)

    with pytest.raises(
        FileNotFoundError,
        match="Locations directory not found",
    ):
        load_locations(
            locations_directory=tmp_path / "missing",
            schema_path=schema_path,
        )


def test_empty_locations_directory_raises(
    tmp_path: Path,
) -> None:
    locations_directory = tmp_path / "locations"
    locations_directory.mkdir()

    schema_path = tmp_path / "schema.json"
    write_schema(schema_path)

    with pytest.raises(
        FileNotFoundError,
        match="No YAML location files found",
    ):
        load_locations(
            locations_directory=locations_directory,
            schema_path=schema_path,
        )


def test_disabled_location_is_not_returned(
    tmp_path: Path,
) -> None:
    locations_directory = tmp_path / "locations"
    locations_directory.mkdir()

    schema_path = tmp_path / "schema.json"
    write_schema(schema_path)

    write_location(
        locations_directory / "disabled-location.yaml",
        enabled=False,
    )

    locations = load_locations(
        locations_directory=locations_directory,
        schema_path=schema_path,
    )

    assert locations == []