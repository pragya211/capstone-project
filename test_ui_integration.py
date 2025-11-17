#!/usr/bin/env python3
"""
Test script to verify the complete UI integration for Research Assessment
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_PDF_PATH = "data/A thorough benchmark of automatic text classificat.pdf"

def test_backend_server():
    """Test if the backend server is running with the new assessment endpoints"""
    print("🔧 Testing Backend Server...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print(f"❌ Backend server error: {response.status_code}")
            return False
        
        # Test assessment types endpoint
        response = requests.get(f"{BACKEND_URL}/assess/assessment-types")
        if response.status_code == 200:
            data = response.json()
            print("✅ Assessment types endpoint working")
            print(f"   Available types: {list(data['assessment_types'].keys())}")
        else:
            print(f"❌ Assessment types endpoint error: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backend server connection failed: {e}")
        return False

def test_frontend_server():
    """Test if the frontend server is running"""
    print("\n🎨 Testing Frontend Server...")
    
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("✅ Frontend server is running")
            return True
        else:
            print(f"❌ Frontend server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend server connection failed: {e}")
        return False

def test_assessment_functionality():
    """Test the assessment functionality with a sample PDF"""
    print("\n🧪 Testing Assessment Functionality...")
    
    if not Path(TEST_PDF_PATH).exists():
        print(f"❌ Test PDF not found at {TEST_PDF_PATH}")
        print("   Please ensure you have a PDF file in the data directory")
        return False
    
    try:
        # Test quick analysis
        with open(TEST_PDF_PATH, "rb") as pdf_file:
            files = {"file": (Path(TEST_PDF_PATH).name, pdf_file, "application/pdf")}
            
            print("   🔄 Testing quick analysis...")
            response = requests.post(
                f"{BACKEND_URL}/assess/quick-missing-analysis",
                files=files,
                timeout=120  # 2 minute timeout for analysis
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Quick analysis working")
                print(f"   Paper: {data.get('paper_title', 'Unknown')}")
                print(f"   Field: {data.get('research_field', 'Unknown')}")
                print(f"   Score: {data.get('completeness_score', 0):.1f}/100")
                print(f"   Critical Issues: {data.get('total_critical_issues', 0)}")
                return True
            else:
                print(f"❌ Quick analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Assessment test failed: {e}")
        return False

def show_usage_instructions():
    """Show instructions for using the new feature"""
    print("\n" + "="*60)
    print("🚀 RESEARCH ASSESSMENT TOOL - READY TO USE!")
    print("="*60)
    
    print("\n📋 How to use the Research Assessment Tool:")
    print("1. Open your browser and go to: http://localhost:3000")
    print("2. Click on the 'Research Assessment' tab")
    print("3. Upload a PDF research paper")
    print("4. Choose assessment type (Comprehensive or Quick)")
    print("5. Click 'Start Assessment' and wait for AI analysis")
    print("6. Review the detailed assessment results")
    
    print("\n🎯 What the tool provides:")
    print("• Missing content analysis with importance levels")
    print("• Completeness score (0-100)")
    print("• Strengths and weaknesses identification")
    print("• Detailed recommendations for improvement")
    print("• Section-by-section analysis (methodology, literature, results, discussion)")
    
    print("\n📊 Assessment Types:")
    print("• Comprehensive: Complete analysis of all paper sections")
    print("• Quick: Fast analysis focusing on critical missing elements")
    
    print("\n🔗 API Endpoints Available:")
    print("• POST /assess/assess-paper - Comprehensive assessment")
    print("• POST /assess/quick-missing-analysis - Quick analysis")
    print("• POST /assess/assess-content - Assess extracted content")
    print("• GET /assess/assessment-types - Get assessment types info")
    
    print("\n⚡ Features:")
    print("• AI-powered analysis using OpenAI GPT")
    print("• Field-specific assessment (Computer Science, Medicine, etc.)")
    print("• Color-coded importance levels (Critical/Important/Beneficial)")
    print("• Detailed suggestions for each missing element")
    print("• Section-specific scoring and recommendations")

def main():
    """Run all integration tests"""
    print("🧪 RESEARCH ASSESSMENT TOOL - INTEGRATION TEST")
    print("="*60)
    
    # Test backend
    backend_ok = test_backend_server()
    
    # Test frontend
    frontend_ok = test_frontend_server()
    
    # Test assessment functionality
    assessment_ok = test_assessment_functionality()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Backend Server: {'✅ OK' if backend_ok else '❌ FAILED'}")
    print(f"Frontend Server: {'✅ OK' if frontend_ok else '❌ FAILED'}")
    print(f"Assessment Functionality: {'✅ OK' if assessment_ok else '❌ FAILED'}")
    
    if backend_ok and frontend_ok and assessment_ok:
        print("\n🎉 ALL TESTS PASSED! The Research Assessment Tool is ready to use.")
        show_usage_instructions()
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        
        if not backend_ok:
            print("\n🔧 Backend Issues:")
            print("   • Make sure the FastAPI server is running:")
            print("     cd capstone_project && python -m uvicorn backend.main:app --reload")
            print("   • Check that OpenAI API key is set in .env file")
        
        if not frontend_ok:
            print("\n🎨 Frontend Issues:")
            print("   • Make sure the React server is running:")
            print("     cd capstone_project/capstone-ui && npm start")
        
        if not assessment_ok:
            print("\n🧪 Assessment Issues:")
            print("   • Ensure you have a test PDF in the data directory")
            print("   • Check OpenAI API key and quota")
            print("   • Verify backend server is running properly")

if __name__ == "__main__":
    main()

