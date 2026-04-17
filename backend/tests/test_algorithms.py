from app.algorithms.pathfinding import dijkstra
from app.services.routing_service import _pick_route_indexes


def test_dijkstra_short_path():
    graph = {
        1: [{"to": 2, "distance_km": 1.0}, {"to": 3, "distance_km": 3.0}],
        2: [{"to": 3, "distance_km": 1.0}],
        3: [],
    }

    path, cost = dijkstra(graph, 1, 3, lambda e: e["distance_km"])

    assert path == [1, 2, 3]
    assert cost == 2.0


def test_pick_route_indexes_shortest_uses_min_distance():
    routes = [
        {"distance_km": 16.237, "duration_min": 20.4},
        {"distance_km": 14.887, "duration_min": 20.6},
        {"distance_km": 15.1, "duration_min": 19.9},
    ]

    shortest_idx, fastest_idx, healthiest_idx = _pick_route_indexes(routes)

    assert shortest_idx == 1
    assert fastest_idx == 2
    assert healthiest_idx == 0
