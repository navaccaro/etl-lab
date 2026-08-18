from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WeatherLocation(BaseModel):
    """Validated configuration for one weather location."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    version: int = Field(default=1, ge=1)
    location_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    display_name: str = Field(min_length=3, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = Field(min_length=1)
    enabled: bool
