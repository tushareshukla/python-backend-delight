from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.validate_schema import ValidationRequest
from app.services.validator import validate_external_url

router = APIRouter()

@router.post("/validate-url", tags=["Validation"])
async def validate_url(payload: ValidationRequest, background_tasks: BackgroundTasks):
    try:
        return await validate_external_url(str(payload.url), background_tasks)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
