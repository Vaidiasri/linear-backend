import asyncio
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lib.database import AsyncSessionLocal
from app import crud


async def list_users():
    try:
        async with AsyncSessionLocal() as session:
            print("Checking users in database...")
            users = await crud.user.get_multi(session)
            print(f"Found {len(users)} users.")
            for user in users:
                print(f"ID: {user.id}, Email: {user.email}, Name: {user.full_name}")
    except Exception as e:
        print(f"Error listing users: {e}")


if __name__ == "__main__":
    asyncio.run(list_users())
