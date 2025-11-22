"""Crop stage detection utilities."""
from typing import Dict, Tuple


def detect_crop_stage(crop_meta: Dict, days_since_sowing: float) -> str:
    """Detect crop stage based on metadata stage ranges."""
    if not crop_meta:
        return "unknown"

    stages = crop_meta.get("stages", {})
    if not isinstance(stages, dict):
        return "unknown"

    for stage, window in stages.items():
        if not isinstance(window, (list, tuple)) or len(window) != 2:
            continue
        start, end = window
        try:
            if float(start) <= days_since_sowing <= float(end):
                return stage
        except (TypeError, ValueError):
            continue
    return "unknown"
