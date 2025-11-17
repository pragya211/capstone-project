# import fitz  # PyMuPDF
# from pathlib import Path

# def extract_layout_sections(pdf_path):
#     doc = fitz.open(pdf_path)
#     sections = {}
#     current_section = "preamble"
#     sections[current_section] = ""

#     for page in doc:
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             if "lines" not in block:
#                 continue
#             for line in block["lines"]:
#                 spans = line["spans"]
#                 for span in spans:
#                     text = span["text"].strip()
#                     if not text or len(text.split()) > 12:
#                         sections[current_section] += text + " "
#                         continue

#                     font_size = span["size"]
#                     is_bold = "bold" in span["font"].lower()
#                     is_capital = text.upper() == text and len(text) > 3

#                     # Heuristic: Likely section heading
#                     if font_size >= 10 and (is_bold or is_capital):
#                         current_section = text.lower()
#                         if current_section not in sections:
#                             sections[current_section] = ""
#                     else:
#                         sections[current_section] += text + " "

#     doc.close()
#     return sections

# # Example usage
# if __name__ == "__main__":
#     pdf_file = "example.pdf"  # Replace with your path
#     output = extract_layout_sections(pdf_file)

#     for heading, content in output.items():
#         print(f"\n\n=== {heading.upper()} ===\n{content[:500]}...")


import fitz  # PyMuPDF
import os
import openai  # Or use anthropic, etc.
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def line_looks_like_heading(line):
    """Heuristic: font size, bold, position, short line"""
    for span in line["spans"]:
        if span["size"] >= 12 and (span["flags"] & 2):  # bold
            text = span["text"].strip()
            if 2 < len(text.split()) < 15:  # Not too short or too long
                return text
    return None


def extract_heading_candidates(pdf_path):
    """Extract potential headings based on layout features"""
    doc = fitz.open(pdf_path)
    candidates = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    heading = line_looks_like_heading(line)
                    if heading:
                        candidates.append((page_num, heading))

    return candidates


def validate_heading_llm(line_text):
    """Use OpenAI to confirm if a candidate is a heading"""
    prompt = f"""
You're analyzing a research paper. Is the following line a section heading?

Line: "{line_text}"

Reply only with 'yes' or 'no'.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or gpt-4, gpt-4o
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3
    )

    answer = response.choices[0].message["content"].strip().lower()
    return answer.startswith("yes")


def extract_layout_sections(pdf_path):
    """Main function to extract validated section headings"""
    candidates = extract_heading_candidates(pdf_path)
    verified_sections = []

    for page_num, heading in candidates:
        try:
            if validate_heading_llm(heading):
                verified_sections.append({"page": page_num + 1, "title": heading})
        except Exception as e:
            print(f"LLM validation failed for '{heading}': {e}")

    return verified_sections
