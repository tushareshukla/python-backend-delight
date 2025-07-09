from pydantic import BaseModel, HttpUrl

class ValidationRequest(BaseModel):
    url: HttpUrl

class TaskRequest(BaseModel):
    url: HttpUrl
    session_id: str
    task: str
