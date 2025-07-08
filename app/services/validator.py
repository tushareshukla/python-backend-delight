import httpx
import uuid
from datetime import datetime
from app.db.mongo_client import get_mongo_collection

COLLY_VALIDATE_URL = "https://colly-delight.patchup.health/website-validate?url="

async def validate_external_url(url: str) -> dict:
    session_id = str(uuid.uuid4())
    full_url = f"{COLLY_VALIDATE_URL}{url}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(full_url)
        response.raise_for_status()
        result = response.json()

    # Save to Mongo
    doc = {
        "session_id": session_id,
        "url": url,
        "validated_at": datetime.utcnow(),
        "result": result
    }
    await get_mongo_collection("url_validations").insert_one(doc)

    return {"session_id": session_id, "result": result}
