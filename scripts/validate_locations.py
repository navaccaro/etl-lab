from __future__ import annotations

import sys

from weather_etl.location_config import load_locations


def main() -> int:
    locations = load_locations()

    print(f"Validated {len(locations)} enabled location(s).")

    for location in locations:
        print(f"- {location.location_id}: {location.display_name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
