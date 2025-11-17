# backend/routes/detect_headings.py
from backend.services.pdf_handler import extract_text_from_pdf, split_into_sections

def extract_headings_from_pdf(pdf_path: str) -> dict:
    """
    Extracts text from PDF and splits it into Abstract, Introduction, and Main Body.
    """
    text = extract_text_from_pdf(pdf_path)
    sections = split_into_sections(text)
    return sections
