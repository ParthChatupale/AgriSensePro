"""
test_weekly_wholesale.py
End-to-end test driver for weekly wholesale price fetching and processing.

Tests the complete workflow:
1. Convert human-friendly names to IDs using MetadataLookup
2. Download weekly wholesale prices Excel file
3. Process and filter the Excel file by district
4. Display results
"""

from app.agmarknet.utils.lookup_ids import MetadataLookup
from app.agmarknet.downloaders.fetch_wholesale_weekly import fetch_wholesale_weekly
from app.agmarknet.processors.process_weekly_wholesale import process_weekly_wholesale


def main():
    """Main test function."""
    print("=" * 60)
    print("Weekly Wholesale Prices - End-to-End Test")
    print("=" * 60)
    
    # ============================================================
    # STEP 1: User inputs (normal text values)
    # ============================================================
    state = "Maharashtra"
    district = "Akola"
    commodity = "Cotton"
    year = 2025
    month = 12
    week = 1
    
    print(f"\n📋 Input Parameters:")
    print(f"  State: {state}")
    print(f"  District: {district}")
    print(f"  Commodity: {commodity}")
    print(f"  Year: {year}")
    print(f"  Month: {month}")
    print(f"  Week: {week}")
    
    # ============================================================
    # STEP 2: Load metadata and convert names → IDs
    # ============================================================
    print(f"\n{'=' * 60}")
    print("STEP 1: Converting names to IDs")
    print("=" * 60)
    
    try:
        lookup = MetadataLookup()
        print(f"✅ Metadata loaded from: {lookup.metadata_dir}")
        
        state_id = lookup.get_state_id(state)
        print(f"✅ State '{state}' → ID: {state_id}")
        
        district_id = lookup.get_district_id(state_id, district)
        print(f"✅ District '{district}' → ID: {district_id}")
        
        commodity_id = lookup.get_commodity_id(commodity)
        print(f"✅ Commodity '{commodity}' → ID: {commodity_id}")
        
    except ValueError as e:
        print(f"❌ Error converting names to IDs: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # STEP 3: Download Excel file
    # ============================================================
    print(f"\n{'=' * 60}")
    print("STEP 2: Downloading Weekly Wholesale Prices Excel")
    print("=" * 60)
    
    try:
        excel_path = fetch_wholesale_weekly(
            state_id=state_id,
            commodity_id=commodity_id,
            year=year,
            month=month,
            week=week
        )
        print(f"✅ Excel file downloaded successfully")
        print(f"   Path: {excel_path}")
        
    except Exception as e:
        print(f"❌ Error downloading Excel file: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # STEP 4: Process Excel file and filter by district
    # ============================================================
    print(f"\n{'=' * 60}")
    print("STEP 3: Processing Excel file and filtering by district")
    print("=" * 60)
    
    try:
        filtered_df = process_weekly_wholesale(
            excel_path=excel_path,
            district=district
        )
        
        print(f"\n{'=' * 60}")
        print("STEP 4: Results Summary")
        print("=" * 60)
        print(f"✅ Processing complete!")
        print(f"   Total matching rows: {len(filtered_df)}")
        print(f"   Columns: {list(filtered_df.columns)}")
        
        if len(filtered_df) > 0:
            print(f"\n📊 Sample Data (first 10 rows):")
            print(filtered_df.head(10).to_string())
        else:
            print(f"\n⚠️  No data found for district '{district}'")
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n{'=' * 60}")
    print("✅ Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

