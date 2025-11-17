from models.summarizer_api import summarize_text

def generate_summary(text: str, max_words: int = 250) -> str:
    """Wrapper that uses the model to generate summary from extracted text."""
    return summarize_text(text, max_words)
