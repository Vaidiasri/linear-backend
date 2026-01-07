from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# .env file se environment variables load karo
load_dotenv()

# 1. URL .env file se load karo
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable nahi mila .env file mein")

# 2. Async Engine banao
engine = create_async_engine(DATABASE_URL, echo=True)

# 3. Async Session factory
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 4. Base class models ke liye
Base = declarative_base()


# 5. Dependency injection function (Jo main.py mein use hoga)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()
