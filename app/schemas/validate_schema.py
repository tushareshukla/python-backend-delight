from pydantic import BaseModel, HttpUrl

class ValidationRequest(BaseModel):
    url: HttpUrl

class OrgExtractionRequest(BaseModel):
    url: str
    session_id: str
