import asyncio
import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path to resolve 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lib.database import AsyncSessionLocal


async def test_db():
    print("Testing DB connection...")
    try:
        async with AsyncSessionLocal() as session:
            print("Session opened.")
            result = await session.execute(text("SELECT 1"))
            print(f"Query result: {result.scalar()}")

            # Now try importing User model and querying count
            from app.model.user import User
            from sqlalchemy import select, func

            print("Querying User count...")
            result = await session.execute(select(func.count()).select_from(User))
            count = result.scalar()
            print(f"User count: {count}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_db())
