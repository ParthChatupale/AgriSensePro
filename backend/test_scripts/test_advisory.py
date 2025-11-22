#!/usr/bin/env python3
"""
Test script for Fusion Engine Advisory endpoint.

Usage:
    python test_scripts/test_advisory.py [crop_name]
    
Examples:
    python test_scripts/test_advisory.py cotton
    python test_scripts/test_advisory.py wheat
    python test_scripts/test_advisory.py rice
"""
import requests
import json
import sys
import os

# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"


def test_advisory(crop_name: str = "cotton"):
    """Test the /fusion/advisory/{crop} endpoint."""
    endpoint = f"{BASE_URL}/fusion/advisory/{crop_name.lower()}"
    
    print("=" * 60)
    print("Testing Fusion Engine Advisory Endpoint")
    print("=" * 60)
    print(f"\nCrop: {crop_name.capitalize()}")
    print(f"Endpoint: {endpoint}\n")
    
    try:
        response = requests.get(endpoint, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}\n")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Advisory data retrieved")
            print("\n" + "-" * 60)
            print("Advisory Details:")
            print("-" * 60)
            
            # Print basic info
            print(f"\n🌾 Crop: {data.get('crop', 'N/A')}")
            print(f"📊 Priority: {data.get('priority', 'N/A')}")
            print(f"⚠️  Severity: {data.get('severity', 'N/A')}")
            print(f"📈 Rule Score: {data.get('rule_score', 0):.2f} ({data.get('rule_score', 0)*100:.0f}%)")
            
            # Print analysis
            if "analysis" in data:
                print(f"\n📝 Analysis:")
                print(f"  {data['analysis']}")
            
            # Print fired rules
            if "fired_rules" in data and data["fired_rules"]:
                print(f"\n🔍 Fired Rules ({len(data['fired_rules'])}):")
                for i, rule in enumerate(data["fired_rules"], 1):
                    print(f"  {i}. {rule}")
            
            # Print recommendations
            if "recommendations" in data and data["recommendations"]:
                print(f"\n💡 Recommendations ({len(data['recommendations'])}):")
                for i, rec in enumerate(data["recommendations"], 1):
                    print(f"  {i}. [{rec.get('priority', 'medium').upper()}] {rec.get('title')}")
                    print(f"     {rec.get('desc', '')}")
                    if rec.get('timeline'):
                        print(f"     Timeline: {rec.get('timeline')}")
            
            # Print rule breakdown
            if "rule_breakdown" in data:
                breakdown = data["rule_breakdown"]
                print(f"\n📊 Rule Breakdown:")
                print(f"  - Pest Detection: {breakdown.get('pest', {}).get('score', 0)*100:.0f}% ({len(breakdown.get('pest', {}).get('fired', []))} rules)")
                print(f"  - Irrigation: {breakdown.get('irrigation', {}).get('score', 0)*100:.0f}% ({len(breakdown.get('irrigation', {}).get('fired', []))} rules)")
                print(f"  - Market: {breakdown.get('market', {}).get('score', 0)*100:.0f}% ({len(breakdown.get('market', {}).get('fired', []))} rules)")
            
            # Print data sources
            if "data_sources" in data:
                sources = data["data_sources"]
                print(f"\n📡 Data Sources:")
                print(f"  - Weather: {sources.get('weather', 'N/A')}")
                print(f"  - Satellite: {sources.get('satellite', 'N/A')}")
                print(f"  - Market: {sources.get('market', 'N/A')}")
            
            if "last_updated" in data:
                print(f"\n🕒 Last Updated: {data['last_updated']}")
            
            print("\n" + "-" * 60)
            print("Full JSON Response:")
            print("-" * 60)
            print(json.dumps(data, indent=2))
            
            return True
        elif response.status_code == 404:
            print(f"❌ ERROR: Advisory not found for crop '{crop_name}'")
            print(f"Response: {response.text}")
            print("\n💡 Available crops: cotton, wheat, rice, sugarcane")
            return False
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server.")
        print(f"   Make sure the backend is running at {BASE_URL}")
        print("   Start it with: uvicorn app.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        return False


def test_all_crops():
    """Test advisory endpoint for all available crops."""
    crops = ["cotton", "wheat", "rice", "sugarcane"]
    results = {}
    
    print("=" * 60)
    print("Testing Advisory Endpoint for All Crops")
    print("=" * 60)
    print()
    
    for crop in crops:
        print(f"\n{'='*60}")
        success = test_advisory(crop)
        results[crop] = success
        print()
    
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    for crop, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {crop.capitalize()}: {status}")
    
    all_passed = all(results.values())
    return all_passed


if __name__ == "__main__":
    if len(sys.argv) > 1:
        crop_name = sys.argv[1]
        success = test_advisory(crop_name)
    else:
        # Test all crops
        success = test_all_crops()
    
    sys.exit(0 if success else 1)

