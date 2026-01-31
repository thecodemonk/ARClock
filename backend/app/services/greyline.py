from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import numpy as np

from app.services.solar import get_subsolar_point


def compute_greyline() -> dict[str, Any]:
    """Compute the current grey line terminator as GeoJSON."""
    subsolar_lat, subsolar_lon = get_subsolar_point()

    n_points = 720
    lat_r = math.radians(subsolar_lat)
    lon_r = math.radians(subsolar_lon)

    # Subsolar unit vector
    sx = math.cos(lat_r) * math.cos(lon_r)
    sy = math.cos(lat_r) * math.sin(lon_r)
    sz = math.sin(lat_r)
    s_vec = np.array([sx, sy, sz])

    # Build two orthonormal vectors perpendicular to S (the terminator plane)
    if abs(sz) < 0.9:
        u = np.array([-sy, sx, 0.0])
    else:
        u = np.array([1.0, 0.0, 0.0])
    u = u - np.dot(u, s_vec) * s_vec
    u = u / np.linalg.norm(u)
    v = np.cross(s_vec, u)

    # Generate terminator points (great circle 90 degrees from subsolar point)
    terminator = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        p = math.cos(angle) * u + math.sin(angle) * v
        lat_deg = math.degrees(math.asin(float(np.clip(p[2], -1, 1))))
        lon_deg = math.degrees(math.atan2(float(p[1]), float(p[0])))
        terminator.append((lon_deg, lat_deg))

    # For the night polygon we need a latitude-per-longitude approach.
    # Sample the terminator at evenly-spaced longitudes to get a clean curve.
    # For each longitude, find the terminator latitude.

    # Build a lookup: for each sampled longitude, compute the terminator lat
    # using the solar declination / hour-angle formula:
    #   sin(alt) = sin(lat)*sin(dec) + cos(lat)*cos(dec)*cos(ha) = 0
    #   => tan(lat) = -cos(ha) / tan(dec)  when dec != 0
    #   => lat = atan(-cos(ha) / tan(dec))
    # where ha = longitude - subsolar_lon, dec = subsolar_lat

    dec = math.radians(subsolar_lat)
    lons = []
    term_lats = []

    for i in range(721):
        lng = -180.0 + i * 0.5
        ha = math.radians(lng - subsolar_lon)
        if abs(dec) < 1e-10:
            # Equinox: terminator is at the poles, ha = +/-90
            tlat = 0.0 if abs(math.cos(ha)) > 1e-10 else 90.0
        else:
            tlat = math.degrees(math.atan(-math.cos(ha) / math.tan(dec)))
        lons.append(lng)
        term_lats.append(tlat)

    # Night polygon: the night side is opposite the sun.
    # If subsolar point is in northern hemisphere, night pole is south.
    night_pole_lat = -90.0 if subsolar_lat >= 0 else 90.0

    # Build ring: trace terminator west to east, then close via the night pole
    ring = []
    for i in range(len(lons)):
        ring.append([lons[i], term_lats[i]])

    # Close the polygon through the night pole
    ring.append([180.0, term_lats[-1]])
    ring.append([180.0, night_pole_lat])
    ring.append([-180.0, night_pole_lat])
    ring.append([-180.0, term_lats[0]])
    ring.append(ring[0])

    # Terminator line (just the curve, no pole extensions)
    terminator_line = [[lons[i], term_lats[i]] for i in range(len(lons))]

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "night"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [ring],
                },
            },
            {
                "type": "Feature",
                "properties": {"name": "terminator"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": terminator_line,
                },
            },
        ],
    }

    return {
        "geojson": geojson,
        "subsolar_lat": round(subsolar_lat, 4),
        "subsolar_lon": round(subsolar_lon, 4),
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
