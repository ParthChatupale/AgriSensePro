"""
weekly_varietywise_fetcher.py
Fetches Weekly Variety-wise Prices Excel files from Agmarknet API.

Supports caching: uses local file first, downloads only if needed.
"""

import json
import requests
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional

BASE_URL = "https://api.agmarknet.gov.in/v1/price-trend/varietywise-prices-weekly"

# Resolve downloads directory relative to this file
# __file__ is: backend/app/agmarknet/fetchers/weekly_varietywise_fetcher.py
# parents[3] gives: backend/ (project root)
BASE_DIR = Path(__file__).resolve().parents[3]  # project root (backend/)
DOWNLOADS_DIR = BASE_DIR / "app" / "agmarknet" / "downloads" / "weekly_varietywise"


def extract_district_variety_rows(df2, district_name):
    """
    Extract rows belonging to a specific district in the Varietywise Weekly Price report.

    Structure of these Excel reports:
        row: district_name
        row+1: variety row (Other)
        row+2: variety row (Yellow)
        ...
        Next district marker → stop
    """
    
    # Normalize input
    target = district_name.strip().lower()
    
    # We assume the first column contains district names OR varieties.
    first_col = df2.columns[0]
    
    rows = df2.fillna("").copy()
    
    district_indices = []
    
    # Identify district-marker rows: they have text in first col but ALL OTHER columns empty.
    for idx, row in rows.iterrows():
        first = str(row[first_col]).strip()
        rest = row.iloc[1:]
        # Check if first column has text and all other columns are empty
        if first and rest.astype(str).str.strip().eq("").all():
            district_indices.append((idx, first.lower()))
    
    # Find target district marker row
    start_idx = None
    for idx, dname in district_indices:
        if target in dname:   # substring match
            start_idx = idx
            break
    
    if start_idx is None:
        print(f"⚠️ District '{district_name}' not found in varietywise Excel.")
        return df2.iloc[0:0]  # empty
    
    # Determine where the next district starts
    next_idx = None
    for idx, dname in district_indices:
        if idx > start_idx:
            next_idx = idx
            break
    
    # Slice rows between current district marker and next marker
    if next_idx:
        data_block = rows.iloc[start_idx+1 : next_idx]
    else:
        data_block = rows.iloc[start_idx+1 : ]
    
    # Remove blank rows
    data_block = data_block[data_block[first_col].astype(str).str.strip() != ""]
    
    data_block = data_block.reset_index(drop=True)
    return data_block


def _process_excel(file_path: Path, district_name: Optional[str] = None) -> pd.DataFrame:
    """
    Process varietywise Excel file and filter by district.
    
    Args:
        file_path: Path to Excel file
        district_name: District name to filter by (optional)
    
    Returns:
        Processed pandas DataFrame
    """
    # Load raw file WITHOUT headers
    df = pd.read_excel(file_path, header=None, engine="openpyxl")
    
    if df.empty:
        raise ValueError("Excel file contains no data")
    
    # -------------------------------------------------------------
    # 1. Remove title row (row 0)
    # -------------------------------------------------------------
    df = df.iloc[1:].reset_index(drop=True)
    
    # -------------------------------------------------------------
    # 2. Promote row 0 to header row
    # -------------------------------------------------------------
    df.columns = df.iloc[0].tolist()
    
    # Drop the header row now that it is applied
    df = df.iloc[1:].reset_index(drop=True)
    
    # df now has clean headers like:
    # ["Variety", "Prices 1-8 Dec 2025 Rs./Quintal", ...]
    # and district rows appear where "Variety" = district name
    
    # Filter by district if provided
    if district_name:
        result_df = extract_district_variety_rows(df, district_name)
    else:
        result_df = df
    
    return result_df


