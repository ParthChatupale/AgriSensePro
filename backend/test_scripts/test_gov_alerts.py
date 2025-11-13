"""Test script for government alerts service."""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.gov_alerts import (
    fetch_farmer_gov_alerts,
    fetch_icar_kvk_alerts,
    normalize_alerts,
    fetch_and_cache_gov_alerts,
)


async def test_direct_services():
    """Test direct service scraping."""
    print("=" * 60)
    print("Testing Direct Service Scraping")
    print("=" * 60)
    
    state = "Maharashtra"
    district = "Pune"
    
    print(f"\n1. Testing farmer.gov.in alerts for {state}, {district}:")
    try:
        farmer_alerts = await fetch_farmer_gov_alerts(state, district)
        print(f"   Found {len(farmer_alerts)} alerts")
        if farmer_alerts:
            print(f"   Sample: {farmer_alerts[0]}")
    except Exception as e:
        print(f"   Error: {type(e).__name__}: {e}")
    
    print(f"\n2. Testing ICAR KVK alerts for {state}, {district}:")
    try:
        kvk_alerts = await fetch_icar_kvk_alerts(state, district)
        print(f"   Found {len(kvk_alerts)} alerts")
        if kvk_alerts:
            print(f"   Sample: {kvk_alerts[0]}")
    except Exception as e:
        print(f"   Error: {type(e).__name__}: {e}")
    
    print(f"\n3. Testing normalize_alerts:")
    try:
        normalized = normalize_alerts(farmer_alerts, kvk_alerts)
        print(f"   Normalized {len(normalized)} alerts")
        if normalized:
            print(f"   Sample normalized alert:")
            for key, value in normalized[0].items():
                print(f"     {key}: {value}")
    except Exception as e:
        print(f"   Error: {type(e).__name__}: {e}")


async def test_cache_logic():
    """Test cache logic."""
    print("\n" + "=" * 60)
    print("Testing Cache Logic")
    print("=" * 60)
    
    state = "Maharashtra"
    district = "Pune"
    
    print(f"\n1. First call (should fetch and cache):")
    try:
        alerts1 = await fetch_and_cache_gov_alerts(state, district)
        print(f"   Retrieved {len(alerts1)} alerts")
    except Exception as e:
        print(f"   Error: {type(e).__name__}: {e}")
        alerts1 = []
    
    print(f"\n2. Second call (should use cache):")
    try:
        alerts2 = await fetch_and_cache_gov_alerts(state, district)
        print(f"   Retrieved {len(alerts2)} alerts")
        print(f"   Cache working: {len(alerts1) == len(alerts2)}")
    except Exception as e:
        print(f"   Error: {type(e).__name__}: {e}")


async def test_fusion_endpoint():
    """Test fusion endpoint."""
    print("\n" + "=" * 60)
    print("Testing Fusion Endpoint")
    print("=" * 60)
    
    import httpx
    
    base_url = "http://localhost:8000"
    url = f"{base_url}/fusion/gov-alerts"
    
    print(f"\nTesting: {url}")
    print("Parameters: state=Maharashtra, district=Pune")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params={"state": "Maharashtra", "district": "Pune"})
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Response received")
                print(f"  Alert count: {data.get('count', 0)}")
                alerts = data.get("alerts", [])
                if alerts:
                    print(f"  Sample alert:")
                    for key, value in alerts[0].items():
                        print(f"    {key}: {value}")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
    except httpx.ConnectError:
        print("✗ Cannot connect to server")
        print("  Make sure FastAPI server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GOVERNMENT ALERTS TEST SUITE")
    print("=" * 60)
    
    await test_direct_services()
    await test_cache_logic()
    await test_fusion_endpoint()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

