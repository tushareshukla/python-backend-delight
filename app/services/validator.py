import httpx
import uuid
import logging
from datetime import datetime
from fastapi import BackgroundTasks
from app.db.mongo_client import get_mongo_collection
from app.config.config import COLLY_MICROSERVICE_BASE_URL
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Optional: configure logging handler if running standalone
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)


# 🔹 Fallback Playwright scraper if /quick-scrape returns no content
async def playwright_scrape_main_and_info_pages(url: str, session_id: str, retries: int = 2):
    for attempt in range(retries):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                logger.info(f"[Playwright] Attempting to scrape {url} [Attempt {attempt+1}]")
                await page.goto(url, timeout=30000)
                main_text = await page.locator("body").inner_text()

                anchors = await page.eval_on_selector_all("a", "els => els.map(a => a.href)")
                filtered_links = [link for link in anchors if any(kw in link.lower() for kw in ["about", "contact", "info"])]

                all_scraped_pages = [{"url": url, "text": main_text[:15000]}]

                for link in filtered_links[:5]:
                    try:
                        sub_page = await context.new_page()
                        await sub_page.goto(link, timeout=10000)
                        sub_text = await sub_page.locator("body").inner_text()
                        all_scraped_pages.append({"url": link, "text": sub_text[:15000]})
                        await sub_page.close()
                    except Exception as sub_err:
                        logger.warning(f"[Playwright] Failed to scrape sub-page {link}: {sub_err}")

                await get_mongo_collection("quick_info_and_description").insert_one({
                    "session_id": session_id,
                    "url": url,
                    "scraped_at": datetime.utcnow(),
                    "playwright_scrape_response": {"pages": all_scraped_pages}
                })
                logger.info(f"[Playwright] Successfully scraped and stored content for {url}")
                break  # Success, exit retry loop

            except PlaywrightTimeout as e:
                logger.error(f"[Playwright] Timeout error for {url}: {e}")
            except Exception as e:
                logger.error(f"[Playwright] General failure scraping {url}: {e}")
            finally:
                await browser.close()


# 🔹 Background task: Call /quick-scrape and save result with session_id
async def trigger_quick_scrape(url: str, session_id: str):
    quick_scrape_url = f"{COLLY_MICROSERVICE_BASE_URL}/quick-scrape"
    payload = {"url": url}
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            logger.info(f"[QuickScrape] Sending request to {quick_scrape_url} for {url}")
            response = await client.post(quick_scrape_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            if not result.get("pages") or not result["pages"]:
                logger.warning(f"[QuickScrape] No 'pages' in response for {url}, falling back to Playwright")
                await playwright_scrape_main_and_info_pages(url, session_id)
            else:
                doc = {
                    "session_id": session_id,
                    "url": url,
                    "scraped_at": datetime.utcnow(),
                    "scrape_result": result
                }
                await get_mongo_collection("quick_info_and_description").insert_one(doc)
                logger.info(f"[QuickScrape] Stored result for {url}")

        except Exception as e:
            logger.error(f"[QuickScrape] Failed for {url}: {e}")


# 🔹 Main validation logic: Call /website-validate, store result, and trigger scrape
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

    background_tasks.add_task(trigger_quick_scrape, url, session_id)

    return {"session_id": session_id, "result": result}
