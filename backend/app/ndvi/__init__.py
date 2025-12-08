"""
NDVI Processing Module

This module provides NDVI (Normalized Difference Vegetation Index) computation
using Sentinel-2 satellite imagery via SentinelHub API.
"""

from .ndvi_router import router
from .ndvi_service import compute_ndvi_timeseries
from .utils import create_bbox

__all__ = ["router", "compute_ndvi_timeseries", "create_bbox"]

