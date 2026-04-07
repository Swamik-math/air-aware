from typing import Dict, List, Tuple

import requests


OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"


def _to_lat_lon_geometry(geojson_coords: List[List[float]]) -> List[List[float]]:
    return [[coord[1], coord[0]] for coord in geojson_coords if len(coord) == 2]


def fetch_osrm_routes(source: Tuple[float, float], destination: Tuple[float, float]) -> List[Dict]:
    lat1, lon1 = source
    lat2, lon2 = destination

    url = OSRM_ROUTE_URL.format(lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2)
    params = {
        "overview": "full",
        "geometries": "geojson",
        "alternatives": "true",
        "steps": "false",
    }

    response = requests.get(url, params=params, timeout=18)
    response.raise_for_status()
    payload = response.json()

    if payload.get("code") != "Ok":
        return []

    routes = payload.get("routes", [])
    normalized: List[Dict] = []

    for route in routes:
        geometry_coords = route.get("geometry", {}).get("coordinates", [])
        normalized.append(
            {
                "geometry": _to_lat_lon_geometry(geometry_coords),
                "distance_km": float(route.get("distance", 0.0)) / 1000.0,
                "duration_min": float(route.get("duration", 0.0)) / 60.0,
            }
        )

    normalized.sort(key=lambda x: (x["duration_min"], x["distance_km"]))
    return normalized
