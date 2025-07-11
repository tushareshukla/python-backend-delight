from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.orchestrator.orchestrator import run_task_pipeline
from app.schemas.validate_schema import AgentOutputBatchRequest, TaskRequest, ValidationRequest
from app.services.agent_outputs_service import get_outputs_by_org_and_url, save_agent_outputs
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
    

@router.post("/agent/output", tags=["Agent Output"])
async def save_outputs(payload: AgentOutputBatchRequest):
    try:
        return await save_agent_outputs(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/output", tags=["Agent Output"])
async def fetch_outputs(organization_id: str, company_url: str):
    try:
        print(f"Fetching outputs for org: {organization_id}, url: {company_url}")
        return await get_outputs_by_org_and_url(organization_id, company_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))