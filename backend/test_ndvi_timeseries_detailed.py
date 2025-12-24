"""
Detailed test script to verify NDVI time series endpoint.
This version prints more debug information and tries multiple coordinate sets.
Run this from the backend directory: python test_ndvi_timeseries_detailed.py
"""

import asyncio
import httpx
from datetime import datetime, timedelta

# Test multiple coordinate sets
TEST_COORDINATES = [
    {"lat": 19.88255422206252, "lon": 75.3298, "name": "Previous working coords"},
    {"lat": 19.7515, "lon": 75.7139, "name": "Original test coords"},
    {"lat": 28.6139, "lon": 77.2090, "name": "Delhi (different region)"},
]

TEST_DAYS = 7

async def test_ndvi_timeseries(lat, lon, name):
    """Test the NDVI time series endpoint with specific coordinates."""
    url = f"http://localhost:8000/api/ndvi/ndvi"
    params = {
        "lat": lat,
        "lon": lon,
        "days": TEST_DAYS
    }
    
    print("=" * 70)
    print(f"Testing: {name}")
    print(f"Coordinates: lat={lat}, lon={lon}, days={TEST_DAYS}")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            print("Sending request...")
            start_time = datetime.now()
            response = await client.get(url, params=params)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            print(f"Response time: {elapsed:.2f} seconds")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                ndvi_data = data.get('ndvi', [])
                print(f"Data points returned: {len(ndvi_data)}")
                
                if ndvi_data:
                    print(f"\n✅ Success! Found {len(ndvi_data)} NDVI data points:")
                    print("-" * 70)
                    print(f"{'Date':<12} {'Mean':<12} {'Min':<12} {'Max':<12}")
                    print("-" * 70)
                    
                    for entry in ndvi_data:
                        date = entry.get('date', 'N/A')
                        mean = entry.get('mean', 'N/A')
                        min_val = entry.get('min', 'N/A')
                        max_val = entry.get('max', 'N/A')
                        
                        mean_str = f"{mean:.4f}" if isinstance(mean, (int, float)) else str(mean)
                        min_str = f"{min_val:.4f}" if isinstance(min_val, (int, float)) else str(min_val)
                        max_str = f"{max_val:.4f}" if isinstance(max_val, (int, float)) else str(max_val)
                        
                        print(f"{date:<12} {mean_str:<12} {min_str:<12} {max_str:<12}")
                    
                    return True
                else:
                    print("⚠️  No data points returned (empty array)")
                    print("Possible reasons:")
                    print("  - No satellite data available for this location/date range")
                    print("  - All data filtered out (clouds, invalid values)")
                    print("  - Location may be over water, urban area, or desert")
                    return False
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except httpx.TimeoutException:
        print(f"❌ Request timed out after 5 minutes")
        return False
    except httpx.ConnectError:
        print(f"❌ Could not connect to server")
        print("Make sure backend is running: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

async def main():
    print("NDVI Time Series Endpoint Test (Detailed)")
    print("=" * 70)
    print("Make sure the backend server is running on http://localhost:8000")
    print("=" * 70)
    print()
    
    success_count = 0
    for coords in TEST_COORDINATES:
        result = await test_ndvi_timeseries(
            coords["lat"], 
            coords["lon"], 
            coords["name"]
        )
        if result:
            success_count += 1
        print()
    
    print("=" * 70)
    print(f"Summary: {success_count}/{len(TEST_COORDINATES)} coordinate sets returned data")
    print("=" * 70)
    print()
    print("Note: The endpoint is working correctly if you see 200 status codes.")
    print("Empty arrays mean no satellite data was found for those coordinates.")
    print("This is normal - satellite data availability varies by location and date.")

if __name__ == "__main__":
    asyncio.run(main())

