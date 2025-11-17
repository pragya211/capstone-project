from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
from pathlib import Path
from backend.services.advanced_pdf_parser import AdvancedPDFParser
from backend.services.figure_table_explainer import FigureTableExplainer
import json
import re

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/advanced-extract")
async def advanced_extract(file: UploadFile = File(...)):
    """Extract text with advanced processing including citations, figures, and math content"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize advanced parser and explainer
        parser = AdvancedPDFParser()
        explainer = FigureTableExplainer()
        
        # Parse PDF with advanced features
        result = parser.parse_pdf_advanced(str(file_path))
        
        print(f"DEBUG: Found {len(result['figures_tables'])} figures/tables")
        for idx, ft in enumerate(result['figures_tables'][:3]):  # Log first 3
            print(f"  [{idx}] {ft.label} - Has image: {bool(ft.image_base64)} - Image size: {len(ft.image_base64) if ft.image_base64 else 0}")
        
        # Generate AI explanations for figures and tables
        figures_tables_with_explanations = explainer.generate_explanations(result['figures_tables'])
        
        print(f"DEBUG: Generated explanations for {len(figures_tables_with_explanations)} items")
        for idx, ft in enumerate(figures_tables_with_explanations[:3]):
            print(f"  [{idx}] {ft.label} - Has explanation: {bool(ft.ai_explanation)} - Has image: {bool(ft.image_base64)}")
        
        # Convert dataclasses to dictionaries for JSON serialization
        reference_map = result.get('references', {})

        processed_result = {
            'sections': result['sections'],
            'citations': [
                {
                    'text': citation.text,
                    'position': citation.position,
                    'citation_type': citation.citation_type,
                    'authors': citation.authors,
                    'year': citation.year,
                    'title': citation.title,
                    'reference_numbers': numbers if citation.citation_type == 'numbered' else [],
                    'resolved_references': [
                        reference_map[num]
                        for num in numbers
                        if num in reference_map
                    ] if citation.citation_type == 'numbered' else []
                }
                for citation in result['citations']
                for numbers in [[
                    int(num)
                    for num in re.findall(r'\d+', citation.text)
                    if num.isdigit()
                ]]
            ],
            'figures_tables': [
                {
                    'caption': ft.caption,
                    'label': ft.label,
                    'content_type': ft.content_type,
                    'position': ft.position,
                    'page_number': ft.page_number,
                    'ai_explanation': ft.ai_explanation,
                    'image_base64': ft.image_base64
                }
                for ft in figures_tables_with_explanations
            ],
            'keywords': result['keywords'],
            'metadata': result['metadata'],
            'references': reference_map
        }
        
        # Clean up uploaded file
        file_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "data": processed_result
        }
        
    except Exception as e:
        # Clean up uploaded file on error
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        
        raise HTTPException(status_code=500, detail=f"Advanced extraction failed: {str(e)}")

@router.post("/extract-citations-only")
async def extract_citations_only(file: UploadFile = File(...)):
    """Extract only citations from the PDF"""
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        parser = AdvancedPDFParser()
        layout_data = parser.extract_text_with_layout(str(file_path))
        citations = parser.extract_citations(layout_data['full_text'])
        
        # Clean up
        file_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "citations": [
                {
                    'text': citation.text,
                    'citation_type': citation.citation_type,
                    'authors': citation.authors,
                    'year': citation.year
                }
                for citation in citations
            ],
            "total_citations": len(citations)
        }
        
    except Exception as e:
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Citation extraction failed: {str(e)}")

@router.post("/extract-figures-tables")
async def extract_figures_tables(file: UploadFile = File(...)):
    """Extract figures and tables with captions"""
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        parser = AdvancedPDFParser()
        layout_data = parser.extract_text_with_layout(str(file_path))
        figures_tables = parser.extract_figures_tables(layout_data['full_text'], layout_data['pages'])
        
        # Clean up
        file_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "figures_tables": [
                {
                    'caption': ft.caption,
                    'label': ft.label,
                    'content_type': ft.content_type,
                    'page_number': ft.page_number
                }
                for ft in figures_tables
            ],
            "total_figures": len([ft for ft in figures_tables if ft.content_type == 'figure']),
            "total_tables": len([ft for ft in figures_tables if ft.content_type == 'table'])
        }
        
    except Exception as e:
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Figure/table extraction failed: {str(e)}")

@router.post("/extract-mathematical-content")
async def extract_mathematical_content(file: UploadFile = File(...)):
    """Extract mathematical content and equations"""
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        parser = AdvancedPDFParser()
        layout_data = parser.extract_text_with_layout(str(file_path))
        math_content = parser.extract_mathematical_content(layout_data['full_text'], layout_data['pages'])
        # Enrich with context/summary/impact similar to advanced extract
        for m in math_content:
            topic = parser._infer_topic_from_headings(m.position, layout_data['pages'], layout_data.get('headings', []))
            nearby = parser._get_nearby_text(layout_data['full_text'], m.position)
            meaning, impact = parser._summarize_equation(m.equation, nearby)
            m.context = topic
            m.summary = meaning
            m.impact = impact
        
        # Clean up
        file_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "mathematical_content": [
                {
                    'equation': math.equation,
                    'equation_type': math.equation_type,
                    'page_number': math.page_number,
                    'context': math.context,
                    'summary': math.summary,
                    'impact': math.impact
                }
                for math in math_content
            ],
            "total_equations": len(math_content)
        }
        
    except Exception as e:
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Mathematical content extraction failed: {str(e)}")
