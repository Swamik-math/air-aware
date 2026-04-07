from typing import Dict, List, Tuple

from app.algorithms.pathfinding import a_star, dijkstra
from app.services.aqi_service import get_aqi_for_point
from app.services.mappls_routing_service import fetch_mappls_routes
from app.services.osm_service import fetch_road_network, haversine_km
from app.services.osrm_routing_service import fetch_osrm_routes
from app.services.population_service import get_population_density
from app.utils.normalization import clamp, min_max_scale


def _nearest_node(nodes: Dict[int, Tuple[float, float]], point: Tuple[float, float]) -> int:
    target_lat, target_lon = point
    best_node = -1
    best_distance = float("inf")

    for node_id, (lat, lon) in nodes.items():
        d = haversine_km(target_lat, target_lon, lat, lon)
        if d < best_distance:
            best_distance = d
            best_node = node_id

    return best_node


def _enrich_graph(nodes: Dict[int, Tuple[float, float]], graph: Dict[int, List[Dict]]) -> None:
    cache = {}

    for u, edges in graph.items():
        lat1, lon1 = nodes[u]
        for edge in edges:
            v = edge["to"]
            lat2, lon2 = nodes[v]
            mid_lat = (lat1 + lat2) / 2
            mid_lon = (lon1 + lon2) / 2

            cache_key = (round(mid_lat, 3), round(mid_lon, 3))
            if cache_key not in cache:
                aqi_payload = get_aqi_for_point(mid_lat, mid_lon)
                density = get_population_density(mid_lat, mid_lon)
                cache[cache_key] = {
                    "aqi": float(aqi_payload["aqi"]),
                    "density": float(density),
                }

            edge["aqi"] = cache[cache_key]["aqi"]
            edge["density"] = cache[cache_key]["density"]


def _edge_lookup(path: List[int], graph: Dict[int, List[Dict]]) -> List[Dict]:
    output = []
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        edge = next((e for e in graph.get(u, []) if e["to"] == v), None)
        if edge:
            output.append(edge)
    return output


def _summarize(path: List[int], nodes: Dict[int, Tuple[float, float]], graph: Dict[int, List[Dict]]) -> Dict:
    edges = _edge_lookup(path, graph)

    total_distance = sum(e["distance_km"] for e in edges)
    total_time_hours = sum(e["distance_km"] / max(e.get("speed_kmph", 25.0), 5.0) for e in edges)
    avg_aqi = sum(e.get("aqi", 70) for e in edges) / max(len(edges), 1)
    avg_density = sum(e.get("density", 1000) for e in edges) / max(len(edges), 1)

    pollution_index = min(1.0, ((avg_aqi / 300.0) * 0.7) + ((avg_density / 15000.0) * 0.3))
    health_score = int(100 - pollution_index * 100)

    return {
        "path_nodes": path,
        "geometry": [[nodes[n][0], nodes[n][1]] for n in path],
        "distance_km": round(total_distance, 3),
        "duration_min": round(total_time_hours * 60, 1),
        "avg_aqi": round(avg_aqi, 1),
        "avg_density": round(avg_density, 1),
        "health_score": clamp(health_score, 1, 100),
    }


def _weights_from_preference(preference: str, payload_weights: Dict) -> Dict[str, float]:
    if payload_weights:
        return {
            "distance": float(payload_weights.get("distance", 0.34)),
            "aqi": float(payload_weights.get("aqi", 0.33)),
            "density": float(payload_weights.get("density", 0.33)),
        }

    table = {
        "shortest": {"distance": 0.7, "aqi": 0.2, "density": 0.1},
        "fastest": {"distance": 0.45, "aqi": 0.25, "density": 0.3},
        "healthiest": {"distance": 0.15, "aqi": 0.6, "density": 0.25},
    }
    return table.get(preference, table["healthiest"])


def build_routes(
    source: Tuple[float, float],
    destination: Tuple[float, float],
    preference: str,
    custom_weights: Dict,
) -> Dict:
    osm_result = fetch_road_network(source, destination)
    nodes = osm_result["nodes"]
    graph = osm_result["graph"]

    _enrich_graph(nodes, graph)

    start = _nearest_node(nodes, source)
    end = _nearest_node(nodes, destination)

    if start == -1 or end == -1:
        raise ValueError("No nearby road nodes found for source or destination")

    all_edges = [edge for edges in graph.values() for edge in edges]
    max_distance = max((e["distance_km"] for e in all_edges), default=1.0)
    min_distance = min((e["distance_km"] for e in all_edges), default=0.0)
    max_aqi = max((e.get("aqi", 70) for e in all_edges), default=1.0)
    min_aqi = min((e.get("aqi", 70) for e in all_edges), default=0.0)
    max_density = max((e.get("density", 1000) for e in all_edges), default=1.0)
    min_density = min((e.get("density", 1000) for e in all_edges), default=0.0)

    route_weights = _weights_from_preference(preference, custom_weights)

    shortest_path, _ = dijkstra(graph, start, end, lambda e: e["distance_km"])
    fastest_path, _ = dijkstra(
        graph,
        start,
        end,
        lambda e: e["distance_km"] / max(e.get("speed_kmph", 25.0), 5.0),
    )

    def healthy_weight(edge: Dict) -> float:
        nd = min_max_scale(edge["distance_km"], min_distance, max_distance)
        na = min_max_scale(edge.get("aqi", 70), min_aqi, max_aqi)
        np = min_max_scale(edge.get("density", 1000), min_density, max_density)
        return (
            route_weights["distance"] * nd
            + route_weights["aqi"] * na
            + route_weights["density"] * np
        )

    healthiest_path, _ = a_star(
        graph,
        nodes,
        start,
        end,
        healthy_weight,
        lambda a, b: haversine_km(a[0], a[1], b[0], b[1]),
    )

    # Safe fallback in rare disconnected cases.
    if not healthiest_path:
        healthiest_path, _ = dijkstra(graph, start, end, healthy_weight)

    shortest = _summarize(shortest_path, nodes, graph)
    fastest = _summarize(fastest_path, nodes, graph)
    healthiest = _summarize(healthiest_path, nodes, graph)

    try:
        mappls_routes = fetch_mappls_routes(source, destination)
    except Exception:
        mappls_routes = []

    if mappls_routes:
        selected_routes = mappls_routes
    else:
        try:
            selected_routes = fetch_osrm_routes(source, destination)
        except Exception:
            selected_routes = []

    if selected_routes:
        # Map API geometry ensures map polylines follow actual drivable roads.
        shortest["geometry"] = selected_routes[0]["geometry"]
        shortest["distance_km"] = round(selected_routes[0]["distance_km"], 3)
        shortest["duration_min"] = round(selected_routes[0]["duration_min"], 1)

        fastest_index = 1 if len(selected_routes) > 1 else 0
        fastest["geometry"] = selected_routes[fastest_index]["geometry"]
        fastest["distance_km"] = round(selected_routes[fastest_index]["distance_km"], 3)
        fastest["duration_min"] = round(selected_routes[fastest_index]["duration_min"], 1)

        healthiest_index = 2 if len(selected_routes) > 2 else fastest_index
        healthiest["geometry"] = selected_routes[healthiest_index]["geometry"]
        healthiest["distance_km"] = round(selected_routes[healthiest_index]["distance_km"], 3)
        healthiest["duration_min"] = round(selected_routes[healthiest_index]["duration_min"], 1)

    return {
        "preference": preference,
        "weights": route_weights,
        "shortest": shortest,
        "fastest": fastest,
        "healthiest": healthiest,
    }
