from playwright.async_api import async_playwright
from datetime import datetime
from app.db.mongo_client import get_mongo_collection
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

QUICK_KEYWORDS = {"about", "about-us", "info", "contact"}
EVENT_KEYWORDS = {"event", "events", "webinar", "conference", "summit", "expo", "forum", "seminar"}
PRODUCT_KEYWORDS = {
    "product", "products", "service", "services",
    "solution", "solutions", "offering", "offerings",
    "platform", "feature", "features", "app", "apps"
}


def filter_links(links, keywords):
    return [link for link in links if any(kw in link.lower() for kw in keywords)]


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
            info_links = filter_links(anchors, QUICK_KEYWORDS)
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
        context = await browser.new_context()
        page = await context.new_page()

        try:
            logger.info(f"[Playwright:Event] Scraping event info for {url}")
            await page.goto(url, timeout=30000)
            anchors = await page.eval_on_selector_all("a", "els => els.map(a => a.href)")
            event_links = filter_links(anchors, EVENT_KEYWORDS)

            event_data = []
            for link in event_links[:5]:
                try:
                    event_page = await context.new_page()
                    await event_page.goto(link, timeout=10000)
                    text = await event_page.locator("body").inner_text()
                    event_data.append({"url": link, "text": text[:15000]})
                    await event_page.close()
                except Exception as e:
                    logger.warning(f"[Playwright:Event] Failed on {link}: {e}")

            await get_mongo_collection("event_info").insert_one({
                "session_id": session_id,
                "url": url,
                "scraped_at": datetime.utcnow(),
                "playwright_scrape_response": {"pages": event_data}
            })

        except Exception as e:
            logger.error(f"[Playwright:Event] Failed scraping {url}: {e}")
        finally:
            await browser.close()


async def playwright_product_scrape(url: str, session_id: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            logger.info(f"[Playwright:Product] Scraping product info for {url}")
            await page.goto(url, timeout=30000)
            anchors = await page.eval_on_selector_all("a", "els => els.map(a => a.href)")
            product_links = filter_links(anchors, PRODUCT_KEYWORDS)

            product_data = []
            for link in product_links[:5]:
                try:
                    product_page = await context.new_page()
                    await product_page.goto(link, timeout=10000)
                    text = await product_page.locator("body").inner_text()
                    product_data.append({"url": link, "text": text[:15000]})
                    await product_page.close()
                except Exception as e:
                    logger.warning(f"[Playwright:Product] Failed on {link}: {e}")

            await get_mongo_collection("product_info").insert_one({
                "session_id": session_id,
                "url": url,
                "scraped_at": datetime.utcnow(),
                "playwright_scrape_response": {"pages": product_data}
            })

        except Exception as e:
            logger.error(f"[Playwright:Product] Failed scraping {url}: {e}")
        finally:
            await browser.close()