"""
Dashboard module for Agmarknet data aggregation.
Provides primary crop summary and trending crops analysis.
"""

from .service import get_primary_crop_data, get_trending_crops

__all__ = ["get_primary_crop_data", "get_trending_crops"]

