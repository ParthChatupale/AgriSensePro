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
    
    # Load Excel file
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        raise ValueError(f"Failed to load Excel file: {str(e)}")
    
    if df.empty:
        raise ValueError("Excel file is empty")
    
    print(f"\nOriginal data shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Column names: {list(df.columns)}")
    
    # Normalize column names (handle variations)
    # Look for district-related column names
    district_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if "district" in col_lower and "name" in col_lower:
            district_col = col
            break
        elif col_lower == "district":
            district_col = col
            break
    
    if district_col is None:
        # Try to find any column that might contain district names
        for col in df.columns:
            if df[col].dtype == "object":  # String type
                sample_values = df[col].dropna().head(10).astype(str).tolist()
                # Check if any sample value looks like a district name
                if any(len(str(v)) > 3 and str(v).isalpha() for v in sample_values):
                    district_col = col
                    print(f"⚠️  Using column '{col}' as district column (auto-detected)")
                    break
    
    if district_col is None:
        raise ValueError(
            "Could not find district column in Excel file. "
            f"Available columns: {list(df.columns)}"
        )
    
    print(f"Using district column: '{district_col}'")
    
    # Filter by district name
    if case_sensitive:
        filtered_df = df[df[district_col].astype(str).str.contains(district, na=False)]
    else:
        filtered_df = df[
            df[district_col].astype(str).str.contains(district, case=False, na=False)
        ]
    
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

