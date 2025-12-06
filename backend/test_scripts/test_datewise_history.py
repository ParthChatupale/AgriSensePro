"""
Test script for Date-wise Prices for Specified Commodity
Agmarknet Tier-1 Dataset
"""
import requests
import pandas as pd
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION VARIABLES - Modify these for testing
# ============================================================================
STATE = "Maharashtra"
COMMODITY = "Cotton"
MONTH = "12"  # 01-12
YEAR = "2025"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def fetch_xlsx(url, output_path):
    """
    Downloads XLSX file from URL with error handling.
    
    Args:
        url: URL to download from
        output_path: Local path to save the file
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        print(f"Downloading from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"File saved to: {output_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("Date-wise Prices for Specified Commodity")
    print("=" * 60)
    print(f"State: {STATE}")
    print(f"Commodity: {COMMODITY}")
    print(f"Month: {MONTH}")
    print(f"Year: {YEAR}")
    print()
    
    # TODO: Replace <DOWNLOAD_URL> with the actual export URL once determined.
    # URL should be constructed based on STATE, COMMODITY, MONTH, and YEAR parameters
    download_url = f"https://agmarknet.gov.in/api/report/datewise-history?state={STATE}&commodity={COMMODITY}&month={MONTH}&year={YEAR}"
    
    output_path = "/tmp/datewise_history.xlsx"
    
    # Step 1: Download file
    print("Step 1: Downloading report...")
    if not fetch_xlsx(download_url, output_path):
        print("FAILED: Could not download file")
        return
    
    # Step 2: Check if file exists
    if not os.path.exists(output_path):
        print("FAILED: Downloaded file not found")
        return
    
    # Step 3: Load and parse with pandas
    print("\nStep 2: Parsing XLSX file...")
    try:
        df = pd.read_excel(output_path)
        
        if df.empty:
            print("FAILED: File is empty or has no data")
            return
        
        # Step 4: Print statistics
        print(f"\nNumber of rows: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")
        print(f"\nColumn names:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        # Step 5: Validate expected structure (Date → Price series)
        date_col = None
        price_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if "date" in col_lower:
                date_col = col
            if "price" in col_lower and ("modal" in col_lower or "average" in col_lower or "avg" in col_lower):
                price_col = col
        
        if date_col:
            print(f"\nFound date column: {date_col}")
        else:
            print("\nWARNING: Could not identify date column")
        
        if price_col:
            print(f"Found price column: {price_col}")
        else:
            print("WARNING: Could not identify price column")
        
        # Step 6: Display date-price series if available
        if date_col and price_col:
            try:
                # Convert date column to datetime if possible
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                # Convert price to numeric
                df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
                
                # Show date range
                valid_dates = df[date_col].dropna()
                if len(valid_dates) > 0:
                    print(f"\nDate Range: {valid_dates.min()} to {valid_dates.max()}")
                    print(f"Total dates with data: {len(valid_dates)}")
                
                # Show price statistics
                valid_prices = df[price_col].dropna()
                if len(valid_prices) > 0:
                    print(f"\nPrice Statistics:")
                    print(f"  Min: ₹{valid_prices.min():.2f}")
                    print(f"  Max: ₹{valid_prices.max():.2f}")
                    print(f"  Average: ₹{valid_prices.mean():.2f}")
            except Exception as e:
                print(f"\nWARNING: Could not analyze date-price series: {e}")
        
        # Step 7: Validate multiple rows requirement
        if len(df) < 2:
            print("\nWARNING: Expected multiple rows for date-wise history, but found less than 2")
        
        # Step 8: Display first 5 records
        print("\nFirst 5 records:")
        print(df.head().to_string())
        
        # Step 9: Validate data
        if len(df) >= 1:
            print("\n" + "=" * 60)
            print("SUCCESS: File parsed and contains data")
            if len(df) >= 2:
                print("SUCCESS: Multiple rows found (date series requirement met)")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("FAILED: File has no data rows")
            print("=" * 60)
            
    except pd.errors.EmptyDataError:
        print("FAILED: File is empty or corrupted")
    except Exception as e:
        print(f"FAILED: Error parsing file - {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

