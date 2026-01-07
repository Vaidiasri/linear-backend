from fastapi import FastAPI
from .lib.database import engine, Base

# Iska matlab hai models wali file load karo taaki Base ko pata chale kitni tables hain
from . import model
from .routers import user  # 1. Apne naye router folder ko import karo


# 1. App ko initialize karo
app = FastAPI(title="Linear Clone API")
# 2. Ye line sabse important hai! 
# Isse saare signup routes main app se connect ho jayenge.
app.include_router(user.router)


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

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("Server will start anyway, but database operations won't work.")
