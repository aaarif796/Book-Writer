from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import FileResponse

from app.services.book_service import (
    generate_outline,
    write_chapter,
    review_chapter,
    generate_complete_book
)

router = APIRouter(prefix="/books", tags=["Books"])


# -----------------------
# Request Models
# -----------------------

class OutlineRequest(BaseModel):
    book_title: str
    topic: str


class ChapterRequest(BaseModel):
    outline: str
    chapter_number: int


class ReviewRequest(BaseModel):
    chapter_content: str


class GenerateBookRequest(BaseModel):
    book_title: str
    topic: str
    total_chapters: int = 5


# -----------------------
# Response Models
# -----------------------

class OutlineResponse(BaseModel):
    outline: str
    metadata: dict


class ChapterResponse(BaseModel):
    chapter: str
    metadata: dict


class ReviewResponse(BaseModel):
    reviewed_chapter: str
    metadata: dict


# -----------------------
# Endpoints
# -----------------------

@router.post("/outline", response_model=OutlineResponse)
async def create_outline(request: OutlineRequest):
    try:
        return await generate_outline(request.book_title, request.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chapter", response_model=ChapterResponse)
async def create_chapter(request: ChapterRequest):
    try:
        return await write_chapter(request.outline, request.chapter_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review", response_model=ReviewResponse)
async def review_content(request: ReviewRequest):
    try:
        return await review_chapter(request.chapter_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_book(request: GenerateBookRequest):
    """
    Generate complete book and return PDF file.
    """
    try:
        pdf_path = await generate_complete_book(
            request.book_title,
            request.topic,
            request.total_chapters
        )

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{request.book_title}.pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))