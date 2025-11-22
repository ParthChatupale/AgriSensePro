"""Test script for Agmarknet market price service."""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.market_service import fetch_market_price


async def main():
    """Test market price fetching."""
    print("Testing Agmarknet market price service...\n")
    
    # Test with cotton and Pune district
    print("1. Testing cotton price in Nashik district:")
    result = await fetch_market_price("cotton", "nashik")
    print(f"   Result: {result}\n")
    
    # Test with wheat, no district
    print("2. Testing wheat price (no district):")
    result2 = await fetch_market_price("wheat", None)
    print(f"   Result: {result2}\n")
    
    # Test with rice
    print("3. Testing rice price:")
    result3 = await fetch_market_price("rice", None)
    print(f"   Result: {result3}\n")
    
    print("Market price service test completed!")


if __name__ == "__main__":
    asyncio.run(main())

