from app.db.mongo_client import get_mongo_collection
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any

COLLECTION_NAME = "organization_agent_outputs"

def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB-specific types to JSON-serializable format.
    """
    doc["_id"] = str(doc.get("_id", ""))
    
    if "organization_id" in doc and isinstance(doc["organization_id"], ObjectId):
        doc["organization_id"] = str(doc["organization_id"])

    if "created_at" in doc and hasattr(doc["created_at"], "isoformat"):
        doc["created_at"] = doc["created_at"].isoformat()

    if "updated_at" in doc and hasattr(doc["updated_at"], "isoformat"):
        doc["updated_at"] = doc["updated_at"].isoformat()

    return doc


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

    return {
        "status": "success",
        "message": "Upsert complete",
        "details": results
    }


async def get_outputs_by_org_and_url(organization_id: str, company_url: str):
    collection = get_mongo_collection(COLLECTION_NAME)

    query = {
        "organization_id": ObjectId(organization_id),
        "company_url": company_url
    }

    cursor = collection.find(query)
    docs = await cursor.to_list(length=100)

    return [serialize_doc(doc) for doc in docs] # type: ignore
