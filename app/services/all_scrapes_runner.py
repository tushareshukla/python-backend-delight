# app/services/all_scrapes_runner.py
import asyncio
from app.services.background_tasks import (
    trigger_quick_scrape,
    trigger_event_scrape,
    trigger_product_scrape,
)

async def run_all_scrapes_parallel(url: str, session_id: str):
    await asyncio.gather(
        trigger_quick_scrape(url, session_id),
        trigger_event_scrape(url, session_id),
        trigger_product_scrape(url, session_id)
    )
