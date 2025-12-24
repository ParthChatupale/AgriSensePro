# Plan: NDVI Time Series Endpoint Implementation

## Goal
Create a new endpoint `/api/ndvi/timeseries` that returns past 7 days of NDVI mean values using the existing working `backend/ndvi/pipeline` implementation.

## Current State
- ✅ `/api/ndvi/run` - Works perfectly, uses `run_ndvi()` function
- ✅ `run_ndvi(lat, lon, radius_m, date, out_prefix)` - Core function that fetches and computes NDVI
- ❌ `/api/ndvi/ndvi` - Currently returns empty (from unused `backend/app/ndvi` - being removed)

## Implementation Plan

### Step 1: Add Time Series Endpoint to Existing Router
**File**: `backend/ndvi/ndvi_router.py`

**What to add**:
- New endpoint: `GET /api/ndvi/timeseries?lat={lat}&lon={lon}&days=7`
- New function: `get_ndvi_timeseries()` that:
  1. Takes lat, lon, days (default 7) as query parameters
  2. Loops through past N days (going backwards from today)
  3. For each date, calls `run_ndvi(lat, lon, radius_m=250, date=date_str, out_prefix=temp_prefix)`
  4. Collects the `stats.mean` value from each call
  5. Returns array of `{date: "YYYY-MM-DD", mean: number}` objects

**Key considerations**:
- Use the same `radius_m=250` as the image generation endpoint
- Generate temporary unique prefixes for each date (to avoid file conflicts)
- Handle cases where `run_ndvi()` fails for a date (skip it, don't break)
- Handle cases where `stats.mean` is None (skip that date)
- Sort results by date (oldest to newest)

### Step 2: Response Format
**Format**:
```json
{
  "location": {"lat": 19.7515, "lon": 75.7139},
  "range_days": 7,
  "ndvi": [
    {"date": "2025-12-18", "mean": 0.5976},
    {"date": "2025-12-20", "mean": 0.6048},
    {"date": "2025-12-22", "mean": 0.5921}
  ]
}
```

**Note**: Array may have fewer items than `range_days` if some dates don't have data.

### Step 3: Error Handling
- If no dates return data: Return empty array `[]` (don't error)
- If `run_ndvi()` throws exception for a date: Log it, skip that date, continue
- If coordinates are invalid: Return 400 error (FastAPI validation will handle this)

### Step 4: Performance Considerations
- Sequential calls (one date at a time) - simpler, more reliable
- Each call to `run_ndvi()` can take 5-30 seconds (Sentinel API)
- Total time: ~35-210 seconds for 7 days (acceptable for background fetch)
- Frontend should handle long response times (already has loading states)

### Step 5: Files to Modify
1. ✅ `backend/ndvi/ndvi_router.py` - Add new endpoint
2. ❌ `backend/ndvi/pipeline/ndvi_pipeline.py` - **NO CHANGES** (reuse as-is)
3. ✅ `backend/app/main.py` - Already correct (uses ndvi_image_router)

### Step 6: Testing
- Test with coordinates that work for `/api/ndvi/run`
- Verify returns 0-7 data points (depending on data availability)
- Verify dates are sorted correctly
- Verify handles missing dates gracefully

## Safety Guarantees

### ✅ Won't Break Existing Functionality
- `/api/ndvi/run` endpoint unchanged
- `run_ndvi()` function unchanged  
- All existing code paths remain intact
- New endpoint is completely separate

### ✅ Backward Compatible
- New endpoint doesn't conflict with existing routes
- Uses same underlying implementation
- Same credentials, same API limits

## Implementation Details

### Code Structure
```python
@router.get("/timeseries")
def get_ndvi_timeseries(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    days: int = Query(7, ge=1, le=30)
):
    """
    Get NDVI time series for past N days.
    Returns mean NDVI values for each date with available data.
    """
    # Generate dates (past N days, backwards from today)
    # Loop through dates
    #   Call run_ndvi() for each date
    #   Extract stats.mean
    #   Collect in results array
    # Return formatted response
```

### Date Generation
- Start from today, go back N days
- Format: "YYYY-MM-DD"
- UTC dates to match Sentinel API

### Temporary Prefix Strategy
- Use format: `timeseries_{timestamp}_{date_str}` for uniqueness
- Files will be created but that's okay (they're temporary job outputs)
- Could clean up later if needed, but not critical

## Expected Behavior

### Success Case
```json
{
  "location": {"lat": 19.7515, "lon": 75.7139},
  "range_days": 7,
  "ndvi": [
    {"date": "2025-12-18", "mean": 0.5976},
    {"date": "2025-12-20", "mean": 0.6048},
    {"date": "2025-12-22", "mean": 0.5921}
  ]
}
```

### Partial Data Case (some dates missing)
```json
{
  "location": {"lat": 19.7515, "lon": 75.7139},
  "range_days": 7,
  "ndvi": [
    {"date": "2025-12-20", "mean": 0.6048},
    {"date": "2025-12-22", "mean": 0.5921}
  ]
}
```

### No Data Case
```json
{
  "location": {"lat": 19.7515, "lon": 75.7139},
  "range_days": 7,
  "ndvi": []
}
```

