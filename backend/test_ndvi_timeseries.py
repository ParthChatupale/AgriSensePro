"""
Test script to verify NDVI time series endpoint returns past 7 days of data.
Run this from the backend directory: python test_ndvi_timeseries.py
"""

import asyncio
import httpx
from datetime import datetime

# Test coordinates (you can change these to your location)
# Using coordinates that worked for the image generation endpoint
TEST_LAT = 19.7515  # Try coordinates that worked before
TEST_LON = 75.7139
TEST_DAYS = 7

async def test_ndvi_timeseries():
    """Test the NDVI time series endpoint and print results."""
    url = f"http://localhost:8000/api/ndvi/ndvi"
    params = {
        "lat": TEST_LAT,
        "lon": TEST_LON,
        "days": TEST_DAYS
    }
    
    print("=" * 60)
    print("Testing NDVI Time Series Endpoint")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Parameters: lat={TEST_LAT}, lon={TEST_LON}, days={TEST_DAYS}")
    print("=" * 60)
    print()
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout (API can be slow)
            print("Sending request... (this may take a while)")
            response = await client.get(url, params=params)
            
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
                    return
                
                print(f"✅ Successfully retrieved {len(ndvi_data)} data points")
                print()
                print("=" * 60)
                print("NDVI Mean Values (Past 7 Days)")
                print("=" * 60)
                print(f"{'Date':<12} {'Mean NDVI':<15} {'Min NDVI':<15} {'Max NDVI':<15}")
                print("-" * 60)
                
                for entry in ndvi_data:
                    date = entry.get('date', 'N/A')
                    mean = entry.get('mean', 'N/A')
                    min_val = entry.get('min', 'N/A')
                    max_val = entry.get('max', 'N/A')
                    
                    # Format mean for display
                    if isinstance(mean, (int, float)):
                        mean_str = f"{mean:.4f}"
                    else:
                        mean_str = str(mean)
                    
                    if isinstance(min_val, (int, float)):
                        min_str = f"{min_val:.4f}"
                    else:
                        min_str = str(min_val)
                    
                    if isinstance(max_val, (int, float)):
                        max_str = f"{max_val:.4f}"
                    else:
                        max_str = str(max_val)
                    
                    print(f"{date:<12} {mean_str:<15} {min_str:<15} {max_str:<15}")
                
                print("=" * 60)
                print()
                
                # Summary statistics
                means = [entry.get('mean') for entry in ndvi_data if isinstance(entry.get('mean'), (int, float))]
                if means:
                    avg_mean = sum(means) / len(means)
                    latest_mean = means[-1] if means else None
                    
                    print("Summary:")
                    print(f"  - Number of data points: {len(ndvi_data)}")
                    print(f"  - Average NDVI mean: {avg_mean:.4f}")
                    if latest_mean:
                        print(f"  - Latest NDVI mean: {latest_mean:.4f}")
                    if len(means) > 1:
                        first_mean = means[0]
                        change = latest_mean - first_mean
                        change_pct = (change / first_mean * 100) if first_mean != 0 else 0
                        print(f"  - Change from first to latest: {change:+.4f} ({change_pct:+.2f}%)")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except httpx.TimeoutException:
        print("❌ Request timed out (this API can take a long time)")
        print("Try running the request again or check if the server is running")
    except httpx.ConnectError:
        print("❌ Could not connect to server")
        print("Make sure the backend server is running on http://localhost:8000")
        print("Start it with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("Make sure the backend server is running on http://localhost:8000")
    print("Start it with: uvicorn app.main:app --reload")
    print()
    asyncio.run(test_ndvi_timeseries())

