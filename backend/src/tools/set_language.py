"""This tool used by supervisor_agent to set the language"""

def set_language(language: str) -> str:
    """Set the detected language in state.
    
    Args:
        language: The detected language ('english', 'sinhala', or 'tamil')
        
    Returns:
        Confirmation message
    """
    return f"Language set to {language}"