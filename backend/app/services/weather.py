"""Realtime weather service backed by Open-Meteo."""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

import httpx
from datetime import datetime, timezone

BASE_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY_FIELDS = "temperature_2m,relative_humidity_2m,precipitation,windspeed_10m"

APP_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")
FALLBACK_WEATHER_FILE = os.path.join(DATA_DIR, "weather_data.json")


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
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": HOURLY_FIELDS,
        "forecast_days": 1,
        "timezone": "UTC",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except Exception:
        fallback = _load_fallback(lat, lon)
        return fallback

    hourly = payload.get("hourly", {})
    times = hourly.get("time") or []
    if not times:
        return _load_fallback(lat, lon)

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

    if any(value is None for value in weather.values()):
        fallback = _load_fallback(lat, lon)
        for key, fallback_value in fallback.items():
            weather.setdefault(key, fallback_value)

    return weather
