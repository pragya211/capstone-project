# Capstone Project

AI-assisted research paper analysis toolkit featuring advanced PDF parsing, citation enrichment, and automated assessments.

## Overview
- Extracts structured content (sections, citations, figures/tables, keywords) from research PDFs.
- Runs AI-powered assessments to highlight missing content, strengths, and recommendations.
- Generates targeted summaries and visual explanations for figures/tables.
- Provides a React front-end for uploading papers and exploring the processed insights.
- Includes email/password authentication with JWT-protected APIs.

## Project Structure
```
capstone_project/
├── backend/                # FastAPI application
│   ├── main.py             # API entry point
│   ├── routes/             # Feature-specific routes
│   └── services/           # Parsing, assessment, and utility services
├── capstone-ui/            # React front-end
├── models/                 # External API wrappers (summarizer, vision)
├── tests/                  # Automated test scripts
└── requirements.txt        # Backend dependencies
```

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Git for cloning
- Valid `OPENAI_API_KEY` (required for assessment/summarization features)

## Backend Setup
```bash
cd capstone_project
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux
pip install --upgrade pip
pip install -r requirements.txt
```

Create `.env` in `capstone_project/` (or wherever you run the backend) and add:
```
OPENAI_API_KEY=your-openai-key
```

Start the API:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend Setup
```bash
cd capstone_project/capstone-ui
npm install
```

### Development Mode
- **Backend & Frontend separately:**  
  - Backend: `uvicorn backend.main:app --reload` (from `capstone_project/`)
  - Frontend: `npm run start-frontend` (from `capstone-ui/`)
- **Single command (requires `uvicorn` on PATH):**
  ```bash
  npm start
  ```
  This uses the `start` script to run both `react-scripts start` and the backend server concurrently.

The React app defaults to `http://localhost:3000` and expects the backend at `http://127.0.0.1:8000`.

## Environment Variables
Backend `.env` keys:
- `OPENAI_API_KEY` – required for title extraction, assessments, and AI-based summaries.
- `DATABASE_URL` – optional; defaults to `sqlite:///./app.db`.
- `JWT_SECRET_KEY` – secret used to sign JWT access tokens (change in production).
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` – optional token lifetime (default 60 minutes).

Frontend `.env` (optional):
- `REACT_APP_API_BASE_URL` – set to your deployed backend URL to avoid hard-coded endpoints.

## Authentication
- Visit the app and use the header controls to create an account or sign in.
- Authenticated users receive a JWT token stored locally and sent on subsequent API calls.
- Advanced processing and research assessment tools require a logged-in session; the basic summarizer remains open.

## Running Tests
Backend unit tests (Pytest):
```bash
cd capstone_project
pytest
```

Frontend lint/tests (Create React App defaults):
```bash
cd capstone_project/capstone-ui
npm test
```

## Deployment Notes
1. **Backend**: Deploy the FastAPI app on Render, Railway, Fly.io, etc. Ensure `uvicorn backend.main:app --host 0.0.0.0 --port 8000` is your start command and environment variables are configured.
2. **Frontend**: Build with `npm run build` and deploy the `build/` directory via Vercel, Netlify, or similar. Update API URLs (e.g., `REACT_APP_API_BASE_URL`) to target the hosted backend.
3. **Single Container**: Optionally package both services with Docker/Compose for platforms that support multi-service apps.

## Key API Endpoints
- `POST /advanced/advanced-extract` – Extract sections, enriched citations, figures/tables, keywords.
- `POST /advanced/extract-citations-only` – Return only the citation list.
- `POST /assess/assess-paper` – Run comprehensive research paper assessment.
- `POST /summarize/` – Generate section-wise AI summaries.
- `POST /auth/signup` – Register a new user account.
- `POST /auth/login` – Obtain a JWT access token (OAuth2 password flow).
- `GET /auth/me` – Fetch the currently authenticated user.

See the FastAPI auto docs at `http://127.0.0.1:8000/docs` for the full schema.

## Contributing
1. Fork or create a feature branch.
2. Ensure formatting/linting passes (`pytest`, `npm test` as applicable).
3. Open a PR describing the change, testing performed, and any new configuration required.

## License
This project is provided as-is for academic capstone use. Add a specific license if you plan to distribute it more broadly.