import asyncio
import httpx
import sys
import os

# Base URL
API_URL = "http://127.0.0.1:8080/api/v1"


async def test_api():
    async with httpx.AsyncClient() as client:
        # 1. Login to get token
        print("Logging in as admin...")
        try:
            login_res = await client.post(
                f"{API_URL}/auth/login",
                data={"username": "admin@example.com", "password": "password123"},
            )
            if login_res.status_code != 200:
                print(f"Login failed: {login_res.status_code} {login_res.text}")
                return

            token = login_res.json()["access_token"]
            print("Login successful. Token received.")

            # 2. Fetch Users
            print("Fetching users...")
            headers = {"Authorization": f"Bearer {token}"}

            # Test verification
            url_verify = f"{API_URL}/users/verify_this"
            print(f"Testing verify: {url_verify}")
            verify_res = await client.get(url_verify, headers=headers)
            print(f"Verify Status: {verify_res.status_code}")
            print(f"Verify Response: {verify_res.text}")

            # Test ping Deprecated
            url_dep = "http://127.0.0.1:8080/users/ping"
            print(f"Testing ping Deprecated: {url_dep}")
            ping_dep_res = await client.get(url_dep, headers=headers)
            print(f"Ping Dep Status: {ping_dep_res.status_code}")
            print(f"Ping Dep Response: {ping_dep_res.text}")

            # Test users
            url_users = f"{API_URL}/users/"
            print(f"Fetching users from: {url_users}")
            users_res = await client.get(url_users, headers=headers)

            print(f"Status Code: {users_res.status_code}")
            if users_res.status_code == 200:
                users = users_res.json()
                print(f"Got {len(users)} users.")
                print(users)
            else:
                print(f"Error response: {users_res.text}")

        except Exception as e:
            print(f"Request failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_api())
