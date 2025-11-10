from app.utils.file_manager import save_docx, save_pdf
from app.agents.crew_setup import run_writer_agent

async def generate_book(title: str, topic: str):
    # Call your CrewAI writer agent
    content = await run_writer_agent(title=title, topic=topic)

    # Save as both DOCX and PDF
    docx_path = save_docx(title, content)
    pdf_path = save_pdf(title, content)

    return {
        "title": title,
        "topic": topic,
        "docx_file": docx_path,
        "pdf_file": pdf_path,
    }
