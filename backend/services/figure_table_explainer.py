import os
import requests
from typing import List, Optional
from dotenv import load_dotenv
from .advanced_pdf_parser import FigureTable

load_dotenv()

class FigureTableExplainer:
    """Service to generate AI explanations for figures and tables"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is missing from .env file")
    
    def generate_explanations(self, figures_tables: List[FigureTable]) -> List[FigureTable]:
        """Generate AI explanations for figures and tables"""
        explained_items = []
        
        for item in figures_tables:
            try:
                explanation = self._generate_single_explanation(item)
                # Create a new FigureTable with the explanation
                explained_item = FigureTable(
                    caption=item.caption,
                    label=item.label,
                    content_type=item.content_type,
                    position=item.position,
                    page_number=item.page_number,
                    ai_explanation=explanation,
                    image_base64=item.image_base64
                )
                explained_items.append(explained_item)
            except Exception as e:
                print(f"Error generating explanation for {item.label}: {str(e)}")
                # Keep the item without explanation on error
                explained_items.append(item)
        
        return explained_items
    
    def _generate_single_explanation(self, item: FigureTable) -> str:
        """Generate AI explanation for a single figure or table"""
        
        prompt = f"""
        You are an expert research paper analyst. Analyze the following {item.content_type} from a research paper and provide a detailed explanation of what is happening in it.
        
        Label: {item.label}
        Caption: {item.caption}
        
        Based on the caption and context, explain:
        1. What this {item.content_type} is showing/representing
        2. What key information, data, or visual elements it contains
        3. What insights or conclusions can be drawn from it
        4. How it likely relates to the research paper's methodology or findings
        
        Be specific and detailed. Write 2-4 sentences explaining the content and significance.
        
        Explanation:
        """
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert research paper analyst who provides clear, detailed explanations of figures and tables in academic papers."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 300
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            data = response.json()
            explanation = data["choices"][0]["message"]["content"].strip()
            
            return explanation
            
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return f"Unable to generate explanation. {item.caption}"

