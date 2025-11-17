#!/usr/bin/env python3
"""
Test script for advanced PDF processing features
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.services.advanced_pdf_parser import AdvancedPDFParser

def test_advanced_parser():
    """Test the advanced PDF parser with a sample PDF"""
    
    # Look for a sample PDF in the data directory
    data_dir = Path("data")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the data directory")
        return
    
    # Use the first PDF file found
    test_pdf = pdf_files[0]
    print(f"Testing with PDF: {test_pdf.name}")
    
    try:
        parser = AdvancedPDFParser()
        result = parser.parse_pdf_advanced(str(test_pdf))
        
        print("\n=== ADVANCED PDF PROCESSING RESULTS ===")
        print(f"Total pages: {result['metadata']['total_pages']}")
        print(f"Total citations: {result['metadata']['total_citations']}")
        print(f"Total figures: {result['metadata']['total_figures']}")
        print(f"Total tables: {result['metadata']['total_tables']}")
        print(f"Total equations: {result['metadata']['total_equations']}")
        
        print(f"\n=== KEYWORDS (Top 10) ===")
        for i, keyword in enumerate(result['keywords'][:10], 1):
            print(f"{i}. {keyword}")
        
        print(f"\n=== CITATIONS (First 5) ===")
        for i, citation in enumerate(result['citations'][:5], 1):
            print(f"{i}. {citation.text} ({citation.citation_type})")
            if citation.authors:
                print(f"   Authors: {', '.join(citation.authors)}")
            if citation.year:
                print(f"   Year: {citation.year}")
        
        print(f"\n=== FIGURES & TABLES (First 3) ===")
        for i, item in enumerate(result['figures_tables'][:3], 1):
            print(f"{i}. {item.label} (Page {item.page_number})")
            print(f"   Caption: {item.caption[:100]}...")
        
        print(f"\n=== MATHEMATICAL CONTENT (First 3) ===")
        for i, math in enumerate(result['mathematical_content'][:3], 1):
            print(f"{i}. {math.equation_type} (Page {math.page_number})")
            print(f"   Equation: {math.equation[:100]}...")
        
        print("\n=== SECTIONS ===")
        sections = result['sections']
        print(f"Abstract length: {len(sections['abstract'])} characters")
        print(f"Introduction length: {len(sections['introduction'])} characters")
        print(f"Main body length: {len(sections['main_body'])} characters")
        
        print("\n✅ Advanced PDF processing test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_advanced_parser()
