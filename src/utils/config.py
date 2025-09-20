"""Configuration management for TrustMed AI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTORS_DIR = DATA_DIR / "vectors"

# API Configuration
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "trustmed.ai@example.com")
UMLS_API_KEY = os.getenv("UMLS_API_KEY")
UMLS_USERNAME = os.getenv("UMLS_USERNAME")

# Reddit API (Optional)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "TrustMedAI/1.0")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///trustmed_ai.db")

# Vector Database
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", str(VECTORS_DIR))

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
LANGUAGE_MODEL = os.getenv("LANGUAGE_MODEL", "microsoft/DialoGPT-medium")

# Scraping Configuration
SCRAPING_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Medical Journals to track
MEDICAL_JOURNALS = [
    "New England Journal of Medicine",
    "JAMA",
    "The Lancet",
    "BMJ",
    "Nature Medicine"
]

# Reddit medical subreddits
MEDICAL_SUBREDDITS = [
    "AskDocs",
    "medical",
    "diagnosed",
    "health",
    "medicine"
]

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, VECTORS_DIR]:
    directory.mkdir(exist_ok=True)

