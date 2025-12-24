"""
Test script to verify NDVI time series interpolation logic and generate SVG visualization.
This tests the interpolation algorithm that will be used in the frontend.

Run this from the backend directory: python test_ndvi_interpolation_svg.py
"""

import asyncio
import httpx
from datetime import datetime, timedelta
import json
from pathlib import Path

# Test coordinates (use coordinates that worked for /api/ndvi/run)
TEST_LAT = 19.7515
TEST_LON = 75.7139
TEST_DAYS = 7

def interpolate_ndvi_timeseries(data, days=7):
    """
    Interpolate missing dates in NDVI timeseries using linear interpolation.
    
    Args:
        data: List of {date: str, mean: float} objects
        days: Number of days to generate
    
    Returns:
        List of {date: str, mean: float} with all dates filled in
    """
    if len(data) == 0:
        return []
    
    # Generate all dates for the past N days
    today = datetime.utcnow().date()
    all_dates = []
    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        all_dates.append(date.strftime("%Y-%m-%d"))
    
    # Create a map of available data points
    data_map = {}
    for item in data:
        data_map[item["date"]] = item["mean"]
    
    # Interpolate missing dates
    interpolated = []
    
    for i, current_date in enumerate(all_dates):
        # If we have data for this date, use it
        if current_date in data_map:
            interpolated.append({"date": current_date, "mean": data_map[current_date]})
            continue
        
        # Otherwise, find the nearest data points before and after
        before_date = None
        before_value = None
        after_date = None
        after_value = None
        
        # Look backwards for the nearest data point
        for j in range(i - 1, -1, -1):
            check_date = all_dates[j]
            if check_date in data_map:
                before_date = check_date
                before_value = data_map[check_date]
                break
        
        # Look forwards for the nearest data point
        for j in range(i + 1, len(all_dates)):
            check_date = all_dates[j]
            if check_date in data_map:
                after_date = check_date
                after_value = data_map[check_date]
                break
        
        # Interpolate based on available neighbors
        if before_value is not None and after_value is not None and before_date and after_date:
            # Linear interpolation between two points
            before_time = datetime.strptime(before_date, "%Y-%m-%d").timestamp()
            after_time = datetime.strptime(after_date, "%Y-%m-%d").timestamp()
            current_time = datetime.strptime(current_date, "%Y-%m-%d").timestamp()
            ratio = (current_time - before_time) / (after_time - before_time)
            interpolated_value = before_value + (after_value - before_value) * ratio
            interpolated.append({"date": current_date, "mean": interpolated_value})
        elif before_value is not None:
            # Only have data before - forward fill
            interpolated.append({"date": current_date, "mean": before_value})
        elif after_value is not None:
            # Only have data after - backward fill
            interpolated.append({"date": current_date, "mean": after_value})
        else:
            # No data at all - skip this date (shouldn't happen if we have at least one data point)
            continue
    
    return interpolated


def generate_svg_graph(data, output_path):
    """
    Generate an SVG graph similar to what the frontend would render.
    
    Args:
        data: List of {date: str, mean: float} objects (should be 7 items)
        output_path: Path to save the SVG file
    """
    if len(data) == 0:
        print("⚠️  No data to plot")
        return
    
    # Extract values and dates
    values = [item["mean"] for item in data]
    dates = [item["date"] for item in data]
    
    # Calculate graph dimensions
    width = 400
    height = 200
    padding = 40
    graph_width = width - 2 * padding
    graph_height = height - 2 * padding
    
    # Calculate min/max for scaling
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val
    if range_val == 0:
        range_val = 0.0001  # Avoid division by zero
    
    # Generate points for polyline
    points = []
    for i, value in enumerate(values):
        x = padding + (i / (len(values) - 1)) * graph_width if len(values) > 1 else padding + graph_width / 2
        y = padding + graph_height - ((value - min_val) / range_val) * graph_height
        points.append(f"{x},{y}")
    
    points_str = " ".join(points)
    
    # Determine color based on average NDVI
    avg_ndvi = sum(values) / len(values)
    if avg_ndvi >= 0.7:
        line_color = "#22c55e"  # green (excellent)
    elif avg_ndvi >= 0.5:
        line_color = "#84cc16"  # lime (good)
    elif avg_ndvi >= 0.3:
        line_color = "#eab308"  # yellow (moderate)
    else:
        line_color = "#ef4444"  # red (poor)
    
    # Create SVG content
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#f8f9fa" stroke="#e9ecef" stroke-width="1"/>
  
  <!-- Grid lines -->
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e9ecef" stroke-width="0.5"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#grid)"/>
  
  <!-- Axes -->
  <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height - padding}" stroke="#6c757d" stroke-width="2"/>
  <line x1="{padding}" y1="{height - padding}" x2="{width - padding}" y2="{height - padding}" stroke="#6c757d" stroke-width="2"/>
  
  <!-- Y-axis labels -->
  <text x="{padding - 10}" y="{padding}" text-anchor="end" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">{max_val:.3f}</text>
  <text x="{padding - 10}" y="{height - padding + 5}" text-anchor="end" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">{min_val:.3f}</text>
  <text x="{padding - 10}" y="{(padding + height - padding) / 2 + 5}" text-anchor="end" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">{((min_val + max_val) / 2):.3f}</text>
  
  <!-- Data line -->
  <polyline points="{points_str}" fill="none" stroke="{line_color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  
  <!-- Data points -->
  {"".join([f'<circle cx="{padding + (i / (len(values) - 1)) * graph_width if len(values) > 1 else padding + graph_width / 2}" cy="{padding + graph_height - ((value - min_val) / range_val) * graph_height}" r="4" fill="{line_color}" stroke="white" stroke-width="1.5"/>' for i, value in enumerate(values)])}
  
  <!-- X-axis labels (dates) -->
  {"".join([f'<text x="{padding + (i / (len(values) - 1)) * graph_width if len(values) > 1 else padding + graph_width / 2}" y="{height - padding + 20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#6c757d" transform="rotate(-45 {padding + (i / (len(values) - 1)) * graph_width if len(values) > 1 else padding + graph_width / 2} {height - padding + 20})">{dates[i][5:]}</text>' for i in range(len(dates))])}
  
  <!-- Title -->
  <text x="{width / 2}" y="20" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#212529">NDVI Time Series (7 Days)</text>
  
  <!-- Legend -->
  <text x="{width - padding}" y="30" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#6c757d">Avg: {avg_ndvi:.4f}</text>
