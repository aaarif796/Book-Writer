from fastapi import APIRouter, HTTPException
from app.workflows.workflow_runner import WorkflowRunner
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter()
runner = WorkflowRunner()

class FlowRequest(BaseModel):
    prompt: str

@router.post("/run_book_flow")
async def run_book_flow(req: FlowRequest):
    try:
        result = await runner.run_book_workflow_async(req.prompt)
        return {"status":"ok", "result": result}
    except Exception as e:
        logger.exception("Workflow error")
        raise HTTPException(status_code=500, detail=str(e))