class WeeklyVarietywiseFetcher:
    """
    Fetcher for Weekly Variety-wise Prices Excel files.
    
    Supports caching: uses local cached file first, downloads only if needed.
    """
    
    @staticmethod
    def get_local_file_path(year: int, month: int, week: int) -> Path:
        """
        Get local file path for cached Excel file.
        
        Args:
            year: Year (integer, e.g., 2025)
            month: Month (integer, 1-12)
            week: Week number (integer, typically 1-4)
        
        Returns:
            Path object pointing to the cached Excel file
        """
        DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{year}_{month}_week{week}.xlsx"
        return DOWNLOADS_DIR / filename
    
    @staticmethod
    def fetch_excel(
        state_id: int,
        commodity_id: int,
        year: int,
        month: int,
        week: int,
        timeout: int = 45
    ) -> Tuple[str, Path]:
        """
        Fetch Excel file - check cache first, download if needed.
        
        Args:
            state_id: State ID (integer)
            commodity_id: Commodity ID (integer)
            year: Year (integer, e.g., 2025)
            month: Month (integer, 1-12)
            week: Week number (integer, typically 1-4)
            timeout: Request timeout in seconds (default: 45)
        
        Returns:
            Tuple of (status, file_path) where status is "cached" or "downloaded"
        """
        file_path = WeeklyVarietywiseFetcher.get_local_file_path(year, month, week)
        
        # If file exists, return cached
        if file_path.exists():
            return ("cached", file_path)
        
        # Otherwise, download
        status, path = WeeklyVarietywiseFetcher.download_excel(
            state_id, commodity_id, year, month, week, timeout
        )
        return (status, path)
    
    @staticmethod
    def download_excel(
        state_id: int,
        commodity_id: int,
        year: int,
        month: int,
        week: int,
        timeout: int = 45
    ) -> Tuple[str, Path]:
        """
        Download Excel file from Agmarknet API.
        
        Args:
            state_id: State ID (integer)
            commodity_id: Commodity ID (integer)
            year: Year (integer, e.g., 2025)
            month: Month (integer, 1-12)
            week: Week number (integer, typically 1-4)
            timeout: Request timeout in seconds (default: 45)
        
        Returns:
            Tuple of ("downloaded", file_path)
        
        Raises:
            requests.RequestException: If download fails
        """
        file_path = WeeklyVarietywiseFetcher.get_local_file_path(year, month, week)
        
        # Build API parameters
        params = {
            "report_mode": "Districtwise",
            "commodity": commodity_id,
            "year": year,
            "month": month,
            "export": "true",
            "downloadformat": "excel",
            "state": state_id,
            "district": 0,
            "week": week,
        }
        
        print(f"\n📥 Downloading from API...")
        print(f"URL: {BASE_URL}")
        print(f"Parameters: {params}")
        
        # Make request with timeout
        try:
            resp = requests.get(
                BASE_URL,
                params=params,
                timeout=timeout,
                headers={"User-Agent": "AgriSenseBot/1.0"}
            )
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            raise requests.RequestException(f"Request timed out after {timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise requests.RequestException(f"HTTP error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Request failed: {str(e)}")
        
        # Check if response is Excel file
        content_type = resp.headers.get("Content-Type", "").lower()
        if "excel" not in content_type and "spreadsheet" not in content_type:
            # Check if response is JSON error
            try:
                error_data = resp.json()
                error_msg = error_data.get("message", "Unknown error")
                raise requests.RequestException(f"API returned error: {error_msg}")
            except (ValueError, json.JSONDecodeError):
                pass
            raise requests.RequestException(
                f"Expected Excel file but received Content-Type: {content_type}"
            )
        
        # Remove existing file if it exists (to avoid permission errors)
        if file_path.exists():
            try:
                file_path.unlink()
            except PermissionError:
                raise IOError(
                    f"Cannot overwrite file {file_path}. "
                    "The file is currently open in Excel or locked by another program. "
                    "Please close the file and try again."
                )
        
        # Save file
        try:
            with open(file_path, "wb") as f:
                f.write(resp.content)
            print(f"✅ File saved to: {file_path}")
        except IOError as e:
            raise IOError(f"Failed to save file to {file_path}: {str(e)}")
        
        return ("downloaded", file_path)
    
    @staticmethod
    def fetch_and_process(
        state_id: int,
        commodity_id: int,
        year: int,
        month: int,
        week: int,
        district_name: Optional[str] = None,
        timeout: int = 45
    ) -> Tuple[pd.DataFrame, str]:
        """
        Fetch Excel file and process it, with intelligent caching.
        
        Flow:
        1. Call fetch_excel() to get cached or download file
        2. Load excel via processor
        3. After loading, attempt to download fresh excel:
           - If download successful, overwrite old file
           - Log "Refreshed cache"
        4. Return processed dataframe
        
        Args:
            state_id: State ID (integer)
            commodity_id: Commodity ID (integer)
            year: Year (integer, e.g., 2025)
            month: Month (integer, 1-12)
            week: Week number (integer, typically 1-4)
            district_name: District name to filter by (optional)
            timeout: Request timeout in seconds (default: 45)
        
        Returns:
            Tuple of (processed_dataframe, data_source) where data_source is "cached" or "downloaded"
        """
        # Step 1: Call fetch_excel()
        data_source, file_path = WeeklyVarietywiseFetcher.fetch_excel(
            state_id, commodity_id, year, month, week, timeout
        )
        
        print(f"\n📊 Using file: {file_path}")
        print(f"   Data source: {data_source}")
        
        # Step 2: Load excel via processor
        df = _process_excel(file_path, district_name)
        
        print(f"   Total rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Step 3: After loading, attempt to download fresh excel
        if data_source == "cached":
            print(f"\n🔁 Attempting to refresh cache from API...")
            try:
                # Download fresh file
                _, new_path = WeeklyVarietywiseFetcher.download_excel(
                    state_id, commodity_id, year, month, week, timeout
                )
                print(f"✅ Refreshed cache: {new_path}")
            except Exception as e:
                print(f"❌ Cache refresh failed (keeping old file): {e}")
                # Keep old file, don't raise error
        
        # Step 4: Return processed dataframe
        return df, data_source
