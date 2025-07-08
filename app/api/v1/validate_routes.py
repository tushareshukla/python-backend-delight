from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.validate_schema import ValidationRequest, OrgExtractionRequest
from app.services.validator import validate_external_url

router = APIRouter()

@router.post("/validate-url", tags=["Validation"])
async def validate_url(payload: ValidationRequest, background_tasks: BackgroundTasks):
    try:
        return await validate_external_url(str(payload.url), background_tasks)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
@router.post("/extract-organization-info")
async def extract_org_info(request: OrgExtractionRequest):
    try:
        return await extract_organization_info(request.url, request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))