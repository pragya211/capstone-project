from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
from pathlib import Path
from backend.services.advanced_pdf_parser import AdvancedPDFParser
from backend.services.research_assessment import ResearchPaperAssessor
import json
import hashlib

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Simple in-memory cache for assessment results
assessment_cache = {}

def get_or_create_assessment(file_path: str) -> tuple:
    """
    Get assessment from cache or create new one.
    Returns (assessment, score_breakdown)
    """
    # Create hash of file content for caching
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    # Check if assessment exists in cache
    if file_hash in assessment_cache:
        print(f"Using cached assessment for file hash: {file_hash[:8]}...")
        return assessment_cache[file_hash]
    
    # Create new assessment
    print(f"Creating new assessment for file hash: {file_hash[:8]}...")
    parser = AdvancedPDFParser()
    paper_content = parser.parse_pdf_advanced(file_path)
    
    assessor = ResearchPaperAssessor()
    assessment = assessor.assess_research_paper(paper_content)
    score_breakdown = assessor.get_last_score_breakdown()
    
    # Cache the results
    assessment_cache[file_hash] = (assessment, score_breakdown)
    
    # Limit cache size to prevent memory issues
    if len(assessment_cache) > 10:
        # Remove oldest entry (simple FIFO)
        oldest_key = next(iter(assessment_cache))
        del assessment_cache[oldest_key]
    
    return assessment, score_breakdown

class AssessmentRequest(BaseModel):
    """Request model for research paper assessment"""
    paper_content: dict
    assessment_type: str = "comprehensive"  # "comprehensive", "quick", "methodology", "literature"

@router.post("/assess-paper")
async def assess_research_paper(file: UploadFile = File(...)):
    """
    Comprehensive assessment of a research paper to identify missing content and topics.
    
    This endpoint:
    1. Extracts content from the uploaded PDF
    2. Analyzes what's missing from the paper
    3. Provides detailed recommendations for improvement
    4. Gives a completeness score
    """
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get or create assessment (cached)
        assessment, score_breakdown = get_or_create_assessment(str(file_path))
        
        print(f"COMPREHENSIVE - Completeness Score: {assessment.overall_completeness_score}")
        print(f"COMPREHENSIVE - Score Breakdown: {score_breakdown}")
        
        # Convert assessment to JSON-serializable format
        assessment_data = {
            "paper_title": assessment.paper_title,
            "research_field": assessment.research_field,
            "overall_completeness_score": assessment.overall_completeness_score,
            "missing_content": [
                {
                    "category": content.category,
                    "topic": content.topic,
                    "importance": content.importance,
                    "description": content.description,
                    "suggestion": content.suggestion,
                    "related_sections": content.related_sections
                }
                for content in assessment.missing_content
            ],
            "strengths": assessment.strengths,
            "weaknesses": assessment.weaknesses,
            "recommendations": assessment.recommendations,
            "methodology_analysis": assessment.methodology_analysis,
            "literature_review_analysis": assessment.literature_review_analysis,
            "results_analysis": assessment.results_analysis,
            "discussion_analysis": assessment.discussion_analysis,
            "assessment_summary": {
                "total_missing_items": len(assessment.missing_content),
                "critical_missing": len([c for c in assessment.missing_content if c.importance == "Critical"]),
                "important_missing": len([c for c in assessment.missing_content if c.importance == "Important"]),
                "beneficial_missing": len([c for c in assessment.missing_content if c.importance == "Beneficial"])
            },
            "score_breakdown": score_breakdown
        }
        
        # Clean up uploaded file
        file_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "message": "Research paper assessment completed successfully",
            "assessment": assessment_data
        }
        
    except Exception as e:
        # Clean up uploaded file on error
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        
        raise HTTPException(
            status_code=500, 
            detail=f"Research paper assessment failed: {str(e)}"
        )

