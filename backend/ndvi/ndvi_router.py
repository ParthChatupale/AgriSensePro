from datetime import datetime
import time
import math
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ndvi.pipeline.ndvi_pipeline import run_ndvi


router = APIRouter()


class NDVIRunRequest(BaseModel):
    lat: float = Field(..., description="Latitude in decimal degrees")
    lon: float = Field(..., description="Longitude in decimal degrees")
    radius: float = Field(250, description="Radius in meters (default 250)")
    date: Optional[str] = Field(None, description="Optional date in YYYY-MM-DD")


def _generate_out_prefix() -> str:
    # timestamp-based prefix keeps folder names unique and sortable
    return f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{int(time.time())}"


def _sanitize_stats(stats: dict):
    clean = {}
    for k, v in stats.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            clean[k] = None
        else:
            clean[k] = v
    return clean


@router.post("/run")
def run_ndvi_endpoint(req: NDVIRunRequest):
    out_prefix = _generate_out_prefix()

    try:
        result = run_ndvi(
            req.lat,
            req.lon,
            radius_m=req.radius,
            date=req.date,
            out_prefix=out_prefix,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    stats = result.get("stats", {})
    valid_pixels = stats.get("valid_pixels", 0)

    # 🟡 No valid NDVI data found
    if valid_pixels == 0:
        return {
            "status": "no_valid_data",
            "message": "No valid NDVI pixels found at this location (clouds, snow, water, or no data).",
            "job": out_prefix,
            "output_dir": result.get("output_dir")
        }

    # 🟢 Success
    return {
        "status": "ok",
        "job": out_prefix,
        "output_dir": result.get("output_dir"),
        "stats": stats
    }

