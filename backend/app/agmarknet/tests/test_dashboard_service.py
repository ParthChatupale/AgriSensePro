"""
test_dashboard_service.py
Test driver for Agmarknet dashboard service.

Tests primary crop data and trending crops functionality.
"""

from app.agmarknet.dashboard.service import get_primary_crop_data, get_trending_crops


def test_primary_crop():
    """Test primary crop data retrieval."""
    print("=" * 80)
    print("Testing Primary Crop Data")
    print("=" * 80)
    
    state = "Maharashtra"
    district = "Akola"
    primary_crop = "Soyabean"
    
    print(f"\n📋 Input Parameters:")
    print(f"  State: {state}")
    print(f"  District: {district}")
    print(f"  Primary Crop: {primary_crop}")
    
    try:
        result = get_primary_crop_data(
            state_name=state,
            district_name=district,
            primary_crop=primary_crop
        )
        
        print(f"\n{'=' * 80}")
        print("Results")
        print("=" * 80)
        
        if result:
            print(f"✅ Primary crop data found:")
            print(f"   Crop: {result.get('crop')}")
            print(f"   Modal Price: ₹{result.get('modal_price')}/Quintal" if result.get('modal_price') else "   Modal Price: N/A")
            print(f"   Min Price: ₹{result.get('min_price')}/Quintal" if result.get('min_price') else "   Min Price: N/A")
            print(f"   Max Price: ₹{result.get('max_price')}/Quintal" if result.get('max_price') else "   Max Price: N/A")
            print(f"   Markets: {result.get('markets', [])}")
            print(f"   Date: {result.get('date')}")
            print(f"   Rows Found: {result.get('rows_found')}")
        else:
            print(f"⚠️  No data found for {primary_crop} in {district}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_trending_crops():
    """Test trending crops analysis."""
    print("\n\n" + "=" * 80)
    print("Testing Trending Crops")
    print("=" * 80)
    
    state = "Maharashtra"
    district = "Akola"
    top_n = 5
    
    print(f"\n📋 Input Parameters:")
    print(f"  State: {state}")
    print(f"  District: {district}")
    print(f"  Top N: {top_n}")
    
    try:
        result = get_trending_crops(
            state_name=state,
            district_name=district,
            top_n=top_n
        )
        
        print(f"\n{'=' * 80}")
        print("Results")
        print("=" * 80)
        
        if result:
            print(f"✅ Found {len(result)} trending crops:")
            for i, crop in enumerate(result, 1):
                print(f"\n   {i}. {crop.get('commodity')}")
                print(f"      Old Avg Modal: ₹{crop.get('old_avg_modal')}/Quintal")
                print(f"      New Avg Modal: ₹{crop.get('new_avg_modal')}/Quintal")
                print(f"      Change: +{crop.get('pct_change') * 100:.2f}%")
        else:
            print(f"⚠️  No trending crops found (need at least 2 cached Excel files)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    test_primary_crop()
    test_trending_crops()
    
    print(f"\n\n{'=' * 80}")
    print("✅ All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()

