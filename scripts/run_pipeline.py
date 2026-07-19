from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

from scripts.extract_weather import extract_weather, save_raw_weather
from scripts.load_weather import load_weather
from scripts.logging_config import configure_logging
from scripts.transform_weather import transform_weather


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

        logger.info("Extracting weather data.")
        raw_payload = extract_weather()

        raw_file = save_raw_weather(raw_payload, RAW_DATA_DIRECTORY)
        logger.info("Raw weather data saved to %s", raw_file)

        logger.info("Transforming weather data.")
        transformed_record = transform_weather(raw_payload)

        logger.info(
            "Weather observation: %s | %.1f°C",
            transformed_record["observed_at"],
            transformed_record["temperature_c"],
        )

        logger.info("Loading weather data into PostgreSQL.")
        load_weather(transformed_record)

        logger.info("Weather ETL pipeline completed successfully.")

    except Exception:
        logger.exception("Weather ETL pipeline failed.")
        raise


if __name__ == "__main__":
    run_pipeline()