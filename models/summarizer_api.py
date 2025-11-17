import os
import openai
from dotenv import load_dotenv

load_dotenv()  # Load the API key from .env

openai.api_key = os.getenv("OPENAI_API_KEY")
print("OPENAI KEY:", openai.api_key)
def summarize_text(text: str, max_words: int = 250) -> str:
    """Summarizes a block of text using GPT-3.5 Turbo API."""
    try:
        #prompt = f"Summarize the following research paper text in under {max_words} words:\n\n{text}"
        prompt = (
    f"You are an academic summarization assistant. "
    f"Please provide a concise summary of the following research paper text in **under {max_words} words**. "
    f"Focus on the core ideas and skip redundant information:\n\n{text}"
)


        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.3
        )

        summary = response['choices'][0]['message']['content'].strip()
        return summary

    except Exception as e:
        return f"Error during summarization: {e}"
