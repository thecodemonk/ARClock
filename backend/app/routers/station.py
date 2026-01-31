from __future__ import annotations

import yaml
from fastapi import APIRouter

from app.config import config_path, settings
from app.models.station import StationConfig

router = APIRouter(tags=["station"])


@router.get("/station/de")
async def get_station():
    return StationConfig(
        callsign=settings.de_callsign,
        grid=settings.de_grid,
        latitude=settings.de_latitude,
        longitude=settings.de_longitude,
        timezone=settings.de_timezone,
    )


@router.put("/station/de")
async def update_station(config: StationConfig):
    settings.de_callsign = config.callsign
    settings.de_grid = config.grid
    settings.de_latitude = config.latitude
    settings.de_longitude = config.longitude
    settings.de_timezone = config.timezone

    # Persist to YAML
    config_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "de_callsign": config.callsign,
        "de_grid": config.grid,
        "de_latitude": config.latitude,
        "de_longitude": config.longitude,
        "de_timezone": config.timezone,
    }
    with open(config_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)

    return {"status": "ok", "config": config}
