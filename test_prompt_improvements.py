#!/usr/bin/env python3
"""
Test script to verify the improved AI prompts for JSON parsing
"""

import requests
import json
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_PDF_PATH = "data/A thorough benchmark of automatic text classificat.pdf"

def test_improved_prompts():
    """Test the improved prompts for better JSON parsing"""
    print("🧪 Testing Improved AI Prompts for JSON Parsing")
    print("=" * 60)
    
    if not Path(TEST_PDF_PATH).exists():
        print(f"❌ Test PDF not found at {TEST_PDF_PATH}")
        print("   Please ensure you have a PDF file in the data directory")
        return False
    
    try:
        print("🔍 Testing with Quick Analysis (should have improved JSON parsing)...")
        
        with open(TEST_PDF_PATH, "rb") as pdf_file:
            files = {"file": (Path(TEST_PDF_PATH).name, pdf_file, "application/pdf")}
            
            response = requests.post(
                f"{BACKEND_URL}/assess/quick-missing-analysis",
                files=files,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Quick analysis completed successfully!")
                
                # Check if we got meaningful results
                critical_missing = data.get('critical_missing_content', [])
                
                # Look for parsing error indicators
                has_parsing_error = any(
                    'unable to parse' in str(item).lower() or
                    'analysis error' in str(item).lower()
                    for item in critical_missing
                )
                
                if has_parsing_error:
                    print("❌ Still showing parsing errors - prompts may need further refinement")
                    print("   Error details:")
                    for item in critical_missing:
                        if 'unable to parse' in str(item).lower() or 'analysis error' in str(item).lower():
                            print(f"   - {item}")
                    return False
                else:
                    print("✅ No parsing errors detected!")
                    print(f"   Found {len(critical_missing)} critical missing content items")
                    
                    # Show examples of successful parsing
                    for i, item in enumerate(critical_missing[:2], 1):
                        print(f"   {i}. {item.get('topic', 'Unknown')} ({item.get('category', 'Unknown')})")
                        print(f"      Importance: {item.get('importance', 'Unknown')}")
                        print(f"      Description: {item.get('description', 'No description')[:100]}...")
                    
                    return True
            else:
                print(f"❌ Quick analysis failed: {response.status_code}")
                print(f"   Response: {response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_comprehensive_assessment():
    """Test comprehensive assessment with improved prompts"""
    print("\n🔬 Testing Comprehensive Assessment with Improved Prompts...")
    
    if not Path(TEST_PDF_PATH).exists():
        return False
    
    try:
        with open(TEST_PDF_PATH, "rb") as pdf_file:
            files = {"file": (Path(TEST_PDF_PATH).name, pdf_file, "application/pdf")}
            
            response = requests.post(
                f"{BACKEND_URL}/assess/assess-paper",
                files=files,
                timeout=180
            )
            
            if response.status_code == 200:
                data = response.json()
                assessment = data.get('assessment', {})
                print("✅ Comprehensive assessment completed!")
                
                # Check for parsing errors in all components
                missing_content = assessment.get('missing_content', [])
                strengths = assessment.get('strengths', [])
                weaknesses = assessment.get('weaknesses', [])
                
                # Check for parsing error indicators
                has_parsing_error = False
                
                # Check missing content
                for item in missing_content:
                    if ('unable to parse' in str(item).lower() or 
                        'analysis error' in str(item).lower()):
                        has_parsing_error = True
                        print(f"❌ Parsing error in missing content: {item}")
                
                # Check strengths/weaknesses
                for strength in strengths:
                    if 'unable to identify' in str(strength).lower():
                        has_parsing_error = True
                        print(f"❌ Parsing error in strengths: {strength}")
                
                for weakness in weaknesses:
                    if 'unable to identify' in str(weakness).lower():
                        has_parsing_error = True
                        print(f"❌ Parsing error in weaknesses: {weakness}")
                
                if has_parsing_error:
                    print("❌ Still has parsing errors - prompts need further refinement")
                    return False
                else:
                    print("✅ No parsing errors in comprehensive assessment!")
                    print(f"   Missing content items: {len(missing_content)}")
                    print(f"   Strengths identified: {len(strengths)}")
                    print(f"   Weaknesses identified: {len(weaknesses)}")
                    
                    # Show summary
                    score = assessment.get('overall_completeness_score', 0)
                    print(f"   Overall score: {score:.1f}/100")
                    
                    return True
            else:
                print(f"❌ Comprehensive assessment failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Comprehensive assessment test failed: {e}")
        return False

def main():
    """Run all prompt improvement tests"""
    print("🔧 AI PROMPT IMPROVEMENTS TEST")
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
    quick_test_ok = test_improved_prompts()
    comprehensive_test_ok = test_comprehensive_assessment()
    
    print("\n" + "=" * 60)
    print("📊 PROMPT IMPROVEMENT TEST RESULTS")
    print("=" * 60)
    print(f"Quick Analysis: {'✅ IMPROVED' if quick_test_ok else '❌ STILL HAS ISSUES'}")
    print(f"Comprehensive Assessment: {'✅ IMPROVED' if comprehensive_test_ok else '❌ STILL HAS ISSUES'}")
    
    if quick_test_ok and comprehensive_test_ok:
        print("\n🎉 PROMPT IMPROVEMENTS SUCCESSFUL!")
        print("   The AI should now return proper JSON responses.")
        print("   Parsing errors should be eliminated.")
    else:
        print("\n❌ PROMPT IMPROVEMENTS NEED MORE WORK")
        print("   The AI is still not returning properly formatted JSON.")
        print("   Consider:")
        print("   - Further simplifying the prompts")
        print("   - Using a different AI model")
        print("   - Adding more strict JSON validation")

if __name__ == "__main__":
    main()

