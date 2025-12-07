"""
api/dashboard.py
FastAPI router for Agmarknet dashboard endpoint.

Provides:
GET /agmarknet/dashboard - Primary crop summary + trending crops
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from app.agmarknet.dashboard.service import get_primary_crop_data, get_trending_crops

router = APIRouter(prefix="/agmarknet", tags=["Agmarknet Dashboard"])


@router.get("/dashboard")
async def get_agmarknet_dashboard(
    state: str = Query(..., description="State name (e.g., 'Maharashtra')"),
    district: str = Query(..., description="District name (e.g., 'Akola')"),
    primary_crop: str = Query(..., description="Primary crop name (e.g., 'Soyabean')"),
    top_n: int = Query(3, ge=1, le=10, description="Number of trending crops to return (1-10)")
):
    """
    Get Agmarknet dashboard data: primary crop summary and trending crops.
    
    Returns:
        JSON with primary crop data and trending crops list
    """
    try:
        # Get primary crop data
        primary_data = get_primary_crop_data(
            state_name=state,
            district_name=district,
            primary_crop=primary_crop
        )
        
        # Get trending crops
        trending_data = get_trending_crops(
            state_name=state,
            district_name=district,
            top_n=top_n
        )
        
        # Build response
        response = {
            "state": state,
            "district": district,
            "primary": primary_data if primary_data else {
                "crop": primary_crop,
                "modal_price": None,
                "min_price": None,
                "max_price": None,
                "markets": [],
                "date": None,
                "rows_found": 0
            },
            "trending": trending_data
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        # Defensive: return empty response instead of crashing
        print(f"[Agmarknet Dashboard API] Error: {e}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse({
            "state": state,
            "district": district,
            "primary": {
                "crop": primary_crop,
                "modal_price": None,
                "min_price": None,
                "max_price": None,
                "markets": [],
                "date": None,
                "rows_found": 0
            },
            "trending": []
        })

