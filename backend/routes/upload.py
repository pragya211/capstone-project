from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import fitz

from backend.services.pdf_handler import extract_text_from_pdf, split_into_sections
from backend.services.pdf_handler import extract_text_from_pdf
from backend.services.section_segmenter import extract_layout_sections

# Step 1: Save uploaded PDF
# Step 2: Call structured extraction
#sections = extract_layout_sections("path/to/uploaded.pdf")


router = APIRouter()

UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads a PDF file and extracts text section-wise."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_path = UPLOAD_DIR / file.filename
    
    # Save uploaded file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Extract full text
        extracted_text = extract_text_from_pdf(str(file_path))
        
        # Split into sections
        sections = split_into_sections(extracted_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    return JSONResponse(content={
        "filename": file.filename,
        "sections": sections
    })

# def extract_text_sections(file_bytes):
#     doc = fitz.open(stream=file_bytes, filetype="pdf")
#     abstract, intro, main_body = "", "", ""
#     current_section = "main_body"

#     for page in doc:
#         text = page.get_text()
#         for line in text.split("\n"):
#             if "abstract" in line.lower():
#                 current_section = "abstract"
#                 continue
#             elif "introduction" in line.lower():
#                 current_section = "introduction"
#                 continue

#             if current_section == "abstract":
#                 abstract += line + " "
#             elif current_section == "introduction":
#                 intro += line + " "
#             else:
#                 main_body += line + " "

#     return {
#         "abstract": abstract.strip(),
#         "introduction": intro.strip(),
#         "main_body": main_body.strip()
#     }

