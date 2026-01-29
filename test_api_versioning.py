"""
Quick test script for API versioning
"""

import requests
import json

BASE_URL = "http://localhost:8080"


def test_root():
    """Test root endpoint"""
    print("\n" + "=" * 60)
    print("Testing Root Endpoint")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_v1_endpoints():
    """Test V1 endpoints"""
    print("\n" + "=" * 60)
    print("Testing V1 Endpoints")
    print("=" * 60)

    endpoints = [
        "/api/v1/health",
        "/api/v1/users",
        "/api/v1/issues",
        "/api/v1/teams",
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code in [200, 401, 422] else "❌"
            print(f"{status} {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")


def test_backward_compatibility():
    """Test old endpoints (backward compatibility)"""
    print("\n" + "=" * 60)
    print("Testing Backward Compatibility (Old Endpoints)")
    print("=" * 60)

    endpoints = [
        "/health",
        "/users",
        "/issues",
        "/teams",
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code in [200, 401, 422] else "❌"
            print(f"{status} {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")


if __name__ == "__main__":
    print("\n🚀 API Versioning Test Suite")
    print("=" * 60)
    print("Make sure server is running: python main.py")
    print("=" * 60)

    try:
        test_root()
        test_v1_endpoints()
        test_backward_compatibility()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        print("\n📚 Next Steps:")
        print("1. Open http://localhost:8080/docs to see Swagger UI")
        print("2. Check that endpoints are grouped by version")
        print("3. Verify deprecated endpoints are marked")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Server not running!")
        print("Start server with: python main.py")
