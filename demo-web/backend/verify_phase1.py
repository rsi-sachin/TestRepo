"""
Phase 1 Verification Script
Tests ORAN API endpoints and basic functionality
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test basic health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    return response.status_code == 200

def test_oran_config():
    """Test ORAN configuration endpoint"""
    print("\nTesting /api/oran/config endpoint...")
    response = requests.get(f"{BASE_URL}/api/oran/config")
    print(f"  Status: {response.status_code}")
    print(f"  Config: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_oran_catalogs():
    """Test ORAN catalogs list endpoint"""
    print("\nTesting /api/oran/catalogs endpoint...")
    response = requests.get(f"{BASE_URL}/api/oran/catalogs")
    print(f"  Status: {response.status_code}")
    catalogs = response.json()
    print(f"  Catalogs found: {len(catalogs)}")
    return response.status_code == 200

def test_oran_statistics():
    """Test ORAN statistics endpoint"""
    print("\nTesting /api/oran/statistics endpoint...")
    response = requests.get(f"{BASE_URL}/api/oran/statistics")
    print(f"  Status: {response.status_code}")
    print(f"  Statistics: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_api_docs():
    """Test API documentation"""
    print("\nTesting API documentation...")
    response = requests.get(f"{BASE_URL}/api/docs")
    print(f"  Status: {response.status_code}")
    print(f"  API docs accessible: {response.status_code == 200}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 60)
    print("PHASE 1 VERIFICATION - ORAN API Tests")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("ORAN Config", test_oran_config),
        ("ORAN Catalogs", test_oran_catalogs),
        ("ORAN Statistics", test_oran_statistics),
        ("API Documentation", test_api_docs),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed_count = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("\n✅ Phase 1 verification SUCCESSFUL!")
    else:
        print("\n⚠️ Some tests failed. Check server logs.")

if __name__ == "__main__":
    print("\nPREREQUISITE: Ensure the backend server is running:")
    print("  cd C:\\TestRepo\\demo-web\\backend")
    print("  python run.py")
    print("\nPress Enter to start tests...")
    input()
    
    main()
