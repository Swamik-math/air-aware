from app.algorithms.pathfinding import dijkstra


def test_dijkstra_short_path():
    graph = {
        1: [{"to": 2, "distance_km": 1.0}, {"to": 3, "distance_km": 3.0}],
        2: [{"to": 3, "distance_km": 1.0}],
        3: [],
    }

    path, cost = dijkstra(graph, 1, 3, lambda e: e["distance_km"])

    assert path == [1, 2, 3]
    assert cost == 2.0
