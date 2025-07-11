from fastapi import FastAPI
from app.api.v1 import validate_routes
from fastapi.responses import PlainTextResponse

app = FastAPI(title="LangChain Scraper API")

# ✅ Mount your router
app.include_router(validate_routes.router, prefix="/api-py/v1/onBoarding")

@app.get("/")
async def root():
    return {"message": "LangChain Scraper API Ready"}
@app.get("/health", response_class=PlainTextResponse)
async def healthcheck():
    return "OK"