"""
Utility functions for NDVI processing.
"""

from typing import List


def create_bbox(lat: float, lon: float, km: float = 5.0) -> List[float]:
    """
    Create a bounding box around a point in EPSG:4326 (WGS84).
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        km: Size of the bounding box in kilometers (default: 5km)
    
    Returns:
        List of [min_x, min_y, max_x, max_y] in EPSG:4326 format
    """
    # Approximate conversion: 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)
    lat_offset = km / 111.0
    lon_offset = km / (111.0 * abs(__import__('math').cos(__import__('math').radians(lat))))
    
    min_x = lon - lon_offset
    min_y = lat - lat_offset
    max_x = lon + lon_offset
    max_y = lat + lat_offset
    
    return [min_x, min_y, max_x, max_y]

