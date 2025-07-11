from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
class ValidationRequest(BaseModel):
    url: HttpUrl

class TaskRequest(BaseModel):
    url: HttpUrl
    session_id: str
    task: str
class AgentOutputBatchRequest(BaseModel):
    organization_id: str
    company_url: str
    session_id: str
    task_outputs: Dict[str, Any]

