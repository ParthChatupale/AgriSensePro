"""Reverse geocoding utilities for Agrisense."""
import httpx
from typing import Dict, Optional

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "AgriSense/1.0 (support@agrisense.local)"


async def reverse_geocode(lat: float, lon: float) -> Dict[str, Optional[str]]:
    """Reverse geocode latitude & longitude using Nominatim.

    Returns a dict with state, district, village keys. If lookup fails
    it returns empty strings for missing fields.
    """
    params = {
        "format": "json",
        "addressdetails": 1,
        "lat": lat,
        "lon": lon,
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(NOMINATIM_URL, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        return {"state": None, "district": None, "village": None}

    address = payload.get("address", {})
    state = address.get("state")
    district = (
        address.get("city_district")
        or address.get("district")
        or address.get("county")
    )
    village = (
        address.get("village")
        or address.get("town")
        or address.get("city")
        or address.get("hamlet")
    )

    return {
        "state": state,
        "district": district,
        "village": village,
    }
