"""
daily_state_report_fetcher.py
Fetches Daily State Report Excel files from Agmarknet API.

Supports automatic date fallback and Excel parsing.
"""

import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional
import unicodedata
import re
from difflib import SequenceMatcher

BASE_URL = "https://api.agmarknet.gov.in/v1/prices-and-arrivals/commodity-market/daily-report-state"

# Resolve downloads directory relative to this file
# __file__ is: backend/app/agmarknet/fetchers/daily_state_report_fetcher.py
# parents[3] gives: backend/ (project root)
BASE_DIR = Path(__file__).resolve().parents[3]  # project root (backend/)
DOWNLOADS_DIR = BASE_DIR / "app" / "agmarknet" / "downloads" / "daily_state"


def normalize_market_name(s):
    """Normalize market name for robust matching with Unicode support."""
    if not s:
        return ""
    s = str(s).lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\xa0", " ").replace("\u200b", "")
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _normalize_text(s: Optional[str]) -> str:
    """Normalize text for matching: lower, strip, remove punctuation, collapse whitespace."""
    if not s:
        return ""
    s = str(s).lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)   # replace punctuation with space
    s = re.sub(r"\s+", " ", s)      # collapse multiple spaces
    return s


def _is_close_match(a: str, b: str, threshold: float = 0.85) -> bool:
    """Optional fuzzy check — returns True if similarity >= threshold."""
    if not a or not b:
        return False
    return SequenceMatcher(None, a, b).ratio() >= threshold


def _commodity_matches(parsed_commodity: str, target_name: str) -> bool:
    """
    Decide whether parsed_commodity (from Excel) matches target_name (user).
    Strategy:
      1. Normalize both.
      2. Exact equality -> True
      3. Substring checks (parsed contains target OR target contains parsed) -> True
      4. Fuzzy similarity check as last resort (optional)
    """
    p = _normalize_text(parsed_commodity)
    t = _normalize_text(target_name)
    if not p or not t:
        return False
    if p == t:
        return True
    if t in p or p in t:
        return True
    # fuzzy fallback (keeps false positives low for short strings)
    return _is_close_match(p, t, threshold=0.87)


