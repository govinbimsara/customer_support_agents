"""Supervisor Agent - Root agent for trilingual customer service."""

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
# from google.adk.agents.events_compaction_config import EventsCompactionConfig

from google.adk.plugins.context_filter_plugin import ContextFilterPlugin
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from prompts.supervisor_prompt import SUPERVISOR_PROMPT
from agents.sub_agents.knowledge_base_agent.agent import knowledge_base_agent
from agents.sub_agents.complaint_flow_agent.agent import complaint_flow_agent
from agents.sub_agents.status_check_agent.agent import status_check_agent


from tools .set_language import set_language
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Any, Dict, Optional
from google.genai import types


def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    """Write language to state after set_language tool is called."""
    if tool.name == 'set_language':
        language = args.get('language')
        if language:
            tool_context.state['language'] = language
            print(f"Language set to {language}")

    user_id = tool_context._invocation_context.user_id
    if user_id:
        print(f"User ID: {user_id}")
        tool_context.state['user_id'] = user_id
    

    
    return None

root_agent = Agent(
    name="supervisor_agent",
    model="gemini-2.5-flash",
    instruction=SUPERVISOR_PROMPT,
    description="Supervisor agent for trilingual customer service",
    sub_agents=[knowledge_base_agent,complaint_flow_agent,status_check_agent],
    # sub_agents=[knowledge_base_agent_eng,knowledge_base_agent_multi],
    tools=[set_language],
    after_tool_callback=after_tool_callback,
    generate_content_config=types.GenerationConfig(
        temperature=0.3,
        top_k=40,
        top_p=0.8,
        # candidate_count=1,
        # max_output_tokens=2048,
    ),
)

app = App(
    name="agents",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=1500,
        ttl_seconds=600,  # 10 mins for conversation
        cache_intervals=5,  # Maximum invocations before cache refresh
    ),
    # events_compaction_config=EventsCompactionConfig(
    #     compaction_interval=3,
    #     overlap_size=1
    # ),
    plugins=[
        ContextFilterPlugin(num_invocations_to_keep=10)  # Keep last 5 interactions
    ]
)
