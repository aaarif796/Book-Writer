import os
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

DOCS_DIR = "output/docs"
PDF_DIR = "output/pdfs"

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

def save_docx(book_title: str, content: str) -> str:
    path = os.path.join(DOCS_DIR, f"{book_title}.docx")
    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    doc.save(path)
    return path

def save_pdf(book_title: str, content: str) -> str:
    path = os.path.join(PDF_DIR, f"{book_title}.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)
    story = [Paragraph(line, styles["Normal"]) for line in content.split("\n")]
    doc.build(story)
    return path