def parse_daily_state_excel(file_path: Path) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Parse Daily State Report Excel file into structured data.
    
    Parsing logic:
    - Load Excel with no header
    - Skip top 3 rows
    - Row 2 contains true headers → assign them
    - Rows contain:
      - Commodity Group Line → "Commodity Group Name : X"
      - Commodity Name Line → "Commodity Name : Y"
      - Market rows → actual numeric rows
    
    Args:
        file_path: Path to Excel file
    
    Returns:
        Tuple of (cleaned DataFrame, list of parsed dict rows)
    """
    # Load Excel with no header
    df = pd.read_excel(file_path, header=None, engine="openpyxl")
    
    if df.empty:
        return pd.DataFrame(), []
    
    # Skip top 3 rows (Row 0: Title, Row 1: empty, Row 2: Header)
    # Start processing from Row 3 onwards
    df = df.iloc[3:].reset_index(drop=True)
    
    if len(df) == 0:
        return pd.DataFrame(), []
    
    # Parse using safe logic without ambiguous Series checks
    parsed = []
    current_group = None
    current_commodity = None
    
    for idx, row in df.iterrows():
        # Safely get first column value
        first_val = row.iloc[0] if len(row) > 0 else None
        first = str(first_val).strip() if pd.notna(first_val) else ""
        
        # Skip empty rows safely
        if row.isna().all() or first == "nan" or first == "":
            continue
        
        # Detect Commodity Group Name
        if first.startswith("Commodity Group Name"):
            parts = first.split(":", 1)
            if len(parts) > 1:
                current_group = parts[1].strip()
            continue
        
        # Detect Commodity Name
        if first.startswith("Commodity Name"):
            parts = first.split(":", 1)
            if len(parts) > 1:
                current_commodity = parts[1].strip()
            continue
        
        # Detect Market Row:
        # A valid market row must NOT be a header and NOT a group/commodity line.
        if (
            first not in ("Market", "Variety")
            and not first.startswith("Commodity")
            and current_group is not None
            and current_commodity is not None
        ):
            # Safely extract values using positional indexing
            arrivals_val = row.iloc[1] if len(row) > 1 else None
            unit_arrivals_val = row.iloc[2] if len(row) > 2 else None
            variety_val = row.iloc[3] if len(row) > 3 else None
            min_price_val = row.iloc[4] if len(row) > 4 else None
            max_price_val = row.iloc[5] if len(row) > 5 else None
            modal_price_val = row.iloc[6] if len(row) > 6 else None
            unit_price_val = row.iloc[7] if len(row) > 7 else None
            
            parsed.append({
                "group": current_group,
                "commodity": current_commodity,
                "market": first,
                "arrivals": arrivals_val if pd.notna(arrivals_val) else None,
                "unit_arrivals": unit_arrivals_val if pd.notna(unit_arrivals_val) else None,
                "variety": str(variety_val).strip() if pd.notna(variety_val) else None,
                "min_price": min_price_val if pd.notna(min_price_val) else None,
                "max_price": max_price_val if pd.notna(max_price_val) else None,
                "modal_price": modal_price_val if pd.notna(modal_price_val) else None,
                "unit_price": unit_price_val if pd.notna(unit_price_val) else None,
            })
    
    # Create cleaned DataFrame from parsed rows
    if parsed:
        df_cleaned = pd.DataFrame(parsed)
    else:
        df_cleaned = pd.DataFrame()
    
    return df_cleaned, parsed


def fetch_daily_state_report(
    state_id: int,
    target_date: Optional[str] = None,
    district_name: Optional[str] = None,
    commodity_name: Optional[str] = None,
    refresh_cache: bool = False
) -> Tuple[pd.DataFrame, List[Dict], str]:
    """
    Fetch Daily State Report Excel file with automatic date fallback.
    
    Behavior:
    - If target_date=None, start with 2 days ago
    - Try up to 3 dates: today - 2, today - 3, today - 4
    - For each date, download Excel
    - If file has > 5 data rows, accept it and stop fallback
    - If district_name is provided, filter results to markets in that district
    
    Args:
        state_id: State ID (integer)
        target_date: Target date in YYYY-MM-DD format (optional, defaults to 2 days ago)
        district_name: District name to filter by (optional)
    
    Returns:
        Tuple of (cleaned DataFrame, list of parsed dict rows, chosen date string)
    
    Raises:
        requests.RequestException: If all date attempts fail
        ValueError: If no valid data found after all attempts
    """
    # Create downloads directory
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Determine dates to try
    today = datetime.now()
    dates_to_try = []
    
    if target_date:
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            dates_to_try = [target_dt]
        except ValueError:
            raise ValueError(f"Invalid date format: {target_date}. Expected YYYY-MM-DD")
    else:
        # Try date-2, date-3, date-4
        for i in range(2, 5):
            dates_to_try.append(today - timedelta(days=i))
    
    # Try each date
    last_error = None
    initial_date = dates_to_try[0] if dates_to_try else None  # Store first date for fallback limit
    
    for date_idx, date_obj in enumerate(dates_to_try):
        date_str = date_obj.strftime("%Y-%m-%d")
        file_path = DOWNLOADS_DIR / f"{date_str}.xlsx"
        
        # Only allow fallback dates for the first date in the main loop
        # Fallback dates should only go back 3 days from the first date, not from each date
        allow_fallback = (date_idx == 0) and (initial_date is not None)
        
        # Check if cached file exists and refresh_cache is False
        if file_path.exists() and not refresh_cache:
            print(f"\n⚡ Using cached file: {file_path}")
            try:
                # Parse the cached file immediately
                df_cleaned, parsed_rows = parse_daily_state_excel(file_path)
                
                if len(parsed_rows) > 0:
                    # Apply district filtering if district_name is provided
                    if district_name:
                        # ---------------------------------------------------------
                        # DISTRICT FILTERING (correct implementation)
                        # ---------------------------------------------------------
                        
                        # Load districts.json directly (authoritative source)
                        district_file = BASE_DIR / "app" / "agmarknet" / "metadata" / "districts.json"
                        if not district_file.exists():
                            print(f"⚠️ districts.json not found at {district_file}")
                            return df_cleaned, parsed_rows, date_str
                        
                        districts_data = json.loads(district_file.read_text(encoding="utf-8"))
                        
                        # Find district by name (case-insensitive)
                        district_entry = None
                        for d in districts_data:
                            if str(d.get("district_name", "")).strip().lower() == district_name.strip().lower():
                                district_entry = d
                                break
                        
                        if not district_entry:
                            print(f"⚠️ District '{district_name}' not found in districts.json")
                            return df_cleaned, [], date_str
                        
                        # Extract markets list from districts.json
                        markets_list = district_entry.get("markets", [])
                        if not markets_list:
                            print(f"⚠️ District '{district_name}' has no markets listed in districts.json")
                            return df_cleaned, [], date_str
                        
                        # Normalize market names
                        district_market_names = {normalize_market_name(m.get("mkt_name")) for m in markets_list}
                        
                        # Filter parsed rows by normalized market name
                        district_rows = [
                            r for r in parsed_rows
                            if normalize_market_name(r.get("market")) in district_market_names
                        ]
                        
                        if not district_rows:
                            print(
                                f"⚠️ No rows matched markets for district '{district_name}' on {date_str}.\n"
                                f"   Markets expected: {list(district_market_names)[:10]}"
                            )
                            # Try fallback dates: only for first date, go back up to 3 days from initial date
                            if not allow_fallback:
                                print(f"❌ No data found for district '{district_name}' on {date_str}. Skipping fallback (only allowed for first date).")
                                continue
                            
                            print(f"🔄 Trying fallback dates (up to 3 days before {date_str})...")
                            fallback_found = False
                            
                            for fallback_days in range(1, 4):  # Try 1, 2, 3 days before
                                fallback_date = initial_date - timedelta(days=fallback_days)
                                fallback_date_str = fallback_date.strftime("%Y-%m-%d")
                                fallback_file_path = DOWNLOADS_DIR / f"{fallback_date_str}.xlsx"
                                
                                print(f"   📥 Trying fallback date: {fallback_date_str}")
                                
                                # Download fallback file if not cached
                                if not fallback_file_path.exists() or refresh_cache:
                                    try:
                                        fallback_params = {
                                            "liveDate": fallback_date_str,
                                            "date": fallback_date_str,
                                            "state": state_id,
                                            "includeExcel": "true"
                                        }
                                        print(f"   🔗 Downloading from URL with date: {fallback_date_str}")
                                        fallback_resp = requests.get(
                                            BASE_URL,
                                            params=fallback_params,
                                            timeout=45,
                                            headers={"User-Agent": "AgriSenseBot/1.0"}
                                        )
                                        fallback_resp.raise_for_status()
                                        
                                        content_type = fallback_resp.headers.get("Content-Type", "").lower()
                                        if "excel" not in content_type and "spreadsheet" not in content_type:
                                            print(f"   ⚠️  Skipping {fallback_date_str}: not an Excel file")
                                            continue
                                        
                                        with open(fallback_file_path, "wb") as f:
                                            f.write(fallback_resp.content)
                                        print(f"   ✅ Downloaded fallback file: {fallback_date_str}.xlsx")
                                    except Exception as e:
                                        print(f"   ❌ Failed to download fallback file for {fallback_date_str}: {e}")
                                        continue
                                
                                # Parse fallback file
                                try:
                                    fallback_df, fallback_parsed = parse_daily_state_excel(fallback_file_path)
                                    
                                    if len(fallback_parsed) > 5:
                                        # Filter by district
                                        fallback_district_rows = [
                                            r for r in fallback_parsed
                                            if normalize_market_name(r.get("market")) in district_market_names
                                        ]
                                        
                                        if fallback_district_rows:
                                            print(f"   ✅ Found {len(fallback_district_rows)} rows for district '{district_name}' on {fallback_date_str}")
                                            district_rows = fallback_district_rows
                                            parsed_rows = fallback_parsed  # Update parsed_rows for commodity filtering
                                            date_str = fallback_date_str  # Update to use fallback date
                                            fallback_found = True
                                            break
                                        else:
                                            print(f"   ⚠️  No district data in fallback file {fallback_date_str}")
                                    else:
                                        print(f"   ⚠️  Fallback file {fallback_date_str} has insufficient data")
                                except Exception as e:
                                    print(f"   ❌ Error parsing fallback file {fallback_date_str}: {e}")
                                    continue
                            
                            if not fallback_found:
                                print(f"❌ No data found for district '{district_name}' after trying fallback dates from {date_str}")
                                # Continue to next date in main loop instead of returning
                                continue
                        
                        # At this point `district_rows` is a list of parsed row dicts for the district.
                        # If a commodity_name was provided, filter the district_rows further.
                        if commodity_name:
                            # Primary filter: match by 'commodity' field in parsed rows
                            matches_by_name = [
                                r for r in district_rows
                                if _commodity_matches(r.get("commodity") or "", commodity_name)
                            ]
                            
                            if matches_by_name:
                                df_cleaned = pd.DataFrame(matches_by_name)
                                print(f"✅ Filtered by commodity name '{commodity_name}': {len(matches_by_name)} rows matched.")
                                # Log detailed row information for debugging
                                print(f"   📋 Detailed row data:")
                                for idx, row in enumerate(matches_by_name, 1):
                                    print(f"      Row {idx}: Market='{row.get('market')}', "
                                          f"Commodity='{row.get('commodity')}', "
                                          f"Modal={row.get('modal_price')}, Min={row.get('min_price')}, Max={row.get('max_price')}, "
                                          f"Variety='{row.get('variety')}', Arrivals={row.get('arrivals')}")
                                # Log all markets in district for comparison
                                print(f"   🔍 District '{district_name}' markets in districts.json:")
                                for mkt in markets_list[:5]:  # Show first 5
                                    print(f"      - {mkt.get('mkt_name')}")
                                return df_cleaned, matches_by_name, date_str
                            
                            # Fallback: try matching by commodity group (if user gave an ambiguous name)
                            # e.g. user passes 'Pulses' or 'Oil Seeds' — try matching against parsed 'group'
                            matches_by_group = [
                                r for r in district_rows
                                if _commodity_matches(r.get("group") or "", commodity_name)
                            ]
                            if matches_by_group:
                                df_cleaned = pd.DataFrame(matches_by_group)
                                print(f"⚠️ No exact commodity-name matches for '{commodity_name}', "
                                      f"but matched by group: {len(matches_by_group)} rows returned.")
                                return df_cleaned, matches_by_group, date_str
                            
                            # No matches found - try fallback dates (only for first date)
                            print(f"⚠️ No data found for commodity '{commodity_name}' in district '{district_name}' on {date_str}.")
                            # Try fallback dates: only for first date, go back up to 3 days from initial date
                            if not allow_fallback:
                                print(f"❌ No data found for commodity '{commodity_name}' in district '{district_name}' on {date_str}. Skipping fallback (only allowed for first date).")
                                continue
                            
                            print(f"🔄 Trying fallback dates for commodity (up to 3 days before {date_str})...")
                            fallback_found = False
                            
                            for fallback_days in range(1, 4):  # Try 1, 2, 3 days before
                                fallback_date = initial_date - timedelta(days=fallback_days)
                                fallback_date_str = fallback_date.strftime("%Y-%m-%d")
                                fallback_file_path = DOWNLOADS_DIR / f"{fallback_date_str}.xlsx"
                                
                                print(f"   📥 Trying fallback date: {fallback_date_str}")
                                
                                # Download fallback file if not cached
                                if not fallback_file_path.exists() or refresh_cache:
                                    try:
                                        fallback_params = {
                                            "liveDate": fallback_date_str,
                                            "date": fallback_date_str,
                                            "state": state_id,
                                            "includeExcel": "true"
                                        }
                                        print(f"   🔗 Downloading from URL with date: {fallback_date_str}")
                                        fallback_resp = requests.get(
                                            BASE_URL,
                                            params=fallback_params,
                                            timeout=45,
                                            headers={"User-Agent": "AgriSenseBot/1.0"}
                                        )
                                        fallback_resp.raise_for_status()
                                        
                                        content_type = fallback_resp.headers.get("Content-Type", "").lower()
                                        if "excel" not in content_type and "spreadsheet" not in content_type:
                                            print(f"   ⚠️  Skipping {fallback_date_str}: not an Excel file")
                                            continue
                                        
                                        with open(fallback_file_path, "wb") as f:
                                            f.write(fallback_resp.content)
                                        print(f"   ✅ Downloaded fallback file: {fallback_date_str}.xlsx")
                                    except Exception as e:
                                        print(f"   ❌ Failed to download fallback file for {fallback_date_str}: {e}")
                                        continue
                                
                                # Parse fallback file
                                try:
                                    fallback_df, fallback_parsed = parse_daily_state_excel(fallback_file_path)
                                    
                                    if len(fallback_parsed) > 5:
                                        # Filter by district first
                                        fallback_district_rows = [
                                            r for r in fallback_parsed
                                            if normalize_market_name(r.get("market")) in district_market_names
                                        ]
                                        
                                        if fallback_district_rows:
                                            # Then filter by commodity
                                            fallback_commodity_rows = [
                                                r for r in fallback_district_rows
                                                if _commodity_matches(r.get("commodity") or "", commodity_name)
                                            ]
                                            
                                            if fallback_commodity_rows:
                                                print(f"   ✅ Found {len(fallback_commodity_rows)} rows for commodity '{commodity_name}' in district '{district_name}' on {fallback_date_str}")
                                                df_cleaned = pd.DataFrame(fallback_commodity_rows)
                                                date_str = fallback_date_str  # Update to use fallback date
                                                fallback_found = True
                                                return df_cleaned, fallback_commodity_rows, date_str
                                            else:
                                                print(f"   ⚠️  No commodity data in fallback file {fallback_date_str}")
                                        else:
                                            print(f"   ⚠️  No district data in fallback file {fallback_date_str}")
                                    else:
                                        print(f"   ⚠️  Fallback file {fallback_date_str} has insufficient data")
                                except Exception as e:
                                    print(f"   ❌ Error parsing fallback file {fallback_date_str}: {e}")
                                    continue
                            
                            if not fallback_found:
                                print(f"❌ No data found for commodity '{commodity_name}' in district '{district_name}' after trying fallback dates from {date_str}")
                                # Continue to next date in main loop instead of returning
                                continue
                        
                        # No commodity filter requested → return district_rows
                        df_cleaned = pd.DataFrame(district_rows)
                        return df_cleaned, district_rows, date_str
                    
                    # No district filtering, but check for commodity filtering
                    if commodity_name:
                        # Primary filter: match by 'commodity' field in parsed rows
                        matches_by_name = [
                            r for r in parsed_rows
                            if _commodity_matches(r.get("commodity") or "", commodity_name)
                        ]
                        
                        if matches_by_name:
                            df_cleaned = pd.DataFrame(matches_by_name)
                            print(f"✅ Filtered by commodity name '{commodity_name}': {len(matches_by_name)} rows matched.")
                            return df_cleaned, matches_by_name, date_str
                        
                        # Fallback: try matching by commodity group
                        matches_by_group = [
                            r for r in parsed_rows
                            if _commodity_matches(r.get("group") or "", commodity_name)
                        ]
                        if matches_by_group:
                            df_cleaned = pd.DataFrame(matches_by_group)
                            print(f"⚠️ No exact commodity-name matches for '{commodity_name}', "
                                  f"but matched by group: {len(matches_by_group)} rows returned.")
                            return df_cleaned, matches_by_group, date_str
                        
                        # No matches found
                        print(f"⚠️ No data found for commodity '{commodity_name}' on {date_str}.")
                        return pd.DataFrame([]), [], date_str
                    
                    # No district or commodity filtering, return all parsed rows
                    return df_cleaned, parsed_rows, date_str
                else:
                    # Cached file has no data, proceed to download
                    print(f"⚠️  Cached file has no data. Proceeding to download...")
            except Exception as e:
                print(f"⚠️  Failed to process cached file: {e}. Proceeding to download...")
                # Fall through to download logic
        
        print(f"\n📥 Attempting to fetch Daily State Report for {date_str}...")
        
        # Build URL with parameters
        params = {
            "liveDate": date_str,
            "date": date_str,
            "state": state_id,
            "includeExcel": "true"
        }
        
        print(f"URL: {BASE_URL}")
        print(f"Parameters: {params}")
        
        try:
            # Download Excel
            resp = requests.get(
                BASE_URL,
                params=params,
                timeout=45,
                headers={"User-Agent": "AgriSenseBot/1.0"}
            )
            resp.raise_for_status()
            
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
            
            # Save file
            if file_path.exists():
                try:
                    file_path.unlink()
                except PermissionError:
                    raise IOError(
                        f"Cannot overwrite file {file_path}. "
                        "The file is currently open in Excel or locked by another program. "
                        "Please close the file and try again."
                    )
            
            with open(file_path, "wb") as f:
                f.write(resp.content)
            
            print(f"✅ File saved to: {file_path}")
            
            # Parse Excel
            df_cleaned, parsed_rows = parse_daily_state_excel(file_path)
            
            # Check if we have enough data rows (> 5)
            if len(parsed_rows) > 5:
                print(f"✅ Found {len(parsed_rows)} data rows. Accepting this date.")
                
                # Apply district filtering if district_name is provided
                if district_name:
                    # ---------------------------------------------------------
                    # DISTRICT FILTERING (correct implementation)
                    # ---------------------------------------------------------
                    
                    # Load districts.json directly (authoritative source)
                    district_file = BASE_DIR / "app" / "agmarknet" / "metadata" / "districts.json"
                    if not district_file.exists():
                        print(f"⚠️ districts.json not found at {district_file}")
                        return df_cleaned, parsed_rows, date_str
                    
                    districts_data = json.loads(district_file.read_text(encoding="utf-8"))
                    
                    # Find district by name (case-insensitive)
                    district_entry = None
                    for d in districts_data:
                        if str(d.get("district_name", "")).strip().lower() == district_name.strip().lower():
                            district_entry = d
                            break
                    
                    if not district_entry:
                        print(f"⚠️ District '{district_name}' not found in districts.json")
                        return df_cleaned, [], date_str
                    
                    # Extract markets list from districts.json
                    markets_list = district_entry.get("markets", [])
                    if not markets_list:
                        print(f"⚠️ District '{district_name}' has no markets listed in districts.json")
                        return df_cleaned, [], date_str
                    
                    # Normalize market names
                    district_market_names = {normalize_market_name(m.get("mkt_name")) for m in markets_list}
                    
                    # Filter parsed rows by normalized market name
                    district_rows = [
                        r for r in parsed_rows
                        if normalize_market_name(r.get("market")) in district_market_names
                    ]
                    
                    if not district_rows:
                        print(
                            f"⚠️ No rows matched markets for district '{district_name}' on {date_str}.\n"
                            f"   Markets expected: {list(district_market_names)[:10]}"
                        )
                        # Try fallback dates: only for first date, go back up to 3 days from initial date
                        if not allow_fallback:
                            print(f"❌ No data found for district '{district_name}' on {date_str}. Skipping fallback (only allowed for first date).")
                            last_error = f"No district data found for '{district_name}' on {date_str}"
                            continue
                        
                        print(f"🔄 Trying fallback dates (up to 3 days before {date_str})...")
                        fallback_found = False
                        
                        for fallback_days in range(1, 4):  # Try 1, 2, 3 days before
                            fallback_date = initial_date - timedelta(days=fallback_days)
                            fallback_date_str = fallback_date.strftime("%Y-%m-%d")
                            fallback_file_path = DOWNLOADS_DIR / f"{fallback_date_str}.xlsx"
                            
                            print(f"   📥 Trying fallback date: {fallback_date_str}")
                            
                            # Download fallback file if not cached
                            if not fallback_file_path.exists() or refresh_cache:
                                try:
                                    fallback_params = {
                                        "liveDate": fallback_date_str,
                                        "date": fallback_date_str,
                                        "state": state_id,
                                        "includeExcel": "true"
                                    }
                                    print(f"   🔗 Downloading from URL with date: {fallback_date_str}")
                                    fallback_resp = requests.get(
                                        BASE_URL,
                                        params=fallback_params,
                                        timeout=45,
                                        headers={"User-Agent": "AgriSenseBot/1.0"}
                                    )
                                    fallback_resp.raise_for_status()
                                    
                                    content_type = fallback_resp.headers.get("Content-Type", "").lower()
                                    if "excel" not in content_type and "spreadsheet" not in content_type:
                                        print(f"   ⚠️  Skipping {fallback_date_str}: not an Excel file")
                                        continue
                                    
                                    with open(fallback_file_path, "wb") as f:
                                        f.write(fallback_resp.content)
                                    print(f"   ✅ Downloaded fallback file: {fallback_date_str}.xlsx")
                                except Exception as e:
                                    print(f"   ❌ Failed to download fallback file for {fallback_date_str}: {e}")
                                    continue
                            
                            # Parse fallback file
                            try:
                                fallback_df, fallback_parsed = parse_daily_state_excel(fallback_file_path)
                                
                                if len(fallback_parsed) > 5:
                                    # Filter by district
                                    fallback_district_rows = [
                                        r for r in fallback_parsed
                                        if normalize_market_name(r.get("market")) in district_market_names
                                    ]
                                    
                                    if fallback_district_rows:
                                        print(f"   ✅ Found {len(fallback_district_rows)} rows for district '{district_name}' on {fallback_date_str}")
                                        district_rows = fallback_district_rows
                                        parsed_rows = fallback_parsed  # Update parsed_rows for commodity filtering
                                        date_str = fallback_date_str  # Update to use fallback date
                                        fallback_found = True
                                        break
                                    else:
                                        print(f"   ⚠️  No district data in fallback file {fallback_date_str}")
                                else:
                                    print(f"   ⚠️  Fallback file {fallback_date_str} has insufficient data")
                            except Exception as e:
                                print(f"   ❌ Error parsing fallback file {fallback_date_str}: {e}")
                                continue
                        
                        if not fallback_found:
                            print(f"❌ No data found for district '{district_name}' after trying fallback dates from {date_str}")
                            # Continue to next date in main loop instead of returning
                            last_error = f"No district data found for '{district_name}' on {date_str} and fallback dates"
                            continue
                    
                    # At this point `district_rows` is a list of parsed row dicts for the district.
                    # If a commodity_name was provided, filter the district_rows further.
                    if commodity_name:
                        # Primary filter: match by 'commodity' field in parsed rows
                        matches_by_name = [
                            r for r in district_rows
                            if _commodity_matches(r.get("commodity") or "", commodity_name)
                        ]
                        
                        if matches_by_name:
                            df_cleaned = pd.DataFrame(matches_by_name)
                            print(f"✅ Filtered by commodity name '{commodity_name}': {len(matches_by_name)} rows matched.")
                            return df_cleaned, matches_by_name, date_str
                        
                        # Fallback: try matching by commodity group (if user gave an ambiguous name)
                        # e.g. user passes 'Pulses' or 'Oil Seeds' — try matching against parsed 'group'
                        matches_by_group = [
                            r for r in district_rows
                            if _commodity_matches(r.get("group") or "", commodity_name)
                        ]
                        if matches_by_group:
                            df_cleaned = pd.DataFrame(matches_by_group)
                            print(f"⚠️ No exact commodity-name matches for '{commodity_name}', "
                                  f"but matched by group: {len(matches_by_group)} rows returned.")
                            return df_cleaned, matches_by_group, date_str
                        
                        # No matches found - try fallback dates (only for first date)
                        print(f"⚠️ No data found for commodity '{commodity_name}' in district '{district_name}' on {date_str}.")
                        # Try fallback dates: only for first date, go back up to 3 days from initial date
                        if not allow_fallback:
                            print(f"❌ No data found for commodity '{commodity_name}' in district '{district_name}' on {date_str}. Skipping fallback (only allowed for first date).")
                            last_error = f"No commodity data found for '{commodity_name}' in district '{district_name}' on {date_str}"
                            continue
                        
                        print(f"🔄 Trying fallback dates for commodity (up to 3 days before {date_str})...")
                        fallback_found = False
                        
                        for fallback_days in range(1, 4):  # Try 1, 2, 3 days before
                            fallback_date = initial_date - timedelta(days=fallback_days)
                            fallback_date_str = fallback_date.strftime("%Y-%m-%d")
                            fallback_file_path = DOWNLOADS_DIR / f"{fallback_date_str}.xlsx"
                            
                            print(f"   📥 Trying fallback date: {fallback_date_str}")
                            
                            # Download fallback file if not cached
                            if not fallback_file_path.exists() or refresh_cache:
                                try:
                                    fallback_params = {
                                        "liveDate": fallback_date_str,
                                        "date": fallback_date_str,
                                        "state": state_id,
                                        "includeExcel": "true"
                                    }
                                    print(f"   🔗 Downloading from URL with date: {fallback_date_str}")
                                    fallback_resp = requests.get(
                                        BASE_URL,
                                        params=fallback_params,
                                        timeout=45,
                                        headers={"User-Agent": "AgriSenseBot/1.0"}
                                    )
                                    fallback_resp.raise_for_status()
                                    
                                    content_type = fallback_resp.headers.get("Content-Type", "").lower()
                                    if "excel" not in content_type and "spreadsheet" not in content_type:
                                        print(f"   ⚠️  Skipping {fallback_date_str}: not an Excel file")
                                        continue
                                    
                                    with open(fallback_file_path, "wb") as f:
                                        f.write(fallback_resp.content)
                                    print(f"   ✅ Downloaded fallback file: {fallback_date_str}.xlsx")
                                except Exception as e:
                                    print(f"   ❌ Failed to download fallback file for {fallback_date_str}: {e}")
                                    continue
                            
                            # Parse fallback file
                            try:
                                fallback_df, fallback_parsed = parse_daily_state_excel(fallback_file_path)
                                
                                if len(fallback_parsed) > 5:
                                    # Filter by district first
                                    fallback_district_rows = [
                                        r for r in fallback_parsed
                                        if normalize_market_name(r.get("market")) in district_market_names
                                    ]
                                    
                                    if fallback_district_rows:
                                        # Then filter by commodity
                                        fallback_commodity_rows = [
                                            r for r in fallback_district_rows
                                            if _commodity_matches(r.get("commodity") or "", commodity_name)
                                        ]
                                        
                                        if fallback_commodity_rows:
                                            print(f"   ✅ Found {len(fallback_commodity_rows)} rows for commodity '{commodity_name}' in district '{district_name}' on {fallback_date_str}")
                                            df_cleaned = pd.DataFrame(fallback_commodity_rows)
                                            date_str = fallback_date_str  # Update to use fallback date
                                            fallback_found = True
                                            return df_cleaned, fallback_commodity_rows, date_str
                                        else:
                                            print(f"   ⚠️  No commodity data in fallback file {fallback_date_str}")
                                    else:
                                        print(f"   ⚠️  No district data in fallback file {fallback_date_str}")
                                else:
                                    print(f"   ⚠️  Fallback file {fallback_date_str} has insufficient data")
                            except Exception as e:
                                print(f"   ❌ Error parsing fallback file {fallback_date_str}: {e}")
                                continue
                        
                        if not fallback_found:
                            print(f"❌ No data found for commodity '{commodity_name}' in district '{district_name}' after trying fallback dates from {date_str}")
                            # Continue to next date in main loop instead of returning
                            last_error = f"No commodity data found for '{commodity_name}' in district '{district_name}' on {date_str} and fallback dates"
                            continue
                    
                    # No commodity filter requested → return district_rows
                    df_cleaned = pd.DataFrame(district_rows)
                    return df_cleaned, district_rows, date_str
                
                # No district filtering, but check for commodity filtering
                if commodity_name:
                    # Primary filter: match by 'commodity' field in parsed rows
                    matches_by_name = [
                        r for r in parsed_rows
                        if _commodity_matches(r.get("commodity") or "", commodity_name)
                    ]
                    
                    if matches_by_name:
                        df_cleaned = pd.DataFrame(matches_by_name)
                        print(f"✅ Filtered by commodity name '{commodity_name}': {len(matches_by_name)} rows matched.")
                        return df_cleaned, matches_by_name, date_str
                    
                    # Fallback: try matching by commodity group
                    matches_by_group = [
                        r for r in parsed_rows
                        if _commodity_matches(r.get("group") or "", commodity_name)
                    ]
                    if matches_by_group:
                        df_cleaned = pd.DataFrame(matches_by_group)
                        print(f"⚠️ No exact commodity-name matches for '{commodity_name}', "
                              f"but matched by group: {len(matches_by_group)} rows returned.")
                        return df_cleaned, matches_by_group, date_str
                    
                    # No matches found
                    print(f"⚠️ No data found for commodity '{commodity_name}' on {date_str}.")
                    return pd.DataFrame([]), [], date_str
                
                return df_cleaned, parsed_rows, date_str
            else:
                print(f"⚠️  Only {len(parsed_rows)} data rows found. Trying next date...")
                last_error = f"Only {len(parsed_rows)} data rows found (need > 5)"
                continue
            
        except requests.exceptions.Timeout:
            last_error = f"Request timed out for {date_str}"
            print(f"❌ {last_error}")
            continue
        except requests.exceptions.HTTPError as e:
            last_error = f"HTTP error {e.response.status_code} for {date_str}: {e.response.text}"
            print(f"❌ {last_error}")
            continue
        except requests.exceptions.RequestException as e:
            last_error = f"Request failed for {date_str}: {str(e)}"
            print(f"❌ {last_error}")
            continue
        except Exception as e:
            last_error = f"Unexpected error for {date_str}: {str(e)}"
            print(f"❌ {last_error}")
            continue
    
    # All attempts failed - return empty data gracefully
    error_msg = f"Failed to fetch Daily State Report after trying {len(dates_to_try)} date(s)"
    if last_error:
        error_msg += f". Last error: {last_error}"
    print(f"⚠️ {error_msg}")
    print(f"   Returning empty data instead of raising exception")
    return pd.DataFrame([]), [], dates_to_try[0].strftime("%Y-%m-%d") if dates_to_try else datetime.now().strftime("%Y-%m-%d")

