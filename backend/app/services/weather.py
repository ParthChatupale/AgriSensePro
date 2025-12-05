"""Realtime weather service backed by Open-Meteo."""
from __future__ import annotations

import json
import os
from typing import Dict, Optional, Tuple
from time import time

import httpx
from datetime import datetime, timezone, timedelta

BASE_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY_FIELDS = "temperature_2m,relative_humidity_2m,precipitation,windspeed_10m"

APP_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")
FALLBACK_WEATHER_FILE = os.path.join(DATA_DIR, "weather_data.json")

# In-memory cache: key -> (timestamp, weather_data)
WEATHER_CACHE: Dict[str, Tuple[float, Dict[str, Optional[float]]]] = {}
CACHE_EXPIRY_SECONDS = 600  # 10 minutes


def _load_fallback(lat: float, lon: float) -> Dict[str, Optional[float]]:
    try:
        with open(FALLBACK_WEATHER_FILE, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        payload = {}

    if not payload:
        timestamp = datetime.now(timezone.utc).isoformat()
        return {
            "temperature": None,
            "humidity": None,
            "rainfall": None,
            "wind_speed": None,
            "timestamp": timestamp,
            "location": f"{lat},{lon}",
        }

    return {
        "temperature": payload.get("temperature"),
        "humidity": payload.get("humidity"),
        "rainfall": payload.get("rainfall"),
        "wind_speed": payload.get("wind_speed"),
        "timestamp": payload.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "location": payload.get("location", f"{lat},{lon}"),
    }


async def get_realtime_weather(lat: float, lon: float) -> Dict[str, Optional[float]]:
    # Check cache first
    cache_key = f"{lat},{lon}"
    current_time = time()
    
    if cache_key in WEATHER_CACHE:
        cached_time, cached_weather = WEATHER_CACHE[cache_key]
        if current_time - cached_time < CACHE_EXPIRY_SECONDS:
            return cached_weather
        # Expired, remove from cache
        del WEATHER_CACHE[cache_key]
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": HOURLY_FIELDS,
        "forecast_days": 1,
        "timezone": "UTC",
    }

    # Retry logic: 3 attempts with 5 second timeout each
    max_attempts = 3
    timeout_seconds = 5.0
    
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()
                payload = response.json()
                
                # Success - process the response
                hourly = payload.get("hourly", {})
                times = hourly.get("time") or []
                if not times:
                    break  # Will fall through to fallback
                
                now_hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z")
                try:
                    idx = times.index(now_hour)
                except ValueError:
                    idx = len(times) - 1
                
                def _extract(key: str) -> Optional[float]:
                    values = hourly.get(key) or []
                    if not values:
                        return None
                    try:
                        return float(values[idx])
                    except (IndexError, TypeError, ValueError):
                        return None
                
                weather = {
                    "temperature": _extract("temperature_2m"),
                    "humidity": _extract("relative_humidity_2m"),
                    "rainfall": _extract("precipitation"),
                    "wind_speed": _extract("windspeed_10m"),
                    "timestamp": times[idx] if idx < len(times) else datetime.now(timezone.utc).isoformat(),
                    "location": f"{lat},{lon}",
                }
                
                # Fill missing values from fallback if needed
                if any(value is None for value in [weather.get("temperature"), weather.get("humidity"), weather.get("rainfall"), weather.get("wind_speed")]):
                    fallback = _load_fallback(lat, lon)
                    for key, fallback_value in fallback.items():
                        if weather.get(key) is None:
                            weather[key] = fallback_value
                
                # Cache the result
                WEATHER_CACHE[cache_key] = (current_time, weather)
                return weather
                
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
            # Retry on timeout/connection errors
            if attempt < max_attempts - 1:
                continue
            # All attempts failed, use fallback
            break
        except Exception:
            # Other errors, use fallback
            break
    
    # All attempts failed or no data, return fallback
    fallback = _load_fallback(lat, lon)
    # Cache fallback result too (shorter expiry could be considered, but keeping it simple)
    WEATHER_CACHE[cache_key] = (current_time, fallback)
    return fallback
