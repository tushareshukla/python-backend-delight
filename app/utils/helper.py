import asyncio

from app.db.mongo_client import get_mongo_collection


async def wait_for_mongo_doc(collection_name: str, url: str, session_id: str, max_retries: int = 15, delay: float = 2.0):
    collection = get_mongo_collection(collection_name)

    for attempt in range(max_retries):
        doc = await collection.find_one({
            "url": url,
            "session_id": session_id
        })

        if doc:
            return doc

        print(f"[{collection_name}] Attempt {attempt + 1}/{max_retries}: Not found, retrying in {delay}s...")
        await asyncio.sleep(delay)

    return None  # Or raise an exception if you prefer
