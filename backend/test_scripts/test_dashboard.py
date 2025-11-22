#!/usr/bin/env python3
"""
Test script for Fusion Engine Dashboard endpoint.

Usage:
    python test_scripts/test_dashboard.py
"""
import requests
import json
import sys
import os

# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/fusion/dashboard"


def test_dashboard():
    """Test the /fusion/dashboard endpoint."""
    print("=" * 60)
    print("Testing Fusion Engine Dashboard Endpoint")
    print("=" * 60)
    print(f"\nEndpoint: {ENDPOINT}\n")
    
    try:
        response = requests.get(ENDPOINT, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}\n")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Dashboard data retrieved")
            print("\n" + "-" * 60)
            print("Response Structure:")
            print("-" * 60)
            
            # Print summary
            if "summary" in data:
                summary = data["summary"]
                print(f"\n📊 Summary:")
                print(f"  - Total Alerts: {summary.get('total_alerts', 0)}")
                print(f"  - High Priority: {summary.get('high_priority_count', 0)}")
                print(f"  - Crops Monitored: {summary.get('crops_monitored', 0)}")
            
            # Print weather
            if "weather" in data:
                weather = data["weather"]
                print(f"\n🌤️  Weather:")
                print(f"  - Temperature: {weather.get('temperature')}°C")
                print(f"  - Humidity: {weather.get('humidity')}%")
                print(f"  - Rainfall: {weather.get('rainfall')}mm")
                print(f"  - Wind Speed: {weather.get('wind_speed')} km/h")
            
            # Print market prices
            if "market" in data:
                market = data["market"]
                print(f"\n💰 Market Prices:")
                for crop, price_data in market.items():
                    trend = price_data.get("trend", "stable")
                    change = price_data.get("change_percent", 0)
                    arrow = "↑" if change >= 0 else "↓"
                    print(f"  - {crop.capitalize()}: ₹{price_data.get('price')} {arrow} {abs(change)}%")
            
            # Print alerts
            if "alerts" in data and data["alerts"]:
                alerts = data["alerts"]
                print(f"\n⚠️  Alerts ({len(alerts)}):")
                for alert in alerts[:3]:  # Show first 3
                    print(f"  - [{alert.get('level', 'unknown').upper()}] {alert.get('title')} (Confidence: {alert.get('confidence')}%)")
            
            # Print crop health
            if "crop_health" in data:
                crop_health = data["crop_health"]
                print(f"\n🌾 Crop Health:")
                for crop, health in crop_health.items():
                    print(f"  - {crop.capitalize()}: NDVI {health.get('ndvi', 0):.2f}, Health Score: {health.get('health_score', 0)}%")
            
            print("\n" + "-" * 60)
            print("Full JSON Response:")
            print("-" * 60)
            print(json.dumps(data, indent=2))
            
            return True
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


if __name__ == "__main__":
    success = test_dashboard()
    sys.exit(0 if success else 1)

