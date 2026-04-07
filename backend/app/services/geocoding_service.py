from typing import Dict, List

import requests


NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


def search_places(query: str, limit: int = 5) -> List[Dict]:
    text = (query or "").strip()
    if not text:
        return []

    if "bengaluru" not in text.lower() and "bangalore" not in text.lower():
        text = f"{text}, Bengaluru"

    params = {
        "q": text,
        "format": "jsonv2",
        "limit": max(1, min(limit, 10)),
        "addressdetails": 1,
        "countrycodes": "in",
        "viewbox": "77.35,13.20,77.85,12.75",
        "bounded": 1,
    }

    response = requests.get(
        NOMINATIM_SEARCH_URL,
        params=params,
        timeout=10,
        headers={"User-Agent": "AirAware/1.0 (local dev)"},
    )
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, list):
        return []

    return payload
