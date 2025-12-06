"""
Test script for Market-wise Daily Report for Specific Commodity
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
DATE = "03-12-2025"  # dd-mm-yyyy

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
    print("Market-wise Daily Report for Specific Commodity")
    print("=" * 60)
    print(f"State: {STATE}")
    print(f"Commodity: {COMMODITY}")
    print(f"Date: {DATE}")
    print()
    
    # TODO: Replace <DOWNLOAD_URL> with the actual export URL once determined.
    # URL should be constructed based on STATE, COMMODITY, and DATE parameters
    download_url = f"https://agmarknet.gov.in/api/report/marketwise-daily-specific?state={STATE}&commodity={COMMODITY}&date={DATE}"
    
    output_path = "/tmp/marketwise_daily_specific.xlsx"
    
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
        
        # Step 5: Validate expected columns
        expected_columns = ["Market Name", "Commodity", "Modal Price", "Min Price", "Max Price"]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"\nWARNING: Missing expected columns: {missing_columns}")
        
        # Step 6: Display first 5 records
        print("\nFirst 5 records:")
        print(df.head().to_string())
        
        # Step 7: Validate data
        if len(df) >= 1:
            print("\n" + "=" * 60)
            print("SUCCESS: File parsed and contains data")
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

