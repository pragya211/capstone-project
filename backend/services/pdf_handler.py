import fitz  # PyMuPDF
from pathlib import Path
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from the given PDF file.
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"File {pdf_path} not found.")
    
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    doc.close()
    
    return all_text.strip()

def split_into_sections(text: str) -> dict:
    normalized_text = text.replace("\r", "\n")

    # Enhanced patterns: case-insensitive, optional colon, handles various numbering formats
    abstract_pattern = re.compile(r"^\s*\d*\.?\s*\babstract\b[:\s]*", re.IGNORECASE | re.MULTILINE)
    intro_pattern = re.compile(r"^\s*\d*\.?\s*\bintroduction\b[:\s]*", re.IGNORECASE | re.MULTILINE)

    # Enhanced heading patterns for more section types
    next_heading_pattern = re.compile(
        r"^\s*\d*\.?\s*(related work|literature review|background|methodology|methods?|approach|results?|experiments?|evaluation|discussion|analysis|conclusion|conclusions|references|bibliography|acknowledgments?|future work|limitations)\b[:\s]*",
        re.IGNORECASE | re.MULTILINE
    )

    abstract_match = abstract_pattern.search(normalized_text)
    intro_match = intro_pattern.search(normalized_text)

    abstract = ""
    introduction = ""
    main_body = ""

    if abstract_match and intro_match:
        abstract = normalized_text[abstract_match.end():intro_match.start()].strip()

        next_heading_match = next_heading_pattern.search(normalized_text, intro_match.end())
        if next_heading_match:
            introduction = normalized_text[intro_match.end():next_heading_match.start()].strip()
            main_body = normalized_text[next_heading_match.start():].strip()
        else:
            introduction = normalized_text[intro_match.end():].strip()

    elif intro_match:  # No abstract
        next_heading_match = next_heading_pattern.search(normalized_text, intro_match.end())
        if next_heading_match:
            introduction = normalized_text[intro_match.end():next_heading_match.start()].strip()
            main_body = normalized_text[next_heading_match.start():].strip()
        else:
            introduction = normalized_text[intro_match.end():].strip()

    else:  # No headings found
        main_body = normalized_text.strip()

    print({
        "abstract": abstract,  # Debug only first 200 chars
        "introduction": introduction,
        "main_body": main_body
    })

    # Try to extract other sections as well
    methodology = ""
    results = ""
    discussion = ""
    conclusion = ""
    
    # Look for methodology section
    methodology_pattern = re.compile(r"^\s*\d*\.?\s*(?:methodology|methods?|approach)\b[:\s]*", re.IGNORECASE | re.MULTILINE)
    methodology_match = methodology_pattern.search(normalized_text)
    
    # Look for results section
    results_pattern = re.compile(r"^\s*\d*\.?\s*(?:results?|experiments?|evaluation)\b[:\s]*", re.IGNORECASE | re.MULTILINE)
    results_match = results_pattern.search(normalized_text)
    
    # Look for discussion section
    discussion_pattern = re.compile(r"^\s*\d*\.?\s*(?:discussion|analysis)\b[:\s]*", re.IGNORECASE | re.MULTILINE)
    discussion_match = discussion_pattern.search(normalized_text)
    
    # Look for conclusion section
    conclusion_pattern = re.compile(r"^\s*\d*\.?\s*(?:conclusion|conclusions)\b[:\s]*", re.IGNORECASE | re.MULTILINE)
    conclusion_match = conclusion_pattern.search(normalized_text)
    
    # Extract sections based on found matches
    if methodology_match:
        next_match = results_match or discussion_match or conclusion_match
        if next_match:
            methodology = normalized_text[methodology_match.end():next_match.start()].strip()
        else:
            methodology = normalized_text[methodology_match.end():].strip()
    
    if results_match:
        next_match = discussion_match or conclusion_match
        if next_match:
            results = normalized_text[results_match.end():next_match.start()].strip()
        else:
            results = normalized_text[results_match.end():].strip()
    
    if discussion_match:
        next_match = conclusion_match
        if next_match:
            discussion = normalized_text[discussion_match.end():next_match.start()].strip()
        else:
            discussion = normalized_text[discussion_match.end():].strip()
    
    if conclusion_match:
        conclusion = normalized_text[conclusion_match.end():].strip()

    return {
        "abstract": abstract,
        "introduction": introduction,
        "methodology": methodology,
        "results": results,
        "discussion": discussion,
        "conclusion": conclusion,
        "main_body": main_body
    }
