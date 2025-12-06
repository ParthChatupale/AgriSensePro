"""
process_weekly_wholesale.py
Processes downloaded Weekly Wholesale Prices Excel files.

Loads Excel files, filters by district name, and returns cleaned dataframes.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


def process_weekly_wholesale(
    excel_path: str,
    district: str,
    case_sensitive: bool = False
) -> pd.DataFrame:
    """
    Process weekly wholesale prices Excel file and filter by district.
    
    Args:
        excel_path: Path to downloaded Excel file
        district: District name to filter by (string match)
        case_sensitive: Whether district name matching is case-sensitive (default: False)
    
    Returns:
        Filtered pandas DataFrame
    
    Raises:
        FileNotFoundError: If Excel file doesn't exist
        ValueError: If Excel file cannot be parsed or district column not found
    """
    filepath = Path(excel_path)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")
    
    print(f"\n📊 Processing Excel file: {excel_path}")
    print(f"Filtering by district: {district}")
    
    # Load Excel file - use row index 1 (second row, 0-indexed) as header
    try:
        df = pd.read_excel(filepath, header=1)
    except Exception as e:
        raise ValueError(f"Failed to load Excel file: {str(e)}")
    
    if df.empty:
        raise ValueError("Excel file is empty")
    
    # Normalize column names by stripping whitespace
    df.columns = [str(c).strip() for c in df.columns]
    
    print(f"\nOriginal data shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Column names: {list(df.columns)}")
    
    # Auto-detect district column by searching for column containing "district" (case-insensitive)
    district_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if "district" in col_lower:
            district_col = col
            break
    
    # If no column with "district" in name, assume first column contains district names
    # (This is common in Agmarknet Excel files where first column is district names)
    if district_col is None:
        first_col = df.columns[0]
        first_col_values = df[first_col].dropna().astype(str).head(10)
        
        # Check if first column contains text values (district names are text, not numbers)
        text_count = sum(
            1 for val in first_col_values
            if str(val).strip() and 
            any(c.isalpha() for c in str(val).strip()) and 
            len(str(val).strip()) > 2
        )
        
        # If at least 2 values are text (likely district names), use first column
        if text_count >= 2:
            district_col = first_col
            print(f"⚠️  Auto-detected first column '{first_col}' as district column")
            print(f"    Sample values: {list(first_col_values.head(5))}")
        else:
            raise ValueError(
                "Could not find district column in Excel file. "
                f"Available columns: {list(df.columns)}. "
                f"First column values: {list(first_col_values.head(5))}"
            )
    
    print(f"Using district column: '{district_col}'")
    
    # Filter by district name - exact match
    district_col_values = df[district_col].astype(str).str.strip()
    district_search = district.strip()
    
    if case_sensitive:
        filtered_df = df[district_col_values == district_search]
    else:
        filtered_df = df[district_col_values.str.lower() == district_search.lower()]
    
    print(f"\nFiltered data shape: {filtered_df.shape[0]} rows, {filtered_df.shape[1]} columns")
    
    if filtered_df.empty:
        print(f"⚠️  Warning: No rows found matching district '{district}'")
    else:
        print(f"\n✅ Found {len(filtered_df)} matching rows")
        print("\nFirst few rows:")
        print(filtered_df.head().to_string())
    
    return filtered_df


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python process_weekly_wholesale.py <excel_path> <district_name>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    district = sys.argv[2]
    
    try:
        df = process_weekly_wholesale(excel_path, district)
        print(f"\n✅ Processing complete! {len(df)} rows returned.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

