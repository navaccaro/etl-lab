from weather_etl.location_config import load_locations


def test_load_locations_returns_forest_park() -> None:
    locations = load_locations()

    assert len(locations) == 1

    location = locations[0]

    assert location["location_id"] == "forest-park-il"
    assert location["display_name"] == "Forest Park, Illinois"
    assert location["latitude"] == 41.8795
    assert location["longitude"] == -87.8137
    assert location["timezone"] == "America/Chicago"
    assert location["enabled"] is True


def test_loaded_locations_have_expected_fields() -> None:
    expected_fields = {
        "version",
        "location_id",
        "display_name",
        "latitude",
        "longitude",
        "timezone",
        "enabled",
    }

    for location in load_locations():
        assert set(location) == expected_fields
