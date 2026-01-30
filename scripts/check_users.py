import asyncio
import sys
import os
import traceback

# Add the parent directory to sys.path to resolve 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lib.database import AsyncSessionLocal
from app.services.user import UserService
from app import crud


async def check_users():
    print("Starting user check...")
    try:
        async with AsyncSessionLocal() as session:
            print("Session created. Fetching users...")
            users = await UserService.get_all(session)
            print(f"Found {len(users)} users.")
            for user in users:
                print(
                    f"User - ID: {user.id}, Email: {user.email}, Full Name: {user.full_name}, Role: {user.role}"
                )

            if len(users) == 0:
                print("No users found in database!")
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_users())
