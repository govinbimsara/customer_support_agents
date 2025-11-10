"""Main application entry point for the trilingual customer service system."""

from .agents.supervisor import root_agent

if __name__ == "__main__":
    print("Trilingual Customer Service System")
    print("=" * 50)
    print("Supported languages: English, Sinhala, Tamil")
    print("\nTo run this agent, use: adk web src/")
    print("Or deploy using: adk api_server src/")
