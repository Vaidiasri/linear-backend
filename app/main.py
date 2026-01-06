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
    # Ye line database mein tables create karti hai agar wo nahi hain
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created!")