from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import numpy as np

from app.services.solar import get_subsolar_point


def _terminator_polygon(subsolar_lat: float, subsolar_lon: float, n_points: int = 360) -> list[list[float]]:
    """
    Compute the night-side polygon as GeoJSON coordinates.
    The terminator is the great circle 90 degrees from the subsolar point.
    We generate the terminator ring, then extend it to cover the night hemisphere.
    """
    lat_r = math.radians(subsolar_lat)
    lon_r = math.radians(subsolar_lon)

    # Terminator points: 90 degrees from subsolar point
    angles = np.linspace(0, 2 * math.pi, n_points, endpoint=False)

    term_lats = []
    term_lons = []
    for a in angles:
        # Rodrigues rotation: rotate the anti-solar direction around
        # Point on terminator great circle
        t_lat = math.asin(
            math.cos(lat_r) * math.sin(a) * math.sin(lon_r) * (-1)
            + math.cos(lat_r) * math.cos(a) * 0
            + math.sin(lat_r) * math.sin(a) * math.cos(lon_r) * (-1)
            + math.cos(a) * math.cos(lat_r) * 0
        )
        # Use a simpler parametric approach
        pass

    # Simpler approach: parametric terminator
    term_coords = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        # Terminator latitude as function of longitude offset
        t_lon = subsolar_lon + 180 * math.cos(angle)
        # At the terminator, solar elevation = 0
        # sin(alt) = sin(lat)*sin(dec) + cos(lat)*cos(dec)*cos(ha) = 0
        # where dec = subsolar_lat, ha = lon - subsolar_lon
        # So: cos(lat)*cos(dec)*cos(ha) = -sin(lat)*sin(dec)
        # tan(lat) = -cos(dec)*cos(ha)/sin(dec) = -cos(ha)/tan(dec) ... not general

        pass

    # Most robust approach: direct spherical geometry
    # The terminator is the set of points where the angle to the subsolar point is 90 degrees.
    # In Cartesian: dot(P, S) = 0 where S is subsolar unit vector
    # Parametrize with angle theta around the terminator circle

    sx = math.cos(lat_r) * math.cos(lon_r)
    sy = math.cos(lat_r) * math.sin(lon_r)
    sz = math.sin(lat_r)

    # Build two orthonormal vectors perpendicular to S
    if abs(sz) < 0.9:
        u = np.array([-sy, sx, 0.0])
    else:
        u = np.array([1.0, 0.0, 0.0])
    # Remove component along S
    s_vec = np.array([sx, sy, sz])
    u = u - np.dot(u, s_vec) * s_vec
    u = u / np.linalg.norm(u)
    v = np.cross(s_vec, u)

    coords = []
    for i in range(n_points + 1):
        angle = 2 * math.pi * i / n_points
        p = math.cos(angle) * u + math.sin(angle) * v
        lat_deg = math.degrees(math.asin(np.clip(p[2], -1, 1)))
        lon_deg = math.degrees(math.atan2(p[1], p[0]))
        coords.append((lon_deg, lat_deg))

    return coords


def _build_night_polygon(terminator_coords: list[tuple[float, float]], subsolar_lat: float) -> dict[str, Any]:
    """
    Build a GeoJSON polygon covering the night side of the earth.
    The night side is opposite the subsolar point.
    """
    # Sort terminator points by longitude for proper polygon construction
    # Split into upper and lower halves, then build polygon going around the night side

    # Separate points into those with positive and negative latitudes relative to midpoint
    # For a cleaner approach, we'll create a polygon using the terminator + polar caps

    # Anti-solar latitude
    anti_lat = -subsolar_lat

    # Sort coords by longitude
    sorted_coords = sorted(terminator_coords, key=lambda c: c[0])

    # Split into two tracks: one with higher lat, one with lower lat
    upper = []
    lower = []
    for lon, lat in sorted_coords:
        if lat >= anti_lat:
            upper.append([lon, lat])
        else:
            lower.append([lon, lat])

    # Build night polygon: go across the top, cap at pole, come back on bottom
    # If anti-solar point is in northern hemisphere, night covers south
    # If anti-solar point is in southern hemisphere, night covers north

    if anti_lat >= 0:
        # Night pole is North-ish - the polygon should cover from terminator toward the anti-solar pole
        # Upper track goes west to east, lower track goes east to west
        polygon_ring = upper + [upper[-1]] if upper else []
        polygon_ring += [[180, 90], [-180, 90]]
        polygon_ring += list(reversed(lower))
    else:
        polygon_ring = upper + [[180, -90], [-180, -90]] + list(reversed(lower))

    if not polygon_ring:
        return {"type": "FeatureCollection", "features": []}

    # Close the ring
    if polygon_ring[0] != polygon_ring[-1]:
        polygon_ring.append(polygon_ring[0])

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "night"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_ring],
                },
            }
        ],
    }


def compute_greyline() -> dict[str, Any]:
    """Compute the current grey line terminator as GeoJSON."""
    subsolar_lat, subsolar_lon = get_subsolar_point()

    # Generate terminator ring
    n_points = 360
    lat_r = math.radians(subsolar_lat)
    lon_r = math.radians(subsolar_lon)

    sx = math.cos(lat_r) * math.cos(lon_r)
    sy = math.cos(lat_r) * math.sin(lon_r)
    sz = math.sin(lat_r)
    s_vec = np.array([sx, sy, sz])

    if abs(sz) < 0.9:
        u = np.array([-sy, sx, 0.0])
    else:
        u = np.array([1.0, 0.0, 0.0])
    u = u - np.dot(u, s_vec) * s_vec
    u = u / np.linalg.norm(u)
    v = np.cross(s_vec, u)

    terminator = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        p = math.cos(angle) * u + math.sin(angle) * v
        lat_deg = math.degrees(math.asin(float(np.clip(p[2], -1, 1))))
        lon_deg = math.degrees(math.atan2(float(p[1]), float(p[0])))
        terminator.append((lon_deg, lat_deg))

    # Sort by longitude
    terminator.sort(key=lambda c: c[0])

    # Build the night-side polygon.
    # The night side is the hemisphere opposite the sun.
    # We construct it by taking the terminator line and extending to the anti-solar pole.
    night_pole_lat = -90 if subsolar_lat >= 0 else 90

    # The terminator forms a sinusoidal-like curve across longitudes.
    # To make a valid polygon: trace terminator west→east, then close via the night pole.
    ring = [[lon, lat] for lon, lat in terminator]

    # Close at the east edge, go to night pole, sweep back
    ring.append([180, ring[-1][1]])
    ring.append([180, night_pole_lat])
    ring.append([-180, night_pole_lat])
    ring.append([-180, ring[0][1]])
    ring.append(ring[0])

    # Terminator line for the amber border
    terminator_line = [[lon, lat] for lon, lat in terminator]

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
