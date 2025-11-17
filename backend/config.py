import os
from typing import List

# CORS Configuration
ALLOWED_ORIGINS: List[str] = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

