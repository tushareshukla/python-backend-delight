from playwright.async_api import async_playwright
from datetime import datetime
from app.db.mongo_client import get_mongo_collection
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def playwright_scrape_main_and_info_pages(url: str, session_id: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            logger.info(f"[Playwright:Quick] Scraping main page: {url}")
            await page.goto(url, timeout=30000)
            main_text = await page.locator("body").inner_text()

            anchors = await page.eval_on_selector_all("a", "els => els.map(a => a.href)")
            info_links = [link for link in anchors if any(kw in link.lower() for kw in ["about", "contact", "info"])]
            all_pages = [{"url": url, "text": main_text[:15000]}]

            for link in info_links[:5]:
                try:
                    sub_page = await context.new_page()
                    await sub_page.goto(link, timeout=10000)
                    sub_text = await sub_page.locator("body").inner_text()
                    all_pages.append({"url": link, "text": sub_text[:15000]})
                    await sub_page.close()
                except Exception as e:
                    logger.warning(f"[Playwright:Quick] Failed on {link}: {e}")

            await get_mongo_collection("quick_info_and_description").insert_one({
                "session_id": session_id,
                "url": url,
                "scraped_at": datetime.utcnow(),
                "playwright_scrape_response": {"pages": all_pages}
            })
            logger.info(f"[Playwright:Quick] Fallback scrape complete.")

        except Exception as e:
            logger.error(f"[Playwright:Quick] Failed scraping {url}: {e}")
        finally:
            await browser.close()

async def playwright_event_scrape(url: str, session_id: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            logger.info(f"[Playwright:Event] Scraping event info for {url}")
            await page.goto(url, timeout=30000)
            text = await page.locator("body").inner_text()

            await get_mongo_collection("event_info").insert_one({
                "session_id": session_id,
                "url": url,
                "scraped_at": datetime.utcnow(),
                "event_result_fallback": {"text": text[:15000]}
            })

        except Exception as e:
            logger.error(f"[Playwright:Event] Failed scraping {url}: {e}")
        finally:
            await browser.close()

async def playwright_product_scrape(url: str, session_id: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            logger.info(f"[Playwright:Product] Scraping product info for {url}")
            await page.goto(url, timeout=30000)
            text = await page.locator("body").inner_text()

            await get_mongo_collection("product_info").insert_one({
                "session_id": session_id,
                "url": url,
                "scraped_at": datetime.utcnow(),
                "product_result_fallback": {"text": text[:15000]}
            })

        except Exception as e:
            logger.error(f"[Playwright:Product] Failed scraping {url}: {e}")
        finally:
            await browser.close()
