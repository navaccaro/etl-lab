from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

from weather_etl.extract_weather import extract_weather, save_raw_weather
from weather_etl.load_weather import load_weather
from weather_etl.location_config import load_locations
from weather_etl.logging_config import configure_logging
from weather_etl.transform_weather import transform_weather

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"


def run_pipeline() -> None:
    """Run the complete extract-transform-load workflow."""

    configure_logging()

    try:
        logger.info("Starting weather ETL pipeline.")

        load_dotenv(PROJECT_ROOT / ".env")

        logger.info("Loading environment variables.")

        locations = load_locations()

        for location in locations:
            logger.info(
                "Processing weather location: %s",
                location.location_id,
            )

            raw_payload = extract_weather(location)

            raw_file = save_raw_weather(
                raw_payload,
                RAW_DATA_DIRECTORY,
            )
            logger.info("Raw weather data saved to %s", raw_file)

            transformed_record = transform_weather(
                raw_payload,
                location,
            )

            logger.info(
                "Weather observation: %s | %.1f°C",
                transformed_record["observed_at"],
                transformed_record["temperature_c"],
            )

            load_weather(transformed_record)

        logger.info("Weather ETL pipeline completed successfully.")

    except Exception:
        logger.exception("Weather ETL pipeline failed.")
        raise


if __name__ == "__main__":
    run_pipeline()
