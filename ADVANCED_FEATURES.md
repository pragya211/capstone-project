# Advanced PDF Processing Features

This document describes the enhanced text processing capabilities added to the research paper summarizer.

## Overview

The advanced PDF processor extends the basic summarization functionality with sophisticated text analysis capabilities including:

- **Citation Extraction**: Identifies and extracts various types of citations
- **Figure/Table Detection**: Locates figures and tables with their captions
- **Mathematical Content**: Extracts equations and mathematical expressions
- **Keyword Extraction**: Identifies important terms and concepts
- **Enhanced Section Analysis**: Improved document structure analysis

## New Components

### 1. Advanced PDF Parser (`backend/services/advanced_pdf_parser.py`)

The `AdvancedPDFParser` class provides comprehensive PDF analysis:

```python
from backend.services.advanced_pdf_parser import AdvancedPDFParser

parser = AdvancedPDFParser()
result = parser.parse_pdf_advanced("path/to/paper.pdf")
```

**Features:**
- Layout-aware text extraction
- Multiple citation format recognition
- Figure/table caption extraction
- Mathematical content detection
- Keyword frequency analysis

### 2. Advanced Processing Routes (`backend/routes/advanced_processing.py`)

New API endpoints for advanced processing:

- `POST /advanced/advanced-extract` - Complete advanced analysis
- `POST /advanced/extract-citations-only` - Citations only
- `POST /advanced/extract-figures-tables` - Figures and tables only
- `POST /advanced/extract-mathematical-content` - Mathematical content only

### 3. Enhanced Frontend (`capstone-ui/src/AdvancedPdfProcessor.js`)

New React component with tabbed interface showing:
- Document overview with statistics
- Citation analysis
- Figure and table listings
- Mathematical content
- Keyword extraction

## Citation Detection

The system recognizes multiple citation formats:

### Author-Year Format
- `Smith (2023)`
- `Johnson et al. (2022)`
- `Brown and Davis (2021)`

### Numbered Citations
- `[1]`
- `[2, 3, 5]`
- `[1-5]`

### Footnote Citations
- `^1`
- `^2`

## Figure and Table Detection

Automatically identifies:
- **Figures**: "Figure 1:", "Fig. 2", etc.
- **Tables**: "Table 1:", "Tab. 2", etc.

Extracts associated captions and tracks page numbers.

## Mathematical Content

Detects various mathematical expressions:

### Inline Math
- `$x = y + z$`

### Display Math
- `$$E = mc^2$$`

### LaTeX Equations
- `\begin{equation}...\end{equation}`

### Simple Equations
- `x = y + z`
- `f(x) > 0`

## Keyword Extraction

Identifies important terms by:
- Frequency analysis
- Capitalization patterns
- Length filtering
- Context analysis

## Usage Examples

### Backend API Usage

```python
import requests

# Upload PDF for advanced processing
with open("paper.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/advanced/advanced-extract",
        files=files
    )

data = response.json()
print(f"Found {data['data']['metadata']['total_citations']} citations")
```

### Frontend Integration

```javascript
// The AdvancedPdfProcessor component provides a complete UI
import AdvancedPdfProcessor from './AdvancedPdfProcessor';

function App() {
  return <AdvancedPdfProcessor />;
}
```

## API Response Format

```json
{
  "status": "success",
  "data": {
    "sections": {
      "abstract": "...",
      "introduction": "...",
      "main_body": "..."
    },
    "citations": [
      {
        "text": "Smith (2023)",
        "citation_type": "author_year",
        "authors": ["Smith"],
        "year": "2023",
        "position": 1234
      }
    ],
    "figures_tables": [
      {
        "caption": "Experimental setup...",
        "label": "Figure 1",
        "content_type": "figure",
        "page_number": 3
      }
    ],
    "mathematical_content": [
      {
        "equation": "E = mc^2",
        "equation_type": "display_math",
        "page_number": 5
      }
    ],
    "keywords": ["machine learning", "neural networks", ...],
    "metadata": {
      "total_pages": 10,
      "total_citations": 25,
      "total_figures": 5,
      "total_tables": 3,
      "total_equations": 8
    }
  }
}
```

## Testing

Run the test script to verify functionality:

```bash
cd capstone_project
python test_advanced_features.py
```

## Dependencies

The advanced features require the same dependencies as the basic system:
- `PyMuPDF` for PDF processing
- `FastAPI` for the backend API
- `React` for the frontend

## Performance Considerations

- Large PDFs may take longer to process
- Mathematical content detection is regex-based and may miss complex LaTeX
- Citation extraction works best with standard academic formats
- Figure/table detection relies on common caption patterns

## Future Enhancements

Potential improvements include:
- Machine learning-based citation extraction
- Image recognition for figure analysis
- LaTeX equation parsing
- Multi-language support
- Citation network analysis
