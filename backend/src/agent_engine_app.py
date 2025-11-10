"""Agent Engine App - Deploy agent to Google Cloud."""

import copy
import datetime
import json
import os
from pathlib import Path
from typing import Any

import vertexai
from google.adk.artifacts import GcsArtifactService
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from src.utils.gcs import create_bucket_if_not_exists
from src.utils.tracing import CloudTraceLoggingSpanExporter
from src.utils.typing import Feedback
from src.deployment_config import (
    config,
    get_deployment_config,
    initialize_vertex_ai,
)

# Initialize Vertex AI before importing agents
initialize_vertex_ai(config)

from src.agents.agent import app


class AgentEngineApp(AdkApp):
    """ADK Application wrapper for Agent Engine deployment."""

    def set_up(self) -> None:
        """Set up logging and tracing."""
        super().set_up()
        logging_client = google_cloud_logging.Client()
        self.logger = logging_client.logger(__name__)
        provider = TracerProvider()
        processor = export.BatchSpanProcessor(
            CloudTraceLoggingSpanExporter(
                project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                service_name=f"{config.deployment_name}-service",
            )
        )
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        self.enable_tracing = True

    def register_feedback(self, feedback: dict[str, Any]) -> None:
        """Collect and log feedback from users."""
        feedback_obj = Feedback.model_validate(feedback)
        self.logger.log_struct(feedback_obj.model_dump(), severity="INFO")

    def register_operations(self) -> dict[str, list[str]]:
        """Register available operations."""
        operations = super().register_operations()
        operations[""] = operations[""] + ["register_feedback"]
        return operations

    def clone(self) -> "AgentEngineApp":
        """Create a copy of this application."""
        template_attributes = self._tmpl_attrs

        return self.__class__(
            agent=copy.deepcopy(template_attributes["agent"]),
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
    """Deploy the agent to Vertex AI Agent Engine.

    Returns:
        The deployed agent engine instance
    """
    print("🚀 Starting Agent Engine deployment...")

    deployment_config = get_deployment_config()
    print(f"📋 Deploying agent: {deployment_config.agent_name}")
    print(f"📋 Project: {deployment_config.project}")
    print(f"📋 Location: {deployment_config.location}")
    print(f"📋 Staging bucket: {deployment_config.staging_bucket}")

    env_vars = {
        "NUM_WORKERS": "1",
        "GOOGLE_GENAI_USE_VERTEXAI": "True",
    }

    if deployment_config.corpus_id:
        env_vars["CORPUS_ID"] = deployment_config.corpus_id
        print(f"📋 Corpus ID: {deployment_config.corpus_id}")
    
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
        agent=app,
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
