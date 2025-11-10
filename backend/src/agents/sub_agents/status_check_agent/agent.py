"""StatusCheck Agent implementation."""

import logging
import sys
from pathlib import Path
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ticket import get_user_tickets, get_ticket_by_key
from prompts.status_check_prompt import STATUS_CHECK_PROMPT

logger = logging.getLogger(__name__)

def before_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Read language from state and update instruction."""
    state = callback_context.state
    if "language" not in state:
        state["language"] = "english"

    language = state.get("language", "english")
    user_id = state.get("user_id", None)
    callback_context.instruction = STATUS_CHECK_PROMPT.format(
        language=language, user_id=user_id
    )
    logger.info(f"StatusCheck Agent - Language: {language}, User ID: {user_id}")

    return None


status_check_agent = LlmAgent(
    name="status_check_agent",
    model="gemini-2.5-flash",
    instruction=STATUS_CHECK_PROMPT,
    before_agent_callback=before_agent_callback,
    description="Agent for checking ticket status",
    tools=[get_user_tickets, get_ticket_by_key],
    generate_content_config=types.GenerationConfig(
        temperature=0.3,
        top_k=40,
        top_p=0.8,
        # candidate_count=1,
        # max_output_tokens=2048,
    ),
)
