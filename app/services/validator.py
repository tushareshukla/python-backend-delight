import httpx
import uuid
import logging
from datetime import datetime
from fastapi import BackgroundTasks
from app.db.mongo_client import get_mongo_collection
from app.config.config import COLLY_MICROSERVICE_BASE_URL
from app.services.all_scrapes_runner import run_all_scrapes_parallel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

# 🔹 Main validation logic: Call /website-validate, store result, and trigger all scrapers concurrently
async def validate_external_url(url: str, background_tasks: BackgroundTasks) -> dict:
    session_id = str(uuid.uuid4())
    validate_url = f"{COLLY_MICROSERVICE_BASE_URL}/website-validate?url={url}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(validate_url)
        response.raise_for_status()
        result = response.json()

    doc = {
        "session_id": session_id,
        "url": url,
        "validated_at": datetime.utcnow(),
        "result": result
    }
    await get_mongo_collection("url_validations").insert_one(doc)
    logger.info(f"[Validator] Stored validation result for {url}")

    background_tasks.add_task(run_all_scrapes_parallel, url, session_id)

    return {"session_id": session_id, "result": result}