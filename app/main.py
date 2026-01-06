from fastapi import FastAPI
from .database import engine, Base

# Iska matlab hai models wali file load karo taaki Base ko pata chale kitni tables hain
from . import model

# 1. App ko initialize karo
app = FastAPI(title="Linear Clone API")


# 2. Ek test route banao (Browser pe dikhega)
@app.get("/")
async def root():
    return {"message": "Bhai, Linear Clone ka server ekdum mast chal raha hai!"}


# 3. Ek aur route banao health check ke liye
@app.get("/health")
async def health_check():
    return {"status": "online", "database": "checking..."}


@app.on_event("startup")
async def startup():
    try:
        from . import model  # Import ko yahan andar le aao

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("Server will start anyway, but database operations won't work.")
