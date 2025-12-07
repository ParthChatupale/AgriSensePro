"""
test_daily_state_report.py
Test driver for Daily State Report fetcher.

Tests the daily state report fetcher with automatic date fallback.
"""

from app.agmarknet.fetchers.daily_state_report_fetcher import fetch_daily_state_report
from app.agmarknet.utils.lookup_ids import MetadataLookup


def main():
    """Main test function."""
    print("=" * 60)
    print("Daily State Report - End-to-End Test")
    print("=" * 60)
    
    # ============================================================
    # Input parameters
    # ============================================================
    state = "Maharashtra"
    district = "Chattrapati Sambhajinagar"       # <--- NEW: pass district name here
    commodity = "soyabean"   # <--- pass the commodity name from test inputs
    
    print(f"\n📋 Input Parameters:")
    print(f"  State: {state}")
    print(f"  District: {district}")
    print(f"  Commodity: {commodity}")
    
    # ============================================================
    # STEP 1: Convert state name to ID
    # ============================================================
    print(f"\n{'=' * 60}")
    print("STEP 1: Converting state name to ID")
    print("=" * 60)
    
    try:
        lookup = MetadataLookup()
        print(f"✅ Metadata loaded from: {lookup.metadata_dir}")
        
        state_id = lookup.get_state_id(state)
        print(f"✅ State '{state}' → ID: {state_id}")
        
    except ValueError as e:
        print(f"❌ Error converting state name to ID: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # STEP 2: Fetch Daily State Report
    # ============================================================
    print(f"\n{'=' * 60}")
    print("STEP 2: Fetching Daily State Report")
    print("=" * 60)
    
    try:
        df, parsed_rows, chosen_date = fetch_daily_state_report(
            state_id=state_id,
            district_name=district,
            commodity_name=commodity,
            refresh_cache=False  # use cached file if present; set True to force download
        )
        
        print(f"\n{'=' * 60}")
        print("Results Summary")
        print("=" * 60)
        print(f"✅ Processing complete!")
        print(f"   Selected date: {chosen_date}")
        print(f"   Total rows: {len(parsed_rows)}")
        
        if len(parsed_rows) > 0:
            print(f"\n📊 First 10 rows of parsed output:")
            for i, row in enumerate(parsed_rows[:10], 1):
                print(f"\n   Row {i}:")
                print(f"      Commodity Group: {row.get('group', 'N/A')}")
                print(f"      Commodity Name: {row.get('commodity', 'N/A')}")
                print(f"      Market: {row.get('market', 'N/A')}")
                print(f"      Arrivals: {row.get('arrivals', 'N/A')}")
                print(f"      Unit Arrivals: {row.get('unit_arrivals', 'N/A')}")
                print(f"      Variety: {row.get('variety', 'N/A')}")
                print(f"      Min Price: {row.get('min_price', 'N/A')}")
                print(f"      Max Price: {row.get('max_price', 'N/A')}")
                print(f"      Modal Price: {row.get('modal_price', 'N/A')}")
                print(f"      Unit Price: {row.get('unit_price', 'N/A')}")
        else:
            print(f"\n⚠️  No data found")
        
    except Exception as e:
        print(f"❌ Error fetching Daily State Report: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n{'=' * 60}")
    print("✅ Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

