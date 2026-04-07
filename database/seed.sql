INSERT INTO route_history (
    source_lat,
    source_lon,
    destination_lat,
    destination_lon,
    preference,
    shortest_summary,
    fastest_summary,
    healthiest_summary
)
VALUES
(
    28.6139,
    77.2090,
    28.5355,
    77.3910,
    'healthiest',
    '{"distance_km": 18.2, "duration_min": 42.5, "avg_aqi": 110, "health_score": 64}',
    '{"distance_km": 20.1, "duration_min": 35.8, "avg_aqi": 128, "health_score": 55}',
    '{"distance_km": 22.4, "duration_min": 47.2, "avg_aqi": 92, "health_score": 74}'
);
