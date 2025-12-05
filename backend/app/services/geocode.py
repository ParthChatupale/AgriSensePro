"""Reverse geocoding utilities for Agrisense."""
import httpx
from typing import Dict, Optional, Tuple
from time import time

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "AgriSense/1.0 (support@agrisense.local)"

# In-memory cache: key -> (timestamp, geo_data)
GEOCODE_CACHE: Dict[str, Tuple[float, Dict[str, Optional[str]]]] = {}
CACHE_EXPIRY_SECONDS = 86400  # 24 hours


async def reverse_geocode(lat: float, lon: float) -> Dict[str, Optional[str]]:
    """Reverse geocode latitude & longitude using Nominatim.

    Returns a dict with state, district, village keys. If lookup fails
    it returns empty strings for missing fields.
    """
    # Check cache first
    cache_key = f"{lat},{lon}"
    current_time = time()
    
    if cache_key in GEOCODE_CACHE:
        cached_time, cached_result = GEOCODE_CACHE[cache_key]
        if current_time - cached_time < CACHE_EXPIRY_SECONDS:
            return cached_result
        # Expired, remove from cache
        del GEOCODE_CACHE[cache_key]
    
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
        result = {"state": None, "district": None, "village": None}
        # Cache failed lookups too (shorter expiry could be considered, but keeping it simple)
        GEOCODE_CACHE[cache_key] = (current_time, result)
        return result

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

    result = {
        "state": state,
        "district": district,
        "village": village,
    }
    
    # Cache the result
    GEOCODE_CACHE[cache_key] = (current_time, result)
    return result
