# backend/routes/headings_route.py
from fastapi import APIRouter, UploadFile, File
import shutil
from pathlib import Path
from backend.routes.detect_headings import extract_headings_from_pdf

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/extract-headings")
async def extract_headings(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    sections = extract_headings_from_pdf(str(file_path))
    return {"sections": sections}

# DEBUG: print what’s being returned
    print("Extracted sections:", sections)

    # Ensure the frontend receives something even if empty
    response = {
        "abstract": sections.get("abstract", "No abstract found"),
        "introduction": sections.get("introduction", "No introduction found"),
        "main_body": sections.get("main_body", "No main body text found")
    }

    print("Response sent to frontend:", response)  # DEBUG

    return response