from fastapi import FastAPI
from app.api.v1 import validate_routes

app = FastAPI(title="LangChain Scraper API")

# ✅ Mount your router
app.include_router(validate_routes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "LangChain Scraper API Ready"}
