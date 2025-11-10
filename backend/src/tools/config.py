import os
from dotenv import load_dotenv

load_dotenv()


def _get_required_env(key: str) -> str:
    """Get required environment variable or raise error."""
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


# Vertex AI settings
PROJECT_ID = _get_required_env("GOOGLE_CLOUD_PROJECT")
LOCATION = _get_required_env("GOOGLE_CLOUD_LOCATION")

# RAG Settings
DEFAULT_TOP_K = 3
DEFAULT_DISTANCE_THRESHOLD = 0.5
CORPUS_ID = _get_required_env("CORPUS_ID")