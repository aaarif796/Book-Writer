from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from app.services.book_service import (
    generate_outline,
    write_chapter,
    review_chapter,
    generate_complete_book
)
from app.api.routes_workflows import run_book_flow  # if exists


app = FastAPI(title="Book Writer MCP")

mcp = FastApiMCP(app)
# ----------------------------
# Book Tools
# ----------------------------

@mcp.tool()
async def create_outline(book_title: str, topic: str):
    """Generate a structured book outline."""
    return await generate_outline(book_title, topic)


@mcp.tool()
async def write_chapter(outline: str, chapter_number: int):
    """Generate a chapter from outline."""
    return await write_chapter(outline, chapter_number)


@mcp.tool()
async def review_content(chapter_content: str):
    """Review and improve chapter content."""
    return await review_chapter(chapter_content)


@mcp.tool()
async def generate_book(book_title: str, topic: str, total_chapters: int):
    """Generate complete book and return PDF path."""
    return await generate_complete_book(book_title, topic, total_chapters)


# ----------------------------
# Workflow Tool
# ----------------------------

@mcp.tool()
async def run_book_workflow(book_title: str, topic: str, total_chapters: int):
    """Run full book workflow pipeline."""
    return await run_book_flow(book_title, topic, total_chapters)