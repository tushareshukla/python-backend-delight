import os
from typing import Union, Any, Mapping

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:secret@localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "delightloop")

_client = AsyncIOMotorClient(MONGO_URI)
_db = _client[MONGO_DB_NAME]

def get_mongo_collection(collection_name: str) -> AsyncIOMotorCollection[Union[Mapping[str, Any], Any]]:
    return _db[collection_name]
