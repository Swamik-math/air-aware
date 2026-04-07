from itertools import pairwise
from typing import Dict, List, Tuple

import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import asin, cos, radians, sin, sqrt

    r = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    return r * c


def _speed_from_highway(highway: str) -> float:
    defaults = {
        "motorway": 80,
        "trunk": 70,
        "primary": 55,
        "secondary": 45,
        "tertiary": 35,
        "residential": 25,
        "service": 18,
    }
    return float(defaults.get(highway, 30))


def _bbox(source: Tuple[float, float], destination: Tuple[float, float]) -> Tuple[float, float, float, float]:
    s_lat, s_lon = source
    d_lat, d_lon = destination

    min_lat = min(s_lat, d_lat)
    max_lat = max(s_lat, d_lat)
    min_lon = min(s_lon, d_lon)
    max_lon = max(s_lon, d_lon)

    pad = max(0.01, max(max_lat - min_lat, max_lon - min_lon) * 0.35)
    return min_lat - pad, min_lon - pad, max_lat + pad, max_lon + pad


def _build_fallback_graph(source: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
    s_lat, s_lon = source
    d_lat, d_lon = destination

    nodes = {
        1: (s_lat, s_lon),
        2: (s_lat, d_lon),
        3: (d_lat, s_lon),
        4: (d_lat, d_lon),
        5: ((s_lat + d_lat) / 2, (s_lon + d_lon) / 2),
    }

    graph: Dict[int, List[Dict]] = {node_id: [] for node_id in nodes}

    def add_edge(a: int, b: int, speed: float) -> None:
        lat1, lon1 = nodes[a]
        lat2, lon2 = nodes[b]
        graph[a].append(
            {
                "to": b,
                "distance_km": haversine_km(lat1, lon1, lat2, lon2),
                "speed_kmph": speed,
            }
        )

    # Build a small connected graph so routing always works in offline mode.
    add_edge(1, 2, 32)
    add_edge(2, 4, 35)
    add_edge(1, 3, 28)
    add_edge(3, 4, 30)
    add_edge(1, 5, 38)
    add_edge(5, 4, 38)
    add_edge(2, 5, 24)
    add_edge(3, 5, 24)

    # Bidirectional roads
    reverse = {k: [] for k in graph}
    for u, edges in graph.items():
        for edge in edges:
            reverse[edge["to"]].append(
                {
                    "to": u,
                    "distance_km": edge["distance_km"],
                    "speed_kmph": edge["speed_kmph"],
                }
            )
    for node_id in graph:
        graph[node_id].extend(reverse[node_id])

    return {"nodes": nodes, "graph": graph}


def fetch_road_network(source: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
    south, west, north, east = _bbox(source, destination)
    query = f"""
    [out:json][timeout:25];
    (
      way["highway"]({south},{west},{north},{east});
    );
    (._;>;);
    out body;
    """

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=35,
        )
        response.raise_for_status()
        payload = response.json()
        elements = payload.get("elements", [])

        node_map: Dict[int, Tuple[float, float]] = {}
        ways = []

        for item in elements:
            if item.get("type") == "node":
                node_map[item["id"]] = (item["lat"], item["lon"])
            elif item.get("type") == "way":
                ways.append(item)

        graph: Dict[int, List[Dict]] = {node_id: [] for node_id in node_map.keys()}

        for way in ways:
            tags = way.get("tags", {})
            highway = tags.get("highway", "residential")
            speed = _speed_from_highway(highway)
            is_one_way = str(tags.get("oneway", "no")).lower() in {"yes", "1", "true"}
            chain = way.get("nodes", [])

            for a, b in pairwise(chain):
                if a not in node_map or b not in node_map:
                    continue

                lat1, lon1 = node_map[a]
                lat2, lon2 = node_map[b]
                distance = haversine_km(lat1, lon1, lat2, lon2)

                graph[a].append(
                    {
                        "to": b,
                        "distance_km": distance,
                        "speed_kmph": speed,
                    }
                )
                if not is_one_way:
                    graph[b].append(
                        {
                            "to": a,
                            "distance_km": distance,
                            "speed_kmph": speed,
                        }
                    )

        # Use fallback if OSM result is empty or disconnected.
        edge_count = sum(len(v) for v in graph.values())
        if len(node_map) < 2 or edge_count < 2:
            return _build_fallback_graph(source, destination)

        return {"nodes": node_map, "graph": graph}

    except Exception:
        return _build_fallback_graph(source, destination)
