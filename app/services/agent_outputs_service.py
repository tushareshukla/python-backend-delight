# agent_outputs_service.py
from app.db.mongo_client import get_mongo_collection
from datetime import datetime
from bson import ObjectId

COLLECTION_NAME = "organization_agent_outputs"

from app.db.mongo_client import get_mongo_collection
from datetime import datetime
from bson import ObjectId

COLLECTION_NAME = "organization_agent_outputs"

async def save_agent_outputs(payload):
    collection = get_mongo_collection(COLLECTION_NAME)
    results = []

    for task, result in payload.task_outputs.items():
        filter_query = {
            "organization_id": ObjectId(payload.organization_id),
            "company_url": payload.company_url,
            "session_id": payload.session_id,
            "task_name": task
        }

        update_doc = {
            "$set": {
                "output": result,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        }

        op_result = await collection.update_one(filter_query, update_doc, upsert=True)
        results.append({
            "task": task,
            "matched": op_result.matched_count,
            "modified": op_result.modified_count,
            "upserted_id": str(op_result.upserted_id) if op_result.upserted_id else None
        })

    return {"status": "success", "message": "Upsert complete", "details": results}



async def get_outputs_by_org_and_url(organization_id: str, company_url: str):
    collection = get_mongo_collection(COLLECTION_NAME)

    docs = await collection.find({
        "organization_id": ObjectId(organization_id),
        "company_url": company_url
    }).to_list(length=100)

    return {"status": "success", "results": docs}
