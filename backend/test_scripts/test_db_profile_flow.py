#!/usr/bin/env python3
"""
Test script for user profile flow with crop and location.

Tests:
1. Create user with crop and location
2. Update user profile
3. Fetch dashboard with crop param
4. Fetch advisory for user's crop

Usage:
    python test_scripts/test_db_profile_flow.py
"""
import sys
import os
import requests
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"

def test_profile_flow():
    """Test complete profile flow."""
    print("=" * 60)
    print("Testing User Profile Flow with Crop & Location")
    print("=" * 60)
    print()
    
    # Test user credentials
    test_email = f"test_user_{os.getpid()}@test.com"
    test_password = "testpass123"
    
    results = {}
    
    # 1. Signup with crop and location
    print("1. Testing Signup with Crop & Location")
    print("-" * 60)
    try:
        signup_data = {
            "name": "Test Farmer",
            "email": test_email,
            "password": test_password,
            "userType": "farmer",
            "crop": "cotton",
            "location": "Punjab, India"
        }
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, timeout=10)
        
        if response.status_code == 201:
            user_data = response.json()
            print(f"✅ User created: {user_data.get('email')}")
            print(f"   Crop: {user_data.get('crop')}")
            print(f"   Location: {user_data.get('location')}")
            results["signup"] = True
            access_token = None  # Signup doesn't return token in this endpoint
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"   Response: {response.text}")
            results["signup"] = False
            return results
    except Exception as e:
        print(f"❌ Signup error: {str(e)}")
        results["signup"] = False
        return results
    
    # 2. Login to get token
    print("\n2. Testing Login")
    print("-" * 60)
    try:
        login_data = {
            "email": test_email,
            "password": test_password
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            login_response = response.json()
            access_token = login_response.get("access_token")
            user_info = login_response.get("user", {})
            print(f"✅ Login successful")
            print(f"   Token: {access_token[:20]}...")
            print(f"   User crop: {user_info.get('crop')}")
            print(f"   User location: {user_info.get('location')}")
            results["login"] = True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            results["login"] = False
            return results
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        results["login"] = False
        return results
    
    # 3. Get current user profile
    print("\n3. Testing GET /auth/me")
    print("-" * 60)
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Profile retrieved")
            print(f"   Name: {user_data.get('name')}")
            print(f"   Crop: {user_data.get('crop')}")
            print(f"   Location: {user_data.get('location')}")
            results["get_profile"] = True
        else:
            print(f"❌ Get profile failed: {response.status_code}")
            print(f"   Response: {response.text}")
            results["get_profile"] = False
    except Exception as e:
        print(f"❌ Get profile error: {str(e)}")
        results["get_profile"] = False
    
    # 4. Update profile
    print("\n4. Testing PATCH /auth/profile")
    print("-" * 60)
    try:
        update_data = {
            "crop": "wheat",
            "location": "Haryana, India"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.patch(f"{BASE_URL}/auth/profile", json=update_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            updated_user = response.json()
            print(f"✅ Profile updated")
            print(f"   New crop: {updated_user.get('crop')}")
            print(f"   New location: {updated_user.get('location')}")
            results["update_profile"] = True
        else:
            print(f"❌ Update profile failed: {response.status_code}")
            print(f"   Response: {response.text}")
            results["update_profile"] = False
    except Exception as e:
        print(f"❌ Update profile error: {str(e)}")
        results["update_profile"] = False
    
    # 5. Fetch dashboard with crop param
    print("\n5. Testing GET /fusion/dashboard?crop=wheat")
    print("-" * 60)
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/fusion/dashboard?crop=wheat", headers=headers, timeout=10)
        
        if response.status_code == 200:
            dashboard_data = response.json()
            print(f"✅ Dashboard data retrieved")
            print(f"   User crop in response: {dashboard_data.get('user_crop')}")
            print(f"   Crops monitored: {dashboard_data.get('summary', {}).get('crops_monitored', 0)}")
            results["dashboard_with_crop"] = True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            print(f"   Response: {response.text}")
            results["dashboard_with_crop"] = False
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
        results["dashboard_with_crop"] = False
    
    # 6. Fetch advisory for user's crop
    print("\n6. Testing GET /fusion/advisory/wheat")
    print("-" * 60)
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/fusion/advisory/wheat", headers=headers, timeout=10)
        
        if response.status_code == 200:
            advisory_data = response.json()
            print(f"✅ Advisory retrieved")
            print(f"   Crop: {advisory_data.get('crop')}")
            print(f"   Priority: {advisory_data.get('priority')}")
            print(f"   Recommendations: {len(advisory_data.get('recommendations', []))}")
            results["advisory"] = True
        else:
            print(f"❌ Advisory failed: {response.status_code}")
            print(f"   Response: {response.text}")
            results["advisory"] = False
    except Exception as e:
        print(f"❌ Advisory error: {str(e)}")
        results["advisory"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = test_profile_flow()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print(f"   Make sure the backend is running at {BASE_URL}")
        print("   Start it with: uvicorn app.main:app --reload")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)

