from fastapi import APIRouter, HTTPException, Request
from app.agents.crew_setup import CrewManager
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter()
crew = CrewManager.load_from_folder()

class WriteRequest(BaseModel):
    prompt: str

class ReviewRequest(BaseModel):
    text: str

class DesignRequest(BaseModel):
    context: str

@router.post("/write")
async def write_endpoint(req: WriteRequest):
    try:
        out = await crew.run_agent_async("writer", prompt=req.prompt)
        return {"status":"ok", "output": out}
    except Exception as e:
        logger.exception("Writer error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review")
async def review_endpoint(req: ReviewRequest):
    try:
        out = await crew.run_agent_async("reviewer", text=req.text)
        return {"status":"ok", "output": out}
    except Exception as e:
        logger.exception("Reviewer error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/design")
async def design_endpoint(req: DesignRequest):
    try:
        out = await crew.run_agent_async("designer", context=req.context)
        return {"status":"ok", "output": out}
    except Exception as e:
        logger.exception("Designer error")
        raise HTTPException(status_code=500, detail=str(e))