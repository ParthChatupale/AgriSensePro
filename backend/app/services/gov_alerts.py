"""Government alerts service for farmer.gov.in API integration."""
from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime

import httpx


async def fetch_gov_alerts(lat: float, lon: float) -> List[Dict[str, Any]]:
    """
    Fetch government alerts from farmer.gov.in agrilocatorservice.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        List of normalized alert dictionaries, or empty list on failure
    """
    try:
        url = "https://farmer.gov.in/FarmerHome/agrilocatorservice"
        params = {
            "lat": lat,
            "lon": lon,
        }
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Normalize response - handle different possible response formats
            alerts = []
            
            # Check if response is a list
            if isinstance(data, list):
                for item in data:
                    alert = _normalize_alert(item)
                    if alert:
                        alerts.append(alert)
            # Check if response has a data/records/alerts key
            elif isinstance(data, dict):
                # Try common keys
                items = (
                    data.get("data") or
                    data.get("records") or
                    data.get("alerts") or
                    data.get("results") or
                    []
                )
                if isinstance(items, list):
                    for item in items:
                        alert = _normalize_alert(item)
                        if alert:
                            alerts.append(alert)
                # If it's a single alert object
                elif isinstance(items, dict):
                    alert = _normalize_alert(items)
                    if alert:
                        alerts.append(alert)
            
            return alerts
            
    except httpx.TimeoutException:
        return []
    except httpx.HTTPStatusError:
        return []
    except Exception:
        return []


def _normalize_alert(item: Dict[str, Any]) -> Dict[str, Any] | None:
    """Normalize a single alert item from the API response."""
    if not isinstance(item, dict):
        return None
    
    # Extract fields with fallbacks for different possible field names
    title = (
        item.get("title") or
        item.get("alert_title") or
        item.get("subject") or
        item.get("name") or
        ""
    )
    
    description = (
        item.get("description") or
        item.get("alert_description") or
        item.get("message") or
        item.get("content") or
        item.get("details") or
        ""
    )
    
    alert_type = (
        item.get("alert_type") or
        item.get("type") or
        item.get("category") or
        item.get("alert_category") or
        "general"
    )
    
    # Extract date with various formats
    date_str = (
        item.get("date") or
        item.get("alert_date") or
        item.get("published_date") or
        item.get("created_at") or
        item.get("updated_at") or
        datetime.now().strftime("%Y-%m-%d")
    )
    
    # Normalize date format to YYYY-MM-DD
    try:
        # Try to parse various date formats
        if isinstance(date_str, str):
            # If it's already in YYYY-MM-DD format
            if len(date_str) >= 10 and date_str[4] == "-" and date_str[7] == "-":
                normalized_date = date_str[:10]
            else:
                # Try parsing with datetime
                parsed_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                normalized_date = parsed_date.strftime("%Y-%m-%d")
        else:
            normalized_date = datetime.now().strftime("%Y-%m-%d")
    except Exception:
        normalized_date = datetime.now().strftime("%Y-%m-%d")
    
    # Only return alert if it has at least a title or description
    if not title and not description:
        return None
    
    return {
        "title": title,
        "description": description,
        "alert_type": alert_type,
        "date": normalized_date,
        "source": "farmer_gov",
    }


__all__ = ["fetch_gov_alerts"]
