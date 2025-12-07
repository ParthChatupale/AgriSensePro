"""
dashboard/service.py
Service layer for Agmarknet dashboard data aggregation.

Provides:
- Primary crop price summary
- Trending crops analysis (comparing two cached Excel files)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd

# Import existing functions from fetcher (read-only, no modifications)
from app.agmarknet.fetchers.daily_state_report_fetcher import (
    fetch_daily_state_report,
    parse_daily_state_excel,
    normalize_market_name,
    _commodity_matches,
)
from app.agmarknet.utils.lookup_ids import MetadataLookup

# Resolve paths relative to this file
# __file__ is: backend/app/agmarknet/dashboard/service.py
# parents[3] gives: backend/ (project root, consistent with fetcher)
BASE_DIR = Path(__file__).resolve().parents[3]  # project root (backend/)
DOWNLOADS_DIR = BASE_DIR / "app" / "agmarknet" / "downloads" / "daily_state"
METADATA_DIR = BASE_DIR / "app" / "agmarknet" / "metadata"


def _load_districts_json() -> List[Dict]:
    """Load districts.json safely."""
    districts_file = METADATA_DIR / "districts.json"
    if not districts_file.exists():
        return []
    try:
        with open(districts_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _get_district_markets(district_name: str) -> set:
    """Get normalized market names for a district."""
    districts_data = _load_districts_json()
    if not districts_data:
        return set()
    
    # Find district by name (case-insensitive)
    district_entry = None
    for d in districts_data:
        if str(d.get("district_name", "")).strip().lower() == district_name.strip().lower():
            district_entry = d
            break
    
    if not district_entry:
        return set()
    
    markets_list = district_entry.get("markets", [])
    return {normalize_market_name(m.get("mkt_name")) for m in markets_list}


def _filter_rows_by_district(parsed_rows: List[Dict], district_name: str) -> List[Dict]:
    """Filter parsed rows by district using districts.json."""
    if not district_name:
        return parsed_rows
    
    district_markets = _get_district_markets(district_name)
    if not district_markets:
        return []
    
    return [
        r for r in parsed_rows
        if normalize_market_name(r.get("market")) in district_markets
    ]


def _filter_rows_by_commodity(parsed_rows: List[Dict], commodity_name: str) -> List[Dict]:
    """Filter parsed rows by commodity name."""
    if not commodity_name:
        return parsed_rows
    
    return [
        r for r in parsed_rows
        if _commodity_matches(r.get("commodity") or "", commodity_name)
    ]


def get_primary_crop_data(
    state_name: str,
    district_name: str,
    primary_crop: str
) -> Dict:
    """
    Get primary crop price summary.
    
    Args:
        state_name: State name (e.g., "Maharashtra")
        district_name: District name (e.g., "Akola")
        primary_crop: Primary crop name (e.g., "Soyabean")
    
    Returns:
        Dictionary with primary crop summary or empty dict if not found
    """
    try:
        # Print input variables
        print(f"\n📊 [Dashboard] Primary Crop Request:")
        print(f"   District: {district_name}")
        print(f"   Commodity: {primary_crop}")
        
        # Get state ID
        lookup = MetadataLookup()
        state_id = lookup.get_state_id(state_name)
        
        # Fetch data using existing fetcher
        df_cleaned, parsed_rows, chosen_date = fetch_daily_state_report(
            state_id=state_id,
            district_name=district_name,
            commodity_name=primary_crop,
            refresh_cache=False  # Use cached files
        )
        
        if not parsed_rows:
            print(f"   ❌ No data found")
            return {}
        
        # Calculate averages
        modal_prices = [r.get("modal_price") for r in parsed_rows if r.get("modal_price") is not None]
        min_prices = [r.get("min_price") for r in parsed_rows if r.get("min_price") is not None]
        max_prices = [r.get("max_price") for r in parsed_rows if r.get("max_price") is not None]
        
        # Get unique markets
        markets = list(set(r.get("market") for r in parsed_rows if r.get("market")))
        
        modal_price = sum(modal_prices) / len(modal_prices) if modal_prices else None
        
        # Print output
        if modal_price:
            print(f"   ✅ Modal Price: ₹{modal_price:.2f}/Quintal")
        else:
            print(f"   ⚠️  Modal Price: N/A")
        
        return {
            "crop": primary_crop,
            "modal_price": modal_price,
            "min_price": sum(min_prices) / len(min_prices) if min_prices else None,
            "max_price": sum(max_prices) / len(max_prices) if max_prices else None,
            "markets": markets,
            "date": chosen_date,
            "rows_found": len(parsed_rows)
        }
    except Exception as e:
        print(f"[Dashboard Service] Error getting primary crop data: {e}")
        return {}


def _get_latest_cached_files(count: int = 2) -> List[Path]:
    """Get the N most recent cached Excel files."""
    if not DOWNLOADS_DIR.exists():
        return []
    
    excel_files = list(DOWNLOADS_DIR.glob("*.xlsx"))
    # Filter out temporary Excel files (starting with ~$)
    excel_files = [f for f in excel_files if not f.name.startswith("~$")]
    
    if not excel_files:
        return []
    
    # Sort by modification time (most recent first)
    excel_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    return excel_files[:count]


def _parse_and_filter_file(
    file_path: Path,
    district_name: Optional[str] = None
) -> Tuple[List[Dict], str]:
    """
    Parse a cached Excel file and filter by district.
    
    Returns:
        Tuple of (parsed_rows, date_string)
    """
    try:
        # Parse using existing function
        df_cleaned, parsed_rows = parse_daily_state_excel(file_path)
        
        # Extract date from filename (format: YYYY-MM-DD.xlsx)
        date_str = file_path.stem
        
        # Filter by district if provided
        if district_name:
            parsed_rows = _filter_rows_by_district(parsed_rows, district_name)
        
        return parsed_rows, date_str
    except Exception as e:
        print(f"[Dashboard Service] Error parsing file {file_path}: {e}")
        return [], ""


def _group_by_commodity(parsed_rows: List[Dict]) -> Dict[str, List[Dict]]:
    """Group parsed rows by commodity name."""
    grouped = {}
    for row in parsed_rows:
        commodity = row.get("commodity")
        if commodity:
            if commodity not in grouped:
                grouped[commodity] = []
            grouped[commodity].append(row)
    return grouped


def _calculate_avg_modal_price(rows: List[Dict]) -> Optional[float]:
    """Calculate average modal price from rows."""
    prices = [r.get("modal_price") for r in rows if r.get("modal_price") is not None]
    if not prices:
        return None
    return sum(prices) / len(prices)


def get_trending_crops(
    state_name: str,
    district_name: Optional[str] = None,
    top_n: int = 3
) -> List[Dict]:
    """
    Get trending crops by comparing two most recent cached Excel files.
    
    Args:
        state_name: State name (for validation, not used in filtering)
        district_name: Optional district name to filter by
        top_n: Number of top trending crops to return
    
    Returns:
        List of trending crop dictionaries with percentage change
    """
    try:
        # Get two most recent cached files
        cached_files = _get_latest_cached_files(count=2)
        
        if len(cached_files) < 2:
            print(f"[Dashboard Service] Need at least 2 cached files, found {len(cached_files)}")
            return []
        
        # Parse both files
        file1_path = cached_files[1]  # Older file
        file2_path = cached_files[0]  # Newer file
        
        rows1, date1 = _parse_and_filter_file(file1_path, district_name)
        rows2, date2 = _parse_and_filter_file(file2_path, district_name)
        
        if not rows1 or not rows2:
            print(f"[Dashboard Service] One or both files have no data after filtering")
            return []
        
        # Group by commodity for both files
        grouped1 = _group_by_commodity(rows1)
        grouped2 = _group_by_commodity(rows2)
        
        # Calculate trending (commodities present in both files)
        trending = []
        
        for commodity, rows2_list in grouped2.items():
            if commodity not in grouped1:
                continue  # Skip if not in older file
            
            rows1_list = grouped1[commodity]
            
            avg1 = _calculate_avg_modal_price(rows1_list)
            avg2 = _calculate_avg_modal_price(rows2_list)
            
            if avg1 is None or avg2 is None or avg1 == 0:
                continue  # Skip if can't calculate percentage
            
            # Calculate percentage change: (new - old) / old
            pct_change = (avg2 - avg1) / avg1
            
            # Only include increasing commodities
            if pct_change > 0:
                trending.append({
                    "commodity": commodity,
                    "old_avg_modal": round(avg1, 2),
                    "new_avg_modal": round(avg2, 2),
                    "pct_change": round(pct_change, 4)  # 4 decimal places for precision
                })
        
        # Sort by percentage change (descending) and return top N
        trending.sort(key=lambda x: x["pct_change"], reverse=True)
        
        return trending[:top_n]
        
    except Exception as e:
        print(f"[Dashboard Service] Error getting trending crops: {e}")
        import traceback
        traceback.print_exc()
        return []


