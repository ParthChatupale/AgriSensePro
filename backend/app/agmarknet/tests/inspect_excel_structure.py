"""
Inspect Excel file structure to debug column mapping issues.
"""
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

BASE_DIR = Path(__file__).resolve().parents[3]
DOWNLOADS_DIR = BASE_DIR / "app" / "agmarknet" / "downloads" / "daily_state"

def inspect_excel():
    """Inspect the Excel file structure."""
    # Find the most recent Excel file (skip temporary files)
    excel_files = [f for f in DOWNLOADS_DIR.glob("*.xlsx") if not f.name.startswith("~$")]
    excel_files = sorted(excel_files, key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not excel_files:
        print("No Excel files found in downloads directory")
        return
    
    file_path = excel_files[0]
    print(f"Inspecting: {file_path}")
    print("=" * 80)
    
    # Load Excel with no header
    df = pd.read_excel(file_path, header=None, engine="openpyxl")
    
    print(f"\nTotal rows: {len(df)}, Total columns: {len(df.columns)}")
    
    # Show first 10 rows to understand structure
    print("\nFirst 10 rows (raw):")
    for idx in range(min(10, len(df))):
        row = df.iloc[idx]
        print(f"\nRow {idx}:")
        for col_idx in range(min(10, len(row))):
            val = row.iloc[col_idx]
            if pd.notna(val):
                print(f"  Col {col_idx}: {val}")
    
    # Look for Soyabean rows specifically
    print("\n\nSearching for 'Soyabean' rows...")
    print("=" * 80)
    
    current_commodity = None
    for idx, row in df.iterrows():
        first_val = row.iloc[0] if len(row) > 0 else None
        first = str(first_val).strip() if pd.notna(first_val) else ""
        
        if "Soyabean" in first or "Soybean" in first:
            print(f"\nFound at row {idx}: '{first}'")
            print(f"   Full row data:")
            for col_idx in range(min(10, len(row))):
                val = row.iloc[col_idx]
                if pd.notna(val):
                    print(f"      Col {col_idx}: {val} (type: {type(val).__name__})")
        
        if first.startswith("Commodity Name"):
            parts = first.split(":", 1)
            if len(parts) > 1:
                current_commodity = parts[1].strip()
                if "Soyabean" in current_commodity or "Soybean" in current_commodity:
                    print(f"\nCommodity Name found at row {idx}: '{current_commodity}'")
                    # Show next few rows (market data)
                    print(f"   Next 5 rows (market data):")
                    for next_idx in range(idx + 1, min(idx + 6, len(df))):
                        next_row = df.iloc[next_idx]
                        next_first = str(next_row.iloc[0]).strip() if len(next_row) > 0 and pd.notna(next_row.iloc[0]) else ""
                        if next_first and not next_first.startswith("Commodity"):
                            print(f"      Row {next_idx}: Market='{next_first}'")
                            for col_idx in range(min(10, len(next_row))):
                                val = next_row.iloc[col_idx]
                                if pd.notna(val):
                                    print(f"         Col {col_idx}: {val}")

if __name__ == "__main__":
    inspect_excel()

