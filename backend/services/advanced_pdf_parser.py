import fitz  # PyMuPDF
import re
import base64
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Citation:
    """Represents a citation found in the text"""
    text: str
    position: int
    citation_type: str  # 'author_year', 'numbered', 'footnote'
    authors: List[str]
    year: Optional[str]
    title: Optional[str]

@dataclass
class FigureTable:
    """Represents a figure or table found in the text"""
    caption: str
    label: str  # e.g., "Figure 1", "Table 2"
    content_type: str  # 'figure' or 'table'
    position: int
    page_number: int
    ai_explanation: Optional[str] = None  # AI-generated explanation of the figure/table content
    image_base64: Optional[str] = None  # Base64-encoded image of the figure/table

@dataclass
class MathematicalContent:
    """Represents mathematical content found in the text"""
    equation: str
    equation_type: str  # 'inline', 'display', 'numbered'
    position: int
    page_number: int
    context: Optional[str] = None  # Nearby section/topic
    summary: Optional[str] = None  # Plain-English meaning
    impact: Optional[str] = None   # Expected effect on results

class AdvancedPDFParser:
    """Enhanced PDF parser with advanced text processing capabilities"""
    
    def __init__(self):
        # Citation patterns
        self.citation_patterns = {
            'author_year': re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\((\d{4})\)', re.IGNORECASE),
            'numbered': re.compile(r'\[(\d{1,3}(?:,\s*\d{1,3})*)\]'),  # More reasonable citation numbers (1-999)
            'footnote': re.compile(r'\^(\d+)\b'),
            'et_al': re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+et\s+al\.?\s*\((\d{4})\)', re.IGNORECASE)
        }
        
        # Figure/Table patterns - only match caption definitions (not references)
        # Caption definitions typically start a new line or are preceded by blank lines
        self.figure_patterns = {
            'figure': re.compile(r'\n\s*(?:Figure|Fig\.?)\s*(\d+(?:\.\d+)?)[:\.]\s*(.+?)(?=\n\s*(?:Figure|Table|Fig\.?|Tab\.?)\s*\d|$)', re.IGNORECASE | re.DOTALL),
            'table': re.compile(r'\n\s*(?:Table|Tab\.?)\s*(\d+(?:\.\d+)?)[:\.]\s*(.+?)(?=\n\s*(?:Figure|Table|Fig\.?|Tab\.?)\s*\d|$)', re.IGNORECASE | re.DOTALL)
        }
        
        # Mathematical content patterns (ordered by priority: display -> numbered -> inline -> simple)
        self.math_patterns = [
            ('display_math', re.compile(r'\$\$([^$]+)\$\$', re.DOTALL)),
            ('numbered_equation', re.compile(r'\\begin\{equation\}(.*?)\\end\{equation\}', re.DOTALL)),
            ('inline_math', re.compile(r'\$(?!\$)([^$]+)\$(?!\$)', re.DOTALL)),
            # Only match self-contained single-line equations, not fragments
            ('simple_equation', re.compile(r'(^|\n)\s*([a-zA-Z]\s*[=<>≤≥≠≈]\s*[^,\n]+?)(?=\s*(?:,|\n\n|[A-Z][a-z]|$))', re.MULTILINE)),
        ]

        self.keyword_stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'while', 'where',
            'with', 'without', 'within', 'between', 'among', 'into', 'onto', 'through', 'across',
            'from', 'into', 'over', 'under', 'above', 'below', 'around', 'about', 'before', 'after',
            'first', 'second', 'third', 'fourth', 'fifth', 'last', 'former', 'latter', 'new', 'old',
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'per',
            'each', 'every', 'many', 'several', 'various', 'other', 'another', 'any', 'all', 'both',
            'few', 'more', 'most', 'some', 'such', 'same', 'different', 'similar', 'varied',
            'we', 'you', 'they', 'he', 'she', 'it', 'our', 'your', 'their', 'its', 'his', 'her',
            'who', 'whom', 'whose', 'which', 'that', 'this', 'these', 'those', 'there', 'here',
            'been', 'being', 'was', 'were', 'are', 'is', 'am', 'be', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'also', 'however', 'therefore', 'furthermore', 'moreover',
            'because', 'since', 'although', 'though', 'whereas', 'yet', 'besides', 'overall',
            'research', 'paper', 'study', 'article', 'work', 'result', 'results', 'finding',
            'findings', 'approach', 'approaches', 'method', 'methods', 'analysis', 'data', 'dataset',
            'datasets', 'model', 'models', 'system', 'systems', 'figure', 'figures', 'table', 'tables',
            'section', 'sections', 'introduction', 'related', 'work', 'conclusion', 'discussion',
            'abstract', 'summary', 'contributions', 'overview', 'proposed', 'presented', 'including',
            'via', 'based', 'using', 'use', 'used', 'according', 'towards', 'toward', 'across',
            'amongst', 'throughout', 'towards', 'across', 'whose', 'whereby', 'whichever', 'whenever'
        }
    
    def extract_text_with_layout(self, pdf_path: str) -> Dict:
        """Extract text with layout information for advanced processing"""
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"File {pdf_path} not found.")
        
        doc = fitz.open(pdf_path)
        full_text = ""
        page_texts = []
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            page_texts.append({
                'page_number': page_num + 1,
                'text': page_text,
                'blocks': page.get_text("dict")["blocks"]
            })
            full_text += page_text + "\n"
        
        doc.close()
        
        # Extract title and headings
        title = self._extract_title(page_texts)
        headings = self._extract_headings(page_texts)
        
        return {
            'full_text': full_text.strip(),
            'pages': page_texts,
            'total_pages': len(page_texts),
            'title': title,
            'headings': headings
        }
    
    def _extract_title(self, page_texts: List[Dict]) -> str:
        """Extract the paper title from the first page"""
        if not page_texts:
            print("DEBUG - No page texts available")
            return "Unknown Title"
        
        first_page = page_texts[0]
        blocks = first_page.get('blocks', [])
        print(f"DEBUG - Found {len(blocks)} blocks in first page")
        
        # Look for the largest font size text in the first few blocks (likely the title)
        title_candidates = []
        
        for i, block in enumerate(blocks[:10]):  # Check first 10 blocks
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        font_size = span.get("size", 0)
                        
                        # Title characteristics: large font, short lines, first few blocks
                        # Exclude arXiv identifiers, dates, and metadata
                        excluded_patterns = [
                            'abstract', 'introduction', 'arxiv:', 'submitted', 'received', 
                            'accepted', 'published', 'volume', 'issue', 'doi:', 'issn:',
                            'proceedings', 'conference', 'journal', 'workshop', 'symposium'
                        ]
                        
                        is_excluded = any(text.lower().startswith(pattern) for pattern in excluded_patterns)
                        has_date = any(char.isdigit() for char in text) and any(month in text.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])
                        has_arxiv_id = 'arxiv:' in text.lower() or '[cs.' in text.lower() or 'v1' in text.lower()
                        
                        if (font_size >= 12 and len(text) > 10 and 
                            len(text) < 200 and not is_excluded and 
                            not has_date and not has_arxiv_id):
                            title_candidates.append((text, font_size))
                            print(f"DEBUG - Title candidate: '{text}' (font size: {font_size})")
                        else:
                            print(f"DEBUG - Excluded candidate: '{text}' (excluded: {is_excluded}, has_date: {has_date}, has_arxiv: {has_arxiv_id})")
        
        # Return the text with the largest font size
        if title_candidates:
            title_candidates.sort(key=lambda x: x[1], reverse=True)
            selected_title = title_candidates[0][0]
            print(f"DEBUG - Selected title from candidates: '{selected_title}'")
            return selected_title
        
        # Fallback: look for the first substantial line of text
        first_page_text = first_page.get('text', '')
        lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
        print(f"DEBUG - First page text lines: {lines[:10]}")  # Show more lines for debugging
        
        # Try multiple approaches
        for approach in ['first_line', 'longest_line', 'pattern_match']:
            if approach == 'first_line':
                # First approach: take the first substantial line
                for line in lines[:5]:
                    if self._is_valid_title(line):
                        print(f"DEBUG - Selected title from first line approach: '{line}'")
                        return line
            
            elif approach == 'longest_line':
                # Second approach: take the longest line in first 10 lines
                candidate_lines = [line for line in lines[:10] 
                                 if self._is_valid_title(line) and len(line) > 20]
                if candidate_lines:
                    longest_line = max(candidate_lines, key=len)
                    print(f"DEBUG - Selected title from longest line approach: '{longest_line}'")
                    return longest_line
            
            elif approach == 'pattern_match':
                # Third approach: look for title-like patterns
                for line in lines[:10]:
                    if (self._is_valid_title(line) and len(line) > 15 and len(line) < 150 and 
                        any(word in line.lower() for word in ['analysis', 'study', 'method', 'approach', 'system', 'model', 'framework', 'learning', 'algorithm', 'neural', 'deep', 'machine'])):
                        print(f"DEBUG - Selected title from pattern match approach: '{line}'")
                        return line
        
        # Final fallback: Use AI to extract title from first page text
        print("DEBUG - Trying AI-based title extraction")
        return self._extract_title_with_ai(first_page_text)
    
    def _is_valid_title(self, text: str) -> bool:
        """Check if a text line is a valid paper title"""
        if not text or len(text) < 10 or len(text) > 200:
            return False
        
        text_lower = text.lower()
        
        # Exclude common non-title patterns
        excluded_patterns = [
            'abstract', 'introduction', 'author', 'university', 'journal', 'proceedings',
            'conference', 'workshop', 'symposium', 'arxiv:', 'submitted', 'received',
            'accepted', 'published', 'volume', 'issue', 'doi:', 'issn:', 'email:',
            'address:', 'department', 'institute', 'college', 'school'
        ]
        
        # Check if starts with excluded patterns
        if any(text_lower.startswith(pattern) for pattern in excluded_patterns):
            return False
        
        # Exclude lines with arXiv identifiers
        if 'arxiv:' in text_lower or '[cs.' in text_lower or 'v1' in text_lower or 'v2' in text_lower:
            return False
        
        # Exclude lines with dates (contain digits and month names)
        has_digit = any(char.isdigit() for char in text)
        has_month = any(month in text_lower for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])
        if has_digit and has_month:
            return False
        
        # Exclude lines that are mostly numbers or special characters
        if len([c for c in text if c.isalnum()]) < len(text) * 0.7:
            return False
        
        # Exclude very short words (likely metadata)
        words = text.split()
        if len(words) < 2 or any(len(word) > 50 for word in words):
            return False
        
        return True
    
    def _extract_title_with_ai(self, first_page_text: str) -> str:
        """Use AI to extract title from first page text"""
        try:
            import os
            import requests
            from dotenv import load_dotenv
            
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                print("DEBUG - No OpenAI API key found")
                return "Unknown Title"
            
            # Truncate text to avoid token limits
            text_sample = first_page_text[:2000] if len(first_page_text) > 2000 else first_page_text
            
            prompt = f"""
            Extract the title of this research paper from the following text. 
            
            IMPORTANT: 
            - Return ONLY the actual paper title, not arXiv identifiers, dates, or metadata
            - Do not include "Title:", "arXiv:", dates, or author information
            - The title should be the main research topic/study name
            - Exclude lines that start with "arXiv:", contain dates like "Mar 2025", or have identifiers like "[cs.LG]"
            
            Text: {text_sample}
            """
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are an expert at extracting research paper titles. Return only the title text, nothing else."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.0,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                title = data["choices"][0]["message"]["content"].strip()
                print(f"DEBUG - AI extracted title: '{title}'")
                return title if title and len(title) > 5 else "Unknown Title"
            else:
                print(f"DEBUG - AI title extraction failed: {response.status_code}")
                return "Unknown Title"
                
        except Exception as e:
            print(f"DEBUG - AI title extraction error: {e}")
            return "Unknown Title"
    
    def _extract_title_from_filename(self, pdf_path: str) -> str:
        """Extract title from PDF filename as last resort"""
        try:
            from pathlib import Path
            filename = Path(pdf_path).stem  # Get filename without extension
            
            # Clean up common filename patterns
            title = filename.replace('_', ' ').replace('-', ' ')
            
            # Remove common prefixes/suffixes
            title = title.replace('paper', '').replace('research', '').replace('study', '')
            title = title.replace('.pdf', '').replace('.PDF', '')
            
            # Clean up extra spaces
            title = ' '.join(title.split())
            
            # Check if it's a reasonable title
            if len(title) > 10 and len(title) < 200:
                print(f"DEBUG - Extracted title from filename: '{title}'")
                return title
            else:
                return "Unknown Title"
                
        except Exception as e:
            print(f"DEBUG - Filename title extraction error: {e}")
            return "Unknown Title"
    
    def _extract_headings(self, page_texts: List[Dict]) -> List[Dict]:
        """Extract section headings from all pages"""
        headings = []
        
        # Common heading patterns
        heading_patterns = [
            re.compile(r'^\d+\.?\s+([A-Z][^a-z]*(?:\s+[A-Z][^a-z]*)*)', re.MULTILINE),  # "1. INTRODUCTION"
            re.compile(r'^([A-Z][A-Z\s]+)$', re.MULTILINE),  # "INTRODUCTION"
            re.compile(r'^\d+\.\d+\s+([A-Z][^a-z]*(?:\s+[A-Z][^a-z]*)*)', re.MULTILINE),  # "1.1 INTRODUCTION"
        ]
        
        for page in page_texts:
            page_num = page.get('page_number', 1)
            text = page.get('text', '')
            
            for pattern in heading_patterns:
                matches = pattern.findall(text)
                for match in matches:
                    heading_text = match.strip()
                    # Filter out likely false positives
                    if (len(heading_text) > 3 and len(heading_text) < 100 and
                        not heading_text.lower() in ['abstract', 'references', 'bibliography']):
                        headings.append({
                            'text': heading_text,
                            'page': page_num,
                            'type': 'section_heading'
                        })
        
        return headings
    
    def extract_citations(self, text: str) -> List[Citation]:
        """Extract citations from the text"""
        citations = []
        
        for citation_type, pattern in self.citation_patterns.items():
            for match in pattern.finditer(text):
                citation_text = match.group(0)
                position = match.start()
                
                # Filter out likely false positives
                if citation_type == 'numbered':
                    citation_number = match.group(1)
                    # Skip very large numbers that are likely years or other data
                    if int(citation_number.split(',')[0]) > 999:
                        continue
                
                if citation_type == 'numbered':
                    citation_numbers = [
                        int(num.strip())
                        for num in match.group(1).split(',')
                        if num.strip().isdigit()
                    ]
                    # Skip bracketed sequences that clearly aren't citations, e.g., contain 0
                    if not citation_numbers or any(num <= 0 for num in citation_numbers):
                        continue
                    authors = None
                    year = None
                    title = None
                elif citation_type == 'author_year':
                    authors = [match.group(1)]
                    year = match.group(2)
                    title = None
                elif citation_type == 'footnote':
                    authors = None
                    year = None
                    title = None
                elif citation_type == 'et_al':
                    authors = [match.group(1)]
                    year = match.group(2)
                    title = None
                
                citation = Citation(
                    text=citation_text,
                    position=position,
                    citation_type=citation_type,
                    authors=authors or [],
                    year=year,
                    title=title
                )
                citations.append(citation)
        
        return sorted(citations, key=lambda x: x.position)

    def extract_references(self, text: str) -> Dict[int, str]:
        """Extract numbered references from the references section"""
        references: Dict[int, str] = {}
        lines = text.splitlines()
        collecting = False
        current_number: Optional[int] = None
        current_parts: List[str] = []

        reference_heading_pattern = re.compile(r'^\s*(references|bibliography)\s*$', re.IGNORECASE)
        numbered_bracket_pattern = re.compile(r'^\s*\[(\d+)\]\s*(.+)')
        numbered_dot_pattern = re.compile(r'^\s*(\d+)[\.\)]\s+(.+)')

        for raw_line in lines:
            line = raw_line.strip()

            if not collecting:
                if reference_heading_pattern.match(line):
                    collecting = True
                continue

            if not line:
                if current_number is not None and current_parts:
                    references[current_number] = ' '.join(current_parts).strip()
                    current_number = None
                    current_parts = []
                continue

            # Detect next heading (all caps words) to stop collecting
            if line.isupper() and len(line.split()) <= 6 and not numbered_bracket_pattern.match(line):
                if current_number is not None and current_parts:
                    references[current_number] = ' '.join(current_parts).strip()
                break

            match = numbered_bracket_pattern.match(line) or numbered_dot_pattern.match(line)

            if match:
                if current_number is not None and current_parts:
                    references[current_number] = ' '.join(current_parts).strip()

                try:
                    current_number = int(match.group(1))
                    current_parts = [match.group(2).strip()]
                except ValueError:
                    current_number = None
                    current_parts = []
            else:
                if current_number is not None:
                    current_parts.append(line)

        if current_number is not None and current_parts:
            references[current_number] = ' '.join(current_parts).strip()

        return references
    
    def extract_figures_tables(self, text: str, pages: List[Dict], pdf_path: str = None) -> List[FigureTable]:
        """Extract figures and tables with their captions and images"""
        figures_tables = []
        seen_labels = set()  # Track labels to avoid duplicates
        
        for content_type, pattern in self.figure_patterns.items():
            for match in pattern.finditer(text):
                label = f"{content_type.title()} {match.group(1)}"
                position = match.start()
                
                # Skip if we've already seen this exact label
                if label in seen_labels:
                    print(f"DEBUG: Skipping duplicate {label} at position {position}")
                    continue
                seen_labels.add(label)
                print(f"DEBUG: Processing new {label} at position {position}")
                
                caption = match.group(2).strip()
                
                # Skip if caption is too short (likely just a reference, not a definition)
                if len(caption) < 20:  # Real figure captions are usually longer
                    print(f"DEBUG: Skipping short caption for {label}: '{caption[:50]}'")
                    continue
                
                # Find which page this content is on
                page_number = 1
                current_pos = 0
                for page_info in pages:
                    if position < current_pos + len(page_info['text']):
                        page_number = page_info['page_number']
                        break
                    current_pos += len(page_info['text']) + 1
                
                # Extract image from the page
                image_base64 = None
                if pdf_path:
                    image_base64 = self._extract_page_image(pdf_path, page_number)
                
                figure_table = FigureTable(
                    caption=caption,
                    label=label,
                    content_type=content_type,
                    position=position,
                    page_number=page_number,
                    image_base64=image_base64
                )
                figures_tables.append(figure_table)
        
        return sorted(figures_tables, key=lambda x: x.position)
    
    def extract_mathematical_content(self, text: str, pages: List[Dict]) -> List[MathematicalContent]:
        """Extract mathematical content and equations"""
        math_content = []
        
        seen_ranges: List[Tuple[int, int]] = []
        seen_keys = set()
        for equation_type, pattern in self.math_patterns:
            for match in pattern.finditer(text):
                # Handle groups - for simple_equation we have 2 groups
                if len(match.groups()) > 1 and equation_type == 'simple_equation':
                    equation = match.group(2).strip()
                else:
                    equation = match.group(1).strip()
                
                # Skip very short or likely non-equations
                if len(equation) < 3:
                    continue
                
                position = match.start()
                end_pos = match.end()

                # Skip if overlaps an already captured region (avoid duplicate capture of display vs inline)
                overlaps = any(not (end_pos <= s or position >= e) for s, e in seen_ranges)
                if overlaps:
                    continue
                
                # Find which page this content is on
                page_number = 1
                current_pos = 0
                for page_info in pages:
                    if position < current_pos + len(page_info['text']):
                        page_number = page_info['page_number']
                        break
                    current_pos += len(page_info['text']) + 1
                
                key = (equation, equation_type, page_number)
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                math_item = MathematicalContent(
                    equation=equation,
                    equation_type=equation_type,
                    position=position,
                    page_number=page_number
                )
                math_content.append(math_item)
                seen_ranges.append((position, end_pos))
        
        return sorted(math_content, key=lambda x: x.position)

    def _infer_topic_from_headings(self, position: int, pages: List[Dict], headings: List[Dict]) -> Optional[str]:
        """Infer the most relevant section heading occurring before the given position."""
        # Map positions per page
        current_pos = 0
        position_page = 1
        for page_info in pages:
            page_len = len(page_info['text']) + 1
            if position < current_pos + page_len:
                position_page = page_info['page_number']
                break
            current_pos += page_len
        # Choose the latest heading on or before this page
        prior_headings = [h for h in headings if h.get('page', 0) <= position_page]
        if not prior_headings:
            return None
        # Prefer the most recent
        prior_headings.sort(key=lambda h: (h.get('page', 0)))
        return prior_headings[-1]['text']

    def _summarize_equation(self, equation: str, nearby_text: str) -> Tuple[str, str]:
        """Heuristically summarize what the equation means and its likely impact."""
        eq = equation.strip()
        eq_lower = eq.lower()
        text_lower = nearby_text.lower()

        def contains(*terms: str) -> bool:
            return any(t in eq_lower or t in text_lower for t in terms)

        # Highly specific patterns first
        # Cross-entropy / log-likelihood
        if contains('cross-entropy', 'cross entropy') or re.search(r'-?\sum.*y\s*log\s*p', eq_lower) or contains('log-likelihood', 'log likelihood'):
            return (
                "Cross-entropy/log-likelihood objective for fitting predicted distributions.",
                "Improves classification performance and calibration by maximizing probability of true labels."
            )
        # KL divergence / information terms
        if contains('kl', 'd_kl', 'dkl') or re.search(r'kl\s*\(', eq_lower):
            return (
                "KL-divergence regularizer aligning two distributions.",
                "Stabilizes training and steers solutions toward desired priors; improves generalization."
            )
        # Argmin/argmax objectives
        if re.search(r'arg\s*(min|max)', eq_lower):
            return (
                "Optimization objective defining the best parameters under the stated criterion.",
                "Determines the learned solution; directly impacts accuracy and robustness."
            )
        # Sum-based empirical risk with regularization
        if ('∑' in eq or '\\sum' in eq_lower) and ('||' in eq or 'l2' in eq_lower or 'λ' in eq_lower or 'lambda' in eq_lower):
            return (
                "Empirical risk with regularization (trade-off between fit and complexity).",
                "Reduces overfitting, improving test performance at potential cost of bias."
            )
        # Softmax / attention-like scoring
        if contains('softmax') or re.search(r'e\^[^/]+/\s*\sum', eq_lower):
            return (
                "Softmax-based scoring/attention to weight alternatives.",
                "Focuses the model on salient features; often boosts performance on structured tasks."
            )
        if contains('qk', 'q·k', 'qk^t', 'v', 'attention'):
            return (
                "Attention mechanism computing relevance between query and key to weight values.",
                "Improves representation of long-range dependencies; enhances accuracy and interpretability."
            )
        # Gradient / derivative updates
        if contains('∇', 'nabla', 'gradient', '∂', 'partial') or re.search(r'd[^\s]/d[^\s]', eq_lower):
            return (
                "Gradient/derivative relation governing parameter updates or sensitivities.",
                "Affects convergence speed and stability; critical for achieving reported results."
            )
        # Constraints / bounds / inequalities
        if any(sym in eq for sym in ['≤', '≥', '>=', '<=', '<', '>']) or contains('constraint', 'subject to', 's.t.'):
            return (
                "Constraint or bound restricting feasible solutions or establishing guarantees.",
                "Improves robustness and safety; clarifies validity regime of the method."
            )
        # Metrics
        if contains('f1', 'precision', 'recall', 'auc', 'iou', 'bleu', 'rouge'):
            return (
                "Evaluation metric defining how performance is measured.",
                "Shapes optimization focus and reported improvements."
            )
        # Probabilistic relations
        if contains('p(', 'p(y|x)', 'posterior', 'prior', 'bayes'):
            return (
                "Probabilistic relation modeling uncertainty or conditional dependence.",
                "Improves calibration and decision-making under uncertainty."
            )
        # Norm-based regularization
        if contains('||', 'norm', 'l1', 'l2', 'λ', 'lambda'):
            return (
                "Regularization term controlling parameter magnitude/complexity.",
                "Reduces overfitting and improves generalization stability."
            )
        # Convolution / kernels
        if contains('conv', 'convolution', 'kernel'):
            return (
                "Convolution/kernel operation extracting structured features.",
                "Enables learning of spatial/temporal patterns; boosts representation quality."
            )

        # Fallbacks based on structure
        if '=' in eq and ('∑' in eq or '\\sum' in eq_lower):
            return (
                "Summation-based definition or objective over data or components.",
                "Aggregates evidence across samples/parts; influences final scores and training."
            )
        if '=' in eq and ('arg' in eq_lower or 'min' in eq_lower or 'max' in eq_lower):
            return (
                "Optimization statement defining the learned solution.",
                "Determines the final model parameters and results."
            )
        if any(sym in eq for sym in ['≤', '≥', '>=', '<=', '<', '>']):
            return (
                "Inequality expressing constraint or theoretical bound.",
                "Guides feasible solutions or provides guarantees impacting robustness."
            )

        # Generic fallback
        return (
            "Defines a key relationship used by the method.",
            "Guides the model's behavior and influences reported results."
        )

    def _get_nearby_text(self, text: str, position: int, window: int = 240) -> str:
        start = max(0, position - window)
        end = min(len(text), position + window)
        return text[start:end]
    
    def _extract_page_image(self, pdf_path: str, page_number: int) -> Optional[str]:
        """Extract images from a specific page of the PDF and return the largest one as base64"""
        try:
            if not Path(pdf_path).exists():
                return None
            
            doc = fitz.open(pdf_path)
            if page_number < 1 or page_number > len(doc):
                doc.close()
                return None
            
            page = doc[page_number - 1]  # Convert to 0-based index
            
            # Try to extract embedded images from the page
            image_list = page.get_images()
            
            print(f"DEBUG: Found {len(image_list)} embedded images on page {page_number}")
            
            if image_list:
                # Try to find the largest image (likely the main figure/table)
                largest_image = None
                largest_size = 0
                
                for img in image_list:
                    xref = img[0]
                    try:
                        base_image = doc.extract_image(xref)
                        image_size = len(base_image["image"])
                        if image_size > largest_size:
                            largest_size = image_size
                            largest_image = base_image
                    except:
                        continue
                
                if largest_image:
                    image_bytes = largest_image["image"]
                    # Convert to base64
                    img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    doc.close()
                    
                    print(f"DEBUG: Extracted largest embedded image from page {page_number}, size: {largest_size} bytes")
                    return img_base64
                else:
                    print(f"DEBUG: Could not extract embedded images, rendering full page")
            else:
                print(f"DEBUG: No embedded images found on page {page_number}, rendering full page")
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_bytes = pix.tobytes("png")
            
            # Convert to base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            doc.close()
            return img_base64
            
        except Exception as e:
            print(f"Error extracting image from page {page_number}: {str(e)}")
            return None
    
    def extract_keywords(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        sections: Optional[Dict] = None,
        max_keywords: int = 15
    ) -> List[str]:
        """Extract keywords/phrases that summarize the paper's main topics"""
        if not text:
            return []

        def normalize_keyword(keyword: str) -> str:
            """Create a normalized form for deduplication"""
            return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', keyword.lower())).strip()

        def title_case_keyword(keyword: str) -> str:
            """Convert keyword to title case while preserving acronyms"""
            words = keyword.split()
            title_cased = []
            for word in words:
                if word.isupper() and len(word) > 1:
                    title_cased.append(word)
                else:
                    title_cased.append(word.capitalize())
            return " ".join(title_cased)

        pattern = re.compile(r"[A-Za-z][A-Za-z0-9\-]+")
        word_freq: Dict[str, float] = {}
        word_degree: Dict[str, float] = {}
        phrase_candidates: Dict[str, Dict[str, Any]] = {}
        acronym_counts: Dict[str, int] = {}

        declared_keywords = self._extract_declared_keywords(text)
        normalized_declared = {
            normalize_keyword(keyword): keyword for keyword in declared_keywords
        }

        def register_phrase(token_pairs: List[tuple], weight: float):
            if not token_pairs:
                return

            segment_len = len(token_pairs)
            if segment_len == 1 and len(token_pairs[0][0]) < 4:
                return

            phrase_lower = " ".join(tok[0] for tok in token_pairs)
            letters_only = "".join(ch for ch in phrase_lower if ch.isalpha())
            if len(letters_only) < 4:
                return

            display_phrase = " ".join(tok[1] for tok in token_pairs)

            phrase_entry = phrase_candidates.setdefault(
                phrase_lower,
                {
                    "score": 0.0,
                    "weight": 0.0,
                    "length": segment_len,
                    "display": display_phrase,
                    "count": 0
                }
            )

            phrase_entry["weight"] += weight
            phrase_entry["count"] += 1
            if phrase_entry["count"] == 1:
                # Preserve casing from the first occurrence
                phrase_entry["display"] = display_phrase

            for token_lower, _ in token_pairs:
                word_freq[token_lower] = word_freq.get(token_lower, 0.0) + weight
                word_degree[token_lower] = word_degree.get(token_lower, 0.0) + weight * (segment_len - 1)

        def process_text(source_text: str, weight: float):
            if not source_text:
                return

            tokens = [
                (match.group(0).lower(), match.group(0))
                for match in pattern.finditer(source_text)
            ]

            if not tokens:
                return

            current_phrase: List[tuple] = []

            for token_lower, token_original in tokens:
                if token_lower in self.keyword_stop_words or len(token_lower) < 3:
                    if current_phrase:
                        register_phrase(current_phrase, weight)
                        current_phrase = []
                else:
                    current_phrase.append((token_lower, token_original))

            if current_phrase:
                register_phrase(current_phrase, weight)

        def track_acronyms(source_text: str, weight: float = 1.0):
            if not source_text:
                return
            for match in re.finditer(r'\b[A-Z]{2,}(?:[A-Z\d]+)?\b', source_text):
                token = match.group(0)
                if len(token) <= 2:  # skip trivial acronyms
                    continue
                acronym_counts[token] = acronym_counts.get(token, 0) + weight

        # Gather candidate text pools with weights
        title = metadata.get("title") if metadata else ""
        abstract = sections.get("abstract") if sections else ""
        introduction = sections.get("introduction") if sections else ""
        conclusion = sections.get("conclusion") if sections else ""

        process_text(title, weight=3.0)
        process_text(abstract, weight=2.5)
        process_text(introduction, weight=1.5)
        process_text(conclusion, weight=1.3)
        process_text(text, weight=1.0)

        track_acronyms(title, weight=2.0)
        track_acronyms(abstract, weight=2.0)
        track_acronyms(text, weight=1.0)

        if not word_freq or not phrase_candidates:
            return [
                title_case_keyword(keyword)
                for keyword in declared_keywords[:max_keywords]
            ]

        word_scores = {
            token: (word_degree[token] + word_freq[token]) / word_freq[token]
            for token in word_freq
        }

        phrase_scores: List[Tuple[str, float]] = []
        for phrase_lower, data in phrase_candidates.items():
            tokens = phrase_lower.split()
            token_scores = [word_scores.get(token, 0.0) for token in tokens]
            score = sum(token_scores) * data["weight"] * (1.0 + 0.15 * (data["length"] - 1))
            # Slight boost for phrases seen multiple times
            score *= math.log1p(data["count"] + 1)
            phrase_scores.append((phrase_lower, score))

        ranked_keywords = sorted(
            phrase_scores,
            key=lambda item: item[1],
            reverse=True
        )

        keywords: List[str] = []
        seen_keys: set = set()

        def add_keyword(keyword: str):
            token_count = len(keyword.split())
            if token_count == 0 or token_count > 3:
                return False
            normalized = normalize_keyword(keyword)
            if not normalized or normalized in seen_keys:
                return False
            seen_keys.add(normalized)
            keywords.append(title_case_keyword(keyword))
            return True

        # Prioritize declared keywords
        for original in declared_keywords:
            if len(keywords) >= max_keywords:
                break
            add_keyword(original)

        for phrase_lower, score in ranked_keywords:
            data = phrase_candidates[phrase_lower]
            normalized_key = phrase_lower.replace("-", " ")

            if normalized_key in seen_keys:
                continue

            if not add_keyword(data["display"]):
                continue

            if len(keywords) >= max_keywords:
                break

        # Add acronyms if we still have room
        if len(keywords) < max_keywords:
            sorted_acronyms = sorted(
                acronym_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )
            for acronym, score in sorted_acronyms:
                if len(keywords) >= max_keywords:
                    break
                add_keyword(acronym)

        return keywords

    def _extract_declared_keywords(self, text: str) -> List[str]:
        """Extract author-provided keywords from explicit sections"""
        if not text:
            return []

        declared_keywords: List[str] = []
        keyword_sections: List[str] = []

        keyword_patterns = [
            re.compile(r'\bkeywords?\s*[:\-]\s*(.+)', re.IGNORECASE),
            re.compile(r'\bindex\s+terms?\s*[:\-]\s*(.+)', re.IGNORECASE),
            re.compile(r'\bkey\s+phrases?\s*[:\-]\s*(.+)', re.IGNORECASE)
        ]

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            for pattern in keyword_patterns:
                match = pattern.search(stripped)
                if match:
                    keyword_sections.append(match.group(1))
                    break

        for section in keyword_sections:
            tokens = re.split(r'[;,]', section)
            for token in tokens:
                candidate = token.strip()
                candidate = candidate.rstrip('.;:')
                if len(candidate) < 3:
                    continue
                if len(candidate.split()) > 3:
                    continue
                declared_keywords.append(candidate)

        # Deduplicate while preserving order
        seen = set()
        unique_keywords = []
        for keyword in declared_keywords:
            normalized = re.sub(r'\s+', ' ', keyword.lower()).strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_keywords.append(keyword)

        return unique_keywords
    
    def parse_pdf_advanced(self, pdf_path: str) -> Dict:
        """Main method to parse PDF with all advanced features"""
        layout_data = self.extract_text_with_layout(pdf_path)
        
        # If title extraction failed, try to get it from filename
        if layout_data.get('title', '') == 'Unknown Title':
            filename_title = self._extract_title_from_filename(pdf_path)
            if filename_title != 'Unknown Title':
                print(f"DEBUG - Using filename title: '{filename_title}'")
                layout_data['title'] = filename_title
        
        # Extract all advanced features
        citations = self.extract_citations(layout_data['full_text'])
        reference_map = self.extract_references(layout_data['full_text'])
        figures_tables = self.extract_figures_tables(layout_data['full_text'], layout_data['pages'], pdf_path)
        math_content: List[MathematicalContent] = []
        from .pdf_handler import split_into_sections
        sections = split_into_sections(layout_data['full_text'])

        keywords = self.extract_keywords(
            layout_data['full_text'],
            metadata=layout_data,
            sections=sections
        )
        
        return {
            'sections': sections,
            'citations': citations,
            'figures_tables': figures_tables,
            'mathematical_content': math_content,
            'keywords': keywords,
            'references': reference_map,
            'metadata': {
                'total_pages': layout_data['total_pages'],
                'title': layout_data.get('title', 'Unknown Title'),
                'headings': layout_data.get('headings', []),
                'total_citations': len(citations),
                'total_figures': len([ft for ft in figures_tables if ft.content_type == 'figure']),
                'total_tables': len([ft for ft in figures_tables if ft.content_type == 'table'])
            }
        }
