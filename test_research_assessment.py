#!/usr/bin/env python3
"""
Test script for the Research Paper Assessment functionality
"""

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PDF_PATH = "data/A thorough benchmark of automatic text classificat.pdf"

def test_assessment_types():
    """Test the assessment types endpoint"""
    print("🔍 Testing assessment types endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/assess/assessment-types")
        if response.status_code == 200:
            data = response.json()
            print("✅ Assessment types retrieved successfully:")
            for assessment_type, details in data["assessment_types"].items():
                print(f"   📋 {assessment_type}: {details['description']}")
        else:
            print(f"❌ Failed to get assessment types: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing assessment types: {e}")

def test_quick_analysis():
    """Test quick missing analysis with a sample PDF"""
    print("\n🚀 Testing quick missing analysis...")
    
    if not Path(TEST_PDF_PATH).exists():
        print(f"❌ Test PDF not found at {TEST_PDF_PATH}")
        print("   Please ensure you have a PDF file in the data directory")
        return
    
    try:
        with open(TEST_PDF_PATH, "rb") as pdf_file:
            files = {"file": (Path(TEST_PDF_PATH).name, pdf_file, "application/pdf")}
            
            response = requests.post(
                f"{BASE_URL}/assess/quick-missing-analysis",
                files=files
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Quick analysis completed successfully!")
                print(f"   📄 Paper: {data.get('paper_title', 'Unknown')}")
                print(f"   🔬 Field: {data.get('research_field', 'Unknown')}")
                print(f"   📊 Completeness Score: {data.get('completeness_score', 0):.1f}/100")
                print(f"   ⚠️  Critical Issues: {data.get('total_critical_issues', 0)}")
                
                if data.get('critical_missing_content'):
                    print("\n   🚨 Critical Missing Content:")
                    for i, item in enumerate(data['critical_missing_content'][:3], 1):
                        print(f"      {i}. {item['topic']} ({item['category']})")
                        print(f"         {item['description']}")
            else:
                print(f"❌ Quick analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing quick analysis: {e}")

def test_comprehensive_assessment():
    """Test comprehensive assessment with a sample PDF"""
    print("\n🔬 Testing comprehensive assessment...")
    
    if not Path(TEST_PDF_PATH).exists():
        print(f"❌ Test PDF not found at {TEST_PDF_PATH}")
        return
    
    try:
        with open(TEST_PDF_PATH, "rb") as pdf_file:
            files = {"file": (Path(TEST_PDF_PATH).name, pdf_file, "application/pdf")}
            
            response = requests.post(
                f"{BASE_URL}/assess/assess-paper",
                files=files
            )
            
            if response.status_code == 200:
                data = response.json()
                assessment = data.get('assessment', {})
                print("✅ Comprehensive assessment completed successfully!")
                print(f"   📄 Paper: {assessment.get('paper_title', 'Unknown')}")
                print(f"   🔬 Field: {assessment.get('research_field', 'Unknown')}")
                print(f"   📊 Completeness Score: {assessment.get('overall_completeness_score', 0):.1f}/100")
                
                # Show assessment summary
                summary = assessment.get('assessment_summary', {})
                print(f"   📈 Assessment Summary:")
                print(f"      Total missing items: {summary.get('total_missing_items', 0)}")
                print(f"      Critical: {summary.get('critical_missing', 0)}")
                print(f"      Important: {summary.get('important_missing', 0)}")
                print(f"      Beneficial: {summary.get('beneficial_missing', 0)}")
                
                # Show top recommendations
                recommendations = assessment.get('recommendations', [])
                if recommendations:
                    print(f"\n   💡 Top Recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"      {i}. {rec}")
                
                # Show strengths
                strengths = assessment.get('strengths', [])
                if strengths:
                    print(f"\n   ✅ Key Strengths:")
                    for i, strength in enumerate(strengths[:3], 1):
                        print(f"      {i}. {strength}")
            else:
                print(f"❌ Comprehensive assessment failed: {response.status_code}")
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing comprehensive assessment: {e}")

def main():
    """Run all tests"""
    print("🧪 Research Paper Assessment API Tests")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding correctly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("   Make sure the FastAPI server is running:")
        print("   cd capstone_project && python -m uvicorn backend.main:app --reload")
        return
    
    # Run tests
    test_assessment_types()
    test_quick_analysis()
    test_comprehensive_assessment()
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    main()

