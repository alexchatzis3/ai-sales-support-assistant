"""
Application settings and constants.
"""

from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

# OpenAI models
CHAT_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"

# RAG settings
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K_RESULTS = 5

# Memory settings
KEEP_RECENT_MESSAGES = 5