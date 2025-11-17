from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
from pathlib import Path
from backend.routes.detect_headings import extract_headings_from_pdf
from backend.services.advanced_pdf_parser import AdvancedPDFParser

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/enhanced-extract")
async def enhanced_basic_extract(file: UploadFile = File(...)):
    """Enhanced basic extraction with optional advanced features"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract basic sections
        sections = extract_headings_from_pdf(str(file_path))
        
        # Also extract some advanced features for enhanced UI
        parser = AdvancedPDFParser()
        layout_data = parser.extract_text_with_layout(str(file_path))
        
        # Get basic citation count and keyword extraction
        citations = parser.extract_citations(layout_data['full_text'])
        keywords = parser.extract_keywords(layout_data['full_text'])
        
        # Clean up uploaded file
        file_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "sections": sections,
            "enhanced_data": {
                "total_citations": len(citations),
                "top_keywords": keywords[:10],  # Top 10 keywords
                "total_pages": layout_data['total_pages'],
                "sample_citations": [
                    {
                        'text': citation.text,
                        'citation_type': citation.citation_type,
                        'authors': citation.authors,
                        'year': citation.year
                    }
                    for citation in citations[:5]  # First 5 citations
                ]
            }
        }
        
    except Exception as e:
        # Clean up uploaded file on error
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        
        raise HTTPException(status_code=500, detail=f"Enhanced extraction failed: {str(e)}")
