from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.orchestrator.orchestrator import run_task_pipeline
from app.schemas.validate_schema import TaskRequest, ValidationRequest
from app.services.validator import validate_external_url

router = APIRouter()

@router.post("/validate-url", tags=["Validation"])
async def validate_url(payload: ValidationRequest, background_tasks: BackgroundTasks):
    try:
        return await validate_external_url(str(payload.url), background_tasks)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/agent/run")
async def run_agent(request: TaskRequest):
    try:
        result = await run_task_pipeline(
            url=str(request.url),
            session_id=request.session_id,
            task=request.task
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))