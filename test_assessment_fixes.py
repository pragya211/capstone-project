#!/usr/bin/env python3
"""
Test script to verify the research assessment parsing fixes
"""

import requests
import json
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_PDF_PATH = "data/A thorough benchmark of automatic text classificat.pdf"

def test_assessment_parsing():
    """Test the assessment parsing with improved error handling"""
    print("🧪 Testing Research Assessment Parsing Fixes")
    print("=" * 50)
    
    if not Path(TEST_PDF_PATH).exists():
        print(f"❌ Test PDF not found at {TEST_PDF_PATH}")
        print("   Please ensure you have a PDF file in the data directory")
        return False
    
    try:
        # Test quick analysis first (faster)
        print("🔍 Testing Quick Analysis...")
        with open(TEST_PDF_PATH, "rb") as pdf_file:
            files = {"file": (Path(TEST_PDF_PATH).name, pdf_file, "application/pdf")}
            
            response = requests.post(
                f"{BACKEND_URL}/assess/quick-missing-analysis",
                files=files,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Quick analysis successful!")
                print(f"   Paper: {data.get('paper_title', 'Unknown')}")
                print(f"   Field: {data.get('research_field', 'Unknown')}")
                print(f"   Score: {data.get('completeness_score', 0):.1f}/100")
                
                critical_missing = data.get('critical_missing_content', [])
                print(f"   Critical Issues: {len(critical_missing)}")
                
                # Check if we got meaningful results instead of parsing errors
                if critical_missing:
                    for i, item in enumerate(critical_missing[:2], 1):
                        print(f"      {i}. {item.get('topic', 'Unknown')} - {item.get('category', 'Unknown')}")
                        print(f"         {item.get('description', 'No description')[:100]}...")
                else:
                    print("   No critical issues identified")
                
                return True
            else:
                print(f"❌ Quick analysis failed: {response.status_code}")
                print(f"   Response: {response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Assessment test failed: {e}")
        return False

def test_comprehensive_assessment():
    """Test comprehensive assessment with better error handling"""
    print("\n🔬 Testing Comprehensive Assessment...")
    
    if not Path(TEST_PDF_PATH).exists():
        return False
    
    try:
        with open(TEST_PDF_PATH, "rb") as pdf_file:
            files = {"file": (Path(TEST_PDF_PATH).name, pdf_file, "application/pdf")}
            
            response = requests.post(
                f"{BACKEND_URL}/assess/assess-paper",
                files=files,
                timeout=180  # 3 minute timeout for comprehensive analysis
            )
            
            if response.status_code == 200:
                data = response.json()
                assessment = data.get('assessment', {})
                print("✅ Comprehensive assessment successful!")
                print(f"   Paper: {assessment.get('paper_title', 'Unknown')}")
                print(f"   Field: {assessment.get('research_field', 'Unknown')}")
                print(f"   Score: {assessment.get('overall_completeness_score', 0):.1f}/100")
                
                # Check missing content
                missing_content = assessment.get('missing_content', [])
                print(f"   Missing Content Items: {len(missing_content)}")
                
                # Check for parsing errors
                has_parsing_errors = any(
                    item.get('topic', '').lower() == 'unable to parse ai response' or
                    item.get('category', '').lower() == 'analysis error'
                    for item in missing_content
                )
                
                if has_parsing_errors:
                    print("   ⚠️  Still has parsing errors - needs further investigation")
                    return False
                else:
                    print("   ✅ No parsing errors detected!")
                    
                    # Show some examples
                    for i, item in enumerate(missing_content[:3], 1):
                        importance = item.get('importance', 'Unknown')
                        importance_emoji = "🚨" if importance == "Critical" else "⚠️" if importance == "Important" else "💡"
                        print(f"      {i}. {importance_emoji} {item.get('topic', 'Unknown')} ({item.get('category', 'Unknown')})")
                
                # Check other components
                strengths = assessment.get('strengths', [])
                weaknesses = assessment.get('weaknesses', [])
                recommendations = assessment.get('recommendations', [])
                
                print(f"   Strengths: {len(strengths)}")
                print(f"   Weaknesses: {len(weaknesses)}")
                print(f"   Recommendations: {len(recommendations)}")
                
                return True
            else:
                print(f"❌ Comprehensive assessment failed: {response.status_code}")
                print(f"   Response: {response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Comprehensive assessment test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 RESEARCH ASSESSMENT PARSING FIXES TEST")
    print("=" * 60)
    
    # Test backend server
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code != 200:
            print("❌ Backend server is not running")
            print("   Start it with: cd capstone_project && python -m uvicorn backend.main:app --reload")
            return
        print("✅ Backend server is running")
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        return
    
    # Run tests
    quick_test_ok = test_assessment_parsing()
    comprehensive_test_ok = test_comprehensive_assessment()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Quick Analysis: {'✅ PASSED' if quick_test_ok else '❌ FAILED'}")
    print(f"Comprehensive Assessment: {'✅ PASSED' if comprehensive_test_ok else '❌ FAILED'}")
    
    if quick_test_ok and comprehensive_test_ok:
        print("\n🎉 ALL TESTS PASSED! Parsing issues have been resolved.")
        print("\n💡 The Research Assessment Tool should now work properly in the UI.")
        print("   You can now upload research papers and get meaningful analysis results.")
    else:
        print("\n❌ Some tests failed. Issues may still exist.")
        
        if not quick_test_ok:
            print("\n🔧 Quick Analysis Issues:")
            print("   • Check OpenAI API key and quota")
            print("   • Verify backend server is running properly")
            print("   • Check console logs for detailed error messages")
        
        if not comprehensive_test_ok:
            print("\n🔧 Comprehensive Assessment Issues:")
            print("   • May need OpenAI API quota increase")
            print("   • Check for network connectivity issues")
            print("   • Review backend error logs")

if __name__ == "__main__":
    main()

