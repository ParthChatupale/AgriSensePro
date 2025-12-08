"""
NDVI Router

FastAPI router for NDVI endpoints.
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

from .ndvi_service import compute_ndvi_timeseries

logger = logging.getLogger(__name__)

router = APIRouter(tags=["NDVI"])


@router.get("/ndvi")
async def get_ndvi(
    lat: float = Query(..., description="Latitude in decimal degrees", ge=-90, le=90),
    lon: float = Query(..., description="Longitude in decimal degrees", ge=-180, le=180),
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
) -> JSONResponse:
    """
    Returns NDVI trend for location for past N days.
    
    Uses Sentinel-2 L2A imagery to compute NDVI (Normalized Difference Vegetation Index)
    for a 5km × 5km area around the specified coordinates.
    
    Args:
        lat: Latitude in decimal degrees (-90 to 90)
        lon: Longitude in decimal degrees (-180 to 180)
        days: Number of days to look back (1 to 365, default: 30)
    
    Returns:
        JSON response with NDVI time series data
    """
    try:
        # Validate parameters
        if not (-90 <= lat <= 90):
            raise HTTPException(
                status_code=400,
                detail=f"Latitude must be between -90 and 90, got {lat}"
            )
        
        if not (-180 <= lon <= 180):
            raise HTTPException(
                status_code=400,
                detail=f"Longitude must be between -180 and 180, got {lon}"
            )
        
        if not (1 <= days <= 365):
            raise HTTPException(
                status_code=400,
                detail=f"Days must be between 1 and 365, got {days}"
            )
        
        logger.info(f"NDVI request: lat={lat}, lon={lon}, days={days}")
        
        # Compute NDVI time series
        ndvi_data = await compute_ndvi_timeseries(lat=lat, lon=lon, days=days)
        
        # Format response
        response: Dict[str, Any] = {
            "location": {
                "lat": lat,
                "lon": lon,
            },
            "range_days": days,
            "ndvi": ndvi_data,
        }
        
        logger.info(f"NDVI request completed: {len(ndvi_data)} data points")
        
        return JSONResponse(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in NDVI endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

