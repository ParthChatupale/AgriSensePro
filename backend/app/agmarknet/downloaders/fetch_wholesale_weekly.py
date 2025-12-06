"""
fetch_wholesale_weekly.py
Downloads Weekly Wholesale Prices Excel file from Agmarknet API.

Fetches weekly wholesale price reports and saves them to disk.
"""

import json
import requests
from pathlib import Path
from typing import Optional

BASE_URL = "https://api.agmarknet.gov.in/v1/price-trend/wholesale-prices-weekly"

# Resolve downloads directory relative to this file
# __file__ is: backend/app/agmarknet/downloaders/fetch_wholesale_weekly.py
# parents[3] gives: backend/ (project root)
# Then: backend/app/agmarknet/downloads/weekly_wholesale/
BASE_DIR = Path(__file__).resolve().parents[3]  # project root (backend/)
DOWNLOADS_DIR = BASE_DIR / "app" / "agmarknet" / "downloads" / "weekly_wholesale"


def fetch_wholesale_weekly(
    state_id: int,
    commodity_id: int,
    year: int,
    month: int,
    week: int,
    timeout: int = 30
) -> str:
    """
    Download weekly wholesale prices Excel file from Agmarknet API.
    
    Args:
        state_id: State ID (integer)
        commodity_id: Commodity ID (integer)
        year: Year (integer, e.g., 2025)
        month: Month (integer, 1-12)
        week: Week number (integer, typically 1-4)
        timeout: Request timeout in seconds (default: 30)
    
    Returns:
        Path to downloaded Excel file (string)
    
    Raises:
        ValueError: If inputs are invalid
        requests.RequestException: If download fails
    """
    # Validate inputs
    if not isinstance(state_id, int) or state_id <= 0:
        raise ValueError(f"Invalid state_id: {state_id}. Must be a positive integer.")
    
    if not isinstance(commodity_id, int) or commodity_id <= 0:
        raise ValueError(f"Invalid commodity_id: {commodity_id}. Must be a positive integer.")
    
    if not isinstance(year, int) or year < 2000 or year > 2100:
        raise ValueError(f"Invalid year: {year}. Must be between 2000 and 2100.")
    
    if not isinstance(month, int) or month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be between 1 and 12.")
    
    if not isinstance(week, int) or week < 1 or week > 5:
        raise ValueError(f"Invalid week: {week}. Must be between 1 and 5.")
    
    # Build API URL with query parameters
    params = {
        "report_mode": "Districtwise",
        "commodity": commodity_id,
        "year": year,
        "month": month,
        "export": "true",
        "downloadformat": "excel",
        "state": state_id,
        "district": 0,  # 0 means all districts
        "week": week,
    }
    
    print(f"\n📥 Downloading Weekly Wholesale Prices...")
    print(f"URL: {BASE_URL}")
    print(f"Parameters: {params}")
    
    # Make request
    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=timeout,
            headers={"User-Agent": "AgriSenseBot/1.0"}
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise requests.RequestException(f"Request timed out after {timeout} seconds")
    except requests.exceptions.HTTPError as e:
        raise requests.RequestException(f"HTTP error {e.response.status_code}: {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Request failed: {str(e)}")
    
    # Check if response is Excel file
    content_type = response.headers.get("Content-Type", "").lower()
    if "excel" not in content_type and "spreadsheet" not in content_type:
        # Check if response is JSON error
        try:
            error_data = response.json()
            error_msg = error_data.get("message", "Unknown error")
            raise requests.RequestException(f"API returned error: {error_msg}")
        except (ValueError, json.JSONDecodeError):
            pass
        raise requests.RequestException(
            f"Expected Excel file but received Content-Type: {content_type}"
        )
    
    # Create downloads directory if it doesn't exist
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate filename: YYYY_MM_weekX.xlsx
    filename = f"{year}_{month:02d}_week{week}.xlsx"
    filepath = DOWNLOADS_DIR / filename
    
    # Save file
    try:
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"✅ File saved to: {filepath}")
    except IOError as e:
        raise IOError(f"Failed to save file to {filepath}: {str(e)}")
    
    return str(filepath)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 6:
        print("Usage: python fetch_wholesale_weekly.py <state_id> <commodity_id> <year> <month> <week>")
        sys.exit(1)
    
    try:
        state_id = int(sys.argv[1])
        commodity_id = int(sys.argv[2])
        year = int(sys.argv[3])
        month = int(sys.argv[4])
        week = int(sys.argv[5])
        
        filepath = fetch_wholesale_weekly(state_id, commodity_id, year, month, week)
        print(f"\n✅ Success! File downloaded to: {filepath}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

