import json
from pathlib import Path

import pytest
import yaml

from scripts.add_location import add_location


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

    path.write_text(
        json.dumps(schema),
        encoding="utf-8",
    )


def valid_location() -> dict[str, object]:
    return {
        "version": 1,
        "location_id": "chicago-il",
        "display_name": "Chicago, Illinois",
        "latitude": 41.8781,
        "longitude": -87.6298,
        "timezone": "America/Chicago",
        "enabled": True,
    }


def test_add_location_creates_yaml(tmp_path: Path) -> None:
    locations_directory = tmp_path / "locations"
    locations_directory.mkdir()

    schema_path = tmp_path / "schema.json"
    write_schema(schema_path)

    destination = add_location(
        location=valid_location(),
        locations_directory=locations_directory,
        schema_path=schema_path,
    )

    assert destination.exists()

    contents = yaml.safe_load(destination.read_text(encoding="utf-8"))

    assert contents == valid_location()


def test_add_location_refuses_overwrite(tmp_path: Path) -> None:
    locations_directory = tmp_path / "locations"
    locations_directory.mkdir()

    schema_path = tmp_path / "schema.json"
    write_schema(schema_path)

    existing = locations_directory / "chicago-il.yaml"
    existing.write_text(
        "existing: true\n",
        encoding="utf-8",
    )

    with pytest.raises(FileExistsError):
        add_location(
            location=valid_location(),
            locations_directory=locations_directory,
            schema_path=schema_path,
        )

    assert existing.read_text(encoding="utf-8") == "existing: true\n"


def test_add_location_invalid_config_is_removed(
    tmp_path: Path,
) -> None:
    locations_directory = tmp_path / "locations"
    locations_directory.mkdir()

    schema_path = tmp_path / "schema.json"
    write_schema(schema_path)

    location = valid_location()
    location["latitude"] = 100.0

    destination = locations_directory / "chicago-il.yaml"

    with pytest.raises(ValueError):
        add_location(
            location=location,
            locations_directory=locations_directory,
            schema_path=schema_path,
        )

    assert not destination.exists()


def test_add_location_preserves_existing_files_on_failure(
    tmp_path: Path,
) -> None:
    locations_directory = tmp_path / "locations"
    locations_directory.mkdir()

    schema_path = tmp_path / "schema.json"
    write_schema(schema_path)

    existing = locations_directory / "existing-location.yaml"
    existing.write_text(
        (
            "version: 1\n"
            "location_id: existing-location\n"
            "display_name: Existing Location\n"
            "latitude: 40.0\n"
            "longitude: -80.0\n"
            "timezone: America/New_York\n"
            "enabled: true\n"
        ),
        encoding="utf-8",
    )

    location = valid_location()
    location["latitude"] = 100.0

    with pytest.raises(ValueError):
        add_location(
            location=location,
            locations_directory=locations_directory,
            schema_path=schema_path,
        )

    assert existing.exists()
