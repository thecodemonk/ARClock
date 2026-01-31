from __future__ import annotations


def latlon_to_grid(lat: float, lon: float) -> str:
    """Convert latitude/longitude to Maidenhead grid square (6 characters)."""
    lon = lon + 180
    lat = lat + 90

    field_lon = int(lon / 20)
    field_lat = int(lat / 10)
    square_lon = int((lon % 20) / 2)
    square_lat = int((lat % 10) / 1)
    sub_lon = int(((lon % 20) % 2) / (2 / 24))
    sub_lat = int(((lat % 10) % 1) / (1 / 24))

    grid = (
        chr(ord("A") + field_lon)
        + chr(ord("A") + field_lat)
        + str(square_lon)
        + str(square_lat)
        + chr(ord("a") + sub_lon)
        + chr(ord("a") + sub_lat)
    )
    return grid


def grid_to_latlon(grid: str) -> tuple[float, float]:
    """Convert Maidenhead grid square to latitude/longitude (center of square)."""
    grid = grid.strip().upper()
    lon = (ord(grid[0]) - ord("A")) * 20 - 180
    lat = (ord(grid[1]) - ord("A")) * 10 - 90

    if len(grid) >= 4:
        lon += int(grid[2]) * 2
        lat += int(grid[3]) * 1

    if len(grid) >= 6:
        lon += (ord(grid[4]) - ord("A")) * (2 / 24)
        lat += (ord(grid[5]) - ord("A")) * (1 / 24)
        # Center of subsquare
        lon += 1 / 24
        lat += 0.5 / 24
    elif len(grid) >= 4:
        # Center of square
        lon += 1
        lat += 0.5
    else:
        # Center of field
        lon += 10
        lat += 5

    return lat, lon
