from __future__ import annotations

from fastapi import APIRouter, Query

from app.config import settings
from app.models.station import LocationInfo
from app.services.geodesic import bearing_and_distance
from app.services.grid_square import latlon_to_grid

router = APIRouter(tags=["location"])


@router.get("/location/info")
async def get_location_info(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    grid = latlon_to_grid(lat, lon)

    bearing = None
    distance_km = None
    distance_mi = None

    if settings.de_latitude != 0 or settings.de_longitude != 0:
        bearing, distance_km = bearing_and_distance(
            settings.de_latitude, settings.de_longitude, lat, lon
        )
        distance_mi = distance_km * 0.621371
        bearing = round(bearing, 1)
        distance_km = round(distance_km, 1)
        distance_mi = round(distance_mi, 1)

    return LocationInfo(
        latitude=round(lat, 4),
        longitude=round(lon, 4),
        grid=grid,
        bearing=bearing,
        distance_km=distance_km,
        distance_mi=distance_mi,
    )