@router.post("/assess-content")
async def assess_paper_content(request: AssessmentRequest):
    """
    Assess research paper content that's already been extracted.
    Useful when you have the paper content in memory.
    """
    try:
        # Initialize research assessor
        assessor = ResearchPaperAssessor()
        
        # Perform assessment based on type
        if request.assessment_type == "comprehensive":
            assessment = assessor.assess_research_paper(request.paper_content)
            score_breakdown = assessor.get_last_score_breakdown()
        elif request.assessment_type == "quick":
            # Quick assessment focusing only on major missing elements
            assessment = assessor.assess_research_paper(request.paper_content)
            score_breakdown = assessor.get_last_score_breakdown()
            # Filter to only critical and important missing content
            assessment.missing_content = [
                content for content in assessment.missing_content 
                if content.importance in ["Critical", "Important"]
            ]
        elif request.assessment_type == "methodology":
            # Focus on methodology analysis
            assessment = assessor.assess_research_paper(request.paper_content)
            score_breakdown = assessor.get_last_score_breakdown()
            assessment.missing_content = [
                content for content in assessment.missing_content 
                if content.category.lower() == "methodology"
            ]
        elif request.assessment_type == "literature":
            # Focus on literature review analysis
            assessment = assessor.assess_research_paper(request.paper_content)
            score_breakdown = assessor.get_last_score_breakdown()
            assessment.missing_content = [
                content for content in assessment.missing_content 
                if content.category.lower() in ["literature review", "literature", "related work"]
            ]
        else:
            raise HTTPException(status_code=400, detail="Invalid assessment type")
        
        # Convert to JSON-serializable format
        assessment_data = {
            "paper_title": assessment.paper_title,
            "research_field": assessment.research_field,
            "overall_completeness_score": assessment.overall_completeness_score,
            "missing_content": [
                {
                    "category": content.category,
                    "topic": content.topic,
                    "importance": content.importance,
                    "description": content.description,
                    "suggestion": content.suggestion,
                    "related_sections": content.related_sections
                }
                for content in assessment.missing_content
            ],
            "strengths": assessment.strengths,
            "weaknesses": assessment.weaknesses,
            "recommendations": assessment.recommendations,
            "methodology_analysis": assessment.methodology_analysis,
            "literature_review_analysis": assessment.literature_review_analysis,
            "results_analysis": assessment.results_analysis,
            "discussion_analysis": assessment.discussion_analysis,
            "assessment_type": request.assessment_type,
            "score_breakdown": score_breakdown
        }
        
        return {
            "status": "success",
            "message": f"{request.assessment_type.title()} assessment completed",
            "assessment": assessment_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Paper content assessment failed: {str(e)}"
        )

@router.post("/quick-missing-analysis")
async def quick_missing_analysis(file: UploadFile = File(...)):
    """
    Quick analysis to identify only the most critical missing content.
    This reuses the comprehensive assessment logic to ensure score consistency.
    """
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get or create assessment (cached - same as comprehensive)
        assessment, score_breakdown = get_or_create_assessment(str(file_path))
        
        print(f"QUICK - Completeness Score: {assessment.overall_completeness_score}")
        print(f"QUICK - Score Breakdown: {score_breakdown}")
        
        # Filter to only critical missing content
        critical_missing = [
            {
                "category": content.category,
                "topic": content.topic,
                "importance": content.importance,
                "description": content.description,
                "suggestion": content.suggestion,
                "related_sections": content.related_sections
            }
            for content in assessment.missing_content 
            if content.importance == "Critical"
        ]
        
        # Clean up uploaded file
        file_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "message": "Quick missing content analysis completed",
            "paper_title": assessment.paper_title,
            "research_field": assessment.research_field,
            "completeness_score": assessment.overall_completeness_score,
            "critical_missing_content": critical_missing,
            "total_critical_issues": len(critical_missing),
            # Include score breakdown to ensure consistency with comprehensive analysis
            "score_breakdown": score_breakdown,
            # Include assessment summary for consistency
            "assessment_summary": {
                "total_missing_items": len(assessment.missing_content),
                "critical_missing": len([c for c in assessment.missing_content if c.importance == "Critical"]),
                "important_missing": len([c for c in assessment.missing_content if c.importance == "Important"]),
                "beneficial_missing": len([c for c in assessment.missing_content if c.importance == "Beneficial"])
            }
        }
        
    except Exception as e:
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        
        raise HTTPException(
            status_code=500, 
            detail=f"Quick analysis failed: {str(e)}"
        )

@router.get("/assessment-types")
async def get_assessment_types():
    """
    Get available assessment types and their descriptions
    """
    return {
        "status": "success",
        "assessment_types": {
            "comprehensive": {
                "description": "Complete analysis of the research paper including all missing content, strengths, weaknesses, and detailed recommendations",
                "estimated_time": "30-60 seconds",
                "covers": ["All sections", "Missing content", "Methodology", "Literature review", "Results", "Discussion"]
            },
            "quick": {
                "description": "Fast analysis focusing only on critical and important missing elements",
                "estimated_time": "15-30 seconds", 
                "covers": ["Critical missing content", "Important gaps", "Basic recommendations"]
            },
            "methodology": {
                "description": "Detailed analysis of methodology section and related missing elements",
                "estimated_time": "20-40 seconds",
                "covers": ["Methodology completeness", "Statistical analysis", "Experimental design"]
            },
            "literature": {
                "description": "Focus on literature review quality and missing related work",
                "estimated_time": "20-40 seconds",
                "covers": ["Literature coverage", "Research gaps", "Citation analysis"]
            }
        }
    }

