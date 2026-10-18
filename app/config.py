"""Reads all settings from the .env file in the project root."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.8-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))

# Project settings (simple constants)
DOCS_DIR = PROJECT_ROOT / "docs"          # uploaded files are stored here
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
CHUNK_SIZE = 1000                         # characters per chunk
CHUNK_OVERLAP = 200                       # characters shared between chunks
DEFAULT_TOP_K = 5


def get_database_url() -> str:
    
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing. Add it to the .env file.")
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def require_gemini_key() -> str:
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("your_"):
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to the .env file.")
    return GEMINI_API_KEY
