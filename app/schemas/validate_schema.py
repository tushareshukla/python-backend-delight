from pydantic import BaseModel, HttpUrl

class ValidationRequest(BaseModel):
    url: HttpUrl
