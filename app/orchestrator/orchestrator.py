import os
from datetime import datetime
from langchain_core.output_parsers import StrOutputParser
from app.agents.company_info_agent import get_company_info_chain
from app.agents.customer_personas_agent import get_customer_personas_chain
from app.agents.product_agent import get_product_details_chain
from app.agents.event_agent import get_event_details_chain
from app.agents.use_case_agent import get_use_cases_chain

from app.db.mongo_client import get_mongo_collection
from app.utils.helper import wait_for_mongo_doc

AGENT_MAPPING = {
    "get_company_info": get_company_info_chain,
    "get_customer_personas": get_customer_personas_chain,
    "get_product_and_service_details": get_product_details_chain,
    "get_event_details": get_event_details_chain,
    "get_use_cases": get_use_cases_chain
}

COLLECTION_MAPPING = {
    "get_company_info": "onboarding_organisation_details",
    "get_customer_personas": "customer_personas",
    "get_product_and_service_details": "product_service_details",
    "get_event_details": "event_details",
    "get_use_cases": "product_use_cases"
}

SCRAPE_COLLECTION_MAPPING = {
    "get_company_info": "quick_info_and_description",
    "get_customer_personas": "quick_info_and_description",
    "get_product_and_service_details": "product_info",
    "get_event_details": "event_info",
    "get_use_cases": "quick_info_and_description"
}

async def fetch_scraped_doc(task: str, url: str, session_id: str):
    if task not in SCRAPE_COLLECTION_MAPPING:
        raise ValueError(f"Unsupported task for fetching scraped data: {task}")

    collection_name = SCRAPE_COLLECTION_MAPPING[task]
    return await wait_for_mongo_doc(
        collection_name=collection_name,
        url=url,
        session_id=session_id
    )

async def run_task_pipeline(url: str, session_id: str, task: str) -> dict:
    # Step 1: Fetch scraped content
    scraped_doc = await fetch_scraped_doc(task, url, session_id)

    if not scraped_doc:
        raise Exception("Document not found after multiple retries.")

    # Step 2: Extract text content
    text_blocks = []
    for source_key in ["scrape_result", "playwright_scrape_response"]:
        if source_key in scraped_doc and scraped_doc[source_key].get("pages"):
            text_blocks.extend(page.get("text", "") for page in scraped_doc[source_key]["pages"])
            break

    combined_text = "\n\n".join(text_blocks)[:15000]

    # # Step 3: Append fallback hint if needed
    # if len(combined_text) < 1000 and task == "get_company_info":
    #     combined_text += "\n\n[TOOL] Use SerpAPI to enrich if data insufficient."

    # Step 4: Validate and run agent chain
    if task not in AGENT_MAPPING:
        raise ValueError(f"Unsupported task: {task}")

    chain_fn = AGENT_MAPPING[task]
    chain = chain_fn()
    result = chain.invoke({"input": combined_text})

    # Step 5: Store results in database
    collection = get_mongo_collection(COLLECTION_MAPPING[task])
    output_doc = {
        "session_id": session_id,
        "url": url,
        "task": task,
        "result": result,
        "created_at": datetime.utcnow()
    }
    await collection.insert_one(output_doc)

    # Step 6: Return response
    return {
        "session_id": session_id,
        "url": url,
        "task": task,
        "output": result
    }
