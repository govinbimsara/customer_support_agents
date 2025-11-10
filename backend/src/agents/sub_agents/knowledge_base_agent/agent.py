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
        state["language"] = "English"
    
    language = state.get("language", "English")
    callback_context.instruction = KNOWLEDGE_BASE_PROMPT.format(language=language)
    print(f"Language: {language}")
    
    return None

knowledge_base_agent = LlmAgent(
    name="knowledge_base_agent",
    model="gemini-2.5-flash-lite",
    instruction=KNOWLEDGE_BASE_PROMPT,
    description="Agent for handling general inquiries",
    tools=[query_knowledge_base],
    before_agent_callback=before_agent_callback,
    generate_content_config=types.GenerationConfig(
        temperature=0.4,
        top_k=40,
        top_p=0.8,
        # candidate_count=1,
        # max_output_tokens=2048,
    ),
)