</svg>'''
    
    # Save SVG file
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"✅ SVG graph saved to: {output_path}")


async def test_interpolation():
    """Test the interpolation logic with real API data."""
    url = "http://localhost:8000/api/ndvi/timeseries"
    params = {
        "lat": TEST_LAT,
        "lon": TEST_LON,
        "days": TEST_DAYS
    }
    
    print("=" * 70)
    print("Testing NDVI Time Series Interpolation")
    print("=" * 70)
    print(f"URL: {url}")
    print(f"Parameters: lat={TEST_LAT}, lon={TEST_LON}, days={TEST_DAYS}")
    print("=" * 70)
    print()
    
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            print("Sending request to API...")
            start_time = datetime.now()
            
            response = await client.get(url, params=params)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"Response time: {elapsed:.2f} seconds")
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                raw_data = data.get('ndvi', [])
                
                print(f"Raw data points: {len(raw_data)}/{TEST_DAYS}")
                print("-" * 70)
                print(f"{'Date':<12} {'Mean NDVI':<15} {'Type'}")
                print("-" * 70)
                for entry in raw_data:
                    print(f"{entry['date']:<12} {entry['mean']:<15.4f} {'Real'}")
                print()
                
                # Apply interpolation
                print("Applying interpolation...")
                interpolated_data = interpolate_ndvi_timeseries(raw_data, TEST_DAYS)
                
                print(f"Interpolated data points: {len(interpolated_data)}/{TEST_DAYS}")
                print("-" * 70)
                print(f"{'Date':<12} {'Mean NDVI':<15} {'Type'}")
                print("-" * 70)
                
                # Create a set of original dates for comparison
                original_dates = {item["date"] for item in raw_data}
                
                for entry in interpolated_data:
                    data_type = "Real" if entry["date"] in original_dates else "Interpolated"
                    print(f"{entry['date']:<12} {entry['mean']:<15.4f} {data_type}")
                print()
                
                # Generate SVG
                output_dir = Path(__file__).parent / "ndvi" / "ndvi" / "data" / "ndvi_timeseries"
                output_dir.mkdir(parents=True, exist_ok=True)
                svg_path = output_dir / f"ndvi_graph_{TEST_LAT}_{TEST_LON}_{TEST_DAYS}days.svg"
                
                print("Generating SVG graph...")
                generate_svg_graph(interpolated_data, svg_path)
                print()
                
                # Save interpolated data as JSON
                json_path = output_dir / f"interpolated_{TEST_LAT}_{TEST_LON}_{TEST_DAYS}days.json"
                with open(json_path, 'w') as f:
                    json.dump({
                        "location": {"lat": TEST_LAT, "lon": TEST_LON},
                        "range_days": TEST_DAYS,
                        "raw_data": raw_data,
                        "interpolated_data": interpolated_data,
                        "interpolation_date": datetime.utcnow().isoformat()
                    }, f, indent=2)
                
                print(f"✅ Interpolated data saved to: {json_path}")
                print()
                print("=" * 70)
                print("✅ Test completed successfully!")
                print("=" * 70)
                print(f"📊 SVG Graph: {svg_path}")
                print(f"📄 Interpolated Data: {json_path}")
                print()
                print("Summary:")
                print(f"  - Raw data points: {len(raw_data)}/{TEST_DAYS}")
                print(f"  - Interpolated data points: {len(interpolated_data)}/{TEST_DAYS}")
                if interpolated_data:
                    avg_ndvi = sum(item["mean"] for item in interpolated_data) / len(interpolated_data)
                    print(f"  - Average NDVI: {avg_ndvi:.4f}")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except httpx.TimeoutException:
        print("❌ Request timed out")
        return False
    except httpx.ConnectError:
        print("❌ Could not connect to server")
        print("Make sure the backend server is running on http://localhost:8000")
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
    print("This test will:")
    print("1. Fetch NDVI timeseries data from the API")
    print("2. Apply linear interpolation to fill missing dates")
    print("3. Generate an SVG graph visualization")
    print("4. Save both the graph and interpolated data to files")
    print()
    input("Press Enter to start the test...")
    print()
    
    success = asyncio.run(test_interpolation())
    
    if not success:
        print()
        print("=" * 70)
        print("❌ Test failed")
        print("=" * 70)

