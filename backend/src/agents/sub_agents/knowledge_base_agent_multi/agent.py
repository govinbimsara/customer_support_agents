"""KnowledgeBase Agent implementation."""

from google.adk.agents import LlmAgent
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.rag_engine import query_knowledge_base
from prompts.knowledge_base_prompt import KNOWLEDGE_BASE_PROMPT
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Read language from state and update instruction."""
    state = callback_context.state
    if "language" not in state:
        state["language"] = "english"
    
    language = state.get("language", "english")
    callback_context.instruction = KNOWLEDGE_BASE_PROMPT.format(language=language)
    print(f"Language: {language}")
    
    return None

knowledge_base_agent_multi = LlmAgent(
    name="knowledge_base_agent_multi",
    model="gemini-2.5-flash",
    instruction=KNOWLEDGE_BASE_PROMPT,
    description="Agent for handling general inquiries",
    tools=[query_knowledge_base],
    before_agent_callback=before_agent_callback,
)
