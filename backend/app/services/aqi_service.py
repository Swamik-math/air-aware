import math
from typing import Dict

import requests
from flask import current_app


def _fallback_aqi(lat: float, lon: float) -> int:
    """Deterministic fallback AQI so development works without API keys."""
    raw = 70 + (abs(math.sin(lat * 0.17) + math.cos(lon * 0.11)) * 120)
    return int(max(20, min(250, raw)))


def get_aqi_for_point(lat: float, lon: float) -> Dict:
    token = current_app.config.get("AQI_API_TOKEN", "")
    base_url = current_app.config.get("AQI_API_URL", "")

    if not token or not base_url:
        value = _fallback_aqi(lat, lon)
        return {"aqi": value, "source": "fallback"}

    url = base_url.format(lat=lat, lon=lon)
    try:
        response = requests.get(url, params={"token": token}, timeout=8)
        response.raise_for_status()
        payload = response.json()

        if payload.get("status") == "ok":
            aqi = payload.get("data", {}).get("aqi")
            if isinstance(aqi, (int, float)):
                return {"aqi": int(aqi), "source": "aqicn"}
    except Exception:
        pass

    value = _fallback_aqi(lat, lon)
    return {"aqi": value, "source": "fallback"}
