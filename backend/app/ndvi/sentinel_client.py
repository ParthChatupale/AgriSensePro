"""
SentinelHub API Client

Handles OAuth token management and Sentinel Process API requests.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

# Token cache
_token_cache: Optional[Dict[str, Any]] = None
_TOKEN_EXPIRY_SECONDS = 3600  # 1 hour


async def get_oauth_token() -> Optional[str]:
    """
    Get OAuth token from SentinelHub.
    
    Uses cached token if available and not expired.
    
    Returns:
        OAuth token string, or None if authentication fails
    """
    global _token_cache
    
    # Check cache
    if _token_cache is not None:
        cached_time = _token_cache.get("timestamp", 0)
        if time.time() - cached_time < _TOKEN_EXPIRY_SECONDS:
            logger.debug("Using cached OAuth token")
            return _token_cache.get("token")
    
    # Get credentials from environment
    client_id = os.getenv("SENTINEL_CLIENT_ID")
    client_secret = os.getenv("SENTINEL_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.error("SENTINEL_CLIENT_ID or SENTINEL_CLIENT_SECRET not found in environment")
        return None
    
    # Request token
    token_url = "https://services.sentinel-hub.com/oauth/token"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            token = data.get("access_token")
            if not token:
                logger.error("No access_token in OAuth response")
                return None
            
            # Cache token
            _token_cache = {
                "token": token,
                "timestamp": time.time(),
            }
            
            logger.info("Successfully obtained OAuth token from SentinelHub")
            return token
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting OAuth token: {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Request error getting OAuth token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting OAuth token: {e}", exc_info=True)
        return None


async def sentinel_request(
    bbox: list,
    date: str,
    evalscript: str,
    instance_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Make a request to SentinelHub Process API.
    
    Args:
        bbox: Bounding box [min_x, min_y, max_x, max_y] in EPSG:4326
        date: Date string in format "YYYY-MM-DD"
        evalscript: Evalscript code for processing
        instance_id: Optional SentinelHub instance ID (from env if not provided)
    
    Returns:
        Response data as dict, or None if request fails
    """
    token = await get_oauth_token()
    if not token:
        logger.error("Cannot make Sentinel request: no OAuth token")
        return None
    
    if instance_id is None:
        instance_id = os.getenv("SENTINEL_INSTANCE_ID")
        if not instance_id:
            logger.warning("SENTINEL_INSTANCE_ID not found, using default endpoint")
            instance_id = "default"
    
    # Process API endpoint (with instance ID if provided)
    if instance_id and instance_id != "default":
        process_url = f"https://services.sentinel-hub.com/api/v1/process/{instance_id}"
    else:
        process_url = "https://services.sentinel-hub.com/api/v1/process"
    
    # Request payload
    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                }
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{date}T00:00:00Z",
                            "to": f"{date}T23:59:59Z"
                        }
                    }
                }
            ]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "application/json"
                    }
                }
            ]
        },
        "evalscript": evalscript
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                process_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Successfully retrieved Sentinel data for {date}")
            return data
            
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error in Sentinel request: {e.response.status_code} - {e.response.text}"
        )
        return None
    except httpx.RequestError as e:
        logger.error(f"Request error in Sentinel request: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in Sentinel request: {e}", exc_info=True)
        return None

