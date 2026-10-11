"""
PROJECTIQ - Central Configuration
Loads environment variables and exposes application-wide constants.
Never hardcode secrets here; values are read from the environment / .env file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ------------------------------------------------------------------
# Load .env file if present (safe no-op if the file does not exist)
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ------------------------------------------------------------------
# Secrets / external services (never expose these to the browser -
# Streamlit renders server-side, so this is safe by construction)
# ------------------------------------------------------------------
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "").strip()

# ------------------------------------------------------------------
# Database
# ------------------------------------------------------------------
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

PROJECTS_DIR = STORAGE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{(STORAGE_DIR / 'projectiq.db').as_posix()}")

# ------------------------------------------------------------------
# Upload safety limits
# ------------------------------------------------------------------
MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "100"))
MAX_UPLOAD_BYTES: int = MAX_UPLOAD_MB * 1024 * 1024
MAX_FILES_PER_PROJECT: int = 4000
MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB per individual file read for analysis

ALLOWED_UPLOAD_EXTENSIONS = {".zip"}

IGNORED_DIRECTORIES = {
    "node_modules", ".git", "venv", ".venv", "env", "__pycache__",
    "dist", "build", ".next", ".idea", ".vscode", "target", "bin", "obj",
    ".pytest_cache", ".mypy_cache", "coverage", ".tox", "egg-info",
}

IGNORED_FILE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".bmp",
    ".mp4", ".mov", ".avi", ".mp3", ".wav", ".pdf", ".zip", ".tar",
    ".gz", ".rar", ".7z", ".exe", ".dll", ".so", ".dylib", ".class",
    ".pyc", ".woff", ".woff2", ".ttf", ".eot", ".db", ".sqlite",
}

# ------------------------------------------------------------------
# Application metadata
# ------------------------------------------------------------------
APP_NAME = "PROJECTIQ"
APP_TAGLINE = "Understand. Evaluate. Evolve."

GEMINI_MODEL_NAME = "gemini-1.5-flash"


def gemini_configured() -> bool:
    """Whether a Gemini API key has been supplied."""
    return bool(GEMINI_API_KEY)


def github_configured() -> bool:
    """Whether a GitHub token has been supplied (optional integration)."""
    return bool(GITHUB_TOKEN)
