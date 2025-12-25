from datetime import datetime, timedelta
import time
import math
import os
from typing import Optional, List, Dict, Any, Tuple
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


def _round_to_grid(lat: float, lon: float, grid_size: float = 0.01) -> Tuple[float, float]:
    """
    Round coordinates to grid cells for caching (1km grid by default).
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        grid_size: Grid size in degrees (default 0.01° ≈ 1km)
    
    Returns:
        Tuple of (grid_lat, grid_lon) rounded to grid
    """
    grid_lat = round(lat / grid_size) * grid_size
    grid_lon = round(lon / grid_size) * grid_size
    return grid_lat, grid_lon


def _get_cache_file_path(base_dir: Path, grid_lat: float, grid_lon: float) -> Path:
    """
    Get cache file path for grid coordinates.
    
    Args:
        base_dir: Base directory for timeseries data
        grid_lat: Grid latitude (rounded)
        grid_lon: Grid longitude (rounded)
    
    Returns:
        Path to cache file
    """
    # Round to 2 decimal places for filename (0.01 precision)
    cache_filename = f"timeseries_cache_{grid_lat:.2f}_{grid_lon:.2f}.json"
    return base_dir / cache_filename


def _load_cache(cache_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load cache file if it exists.
    
    Args:
        cache_path: Path to cache file
    
    Returns:
        Cache data dict or None if file doesn't exist
    """
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        return cache_data
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error loading cache file {cache_path}: {e}", exc_info=True)
        return None


def _save_cache(cache_path: Path, cache_data: Dict[str, Any]) -> None:
    """
    Save cache data to file.
    
    Args:
        cache_path: Path to cache file
        cache_data: Cache data dict to save
    """
    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving cache file {cache_path}: {e}", exc_info=True)


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


def _interpolate_ndvi_timeseries_backend(data: List[Dict[str, Any]], days: int = 7) -> List[Dict[str, Any]]:
    """
    Backend version of interpolation logic to compute all 7 interpolated values for logging.
    Same logic as frontend interpolation.
    
    Args:
        data: List of {date: str, mean: float} objects (raw data from API)
        days: Number of days to generate (default: 7)
    
    Returns:
        List of {date: str, mean: float, type: str} with all dates filled in (7 items)
        type is "real" for actual data, "interpolated" for computed values
    """
    if not data:
        return []

    today = datetime.utcnow().date()
    all_dates = []
    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        all_dates.append(date.strftime("%Y-%m-%d"))

    data_map = {item["date"]: item["mean"] for item in data if item.get("mean") is not None}
    interpolated_results = []

    for i, current_date_str in enumerate(all_dates):
        if current_date_str in data_map:
            interpolated_results.append({"date": current_date_str, "mean": data_map[current_date_str], "type": "real"})
            continue

        before_date_str = None
        before_value = None
        after_date_str = None
        after_value = None

        # Look backwards for the nearest data point
        for j in range(i - 1, -1, -1):
            check_date_str = all_dates[j]
            if check_date_str in data_map:
                before_date_str = check_date_str
                before_value = data_map[check_date_str]
                break

        # Look forwards for the nearest data point
        for j in range(i + 1, len(all_dates)):
            check_date_str = all_dates[j]
            if check_date_str in data_map:
                after_date_str = check_date_str
                after_value = data_map[check_date_str]
                break

        if before_value is not None and after_value is not None and before_date_str and after_date_str:
            # Linear interpolation between two points
            before_time = datetime.strptime(before_date_str, "%Y-%m-%d").timestamp()
            after_time = datetime.strptime(after_date_str, "%Y-%m-%d").timestamp()
            current_time = datetime.strptime(current_date_str, "%Y-%m-%d").timestamp()
            ratio = (current_time - before_time) / (after_time - before_time)
            interpolated_value = before_value + (after_value - before_value) * ratio
            interpolated_results.append({"date": current_date_str, "mean": round(float(interpolated_value), 4), "type": "interpolated"})
        elif before_value is not None:
            # Only have data before - forward fill
            interpolated_results.append({"date": current_date_str, "mean": round(float(before_value), 4), "type": "interpolated"})
        elif after_value is not None:
            # Only have data after - backward fill
            interpolated_results.append({"date": current_date_str, "mean": round(float(after_value), 4), "type": "interpolated"})
        else:
            # No data at all - skip this date (shouldn't happen if we have at least one data point)
            continue
    
    return interpolated_results


def _log_ndvi_data_and_change(raw_data: List[Dict[str, Any]], days: int):
    """
    Helper to log raw and interpolated NDVI data, and the 7-day change.
    """
    import logging
    logger = logging.getLogger(__name__)

    print("\n" + "=" * 70)
    print(f"[TIMESERIES DEBUG] Raw data ({len(raw_data)}/{days} days with valid satellite data):")
    print("=" * 70)
    if raw_data:
        for entry in raw_data:
            print(f"  {entry['date']}: NDVI = {entry['mean']:.4f} (real data)")
    else:
        print("  No raw data available.")

    # Interpolate for logging purposes (same logic as frontend)
    interpolated_for_log = _interpolate_ndvi_timeseries_backend(raw_data, days)

    print("\n" + "=" * 70)
    print(f"[TIMESERIES DEBUG] Interpolated {days}-day NDVI values (for graph):")
    print("=" * 70)
    if interpolated_for_log:
        for i, entry in enumerate(interpolated_for_log, 1):
            date_label = f"Day {i} ({entry['date']})"
            mean_val = f"{entry['mean']:.4f}" if entry['mean'] is not None else "N/A"
            data_type = entry.get('type', 'unknown')
            print(f"  {date_label:<20}: NDVI = {mean_val:<8} ({data_type})")
    else:
        print("  No interpolated data available.")

    if len(interpolated_for_log) == days and interpolated_for_log[0]['mean'] is not None and interpolated_for_log[-1]['mean'] is not None:
        first_mean = interpolated_for_log[0]['mean']
        last_mean = interpolated_for_log[-1]['mean']
        change = last_mean - first_mean
        print("\n" + "=" * 70)
        print(f"Change (Day {days} - Day 1): {last_mean:.4f} - {first_mean:.4f} = {change:+.4f}")
        print("======================================================================")
    else:
        print("\n" + "=" * 70)
        print("Cannot calculate 7-day change: Not enough interpolated data points or missing values.")
        print("======================================================================")


@router.get("/timeseries")
def get_ndvi_timeseries(
    lat: float = Query(..., description="Latitude in decimal degrees", ge=-90, le=90),
    lon: float = Query(..., description="Longitude in decimal degrees", ge=-180, le=180),
    days: int = Query(7, description="Number of days to look back", ge=1, le=30)
) -> Dict[str, Any]:
    """
    Get NDVI time series for past N days with smart caching (1km grid-based).
    
    Uses 1km grid-based caching to reuse data for nearby coordinates.
    Only computes today's date if cache exists, significantly improving performance.
    
    Returns mean NDVI values for each date with available satellite data.

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
    
    # Round to 1km grid for caching
    grid_lat, grid_lon = _round_to_grid(lat, lon, grid_size=0.01)
    
    print(f"[TIMESERIES] Request: lat={lat}, lon={lon} (grid: {grid_lat}, {grid_lon}), days={days}")
    logger.info(f"NDVI timeseries request: lat={lat}, lon={lon} (grid: {grid_lat}, {grid_lon}), days={days}")
    
    # Create timeseries storage directory
    BASE_DIR = Path(__file__).parent  # backend/ndvi/
    TIMESERIES_DIR = BASE_DIR / "ndvi" / "data" / "ndvi_timeseries"
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get cache file path
    cache_path = _get_cache_file_path(TIMESERIES_DIR, grid_lat, grid_lon)
    
    # Get today's date
    today = datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    
    # Try to load cache
    cache_data = _load_cache(cache_path)
    
    if cache_data and cache_data.get("last_updated"):
        last_updated_str = cache_data["last_updated"]
        try:
            last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d").date()
            
            # If cache is up to date (updated today), return cached data
            if last_updated == today:
                print(f"[TIMESERIES] Using cache (updated today): {cache_path}")
                logger.info(f"[TIMESERIES] Cache hit - returning cached data")
                
                cached_ndvi = cache_data.get("ndvi", [])
                # Filter to only include dates within the requested range
                cutoff_date = today - timedelta(days=days)
                filtered_ndvi = [
                    item for item in cached_ndvi 
                    if datetime.strptime(item["date"], "%Y-%m-%d").date() >= cutoff_date
                ]
                
                # Debug: Print all 7 values and change calculation
                _log_ndvi_data_and_change(filtered_ndvi, days)
                
                return {
                    "location": {"lat": lat, "lon": lon},
                    "range_days": days,
                    "ndvi": filtered_ndvi
                }
            
            # Cache exists but needs update (last updated before today)
            print(f"[TIMESERIES] Cache exists but outdated (last_updated: {last_updated_str}), computing only today")
            logger.info(f"[TIMESERIES] Cache exists but outdated, computing today's data only")
            
            # Load cached NDVI data
            cached_ndvi = cache_data.get("ndvi", [])
            cached_data_map = {item["date"]: item["mean"] for item in cached_ndvi if item.get("mean") is not None}
            
            # Compute only today's date
            today_stats = _compute_ndvi_mean_only(lat, lon, radius_m=250, date=today_str)
            
            if today_stats and today_stats.get("mean") is not None and today_stats.get("valid_pixels", 0) > 0:
                today_mean = round(float(today_stats["mean"]), 4)
                cached_data_map[today_str] = today_mean
                print(f"[TIMESERIES] ✓ Today ({today_str}): mean={today_mean:.4f}")
                logger.info(f"[TIMESERIES] ✓ Today ({today_str}): mean={today_mean:.4f}")
            else:
                print(f"[TIMESERIES] ✗ Today ({today_str}): No valid data (keeping cached data)")
                logger.debug(f"[TIMESERIES] ✗ Today ({today_str}): No valid data")
            
            # Remove dates older than requested range
            cutoff_date = today - timedelta(days=days)
            updated_ndvi = []
            for date_str, mean_val in sorted(cached_data_map.items()):
                item_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if item_date >= cutoff_date:
                    updated_ndvi.append({"date": date_str, "mean": mean_val})
            
            # Update cache
            cache_data["last_updated"] = today_str
            cache_data["ndvi"] = updated_ndvi
            cache_data["location"] = {"lat": lat, "lon": lon}  # Update with actual coordinates
            cache_data["grid_location"] = {"lat": grid_lat, "lon": grid_lon}
            
            _save_cache(cache_path, cache_data)
            
            # Debug: Print all 7 values and change calculation
            _log_ndvi_data_and_change(updated_ndvi, days)
            
            return {
                "location": {"lat": lat, "lon": lon},
                "range_days": days,
                "ndvi": updated_ndvi
            }
            
        except Exception as e:
            print(f"[TIMESERIES] Error processing cache: {e}, falling back to full computation")
            logger.warning(f"[TIMESERIES] Error processing cache: {e}", exc_info=True)
            # Fall through to full computation
    
    # No cache exists or cache is invalid - compute all dates (initial load)
    print(f"[TIMESERIES] No cache found, computing all {days} days (initial load)")
    logger.info(f"[TIMESERIES] No cache found, performing initial computation")
    
    results: List[Dict[str, Any]] = []
    
    # Generate all dates in the range
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
                
                results.append({
                    "date": date_str,
                    "mean": round(float(mean_ndvi), 4)
                })
                
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
    
    # Sort results by date
    results.sort(key=lambda x: x["date"])
    
    # Save to cache
    cache_data = {
        "location": {"lat": lat, "lon": lon},
        "grid_location": {"lat": grid_lat, "lon": grid_lon},
        "last_updated": today_str,
        "range_days": days,
        "ndvi": results
    }
    _save_cache(cache_path, cache_data)
    
    print(f"[TIMESERIES] Request completed: {len(results)}/{days} data points retrieved, cache saved")
    print(f"[TIMESERIES] Cache saved to: {cache_path}")
    logger.info(f"Timeseries request completed: {len(results)}/{days} data points")
    
    # Debug: Print all 7 values and change calculation
    _log_ndvi_data_and_change(results, days)
    
    return {
        "location": {"lat": lat, "lon": lon},
        "range_days": days,
        "ndvi": results
    }

