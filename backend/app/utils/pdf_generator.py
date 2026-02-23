import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def clean_markdown(text: str) -> str:
    """
    Remove markdown elements that break ReportLab.
    """

    # Remove code blocks ```...```
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove inline code `
    text = re.sub(r"`.*?`", "", text)

    # Remove markdown tables (lines starting with |)
    lines = text.split("\n")
    lines = [line for line in lines if not line.strip().startswith("|")]
    text = "\n".join(lines)

    # Remove HTML tags
    text = re.sub(r"<.*?>", "", text)

    return text


def generate_pdf(title: str, content: str, filename: str):

    os.makedirs("generated", exist_ok=True)
    path = f"generated/{filename}"

    doc = SimpleDocTemplate(path)
    elements = []

    styles = getSampleStyleSheet()

    # Clean content first
    content = clean_markdown(content)

    # Add title
    elements.append(Paragraph(title, styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    paragraphs = content.split("\n\n")

    for para in paragraphs:
        clean_para = para.strip()
        if not clean_para:
            continue

        elements.append(Paragraph(clean_para, styles["BodyText"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)

    return path