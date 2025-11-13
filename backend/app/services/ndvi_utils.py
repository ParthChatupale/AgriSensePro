"""NDVI analysis utilities."""
from typing import Dict, Optional


def ndvi_stress_level(crop_meta: Dict, ndvi_value: Optional[float]) -> str:
    """Return NDVI stress level relative to typical min/max."""
    if ndvi_value is None or not crop_meta:
        return "unknown"

    low = crop_meta.get("typical_ndvi_min")
    high = crop_meta.get("typical_ndvi_max")
    if low is None or high is None:
        return "unknown"

    try:
        ndvi_val = float(ndvi_value)
    except (TypeError, ValueError):
        return "unknown"

    if ndvi_val < float(low):
        return "below_normal"
    if ndvi_val > float(high):
        return "above_normal"
    return "normal"


def compute_ndvi_change(current: Optional[float], previous: Optional[float]) -> float:
    """Compute NDVI change with safety checks."""
    try:
        curr = float(current)
    except (TypeError, ValueError):
        return 0.0

    if previous is None:
        return 0.0

    try:
        prev = float(previous)
    except (TypeError, ValueError):
        return 0.0

    return round(curr - prev, 3)
