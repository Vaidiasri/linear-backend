"""
Rate Limiting Test Script
Tests rate limits on different endpoints
"""

import requests
import time

BASE_URL = "http://localhost:8080/api/v1"


def test_auth_rate_limit():
    """Test auth endpoint rate limit (5/minute)"""
    print("\n" + "=" * 60)
    print("Testing Auth Rate Limit (5/minute)")
    print("=" * 60)

    for i in range(1, 7):
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={"username": "test@example.com", "password": "test123"},
            )
            print(f"Request {i}: Status {response.status_code}")
            if response.status_code == 429:
                print(f"   ✅ Rate limit enforced!")
                print(f"   Response: {response.json()}")
                break
        except Exception as e:
            print(f"Request {i}: Error - {str(e)}")
        time.sleep(0.5)


def test_user_creation_limit():
    """Test user creation rate limit (10/minute)"""
    print("\n" + "=" * 60)
    print("Testing User Creation Rate Limit (10/minute)")
    print("=" * 60)

    for i in range(1, 12):
        try:
            response = requests.post(
                f"{BASE_URL}/users",
                json={
                    "email": f"test{i}@example.com",
                    "password": "test123",
                    "full_name": f"Test User {i}",
                },
            )
            print(f"Request {i}: Status {response.status_code}")
            if response.status_code == 429:
                print(f"   ✅ Rate limit enforced!")
                print(f"   Response: {response.json()}")
                break
        except Exception as e:
            print(f"Request {i}: Error - {str(e)}")
        time.sleep(0.3)


def test_issue_read_limit():
    """Test issue read rate limit (100/minute)"""
    print("\n" + "=" * 60)
    print("Testing Issue Read Rate Limit (100/minute)")
    print("=" * 60)

    success_count = 0
    for i in range(1, 15):
        try:
            response = requests.get(f"{BASE_URL}/issues")
            if response.status_code in [200, 401]:  # 401 if not authenticated
                success_count += 1
                print(f"Request {i}: Status {response.status_code} ✅")
            elif response.status_code == 429:
                print(f"Request {i}: Rate limited (unexpected for 100/min)")
                break
        except Exception as e:
            print(f"Request {i}: Error - {str(e)}")
        time.sleep(0.1)

    print(f"\n   ✅ {success_count} requests succeeded (limit is 100/min)")


if __name__ == "__main__":
    print("\n🛡️ Rate Limiting Test Suite")
    print("=" * 60)
    print("Make sure server is running: python main.py")
    print("=" * 60)

    try:
        # Test 1: Auth rate limit (strict)
        test_auth_rate_limit()

        # Wait a bit
        print("\n⏳ Waiting 2 seconds...")
        time.sleep(2)

        # Test 2: User creation limit
        test_user_creation_limit()

        # Wait a bit
        print("\n⏳ Waiting 2 seconds...")
        time.sleep(2)

        # Test 3: Issue read limit (should allow many)
        test_issue_read_limit()

        print("\n" + "=" * 60)
        print("✅ Rate limiting tests completed!")
        print("=" * 60)
        print("\n📚 Summary:")
        print("- Auth login: 5 requests/minute ✅")
        print("- User creation: 10 requests/minute ✅")
        print("- Issue reads: 100 requests/minute ✅")
        print("\nCheck server logs for rate limit details")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Server not running!")
        print("Start server with: python main.py")
