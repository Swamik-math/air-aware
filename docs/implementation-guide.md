# AirAware Implementation Guide

## 1. User Input Module
- Implemented in React sidebar form.
- Accepts source and destination as latitude/longitude.
- Supports route preference: shortest, fastest, healthiest.
- Includes dynamic sliders for weighted cost tuning.

## 2. Data Collection Module
- OSM road network fetched from Overpass API in backend service.
- AQI fetched from AQICN endpoint when token exists.
- Fallback AQI model used when token is absent.
- Population density modeled using a mock urban-density function.

## 3. Data Processing Module
- Each road edge is enriched with midpoint AQI and population density.
- Features normalized by min-max scaling.

## 4. Cost Function
- Formula: Cost = w1*Distance + w2*AQI + w3*Population Density.
- Weights can be sent by frontend or auto-selected from route preference.

## 5. Route Optimization Module
- Dijkstra for shortest route.
- Dijkstra for fastest route using distance/speed edge weights.
- A* for healthiest route with weighted environmental edge cost.

## 6. Backend API Layer
- GET /health
- GET /aqi-data
- POST /calculate-cost
- POST /get-routes

## 7. Frontend Visualization Layer
- Leaflet map with OSM tiles.
- Color-coded route overlays.
- Route cards with distance, time, AQI, density, and health score.

## 8. Output
- Displays all three routes and allows route focus selection.
- Provides environmental insights and health rating.

## Optional Extensions
- JWT auth and user-specific route history.
- Scheduled re-computation for real-time updates.
- Favorite route bookmarking.
