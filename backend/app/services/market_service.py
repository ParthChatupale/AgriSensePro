"""Agmarknet market price fetching service with fallback to local JSON."""
from __future__ import annotations

import json
import os
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

import httpx

# Agmarknet API endpoint (public, no auth required)
AGMARKNET_API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = "sample"  # Public sample key

# Backend directory for fallback file
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FALLBACK_FILE = os.path.join(BACKEND_DIR, "data", "market_prices.json")

# Crop name mapping to Agmarknet commodity names
CROP_MAPPING = {
    "cotton": "Cotton",
    "wheat": "Wheat",
    "rice": "Rice",
    "soybean": "Soybean",
    "onion": "Onion",
    "sugarcane": "Sugarcane",
}


def _normalize_crop_name(crop: str) -> str:
    """Convert crop name to Agmarknet format."""
    return CROP_MAPPING.get(crop.lower(), crop.capitalize())


def _load_fallback(crop: str) -> Dict[str, Any]:
    """Load market price from fallback JSON file."""
    try:
        with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            crop_data = data.get(crop.lower(), {})
            if isinstance(crop_data, dict):
                change_pct = crop_data.get("change_percent", 0.0)
                return {
                    "price": crop_data.get("price"),
                    "unit": crop_data.get("unit", "₹/quintal"),
                    "market": crop_data.get("market") or crop_data.get("mandi", "N/A"),
                    "price_change_percent": change_pct,
                    "change_percent": change_pct,  # For backward compatibility
                    "trend": "up" if change_pct > 0 else ("down" if change_pct < 0 else "stable"),
                }
    except Exception:
        pass
    
    # Ultimate fallback
    return {
        "price": None,
        "unit": "₹/quintal",
        "market": "N/A",
        "price_change_percent": 0.0,
        "trend": "stable",
    }


def _calculate_trend(current_price: float, previous_price: Optional[float]) -> tuple[float, str]:
    """Calculate price change percentage and trend."""
    if previous_price is None or previous_price == 0:
        return 0.0, "stable"
    
    change_percent = ((current_price - previous_price) / previous_price) * 100
    
    if change_percent > 0.5:
        trend = "up"
    elif change_percent < -0.5:
        trend = "down"
    else:
        trend = "stable"
    
    return round(change_percent, 2), trend


async def fetch_market_price(crop: str, district: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch real-time market price from Agmarknet API.
    
    Args:
        crop: Crop name (cotton, wheat, rice, etc.)
        district: Optional district name for filtering
    
    Returns:
        Dictionary with price, unit, market, price_change_percent, and trend
    """
    normalized_crop = _normalize_crop_name(crop)
    
    # Build API query parameters
    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[commodity]": normalized_crop,
        "limit": 50,
    }
    
    # Add district filter if provided
    if district:
        params["filters[district]"] = district
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(AGMARKNET_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Parse Agmarknet response
            records = data.get("records", [])
            if not records:
                # No data from API, use fallback
                return _load_fallback(crop)
            
            # Extract prices (Agmarknet structure may vary, handle common fields)
            prices = []
            for record in records:
                # Try common price field names
                price_str = (
                    record.get("modal_price") or
                    record.get("price") or
                    record.get("min_price") or
                    record.get("max_price") or
                    "0"
                )
                try:
                    price = float(str(price_str).replace(",", "").strip())
                    if price > 0:
                        prices.append({
                            "price": price,
                            "market": record.get("market", "N/A"),
                            "district": record.get("district", ""),
                            "date": record.get("arrival_date") or record.get("date", ""),
                        })
                except (ValueError, TypeError):
                    continue
            
            if not prices:
                return _load_fallback(crop)
            
            # Sort by date (most recent first) and district priority
            if district:
                district_prices = [p for p in prices if district.lower() in p.get("district", "").lower()]
                if district_prices:
                    prices = district_prices + [p for p in prices if p not in district_prices]
            
            # Get current price (first entry)
            current = prices[0]
            current_price = current["price"]
            
            # Try to get previous price for trend calculation
            previous_price = None
            if len(prices) >= 2:
                # Look for price from a different date
                current_date = current.get("date", "")
                for price_entry in prices[1:]:
                    if price_entry.get("date") != current_date:
                        previous_price = price_entry["price"]
                        break
            
            # If no previous price found, use fallback for change calculation
            if previous_price is None:
                fallback = _load_fallback(crop)
                previous_price = fallback.get("price")
            
            price_change_percent, trend = _calculate_trend(current_price, previous_price)
            
            return {
                "price": current_price,
                "unit": "₹/quintal",
                "market": current.get("market", "N/A"),
                "price_change_percent": price_change_percent,
                "change_percent": price_change_percent,  # For backward compatibility
                "trend": trend,
            }
            
    except httpx.TimeoutException:
        # API timeout, use fallback
        return _load_fallback(crop)
    except httpx.HTTPStatusError:
        # API error, use fallback
        return _load_fallback(crop)
    except Exception:
        # Any other error, use fallback
        return _load_fallback(crop)


__all__ = ["fetch_market_price"]

