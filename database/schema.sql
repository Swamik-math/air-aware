CREATE TABLE IF NOT EXISTS route_history (
    id SERIAL PRIMARY KEY,
    source_lat DOUBLE PRECISION NOT NULL,
    source_lon DOUBLE PRECISION NOT NULL,
    destination_lat DOUBLE PRECISION NOT NULL,
    destination_lon DOUBLE PRECISION NOT NULL,
    preference VARCHAR(20) NOT NULL,
    shortest_summary JSONB,
    fastest_summary JSONB,
    healthiest_summary JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
