"""ComplaintFlow Agent implementation."""

from google.adk.agents import LlmAgent
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# from schemas.complaint_schemas import ComplaintOutput
from prompts.complaint_flow_prompt import COMPLAINT_FLOW_PROMPT
from tools.ticket import create_jira_ticket
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Read language from state and update instruction."""
    state = callback_context.state
    if "language" not in state:
        state["language"] = "english"
    
    language = state.get("language", "english")
    user_id = state.get("user_id", None)
    callback_context.instruction = COMPLAINT_FLOW_PROMPT.format(language=language, user_id=user_id)
    print(f"Language: {language}")
    print(f"User ID: {user_id}")
    
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
