import httpx
import logging
from datetime import datetime
from app.db.mongo_client import get_mongo_collection
from app.config.config import COLLY_MICROSERVICE_BASE_URL
from app.services.playwright_scrapers import (
    playwright_scrape_main_and_info_pages,
    playwright_event_scrape,
    playwright_product_scrape
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def trigger_quick_scrape(url: str, session_id: str):
    endpoint = f"{COLLY_MICROSERVICE_BASE_URL}/quick-scrape"
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            logger.info(f"[QuickScrape] Calling: {endpoint}")
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()

            if not result.get("pages") or not any(p.get("text") for p in result["pages"]):
                logger.warning(f"[QuickScrape] Empty response. Falling back to Playwright.")
                await playwright_scrape_main_and_info_pages(url, session_id)
            else:
                await get_mongo_collection("quick_info_and_description").insert_one({
                    "session_id": session_id,
                    "url": url,
                    "scraped_at": datetime.utcnow(),
                    "scrape_result": result
                })
                logger.info(f"[QuickScrape] Stored quick scrape result.")
        except Exception as e:
            logger.error(f"[QuickScrape] Error: {e}")

async def trigger_event_scrape(url: str, session_id: str):
    endpoint = f"{COLLY_MICROSERVICE_BASE_URL}/event-scrape"
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            logger.info(f"[EventScrape] Calling: {endpoint}")
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()

            # ✅ Trigger Playwright if response is null or empty dict
            if not result or result is None or result == {}:
                logger.warning(f"[EventScrape] Null or empty response. Fallback to Playwright.")
                await playwright_event_scrape(url, session_id)
            else:
                await get_mongo_collection("event_info").insert_one({
                    "session_id": session_id,
                    "url": url,
                    "scraped_at": datetime.utcnow(),
                    "event_result": result
                })
                logger.info(f"[EventScrape] Stored event result.")
        except Exception as e:
            logger.error(f"[EventScrape] Error: {e}")


async def trigger_product_scrape(url: str, session_id: str):
    endpoint = f"{COLLY_MICROSERVICE_BASE_URL}/product-scrape"
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            logger.info(f"[ProductScrape] Calling: {endpoint}")
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()

            # ✅ Trigger Playwright only if `pages` is explicitly null
            if result.get("pages") is None:
                logger.warning(f"[ProductScrape] pages == null. Fallback to Playwright.")
                await playwright_product_scrape(url, session_id)
            else:
                await get_mongo_collection("product_info").insert_one({
                    "session_id": session_id,
                    "url": url,
                    "scraped_at": datetime.utcnow(),
                    "product_result": result
                })
                logger.info(f"[ProductScrape] Stored product result.")
        except Exception as e:
            logger.error(f"[ProductScrape] Error: {e}")

