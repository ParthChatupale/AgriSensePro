from datetime import datetime, timedelta
import time
import math
import os
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ndvi.pipeline.ndvi_pipeline import run_ndvi, fetch_bands, compute_ndvi, apply_scl_mask
import numpy as np
import json

# Import VALID_SCL from pipeline (needed for apply_scl_mask to work correctly)
# The apply_scl_mask function uses VALID_SCL from the pipeline module


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


def _compute_ndvi_mean_only(lat: float, lon: float, radius_m: float, date: str) -> Optional[Dict[str, Any]]:
    """
    Lightweight function to compute NDVI mean for a single date without generating files.
    Returns stats dict with mean, min, max, valid_pixels or None if no data.
    """
    try:
        # Fetch bands (this downloads data from Sentinel)
        red, nir, scl, bbox = fetch_bands(lat, lon, radius_m, date)
        
        # Compute NDVI
        ndvi = compute_ndvi(red, nir)
        
        # Apply SCL mask (keep only vegetation pixels)
        ndvi_masked, mask = apply_scl_mask(ndvi, scl)
        
        # Compute statistics (same logic as write_stats but without saving)
        valid_mask = ~np.isnan(ndvi_masked)
        valid_pixels = int(np.sum(valid_mask))
        total_pixels = int(ndvi_masked.size)
        
        if valid_pixels == 0:
            return None
        
        def safe_num(x):
            try:
                xf = float(x)
                return None if math.isnan(xf) or math.isinf(xf) else xf
            except:
                return None
        
        stats = {
            "min": safe_num(np.nanmin(ndvi_masked)),
            "max": safe_num(np.nanmax(ndvi_masked)),
            "mean": safe_num(np.nanmean(ndvi_masked)),
            "valid_pixels": valid_pixels,
            "total_pixels": total_pixels
        }
        
        return stats
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error computing NDVI for date {date}: {e}", exc_info=True)
        return None


@router.get("/timeseries")
def get_ndvi_timeseries(
    lat: float = Query(..., description="Latitude in decimal degrees", ge=-90, le=90),
    lon: float = Query(..., description="Longitude in decimal degrees", ge=-180, le=180),
    days: int = Query(7, description="Number of days to look back", ge=1, le=30)
) -> Dict[str, Any]:
    """
    Get NDVI time series for past N days (lightweight - no file generation).
    
    Returns mean NDVI values for each date with available satellite data.
    Stores timeseries data in ndvi_timeseries folder.
    
    Args:
        lat: Latitude in decimal degrees (-90 to 90)
        lon: Longitude in decimal degrees (-180 to 180)
        days: Number of days to look back (1 to 30, default: 7)
    
    Returns:
        JSON response with location, range_days, and ndvi array:
        {
            "location": {"lat": float, "lon": float},
            "range_days": int,
            "ndvi": [
                {"date": "YYYY-MM-DD", "mean": float},
                ...
            ]
        }
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Validate parameters
    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail=f"Latitude must be between -90 and 90, got {lat}")
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail=f"Longitude must be between -180 and 180, got {lon}")
    if not (1 <= days <= 30):
        raise HTTPException(status_code=400, detail=f"Days must be between 1 and 30, got {days}")
    
    print(f"[TIMESERIES] Starting request: lat={lat}, lon={lon}, days={days}")
    logger.info(f"NDVI timeseries request: lat={lat}, lon={lon}, days={days}")
    
    # Create timeseries storage directory
    BASE_DIR = Path(__file__).parent  # backend/ndvi/
    TIMESERIES_DIR = BASE_DIR / "ndvi" / "data" / "ndvi_timeseries"
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate dates (past N days, backwards from today in UTC)
    today = datetime.utcnow().date()
    print(f"[TIMESERIES] Generating dates from {today - timedelta(days=days-1)} to {today}")
    results: List[Dict[str, Any]] = []
    
    # Loop through dates (oldest to newest)
    for day_offset in range(days - 1, -1, -1):  # From (days-1) days ago to today
        check_date = today - timedelta(days=day_offset)
        date_str = check_date.strftime("%Y-%m-%d")
        
        try:
            print(f"[TIMESERIES] Processing date: {date_str} ({days - day_offset}/{days})")
            logger.info(f"[TIMESERIES] Processing date: {date_str} ({days - day_offset}/{days})")
            
            # Compute NDVI mean (lightweight - no file generation)
            stats = _compute_ndvi_mean_only(lat, lon, radius_m=250, date=date_str)
            
            if stats and stats.get("mean") is not None and stats.get("valid_pixels", 0) > 0:
                mean_ndvi = stats["mean"]
                valid_pixels = stats["valid_pixels"]
                
                # Store this date's data
                date_result = {
                    "date": date_str,
                    "mean": round(float(mean_ndvi), 4)
                }
                results.append(date_result)
                
                # Save individual date data to timeseries folder
                date_file = TIMESERIES_DIR / f"{date_str}_{lat:.4f}_{lon:.4f}.json"
                date_data = {
                    "date": date_str,
                    "location": {"lat": lat, "lon": lon},
                    "stats": stats
                }
                with open(date_file, 'w') as f:
                    json.dump(date_data, f, indent=2)
                
                print(f"[TIMESERIES] ✓ {date_str}: mean={mean_ndvi:.4f}, valid_pixels={valid_pixels}")
                logger.info(f"[TIMESERIES] ✓ {date_str}: mean={mean_ndvi:.4f}, valid_pixels={valid_pixels}")
            else:
                print(f"[TIMESERIES] ✗ {date_str}: No valid data")
                logger.debug(f"[TIMESERIES] ✗ {date_str}: No valid data")
                
        except Exception as e:
            # Log error but continue with other dates
            print(f"[TIMESERIES] ✗ Error processing {date_str}: {e}")
            logger.warning(f"[TIMESERIES] Error processing date {date_str}: {e}", exc_info=True)
            continue
    
    # Sort results by date (should already be sorted, but ensure it)
    results.sort(key=lambda x: x["date"])
    
    # Save complete timeseries to a single file
    timeseries_file = TIMESERIES_DIR / f"timeseries_{lat:.4f}_{lon:.4f}_{days}days.json"
    timeseries_data = {
        "location": {"lat": lat, "lon": lon},
        "range_days": days,
        "request_date": datetime.utcnow().isoformat(),
        "ndvi": results
    }
    with open(timeseries_file, 'w') as f:
        json.dump(timeseries_data, f, indent=2)
    
    print(f"[TIMESERIES] Request completed: {len(results)}/{days} data points retrieved")
    print(f"[TIMESERIES] Data saved to: {timeseries_file}")
    logger.info(f"Timeseries request completed: {len(results)}/{days} data points")
    
    return {
        "location": {"lat": lat, "lon": lon},
        "range_days": days,
        "ndvi": results
    }

