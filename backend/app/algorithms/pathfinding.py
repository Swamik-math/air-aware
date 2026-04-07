import heapq
from typing import Callable, Dict, List, Tuple


NodeId = int
Edge = Dict
Graph = Dict[NodeId, List[Edge]]
Coordinates = Dict[NodeId, Tuple[float, float]]


def reconstruct_path(previous: Dict[NodeId, NodeId], goal: NodeId) -> List[NodeId]:
    path = [goal]
    current = goal
    while current in previous:
        current = previous[current]
        path.append(current)
    path.reverse()
    return path


def dijkstra(
    graph: Graph,
    start: NodeId,
    goal: NodeId,
    weight_fn: Callable[[Edge], float],
) -> Tuple[List[NodeId], float]:
    distances = {start: 0.0}
    previous: Dict[NodeId, NodeId] = {}
    queue = [(0.0, start)]
    visited = set()

    while queue:
        current_distance, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            return reconstruct_path(previous, goal), current_distance

        for edge in graph.get(node, []):
            neighbor = edge["to"]
            new_distance = current_distance + weight_fn(edge)

            if new_distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_distance
                previous[neighbor] = node
                heapq.heappush(queue, (new_distance, neighbor))

    return [], float("inf")


def a_star(
    graph: Graph,
    coords: Coordinates,
    start: NodeId,
    goal: NodeId,
    weight_fn: Callable[[Edge], float],
    heuristic_fn: Callable[[Tuple[float, float], Tuple[float, float]], float],
) -> Tuple[List[NodeId], float]:
    g_score = {start: 0.0}
    f_score = {start: heuristic_fn(coords[start], coords[goal])}
    previous: Dict[NodeId, NodeId] = {}

    open_set = [(f_score[start], start)]
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            return reconstruct_path(previous, goal), g_score[current]

        for edge in graph.get(current, []):
            neighbor = edge["to"]
            tentative_g = g_score[current] + weight_fn(edge)

            if tentative_g < g_score.get(neighbor, float("inf")):
                previous[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic_fn(coords[neighbor], coords[goal])
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return [], float("inf")
