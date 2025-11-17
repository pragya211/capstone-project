#!/usr/bin/env python3
"""
Demo script showing how to use the advanced PDF processing features
"""

import requests
import json
from pathlib import Path

def demo_advanced_extraction():
    """Demonstrate the advanced PDF extraction API"""
    
    # Find a sample PDF
    data_dir = Path("data")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in the data directory")
        print("Please add a PDF file to the data/ directory to test")
        return
    
    pdf_file = pdf_files[0]
    print(f"📄 Using PDF: {pdf_file.name}")
    
    # API endpoint
    url = "http://localhost:8000/advanced/advanced-extract"
    
    try:
        print("🚀 Starting advanced PDF extraction...")
        
        with open(pdf_file, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            result = data["data"]
            
            print("✅ Extraction successful!")
            print("\n" + "="*50)
            print("📊 DOCUMENT STATISTICS")
            print("="*50)
            
            metadata = result["metadata"]
            print(f"📄 Total Pages: {metadata['total_pages']}")
            print(f"📚 Citations Found: {metadata['total_citations']}")
            print(f"🖼️  Figures Found: {metadata['total_figures']}")
            print(f"📋 Tables Found: {metadata['total_tables']}")
            print(f"🧮 Equations Found: {metadata['total_equations']}")
            
            print("\n" + "="*50)
            print("🔍 TOP KEYWORDS")
            print("="*50)
            for i, keyword in enumerate(result["keywords"][:10], 1):
                print(f"{i:2d}. {keyword}")
            
            print("\n" + "="*50)
            print("📚 SAMPLE CITATIONS")
            print("="*50)
            for i, citation in enumerate(result["citations"][:5], 1):
                print(f"{i}. {citation['text']} ({citation['citation_type']})")
                if citation['authors']:
                    print(f"   👥 Authors: {', '.join(citation['authors'])}")
                if citation['year']:
                    print(f"   📅 Year: {citation['year']}")
                print()
            
            print("="*50)
            print("🖼️  FIGURES & TABLES")
            print("="*50)
            for i, item in enumerate(result["figures_tables"][:3], 1):
                print(f"{i}. {item['label']} (Page {item['page_number']})")
                print(f"   📝 Caption: {item['caption'][:80]}...")
                print()
            
            print("="*50)
            print("🧮 MATHEMATICAL CONTENT")
            print("="*50)
            for i, math in enumerate(result["mathematical_content"][:3], 1):
                print(f"{i}. {math['equation_type'].upper()} (Page {math['page_number']})")
                print(f"   📐 Equation: {math['equation'][:60]}...")
                print()
            
            print("="*50)
            print("📖 DOCUMENT SECTIONS")
            print("="*50)
            sections = result["sections"]
            print(f"📄 Abstract: {len(sections['abstract'])} characters")
            print(f"📄 Introduction: {len(sections['introduction'])} characters")
            print(f"📄 Main Body: {len(sections['main_body'])} characters")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running")
        print("   Run: cd capstone_project && uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def demo_individual_features():
    """Demonstrate individual feature extraction endpoints"""
    
    data_dir = Path("data")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        return
    
    pdf_file = pdf_files[0]
    base_url = "http://localhost:8000/advanced"
    
    endpoints = [
        ("extract-citations-only", "Citations Only"),
        ("extract-figures-tables", "Figures & Tables Only"),
        ("extract-mathematical-content", "Mathematical Content Only")
    ]
    
    print("\n" + "="*60)
    print("🔧 INDIVIDUAL FEATURE EXTRACTION DEMO")
    print("="*60)
    
    for endpoint, description in endpoints:
        print(f"\n📡 Testing: {description}")
        print("-" * 40)
        
        try:
            with open(pdf_file, "rb") as f:
                files = {"file": f}
                response = requests.post(f"{base_url}/{endpoint}", files=files)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {description} extraction successful!")
                
                # Show sample results based on endpoint
                if "citations" in endpoint:
                    citations = data.get("citations", [])
                    print(f"   Found {len(citations)} citations")
                    if citations:
                        print(f"   Sample: {citations[0]['text']}")
                
                elif "figures" in endpoint:
                    figures_tables = data.get("figures_tables", [])
                    figures = [ft for ft in figures_tables if ft['content_type'] == 'figure']
                    tables = [ft for ft in figures_tables if ft['content_type'] == 'table']
                    print(f"   Found {len(figures)} figures and {len(tables)} tables")
                
                elif "mathematical" in endpoint:
                    math_content = data.get("mathematical_content", [])
                    print(f"   Found {len(math_content)} mathematical expressions")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🎯 Advanced PDF Processing Demo")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server is not responding correctly")
    except:
        print("❌ Backend server is not running")
        print("   Please start the server with: uvicorn backend.main:app --reload")
        exit(1)
    
    # Run demos
    demo_advanced_extraction()
    demo_individual_features()
    
    print("\n🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("   1. Start the frontend: cd capstone-ui && npm start")
    print("   2. Open http://localhost:3000")
    print("   3. Try the 'Advanced Processor' tab")
