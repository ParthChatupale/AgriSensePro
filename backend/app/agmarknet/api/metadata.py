"""
api/metadata.py
FastAPI router for Agmarknet metadata endpoints.

Provides:
GET /agmarknet/metadata/districts - Get all districts with their markets
GET /agmarknet/metadata/states - Get all states
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from typing import List, Dict

router = APIRouter(prefix="/agmarknet/metadata", tags=["Agmarknet Metadata"])

# Resolve paths relative to this file
BASE_DIR = Path(__file__).resolve().parents[3]  # project root (backend/)
METADATA_DIR = BASE_DIR / "app" / "agmarknet" / "metadata"


@router.get("/districts")
async def get_districts():
    """
    Get all districts with their markets from districts.json.
    
    Returns:
        List of districts with their markets
    """
    try:
        districts_file = METADATA_DIR / "districts.json"
        if not districts_file.exists():
            return JSONResponse({"error": "districts.json not found"}, status_code=404)
        
        with open(districts_file, "r", encoding="utf-8") as f:
            districts_data = json.load(f)
        
        return JSONResponse(districts_data)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/states")
async def get_states():
    """
    Get all states from states.json.
    
    Returns:
        List of states
    """
    try:
        states_file = METADATA_DIR / "states.json"
        if not states_file.exists():
            return JSONResponse({"error": "states.json not found"}, status_code=404)
        
        with open(states_file, "r", encoding="utf-8") as f:
            states_data = json.load(f)
        
        return JSONResponse(states_data)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

