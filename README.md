# AI Research Paper Analysis Toolkit

An intelligent web application that automates the analysis of academic research papers using AI-powered extraction, summarization, and assessment capabilities. This tool helps researchers quickly understand paper content, identify missing sections, and receive actionable recommendations for improvement.

## 📋 Table of Contents

- [Features](#features)
- [Project Description](#project-description)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **PDF Processing & Extraction**
  - Automatic section extraction (Abstract, Introduction, Main Body)
  - Advanced citation detection and parsing
  - Figure and table identification with captions
  - Keyword extraction and frequency analysis
  - Mathematical content detection

- **AI-Powered Analysis**
  - Automated research paper assessment
  - Completeness scoring with detailed breakdowns
  - Missing content identification (Critical, Important, Beneficial)
  - Section-specific analysis (Methodology, Literature Review, Results, Discussion)
  - Strengths and weaknesses analysis
  - Actionable recommendations

- **Summarization**
  - AI-generated summaries for each paper section
  - Customizable summary length
  - Enhanced extraction with metadata

- **User Authentication**
  - Secure JWT-based authentication
  - User registration and login
  - Protected routes for advanced features

- **Modern UI**
  - Responsive React frontend
  - Dark theme with light/dark text adaptation
  - Tabbed interface for different features
  - Real-time processing status

## 📖 Project Description

This capstone project is a comprehensive research paper analysis platform that combines PDF parsing, AI-powered content analysis, and automated assessment capabilities. The system processes academic PDFs to extract structured information, generate summaries, and provide detailed assessments of paper completeness and quality.

The application is built with a FastAPI backend for robust API services and a React frontend for an intuitive user experience. It leverages OpenAI's API for intelligent content analysis and summarization.

**Key Capabilities:**
- Extract and structure content from research PDFs
- Identify citations, figures, tables, and keywords
- Generate AI-powered summaries
- Assess paper completeness and quality
- Provide detailed recommendations for improvement
- Support both quick analysis and comprehensive assessment modes

## 🛠 Tech Stack

**Backend:**
- Python 3.10+
- FastAPI - Modern, fast web framework
- SQLAlchemy - Database ORM
- PyMuPDF (fitz) - PDF parsing
- OpenAI API - AI-powered analysis
- JWT - Authentication
- SQLite/PostgreSQL - Database

**Frontend:**
- React 19.1.1
- Axios - HTTP client
- Modern CSS with CSS Variables
- Responsive design

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+ and npm** - [Download Node.js](https://nodejs.org/)
- **OpenAI API Key** - [Get API Key](https://platform.openai.com/api-keys)
- **Git** (optional) - For cloning the repository

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd capstone_project
```

### 2. Backend Setup

Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `capstone_project/` directory:

```env
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=sqlite:///./app.db
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=development
```

**Note:** Generate a secure JWT secret key:
```bash
# Using OpenSSL
openssl rand -hex 32
```

### 4. Frontend Setup

```bash
cd capstone-ui
npm install
```

### 5. Start the Application

**Option 1: Run Both Services Together (Recommended for Development)**

From the `capstone-ui` directory:
```bash
npm start
```

This will start both the backend (port 8000) and frontend (port 3000) concurrently.

**Option 2: Run Services Separately**

Terminal 1 - Backend:
```bash
cd capstone_project
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 - Frontend:
```bash
cd capstone-ui
npm run start-frontend
```

The application will be available at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000
- **API Documentation:** http://127.0.0.1:8000/docs

## 💻 Usage

### Basic Workflow

1. **Access the Application**
   - Open http://localhost:3000 in your browser
   - The app will load with a modern, dark-themed interface

2. **Create an Account (Optional)**
   - Click "Sign Up" in the header
   - Enter your email and password (minimum 8 characters)
   - Advanced features require authentication

3. **Upload a Research Paper**
   - Navigate to the "Basic PDF Processor" tab
   - Click "Choose PDF File" and select your research paper
   - The system will automatically extract sections

4. **Generate Summaries**
   - After extraction, click "Generate Summaries"
   - AI-powered summaries will appear for Abstract, Introduction, and Main Body sections

5. **Advanced Analysis (Requires Login)**
   - Log in to access advanced features
   - Upload a PDF in the "Advanced PDF Processor" tab
   - View extracted citations, figures, tables, and keywords
   - Generate detailed metadata and insights

6. **Research Assessment (Requires Login)**
   - Navigate to the "Research Assessment" tab
   - Choose assessment mode:
     - **Quick Analysis:** Fast assessment focusing on critical issues
     - **Comprehensive Assessment:** Detailed analysis with all sections
   - Upload your paper and click "Start Assessment"
   - Review completeness scores, missing content, strengths, weaknesses, and recommendations

### Key Features Guide

**Basic PDF Processor:**
- Quick section extraction
- AI summarization
- No authentication required

**Advanced PDF Processor:**
- Comprehensive extraction (citations, figures, tables, keywords)
- Document overview with statistics
- Detailed metadata analysis
- Requires authentication

**Research Assessment:**
- Paper completeness scoring
- Missing content identification
- Section-specific analysis
- Actionable recommendations
- Requires authentication

## 🔌 API Endpoints

### Authentication
- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user information

### PDF Processing
- `POST /extract/upload` - Basic PDF section extraction
- `POST /enhanced/enhanced-extract` - Enhanced extraction with metadata
- `POST /advanced/advanced-extract` - Full advanced processing
- `POST /advanced/extract-citations-only` - Extract citations only
- `POST /advanced/extract-figures-tables` - Extract figures and tables only

### Summarization
- `POST /summarize/` - Generate AI summaries for sections

### Assessment
- `POST /assess/assess-paper` - Run research paper assessment
  - Query parameter: `mode=quick` or `mode=comprehensive`

### Interactive API Documentation
Visit http://127.0.0.1:8000/docs for interactive Swagger UI documentation with request/response schemas.

## 🔐 Environment Variables

### Backend (.env)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Yes | - |
| `DATABASE_URL` | Database connection string | No | `sqlite:///./app.db` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes | - |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No | `60` |
| `ENVIRONMENT` | Environment mode (development/production) | No | `development` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | No | `http://localhost:3000,http://127.0.0.1:3000` |

### Frontend (.env)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `REACT_APP_API_BASE_URL` | Backend API base URL | No | `http://127.0.0.1:8000` |

## 🌐 Deployment

### Backend Deployment (Railway/Render)

1. **Prepare for Deployment**
   - Ensure `Procfile` exists with: `web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add `runtime.txt` with Python version: `python-3.11`

2. **Deploy to Railway**
   - Connect GitHub repository
   - Railway auto-detects Python
   - Add environment variables in dashboard
   - Deploy automatically

3. **Deploy to Render**
   - Create new Web Service
   - Connect repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

### Frontend Deployment (Vercel)

1. **Build the Application**
   ```bash
   cd capstone-ui
   npm run build
   ```

2. **Deploy to Vercel**
   - Connect GitHub repository
   - Set root directory to `capstone-ui`
   - Add environment variable: `REACT_APP_API_BASE_URL` = your backend URL
   - Deploy

3. **Update Backend CORS**
   - Add your Vercel URL to `ALLOWED_ORIGINS` in backend environment variables
   - Set `ENVIRONMENT=production` in backend

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md) and [QUICK_DEPLOY.md](./QUICK_DEPLOY.md).

## 🧪 Testing

### Backend Tests

```bash
cd capstone_project
pytest
```

### Frontend Tests

```bash
cd capstone-ui
npm test
```

### Manual Testing

- Test PDF upload and extraction
- Verify authentication flow
- Test assessment generation
- Check API endpoints using `/docs`

## 📁 Project Structure

```
capstone_project/
├── backend/                    # FastAPI backend application
│   ├── __init__.py
│   ├── main.py                 # API entry point and CORS configuration
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and session management
│   ├── routes/                  # API route handlers
│   │   ├── auth.py             # Authentication routes
│   │   ├── upload.py           # Basic PDF upload
│   │   ├── summarize.py        # Summarization endpoints
│   │   ├── advanced_processing.py  # Advanced extraction
│   │   ├── enhanced_basic.py   # Enhanced basic extraction
│   │   └── research_assessment.py  # Assessment endpoints
│   ├── services/                # Business logic services
│   │   ├── pdf_handler.py      # PDF parsing utilities
│   │   ├── advanced_pdf_parser.py  # Advanced PDF analysis
│   │   ├── assessment_service.py   # Assessment logic
│   │   └── auth.py             # Authentication utilities
│   ├── models/                  # Database models
│   │   └── user.py             # User model
│   └── schemas/                 # Pydantic schemas
│       └── auth.py              # Authentication schemas
├── capstone-ui/                 # React frontend
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── LoginForm.js
│   │   │   └── SignupForm.js
│   │   ├── context/             # React context
│   │   │   └── AuthContext.js
│   │   ├── App.js               # Main app component
│   │   ├── App.css              # Main styles
│   │   ├── index.css            # Global styles
│   │   ├── apiClient.js         # API client configuration
│   │   ├── pdfUploader.js       # Basic PDF processor
│   │   ├── AdvancedPdfProcessor.js  # Advanced processor
│   │   └── ResearchAssessment.js    # Assessment component
│   ├── package.json
│   └── package-lock.json
├── models/                      # External API wrappers
├── tests/                       # Test files
├── uploads/                     # Uploaded PDF storage
├── requirements.txt             # Python dependencies
├── Procfile                     # Deployment configuration
├── runtime.txt                  # Python version
├── vercel.json                  # Vercel configuration
├── README.md                    # This file
├── DEPLOYMENT.md                # Detailed deployment guide
└── QUICK_DEPLOY.md              # Quick deployment guide
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository** or create a feature branch
2. **Make your changes** following the existing code style
3. **Test your changes** thoroughly
4. **Ensure code quality**
   - Run backend tests: `pytest`
   - Run frontend linting: `npm test`
   - Check formatting
5. **Submit a Pull Request** with:
   - Clear description of changes
   - Testing performed
   - Any new configuration required
   - Screenshots (if UI changes)

### Code Style Guidelines

- **Python:** Follow PEP 8 style guide
- **JavaScript/React:** Use consistent formatting, prefer functional components
- **Commit Messages:** Use clear, descriptive commit messages

## 📄 License

This project is provided as-is for academic capstone use. 

**License:** MIT License (or specify your preferred license)

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment help
- Review API documentation at `/docs` endpoint

## 🙏 Acknowledgments

- OpenAI for API services
- FastAPI for the excellent web framework
- React team for the frontend framework
- All open-source contributors whose libraries made this project possible

---

**Note:** This project requires an OpenAI API key for full functionality. Ensure you have sufficient API credits and are aware of usage costs.
