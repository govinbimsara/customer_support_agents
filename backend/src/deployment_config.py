"""Configuration for ADK Agent Engine Deployment."""

import os
from dataclasses import dataclass
from pathlib import Path

import google.auth
import vertexai


def load_environment_variables() -> None:
    """Load environment variables from .env file if it exists."""
    try:
        from dotenv import load_dotenv

        env_file = Path(__file__).parent / "agents" / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ Loaded environment variables from {env_file}")
        else:
            print(f"ℹ️  No .env file found at {env_file}")
    except ImportError:
        print("ℹ️  python-dotenv not installed")


@dataclass
class AgentConfiguration:
    """Main configuration for the agent."""

    model: str = os.environ.get("MODEL", "gemini-2.5-flash")
    deployment_name: str = os.environ.get(
        "AGENT_NAME", "customer-service-agent"
    )
    project_id: str | None = None
    location: str = "us-central1"
    staging_bucket: str | None = None
    corpus_id: str | None = None

    def __post_init__(self) -> None:
        """Load environment variables and validate settings."""
        load_environment_variables()

        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            try:
                _, self.project_id = google.auth.default()
            except Exception:
                pass

        if not self.project_id:
            raise ValueError(
                "❌ Missing GOOGLE_CLOUD_PROJECT environment variable!\n"
                "Set it in .env or run: gcloud config set project PROJECT_ID"
            )

        self.location = os.environ.get("LOCATION") or os.environ.get(
            "GOOGLE_CLOUD_LOCATION", "europe-west4"
        )
        if not self.location:
            raise ValueError(
                "❌ Missing GOOGLE_CLOUD_LOCATION environment variable!"
            )

        self.staging_bucket = os.environ.get("GOOGLE_CLOUD_STAGING_BUCKET")
        if not self.staging_bucket:
            raise ValueError(
                "❌ Missing GOOGLE_CLOUD_STAGING_BUCKET environment variable!"
            )

        self.corpus_id = os.environ.get("CORPUS_ID")

    @property
    def internal_agent_name(self) -> str:
        """Convert deployment name to valid Python identifier."""
        name = self.deployment_name.replace("-", "_")
        if not name[0].isalpha() and name[0] != "_":
            name = f"agent_{name}"
        return name


@dataclass
class DeploymentConfiguration:
    """Configuration for Agent Engine deployment."""

    project: str
    location: str
    agent_name: str
    requirements_file: str
    extra_packages: list[str]
    staging_bucket: str
    corpus_id: str | None


def initialize_vertex_ai(config: AgentConfiguration) -> None:
    """Initialize Vertex AI with configuration."""
    try:
        print("\n🔧 Initializing Vertex AI...")
        print(f"  Project: {config.project_id}")
        print(f"  Location: {config.location}")
        print(f"  Staging Bucket: {config.staging_bucket or 'Not set'}")

        if config.staging_bucket:
            vertexai.init(
                project=config.project_id,
                location=config.location,
                staging_bucket=config.staging_bucket,
            )
        else:
            vertexai.init(
                project=config.project_id, location=config.location
            )

        print("✅ Vertex AI initialized successfully!")

    except Exception as e:
        print(f"❌ Failed to initialize Vertex AI: {e}")
        print("\n🔧 Setup checklist:")
        print("  1. Set GOOGLE_CLOUD_PROJECT in .env file")
        print("  2. Run: gcloud auth application-default login")
        print("  3. Run: gcloud config set project YOUR_PROJECT_ID")
        print("  4. Enable required APIs in Google Cloud Console")


def get_deployment_config() -> DeploymentConfiguration:
    """Get deployment configuration with validation."""
    project_id = config.project_id
    if not project_id:
        raise ValueError("❌ Project ID validation failed")

    if not config.staging_bucket:
        raise ValueError(
            "❌ Missing GOOGLE_CLOUD_STAGING_BUCKET environment variable!"
        )

    agent_name = config.deployment_name
    if not agent_name:
        raise ValueError("❌ Missing agent name")

    requirements_file = os.environ.get(
        "REQUIREMENTS_FILE", ".requirements.txt"
    )
    if not Path(requirements_file).exists():
        raise ValueError(
            f"❌ Requirements file not found: {requirements_file}\n"
            "Run 'uv export > .requirements.txt' to generate it"
        )

    extra_packages_str = os.environ.get("EXTRA_PACKAGES", "./backend/src")
    extra_packages = [
        pkg.strip() for pkg in extra_packages_str.split(",") if pkg.strip()
    ]

    if not extra_packages:
        raise ValueError("❌ No extra packages specified")

    return DeploymentConfiguration(
        project=project_id,
        location=config.location,
        agent_name=agent_name,
        requirements_file=requirements_file,
        extra_packages=extra_packages,
        staging_bucket=config.staging_bucket,
        corpus_id=config.corpus_id,
    )


def get_project_id() -> str | None:
    """Get project ID from config."""
    return config.project_id


config = AgentConfiguration()
