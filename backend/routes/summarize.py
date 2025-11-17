from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env
load_dotenv()

router = APIRouter()

# Get API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing from .env file")

# Request model for summarization
class SummarizeRequest(BaseModel):
    abstract: str
    introduction: str
    main_body: str
    summary_length: int | None = 200  # Fixed optimal length for basic summarizer


# Helper function to call LLM
def summarize_text(section_name: str, text: str, summary_length: int = 200) -> str:
    if not text.strip():
        return "No content available."
    
    # Truncate text if it's too long (OpenAI has token limits)
    max_chars = 8000  # Conservative limit to avoid token issues
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
        print(f"Warning: {section_name} text truncated to {max_chars} characters")
    
    # Fixed optimal summary length for basic summarizer
    prompt = f"""
    Summarize the following {section_name} of a research paper in approximately {summary_length} words.
    Focus on the key points, main findings, and important conclusions.
    Make the summary clear, concise, and informative.
    
    Text:
    {text}
    """
    
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
                    {"role": "system", "content": "You are an academic paper summarizer. Provide clear, concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500  # Limit response length
            }
        )
        
        if response.status_code != 200:
            print(f"OpenAI API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return f"API Error: {response.status_code} - {response.text}"
            
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        print(f"Request error for {section_name}: {str(e)}")
        return f"Network error summarizing {section_name}: {str(e)}"
    except KeyError as e:
        print(f"Response parsing error for {section_name}: {str(e)}")
        return f"Response parsing error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error for {section_name}: {str(e)}")
        return f"Error summarizing {section_name}: {str(e)}"

# Route to summarize sections
@router.post("/")
async def summarize_sections(request: SummarizeRequest):
    print("Incoming request:", request.dict())  # 👈 check yeh print ho raha hai
    try:
        # Use fixed optimal length for basic summarizer
        optimal_length = request.summary_length or 200
        
        # Debug: Print text lengths
        print(f"Text lengths - Abstract: {len(request.abstract)}, Introduction: {len(request.introduction)}, Main Body: {len(request.main_body)}")
        
        summaries = {
            "abstract": summarize_text("abstract", request.abstract, optimal_length),
            "introduction": summarize_text("introduction", request.introduction, optimal_length),
            "main_body": summarize_text("main body", request.main_body, optimal_length)
        }
        return {"status": "success", "summaries": summaries}

    except Exception as e:
        import traceback
        print("Backend error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
