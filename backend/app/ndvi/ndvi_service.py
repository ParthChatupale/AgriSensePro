"""
NDVI Service

Computes NDVI time series from Sentinel-2 imagery.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .sentinel_client import sentinel_request
from .utils import create_bbox

# Import math for NaN/Inf checks
import math

logger = logging.getLogger(__name__)

# NDVI Evalscript for Sentinel-2 L2A
NDVI_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: ["B04", "B08"],
      units: "DN"
    }],
    output: {
      id: "default",
      bands: 1,
      sampleType: SampleType.FLOAT32
    }
  };
}

function evaluatePixel(samples) {
  // NDVI = (NIR - Red) / (NIR + Red)
  // B08 = NIR, B04 = Red
  const ndvi = (samples.B08 - samples.B04) / (samples.B08 + samples.B04);
  return [ndvi];
}
"""


async def compute_ndvi_timeseries(
    lat: float,
    lon: float,
    days: int = 30,
) -> List[Dict[str, Any]]:
    """
    Compute NDVI time series for a location over the past N days.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        days: Number of days to look back (default: 30)
    
    Returns:
        List of dictionaries with keys: date, mean_ndvi, max_ndvi, min_ndvi
    """
    # Create bounding box (5km × 5km)
    bbox = create_bbox(lat, lon, km=5.0)
    logger.info(f"Computing NDVI for location ({lat}, {lon}) over {days} days")
    
    # Generate date windows (5 days each to avoid empty scenes)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    results: List[Dict[str, Any]] = []
    
    # Process in 5-day windows
    current_date = start_date
    window_size = 5
    
    while current_date <= end_date:
        window_end = min(current_date + timedelta(days=window_size - 1), end_date)
        
        # Try each day in the window
        for day_offset in range(window_size):
            check_date = current_date + timedelta(days=day_offset)
            if check_date > end_date:
                break
            
            date_str = check_date.strftime("%Y-%m-%d")
            
            try:
                # Request NDVI data
                response_data = await sentinel_request(
                    bbox=bbox,
                    date=date_str,
                    evalscript=NDVI_EVALSCRIPT,
                )
                
                if not response_data:
                    logger.debug(f"No data available for {date_str}")
                    continue
                
                # Extract NDVI values from response
                # Response format: {"outputs": [{"default": {"values": [...]}}]}
                ndvi_values = _extract_ndvi_values(response_data)
                
                if not ndvi_values:
                    logger.debug(f"No valid NDVI values for {date_str}")
                    continue
                
                # Filter out invalid values (NaN, None, out of range)
                valid_values = [
                    v for v in ndvi_values
                    if v is not None
                    and not (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))
                    and -1.0 <= v <= 1.0
                ]
                
                if not valid_values:
                    logger.debug(f"No valid NDVI values after filtering for {date_str}")
                    continue
                
                # Compute statistics
                mean_ndvi = sum(valid_values) / len(valid_values)
                max_ndvi = max(valid_values)
                min_ndvi = min(valid_values)
                
                results.append({
                    "date": date_str,
                    "mean": round(mean_ndvi, 4),
                    "max": round(max_ndvi, 4),
                    "min": round(min_ndvi, 4),
                })
                
                logger.debug(
                    f"NDVI for {date_str}: mean={mean_ndvi:.4f}, "
                    f"min={min_ndvi:.4f}, max={max_ndvi:.4f}"
                )
                
                # Found data for this window, move to next window
                break
                
            except Exception as e:
                logger.error(f"Error processing NDVI for {date_str}: {e}", exc_info=True)
                continue
        
        # Move to next window
        current_date += timedelta(days=window_size)
    
    # Sort by date
    results.sort(key=lambda x: x["date"])
    
    logger.info(f"Computed NDVI for {len(results)} dates")
    return results


def _extract_ndvi_values(response_data: Dict[str, Any]) -> List[float]:
    """
    Extract NDVI values from SentinelHub Process API response.
    
    Args:
        response_data: Response from sentinel_request
    
    Returns:
        List of NDVI values
    """
    try:
        # Response structure can vary:
        # Option 1: {"outputs": [{"default": {"values": [...]}}]}
        # Option 2: {"default": {"values": [...]}}
        # Option 3: Direct array of values
        
        # Try outputs structure first
        if "outputs" in response_data:
            outputs = response_data.get("outputs", [])
            if outputs:
                output = outputs[0]
                default_data = output.get("default", {})
                values = default_data.get("values", [])
                if values:
                    return _flatten_values(values)
        
        # Try direct default structure
        if "default" in response_data:
            default_data = response_data.get("default", {})
            values = default_data.get("values", [])
            if values:
                return _flatten_values(values)
        
        # Try direct values array
        if "values" in response_data:
            values = response_data.get("values", [])
            if values:
                return _flatten_values(values)
        
        # Try statistics format (if available)
        if "statistics" in response_data:
            stats = response_data.get("statistics", {})
            # Extract mean, min, max if available
            result = []
            if "mean" in stats:
                result.append(float(stats["mean"]))
            if "min" in stats:
                result.append(float(stats["min"]))
            if "max" in stats:
                result.append(float(stats["max"]))
            if result:
                return result
        
        logger.warning(f"Could not extract NDVI values from response: {list(response_data.keys())}")
        return []
        
    except Exception as e:
        logger.error(f"Error extracting NDVI values: {e}", exc_info=True)
        return []


def _flatten_values(values: Any) -> List[float]:
    """
    Flatten and convert values to float list.
    
    Args:
        values: Can be list, nested list, or single value
    
    Returns:
        List of float values
    """
    flattened = []
    
    if isinstance(values, (int, float)):
        return [float(values)]
    
    if isinstance(values, list):
        for v in values:
            if isinstance(v, list):
                flattened.extend(_flatten_values(v))
            elif isinstance(v, (int, float)):
                flattened.append(float(v))
            elif v is not None:
                try:
                    flattened.append(float(v))
                except (ValueError, TypeError):
                    continue
    
    return flattened

