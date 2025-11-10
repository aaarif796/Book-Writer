from fastapi import APIRouter
from app.services.book_service import generate_book

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/generate")
async def generate_book_route(title: str, topic: str):
    return await generate_book(title, topic)
