"""Configuration settings for the application."""

import os
from typing import Literal
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application configuration."""

    GOOGLE_GENAI_USE_VERTEXAI: str = os.getenv(
        "GOOGLE_GENAI_USE_VERTEXAI", "TRUE"
    )
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    SUPPORTED_LANGUAGES: list[Literal["english", "sinhala", "tamil"]] = [
        "english",
        "sinhala",
        "tamil",
    ]
    
    INTENTS: list[Literal["knowledge_base", "lodge_complaint", "check_status"]] = [
        "knowledge_base",
        "lodge_complaint",
        "check_status",
    ]


settings = Settings()
