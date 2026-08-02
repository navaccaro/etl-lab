from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from weather_etl.location_config import (
    LOCATIONS_DIRECTORY,
    SCHEMA_PATH,
    load_locations,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Add a validated weather location configuration."
    )

    parser.add_argument("--id", required=True, dest="location_id")
    parser.add_argument("--name", required=True, dest="display_name")
    parser.add_argument("--latitude", required=True, type=float)
    parser.add_argument("--longitude", required=True, type=float)
    parser.add_argument("--timezone", required=True)

    parser.add_argument(
        "--disabled",
        action="store_true",
        help="Create the location with enabled set to false.",
    )

    return parser


def build_location(args: argparse.Namespace) -> dict[str, object]:
    """Build a location configuration from CLI arguments."""

    return {
        "version": 1,
        "location_id": args.location_id,
        "display_name": args.display_name,
        "latitude": args.latitude,
        "longitude": args.longitude,
        "timezone": args.timezone,
        "enabled": not args.disabled,
    }


def write_location(
    location: dict[str, object],
    locations_directory: Path = LOCATIONS_DIRECTORY,
) -> Path:
    """Write a new location configuration without overwriting existing files."""

    location_id = str(location["location_id"])
    destination = locations_directory / f"{location_id}.yaml"

    if destination.exists():
        raise FileExistsError(
            f"Location configuration already exists: {destination}"
        )

    destination.write_text(
        yaml.safe_dump(
            location,
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    return destination

def add_location(
    location: dict[str, object],
    locations_directory: Path = LOCATIONS_DIRECTORY,
    schema_path: Path = SCHEMA_PATH,
) -> Path:
    """Write and validate a new location configuration."""

    destination = write_location(
        location=location,
        locations_directory=locations_directory,
    )

    try:
        load_locations(
            locations_directory=locations_directory,
            schema_path=schema_path,
        )
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    return destination


def main() -> int:
    """Add and validate a new location configuration."""

    parser = build_parser()
    args = parser.parse_args()

    location = build_location(args)
    destination = add_location(location)

    print(f"Created location configuration: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())