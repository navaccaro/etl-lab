import pytest

from weather_etl.models import WeatherLocation
from weather_etl.transform_weather import transform_weather

TEST_LOCATION = WeatherLocation(
    version=1,
    location_id="forest-park-il",
    display_name="Forest Park, Illinois",
    latitude=41.8795,
    longitude=-87.8137,
    timezone="America/Chicago",
    enabled=True,
)


def make_valid_payload():
    """Return a valid sample API payload for use in multiple tests."""

    return {
        "latitude": 41.88,
        "longitude": -87.81,
        "current": {
            "time": "2026-07-18T18:00",
            "temperature_2m": 30.2,
            "relative_humidity_2m": 61,
            "apparent_temperature": 33.1,
            "precipitation": 0,
            "weather_code": 0,
            "wind_speed_10m": 12.4,
        },
    }


def test_valid_weather_payload():
    payload = make_valid_payload()

    record = transform_weather(payload, TEST_LOCATION)

    assert record["temperature_c"] == 30.2
    assert record["relative_humidity_pct"] == 61
    assert record["location_id"] == "forest-park-il"
    assert record["location_name"] == "Forest Park, Illinois"
    assert record["latitude"] == 41.8795
    assert record["longitude"] == -87.8137


def test_temperature_out_of_range():
    payload = make_valid_payload()
    payload["current"]["temperature_2m"] = 500

    with pytest.raises(ValueError, match="Temperature out of range"):
        transform_weather(payload, TEST_LOCATION)


def test_humidity_out_of_range():
    payload = make_valid_payload()
    payload["current"]["relative_humidity_2m"] = 150

    with pytest.raises(ValueError, match="Humidity out of range"):
        transform_weather(payload, TEST_LOCATION)


def test_latitude_out_of_range():
    payload = make_valid_payload()
    payload["latitude"] = 900

    with pytest.raises(ValueError, match="Latitude out of range"):
        transform_weather(payload, TEST_LOCATION)


def test_longitude_out_of_range():
    payload = make_valid_payload()
    payload["longitude"] = 500

    with pytest.raises(ValueError, match="Longitude out of range"):
        transform_weather(payload, TEST_LOCATION)


def test_missing_current_section():
    payload = make_valid_payload()
    del payload["current"]

    with pytest.raises(
        ValueError,
        match="Weather payload does not contain a 'current' section",
    ):
        transform_weather(payload, TEST_LOCATION)


def test_missing_required_field():
    payload = make_valid_payload()
    del payload["current"]["temperature_2m"]

    with pytest.raises(ValueError, match="missing required fields"):
        transform_weather(payload, TEST_LOCATION)
