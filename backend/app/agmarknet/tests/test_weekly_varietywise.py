"""
test_weekly_varietywise.py
Test driver for weekly variety-wise price processing.

Tests the variety-wise fetcher with caching support.
"""

from app.agmarknet.fetchers.weekly_varietywise_fetcher import WeeklyVarietywiseFetcher
from app.agmarknet.utils.lookup_ids import MetadataLookup


def main():
    """Main test function."""
    print("=" * 60)
    print("Weekly Variety-wise Prices - End-to-End Test")
    print("=" * 60)
    
    # ============================================================
    # Input parameters
    # ============================================================
    state = "Maharashtra"
    district = "Akola"
    commodity = "Soyabean"
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
    # STEP 1: Convert names to IDs
    # ============================================================
    print(f"\n{'=' * 60}")
    print("STEP 1: Converting names to IDs")
    print("=" * 60)
    
    try:
        lookup = MetadataLookup()
        print(f"✅ Metadata loaded from: {lookup.metadata_dir}")
        
        state_id = lookup.get_state_id(state)
        print(f"✅ State '{state}' → ID: {state_id}")
        
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
    # STEP 2: Fetch and process Excel file
    # ============================================================
    print(f"\n{'=' * 60}")
    print("STEP 2: Fetching and Processing Excel File")
    print("=" * 60)
    
    try:
        df, data_source = WeeklyVarietywiseFetcher.fetch_and_process(
            state_id=state_id,
            commodity_id=commodity_id,
            year=year,
            month=month,
            week=week,
            district_name=district
        )
        
        print(f"\n{'=' * 60}")
        print("Results Summary")
        print("=" * 60)
        print(f"✅ Processing complete!")
        print(f"   Data source: {data_source}")
        print(f"   Number of rows: {len(df)}")
        print(f"   Column names: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"\n📊 First 10 rows:")
            print(df.head(10).to_string())
        else:
            print(f"\n⚠️  No data found for district '{district}'")
        
    except Exception as e:
        print(f"❌ Error fetching/processing Excel file: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n{'=' * 60}")
    print("✅ Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

