"""This tool used by supervisor_agent to set the language"""

from typing import Literal


def set_language(
    language: Literal["english", "sinhala", "tamil"]
) -> str:
    """Set the detected language in state.
    
    Args:
        language: The detected language ('english', 'sinhala', or 'tamil')
        
    Returns:
        Confirmation message
        
    Raises:
        ValueError: If language is not one of the supported values
    """
    valid_languages = {"english", "sinhala", "tamil"}
    
    if language.lower() not in valid_languages:
        raise ValueError(
            f"Invalid language '{language}'. "
            f"Must be one of: {', '.join(valid_languages)}"
        )
    
    return f"Language set to {language.lower()}"