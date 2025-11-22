"""Synthetic NDVI generation for development and testing."""
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional


def synthetic_ndvi(lat: float, lon: float, crop: str) -> float:
    """
    Generate a synthetic but realistic NDVI value.

    The NDVI follows a smooth seasonal curve:
    - Start of season: low (0.25–0.35)
    - Peak growth: high (0.70–0.85)
    - End of season: declining (0.40–0.60)
    """

    # Normalize crop-based NDVI range
    crop_ranges = {
        "cotton": (0.35, 0.80),
        "wheat": (0.45, 0.85),
        "rice": (0.40, 0.90),
        "soybean": (0.35, 0.80),
        "onion": (0.30, 0.75),
        "sugarcane": (0.50, 0.90),
    }
    base_min, base_max = crop_ranges.get(crop.lower(), (0.30, 0.80))

    # Create seasonal cycle (0–1)
    day_of_year = datetime.now().timetuple().tm_yday
    seasonal_phase = (math.sin(2 * math.pi * (day_of_year / 365)) + 1) / 2

    ndvi = base_min + (base_max - base_min) * seasonal_phase

    # Add small location-based variation
    ndvi += ((lat + lon) % 0.05) - 0.025

    return round(max(0.1, min(0.95, ndvi)), 4)


def synthetic_ndvi_history(lat: float, lon: float, crop: str, days: int = 7) -> List[Dict]:
    history = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        variation = math.sin(i / 3) * 0.02  # small wave
        value = synthetic_ndvi(lat, lon, crop) + variation
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "ndvi": round(max(0.1, min(0.95, value)), 4)
        })
    return list(reversed(history))

