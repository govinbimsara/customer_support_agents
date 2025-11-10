import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from agents directory
env_path = Path(__file__).parent.parent / "agents" / ".env"
load_dotenv(env_path)

def _get_required_env(key: str, default: str | None = None) -> str:
    """Get required environment variable or raise error."""
    value = os.environ.get(key, default)
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

# RAG Settings
DEFAULT_TOP_K = 3
DEFAULT_DISTANCE_THRESHOLD = 0.5


def get_project_id() -> str:
    """Get project ID from environment."""
    project_id = os.environ.get("PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("PROJECT not set")
    return project_id


def get_location() -> str:
    """Get location from environment."""
    return os.environ.get("LOCATION") or os.environ.get("GOOGLE_CLOUD_LOCATION", "europe-west4")


def get_corpus_id() -> str:
    """Get corpus ID from environment."""
    corpus_id = os.environ.get("CORPUS_ID")
    if not corpus_id:
        raise ValueError("CORPUS_ID not set")
    return corpus_id



