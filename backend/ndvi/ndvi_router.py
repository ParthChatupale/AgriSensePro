from datetime import datetime
import time
import math
import os
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
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


@router.get("/image/{job_id}/{filename}")
@router.head("/image/{job_id}/{filename}")
def get_ndvi_image(job_id: str, filename: str):
    """
    Serve NDVI image files.
    Security: Only allows files from the ndvi_jobs directory.
    """
    # Get the base directory - same calculation as ndvi_pipeline.py
    # ndvi_router.py is at: backend/ndvi/ndvi_router.py
    # Files are at: backend/ndvi/ndvi/data/ndvi_jobs/{job_id}/{filename}
    BASE_DIR = Path(__file__).parent  # backend/ndvi/
    # Construct path to ndvi_jobs directory (same as pipeline)
    NDVI_JOBS_DIR = BASE_DIR / "ndvi" / "data" / "ndvi_jobs"
    
    # Construct the full file path
    file_path = NDVI_JOBS_DIR / job_id / filename
    
    # Security: prevent directory traversal
    try:
        file_path = file_path.resolve()
        ndvi_jobs_dir_resolved = NDVI_JOBS_DIR.resolve()
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Requested image: job_id={job_id}, filename={filename}")
        logger.info(f"Resolved file path: {file_path}")
        logger.info(f"NDVI jobs dir: {ndvi_jobs_dir_resolved}")
        logger.info(f"File exists: {file_path.exists()}")
        
        # Ensure the file is within the ndvi_jobs directory (case-insensitive for Windows)
        file_path_str = str(file_path).lower()
        ndvi_jobs_dir_str = str(ndvi_jobs_dir_resolved).lower()
        
        if not file_path_str.startswith(ndvi_jobs_dir_str):
            logger.error(f"Path traversal attempt: {file_path} not in {ndvi_jobs_dir_resolved}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists
        if not file_path.exists() or not file_path.is_file():
            logger.error(f"File not found: {file_path}")
            raise HTTPException(status_code=404, detail=f"Image not found at: {file_path}")
        
        logger.info(f"Serving image: {file_path}")
        return FileResponse(file_path)
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error serving image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")

