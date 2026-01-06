from fastapi import FastAPI

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