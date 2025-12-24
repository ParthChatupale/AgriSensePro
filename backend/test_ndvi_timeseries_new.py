"""
Test script to verify the new NDVI time series endpoint works correctly.
This endpoint uses the working backend/ndvi/pipeline implementation.

Run this from the backend directory: python test_ndvi_timeseries_new.py
"""

import asyncio
import httpx
from datetime import datetime
import json

# Test coordinates (use coordinates that worked for /api/ndvi/run)
TEST_LAT = 19.7515
TEST_LON = 75.7139
TEST_DAYS = 7

async def test_ndvi_timeseries():
    """Test the new NDVI time series endpoint."""
    url = f"http://localhost:8000/api/ndvi/timeseries"
    params = {
        "lat": TEST_LAT,
        "lon": TEST_LON,
        "days": TEST_DAYS
    }
    
    print("=" * 70)
    print("Testing NEW NDVI Time Series Endpoint")
    print("=" * 70)
    print(f"URL: {url}")
    print(f"Parameters: lat={TEST_LAT}, lon={TEST_LON}, days={TEST_DAYS}")
    print("=" * 70)
    print()
    print("⚠️  NOTE: This endpoint calls run_ndvi() for each date,")
    print("   so it may take several minutes (5-30 seconds per date).")
    print("   Please be patient...")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:  # 10 minute timeout
            print("Sending request...")
            start_time = datetime.now()
            
            response = await client.get(url, params=params)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"Response time: {elapsed:.2f} seconds ({elapsed/60:.1f} minutes)")
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                
                print("Response Structure:")
                print(f"  - location: {data.get('location')}")
                print(f"  - range_days: {data.get('range_days')}")
                print(f"  - ndvi array length: {len(data.get('ndvi', []))}")
                print()
                
                ndvi_data = data.get('ndvi', [])
                
                if not ndvi_data:
                    print("⚠️  WARNING: No NDVI data returned!")
                    print("This could mean:")
                    print("  - No satellite data available for this location/date range")
                    print("  - All data points were filtered out (clouds, invalid values)")
                    print("  - Sentinel API returned no valid data")
                    return False
                
                print(f"✅ Successfully retrieved {len(ndvi_data)} data points out of {TEST_DAYS} days")
                print()
                print("=" * 70)
                print("NDVI Mean Values (Time Series)")
                print("=" * 70)
                print(f"{'Date':<12} {'Mean NDVI':<15} {'Status'}")
                print("-" * 70)
                
                for entry in ndvi_data:
                    date = entry.get('date', 'N/A')
                    mean = entry.get('mean', 'N/A')
                    
                    if isinstance(mean, (int, float)):
                        mean_str = f"{mean:.4f}"
                        # Determine status based on NDVI value
                        if mean >= 0.7:
                            status = "Excellent 🌿"
                        elif mean >= 0.5:
                            status = "Good 🌱"
                        elif mean >= 0.3:
                            status = "Moderate 🍂"
                        else:
                            status = "Poor 🍁"
                    else:
                        mean_str = str(mean)
                        status = "N/A"
                    
                    print(f"{date:<12} {mean_str:<15} {status}")
                
                print("=" * 70)
                print()
                
                # Summary statistics
                means = [entry.get('mean') for entry in ndvi_data if isinstance(entry.get('mean'), (int, float))]
                if means:
                    avg_mean = sum(means) / len(means)
                    latest_mean = means[-1] if means else None
                    earliest_mean = means[0] if means else None
                    
                    print("Summary Statistics:")
                    print(f"  - Data points retrieved: {len(ndvi_data)}/{TEST_DAYS}")
                    print(f"  - Average NDVI mean: {avg_mean:.4f}")
                    if latest_mean:
                        print(f"  - Latest NDVI mean: {latest_mean:.4f}")
                    if earliest_mean and len(means) > 1:
                        print(f"  - Earliest NDVI mean: {earliest_mean:.4f}")
                        change = latest_mean - earliest_mean
                        change_pct = (change / earliest_mean * 100) if earliest_mean != 0 else 0
                        trend = "↑ Improving" if change > 0 else "↓ Declining" if change < 0 else "→ Stable"
                        print(f"  - Trend: {trend} ({change:+.4f}, {change_pct:+.2f}%)")
                    print()
                
                # Save raw JSON for inspection
                print("Saving response to 'ndvi_timeseries_response.json'...")
                with open('ndvi_timeseries_response.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print("✅ Response saved!")
                
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except httpx.TimeoutException:
        print("❌ Request timed out (this endpoint can take several minutes)")
        print("The endpoint is processing multiple dates sequentially.")
        print("Try running again or reduce the number of days.")
        return False
    except httpx.ConnectError:
        print("❌ Could not connect to server")
        print("Make sure the backend server is running on http://localhost:8000")
        print("Start it with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Make sure the backend server is running on http://localhost:8000")
    print("Start it with: uvicorn app.main:app --reload")
    print()
    print("This test will call the new /api/ndvi/timeseries endpoint")
    print("which fetches NDVI data for each of the past 7 days.")
    print("Each date may take 5-30 seconds, so total time: ~35-210 seconds")
    print()
    input("Press Enter to start the test...")
    print()
    
    success = asyncio.run(test_ndvi_timeseries())
    
    if success:
        print()
        print("=" * 70)
        print("✅ Test completed successfully!")
        print("=" * 70)
        print("Next steps:")
        print("1. Review the data above")
        print("2. Check 'ndvi_timeseries_response.json' for full response")
        print("3. If data looks good, we can integrate to frontend")
    else:
        print()
        print("=" * 70)
        print("❌ Test failed or returned no data")
        print("=" * 70)
        print("Please check:")
        print("1. Backend server is running")
        print("2. Coordinates are correct")
        print("3. Sentinel API credentials are configured")
        print("4. Backend logs for errors")

