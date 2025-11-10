"""ComplaintFlow Agent implementation."""

import logging
import sys
from pathlib import Path
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from prompts.complaint_flow_prompt import COMPLAINT_FLOW_PROMPT
from tools.ticket import create_jira_ticket

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
    user_id = state.get("user_id", None)
    callback_context.instruction = COMPLAINT_FLOW_PROMPT.format(
        language=language, user_id=user_id
    )
    logger.info(
        f"ComplaintFlow Agent - Language: {language}, User ID: {user_id}"
    )

    return None

complaint_flow_agent = LlmAgent(
    name="complaint_flow_agent",
    model="gemini-2.5-flash",
    instruction=COMPLAINT_FLOW_PROMPT,
    description="Agent for handling customer complaints",
    tools=[create_jira_ticket],
    before_agent_callback=before_agent_callback,
    generate_content_config=types.GenerationConfig(
        temperature=0.3,
        top_k=40,
        top_p=0.8,
        # candidate_count=1,
        # max_output_tokens=2048,
    ),
    
)
