#!/usr/bin/env python3
"""
Test script to verify OpenAI API connection
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def test_openai_connection():
    """Test basic OpenAI API connection"""
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please check your .env file")
        return False
    
    print(f"✅ API Key found: {OPENAI_API_KEY[:10]}...")
    
    # Test with a simple request
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "Say 'Hello, API is working!'"}
                ],
                "max_tokens": 50
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data["choices"][0]["message"]["content"]
            print(f"✅ OpenAI API working! Response: {message}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

def test_long_text():
    """Test with longer text to see if that's the issue"""
    
    long_text = "This is a test. " * 1000  # ~15,000 characters
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": f"Summarize this text in 50 words: {long_text}"}
                ],
                "max_tokens": 100
            }
        )
        
        if response.status_code == 200:
            print("✅ Long text processing works!")
            return True
        else:
            print(f"❌ Long text error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Long text error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing OpenAI API Connection...")
    print("=" * 50)
    
    # Test basic connection
    if test_openai_connection():
        print("\n🔍 Testing long text processing...")
        test_long_text()
    
    print("\n💡 If you're getting 400 errors, check:")
    print("1. API key is valid and has credits")
    print("2. Text length is not too long")
    print("3. Request format is correct")
