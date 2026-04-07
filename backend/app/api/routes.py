from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import RouteHistory
from app.services.aqi_service import get_aqi_for_point
from app.services.geocoding_service import search_places
from app.services.routing_service import build_routes
from app.utils.normalization import min_max_scale


api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok", "service": "airaware-backend"}), 200


@api_bp.get("/aqi-data")
def aqi_data() -> tuple:
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon query params are required"}), 400

    payload = get_aqi_for_point(lat, lon)
    return jsonify({"lat": lat, "lon": lon, **payload}), 200


@api_bp.get("/search-places")
def search_places_endpoint() -> tuple:
    query = request.args.get("q", default="", type=str).strip()
    if not query:
        return jsonify({"results": []}), 200

    try:
        results = search_places(query)
        return jsonify({"results": results}), 200
    except Exception as exc:
        return jsonify({"error": f"Place search failed: {str(exc)}"}), 502


@api_bp.post("/calculate-cost")
def calculate_cost() -> tuple:
    body = request.get_json(silent=True) or {}

    distance = float(body.get("distance", 0))
    aqi = float(body.get("aqi", 0))
    density = float(body.get("density", 0))

    weights = body.get("weights", {})
    w1 = float(weights.get("distance", 0.33))
    w2 = float(weights.get("aqi", 0.33))
    w3 = float(weights.get("density", 0.34))

    # Normalize each variable to keep weighted sum stable across scales.
    nd = min_max_scale(distance, 0, 100)
    na = min_max_scale(aqi, 0, 300)
    np = min_max_scale(density, 0, 15000)

    cost = (w1 * nd) + (w2 * na) + (w3 * np)
    return jsonify({"normalized": {"distance": nd, "aqi": na, "density": np}, "cost": cost}), 200


@api_bp.post("/get-routes")
def get_routes() -> tuple:
    body = request.get_json(silent=True) or {}

    source = body.get("source") or {}
    destination = body.get("destination") or {}
    preference = str(body.get("preference", "healthiest")).lower()
    weights = body.get("weights", {})

    try:
        source_tuple = (float(source["lat"]), float(source["lon"]))
        destination_tuple = (float(destination["lat"]), float(destination["lon"]))
    except Exception:
        return jsonify({"error": "source and destination with lat/lon are required"}), 400

    try:
        routes = build_routes(source_tuple, destination_tuple, preference, weights)

        history = RouteHistory(
            source_lat=source_tuple[0],
            source_lon=source_tuple[1],
            destination_lat=destination_tuple[0],
            destination_lon=destination_tuple[1],
            preference=preference,
            shortest_summary=routes["shortest"],
            fastest_summary=routes["fastest"],
            healthiest_summary=routes["healthiest"],
        )
        db.session.add(history)
        db.session.commit()

        return jsonify(routes), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Route calculation failed: {str(exc)}"}), 500
