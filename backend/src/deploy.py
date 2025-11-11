"""Deployment script for Agent Engine."""

import copy
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any

import vertexai
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.artifacts import GcsArtifactService
from google.adk.plugins.context_filter_plugin import ContextFilterPlugin
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

sys.path.insert(0, str(Path(__file__).parent))

from deployment_config import config, get_deployment_config
from utils.gcs import create_bucket_if_not_exists
from agents.agent import root_agent


class AgentEngineApp(AdkApp):
    """ADK Application wrapper with App-level configurations."""

    def __init__(
        self,
        agent: Any,
        context_cache_config: ContextCacheConfig | None = None,
        plugins: list | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with agent and App-level configs."""
        super().__init__(agent=agent, **kwargs)
        self._context_cache_config = context_cache_config
        self._plugins = plugins

    def clone(self) -> "AgentEngineApp":
        """Create a copy of this application."""
        template_attributes = self._tmpl_attrs
        return self.__class__(
            agent=copy.deepcopy(template_attributes["agent"]),
            context_cache_config=self._context_cache_config,
            plugins=self._plugins,
            enable_tracing=bool(
                template_attributes.get("enable_tracing", False)
            ),
            session_service_builder=template_attributes.get(
                "session_service_builder"
            ),
            artifact_service_builder=template_attributes.get(
                "artifact_service_builder"
            ),
            env_vars=template_attributes.get("env_vars"),
        )


def deploy_agent_engine_app() -> agent_engines.AgentEngine:
    """Deploy the agent to Vertex AI Agent Engine."""
    print("🚀 Starting Agent Engine deployment...")

    deployment_config = get_deployment_config()
    print(f"📋 Deploying agent: {deployment_config.agent_name}")
    print(f"📋 Project: {deployment_config.project}")
    print(f"📋 Location: {deployment_config.location}")
    print(f"📋 Staging bucket: {deployment_config.staging_bucket}")

    env_vars = {
        "NUM_WORKERS": "1",
        "GOOGLE_GENAI_USE_VERTEXAI": "True",
        "PYTHONPATH": "/code/backend/src",
        # "GCP_PROJECT": deployment_config.project,
        # "GCP_LOCATION": deployment_config.location,
    }

    if deployment_config.corpus_id:
        env_vars["CORPUS_ID"] = deployment_config.corpus_id
        env_vars["PROJECT"] = deployment_config.project
        env_vars["LOCATION"] = deployment_config.location
        print(f"📋 Corpus ID: {deployment_config.corpus_id}")
        print(f"📋 Project: {deployment_config.project}")
        print(f"📋 Location: {deployment_config.location}")
        

    # Add Langfuse credentials if available
    langfuse_secret = os.environ.get("LANGFUSE_SECRET_KEY")
    langfuse_public = os.environ.get("LANGFUSE_PUBLIC_KEY")
    langfuse_url = os.environ.get("LANGFUSE_BASE_URL")

    if langfuse_secret and langfuse_public:
        env_vars["LANGFUSE_SECRET_KEY"] = langfuse_secret
        env_vars["LANGFUSE_PUBLIC_KEY"] = langfuse_public
        if langfuse_url:
            env_vars["LANGFUSE_BASE_URL"] = langfuse_url

    # Add JIRA credentials if available
    jira_project = os.environ.get("JIRA_PROJECT")
    if jira_project:
        env_vars["JIRA_PROJECT"] = jira_project
        env_vars["JIRA_CLOUD"] = os.environ.get("JIRA_CLOUD", "")
        env_vars["JIRA_EMAIL"] = os.environ.get("JIRA_EMAIL", "")
        env_vars["JIRA_TOKEN"] = os.environ.get("JIRA_TOKEN", "")

    artifacts_bucket_name = (
        f"{deployment_config.project}-"
        f"{deployment_config.agent_name}-logs-data"
    )

    print(f"📦 Creating artifacts bucket: {artifacts_bucket_name}")

    create_bucket_if_not_exists(
        bucket_name=artifacts_bucket_name,
        project=deployment_config.project,
        location=deployment_config.location,
    )

    vertexai.init(
        project=deployment_config.project,
        location=deployment_config.location,
        staging_bucket=f"gs://{deployment_config.staging_bucket}",
    )

    with open(deployment_config.requirements_file) as f:
        requirements = f.read().strip().split("\n")

    agent_engine = AgentEngineApp(
        agent=root_agent,
        context_cache_config=ContextCacheConfig(
            min_tokens=1500,
            ttl_seconds=600,
            cache_intervals=5,
        ),
        plugins=[ContextFilterPlugin(num_invocations_to_keep=5)],
        artifact_service_builder=lambda: GcsArtifactService(
            bucket_name=artifacts_bucket_name
        ),
    )

    agent_config = {
        "agent_engine": agent_engine,
        "display_name": deployment_config.agent_name,
        "description": "Trilingual customer service agent",
        "extra_packages": deployment_config.extra_packages,
        "env_vars": env_vars,
        "requirements": requirements,
    }

    existing_agents = list(
        agent_engines.list(
            filter=f"display_name={deployment_config.agent_name}"
        )
    )

    if existing_agents:
        print(f"🔄 Updating existing agent: {deployment_config.agent_name}")
        remote_agent = existing_agents[0].update(**agent_config)
    else:
        print(f"🆕 Creating new agent: {deployment_config.agent_name}")
        remote_agent = agent_engines.create(**agent_config)

    metadata = {
        "remote_agent_engine_id": remote_agent.resource_name,
        "deployment_timestamp": datetime.datetime.now().isoformat(),
        "agent_name": deployment_config.agent_name,
        "project": deployment_config.project,
        "location": deployment_config.location,
    }

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    metadata_file = logs_dir / "deployment_metadata.json"

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print("✅ Agent deployed successfully!")
    print(f"📄 Deployment metadata saved to: {metadata_file}")
    print(f"🆔 Agent Engine ID: {remote_agent.resource_name}")

    return remote_agent


if __name__ == "__main__":
    print(
        """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🤖 DEPLOYING AGENT TO VERTEX AI AGENT ENGINE 🤖         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    )

    deploy_agent_engine_app()
