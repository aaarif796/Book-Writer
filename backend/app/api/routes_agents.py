from fastapi import APIRouter, HTTPException, Request
from app.agents.crew import CrewEngine
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter()
crew = CrewEngine()

class WriteRequest(BaseModel):
    prompt: str

class ReviewRequest(BaseModel):
    text: str

class DesignRequest(BaseModel):
    context: str

@router.post("/write")
async def write_endpoint(req: WriteRequest):
    try:
        result = await crew.execute("write_chapter", {"chapter_content": req.prompt})
        return {"status":"ok", "output": result["output"], "metadata": result}
    except Exception as e:
        logger.exception("Writer error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review")
async def review_endpoint(req: ReviewRequest):
    try:
        result = await crew.execute("review_chapter", {"chapter_content": req.text})
        return {"status":"ok", "output": result["output"], "metadata": result}
    except Exception as e:
        logger.exception("Reviewer error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/design")
async def design_endpoint(req: DesignRequest):
    try:
        # Note: Design task not implemented in new system yet
        return {"status":"error", "message": "Design endpoint not implemented in new architecture"}
    except Exception as e:
        logger.exception("Designer error")
        raise HTTPException(status_code=500, detail=str(e))