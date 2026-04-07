from typing import Dict, List, Tuple

import requests
from flask import current_app


def _normalize_route(route: Dict) -> Dict:
    geometry = route.get("geometry", {})
    coords = geometry.get("coordinates", []) if isinstance(geometry, dict) else []

    if not coords and isinstance(route.get("geometry"), list):
        coords = route.get("geometry", [])

    geometry_lat_lon = []
    for point in coords:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            continue
        lon, lat = point
        geometry_lat_lon.append([float(lat), float(lon)])

    return {
        "geometry": geometry_lat_lon,
        "distance_km": float(route.get("distance", 0.0)) / 1000.0,
        "duration_min": float(route.get("duration", 0.0)) / 60.0,
    }


def fetch_mappls_routes(source: Tuple[float, float], destination: Tuple[float, float]) -> List[Dict]:
    api_key = current_app.config.get("MAPPLS_API_KEY", "")
    if not api_key:
        return []

    lat1, lon1 = source
    lat2, lon2 = destination

    origin = f"{lon1},{lat1}"
    target = f"{lon2},{lat2}"

    url_template = current_app.config.get("MAPPLS_ROUTE_URL_TEMPLATE", "")
    if not url_template:
        return []

    url = url_template.format(api_key=api_key, origin=origin, destination=target)

    params = {
        "alternatives": "true",
        "overview": "full",
        "steps": "false",
        "geometries": "geojson",
    }

    response = requests.get(url, params=params, timeout=18)
    response.raise_for_status()
    payload = response.json()

    routes = payload.get("routes", []) if isinstance(payload, dict) else []
    normalized = [_normalize_route(route) for route in routes]
    normalized = [r for r in normalized if len(r["geometry"]) >= 2]
    normalized.sort(key=lambda x: (x["duration_min"], x["distance_km"]))
    return normalized
