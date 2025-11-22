#!/usr/bin/env python3
"""
Test all Fusion Engine endpoints.

Usage:
    python test_scripts/test_all.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_dashboard import test_dashboard
from test_advisory import test_advisory

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FUSION ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*60 + "\n")
    
    results = {}
    
    # Test dashboard
    print("\n" + "="*60)
    print("TEST 1: Dashboard Endpoint")
    print("="*60)
    results["dashboard"] = test_dashboard()
    
    # Test advisory for each crop
    crops = ["cotton", "wheat", "rice"]
    for crop in crops:
        print("\n" + "="*60)
        print(f"TEST {len(results) + 1}: Advisory Endpoint - {crop.capitalize()}")
        print("="*60)
        results[f"advisory_{crop}"] = test_advisory(crop)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

