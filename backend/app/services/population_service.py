import math


def get_population_density(lat: float, lon: float) -> float:
    """
    Mock population density model in people per square km.
    This creates urban pockets to simulate denser zones.
    """
    city_centers = [
        (28.6139, 77.2090, 9000),
        (19.0760, 72.8777, 12000),
        (13.0827, 80.2707, 8500),
        (12.9716, 77.5946, 10000),
    ]

    density = 400
    for c_lat, c_lon, peak in city_centers:
        distance = math.sqrt((lat - c_lat) ** 2 + (lon - c_lon) ** 2)
        density += peak * math.exp(-(distance**2) / 0.15)

    return max(200, min(15000, density))
