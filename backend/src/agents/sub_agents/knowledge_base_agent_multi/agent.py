"""KnowledgeBase Agent implementation."""

import logging
import sys
from pathlib import Path
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.rag_engine import query_knowledge_base
from prompts.knowledge_base_prompt import KNOWLEDGE_BASE_PROMPT

logger = logging.getLogger(__name__)
# amazonq-ignore-next-line

def before_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Read language from state and update instruction."""
    state = callback_context.state
    if "language" not in state:
        state["language"] = "english"

    language = state.get("language", "english")
    callback_context.instruction = KNOWLEDGE_BASE_PROMPT.format(
        language=language
    )
    logger.info(f"KnowledgeBase Agent - Language: {language}")

    return None

knowledge_base_agent_multi = LlmAgent(
    name="knowledge_base_agent_multi",
    model="gemini-2.5-flash",
    instruction=KNOWLEDGE_BASE_PROMPT,
    description="Agent for handling general inquiries",
    tools=[query_knowledge_base],
    before_agent_callback=before_agent_callback,
)
