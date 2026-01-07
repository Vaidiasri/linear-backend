from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. URL mein asyncpg zaroori hai
DATABASE_URL = "postgresql+asyncpg://postgres:vaibhav123@localhost/linear"

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
