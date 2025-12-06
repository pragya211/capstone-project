import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routes import upload, summarize, advanced_processing, enhanced_basic, research_assessment, auth
from backend.models import user  # noqa: F401  # Ensure models are registered

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Capstone Project API")

# CORS Configuration - use environment variable in production
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://capstone-project-8dg9.vercel.app"
]


# In development, allow all origins; in production, use specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    # Development: allow all origins
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=["*"],
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )

# Register routes
app.include_router(upload.router, prefix="/extract", tags=["Extraction"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(advanced_processing.router, prefix="/advanced", tags=["Advanced Processing"])
app.include_router(enhanced_basic.router, prefix="/enhanced", tags=["Enhanced Basic"])
app.include_router(research_assessment.router, prefix="/assess", tags=["Research Assessment"])
app.include_router(auth.router)

# Optional root endpoint for health check
@app.get("/")
async def root():
    return {"message": "Capstone Project API is running"}


