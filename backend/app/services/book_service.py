from typing import Dict, Any
from app.agents.crew import CrewEngine
from app.utils.pdf_generator import generate_pdf
from uuid import uuid4


crew_engine = CrewEngine()

async def generate_outline(book_title: str, topic: str) -> Dict[str, Any]:
    """Generate a book outline."""
    inputs = {
        "book_title": book_title,
        "topic": topic
    }
    result = await crew_engine.execute("generate_outline", inputs)
    return {
        "outline": result["output"],
        "metadata": {
            "task": result["task"],
            "agent": result["agent"],
            "model": result["model"]
        }
    }

async def write_chapter(outline: str, chapter_number: int) -> Dict[str, Any]:
    """Write a chapter based on outline."""
    inputs = {
        "outline": outline,
        "chapter_number": chapter_number
    }
    result = await crew_engine.execute("write_chapter", inputs)
    return {
        "chapter": result["output"],
        "metadata": {
            "task": result["task"],
            "agent": result["agent"],
            "model": result["model"]
        }
    }

async def review_chapter(chapter_content: str) -> Dict[str, Any]:
    """Review and improve chapter content."""
    inputs = {
        "chapter_content": chapter_content
    }
    result = await crew_engine.execute("review_chapter", inputs)
    return {
        "reviewed_chapter": result["output"],
        "metadata": {
            "task": result["task"],
            "agent": result["agent"],
            "model": result["model"]
        }
    }


async def generate_complete_book(book_title: str, topic: str, total_chapters: int):
    """
    Generate full book: outline → chapters → compile → PDF
    """

    # 1️⃣ Generate outline
    outline_result = await generate_outline(book_title, topic)
    outline_text = outline_result["outline"]

    # Simple chapter splitting (adjust if structured)
    chapter_titles = [
        line.strip()
        for line in outline_text.split("\n")
        if line.strip()
    ]

    book_content = f"# {book_title}\n\n"

    # 2️⃣ Generate each chapter
    for i in range(min(total_chapters, len(chapter_titles))):

        chapter_result = await write_chapter(outline_text, i + 1)
        chapter_text = chapter_result["chapter"]

        # 3️⃣ Review chapter
        review_result = await review_chapter(chapter_text)
        reviewed_text = review_result["reviewed_chapter"]

        book_content += f"\n\n## {chapter_titles[i]}\n\n"
        book_content += reviewed_text

    # 4️⃣ Generate PDF
    filename = f"{uuid4()}.pdf"
    pdf_path = generate_pdf(book_title, book_content, filename)

    return pdf_path