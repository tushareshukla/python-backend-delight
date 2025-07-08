from fastapi import APIRouter, HTTPException
from app.schemas.validate_schema import ValidationRequest
from app.services.validator import validate_external_url

router = APIRouter()

@router.post("/validate-url", tags=["Validation"])
async def validate_url(payload: ValidationRequest):
    try:
        return await validate_external_url(str(payload.url))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
