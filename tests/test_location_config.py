import pytest
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
