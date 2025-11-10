# Trilingual Customer Service Multi-Agent System

A production-ready trilingual (English, Sinhala, Tamil) customer service system built with Vertex AI Agent Engine and ADK.

## Architecture

### Agent Hierarchy

```
Supervisor Agent (Root)
├── KnowledgeBase Agent (Sub-Agent A)
├── ComplaintFlow Agent (Sub-Agent B)
│   └── TicketValidation Agent (Sequential Tool)
│       ├── LanguageStructureValidator
│       ├── DataValidator
│       └── ResponseHandler
└── StatusCheck Agent (Sub-Agent C)
```

### Key Features

- **Trilingual Support**: English, Sinhala, Tamil
- **Intent Classification**: Automatic routing to specialized agents
- **Multi-turn Conversations**: Natural dialogue flows
- **Strict State Management**: Event-based updates only
- **Error Handling**: Recoverable and unrecoverable error strategies
- **Mock APIs**: HubSpot integration (ready for production replacement)

## Project Structure

```
trilingual-customer-service/
├── src/
│   ├── agents/           # Agent implementations
│   ├── schemas/          # Pydantic models
│   ├── tools/            # External integrations
│   ├── prompts/          # System prompts
│   ├── config/           # Configuration
│   └── app.py            # Main entry point
├── tests/                # Unit tests
├── notebooks/            # Interactive testing
├── requirements.txt      # Dependencies
└── pyproject.toml        # Project configuration
```

## Setup

### Prerequisites

- Python 3.10+
- Google Cloud Project with Vertex AI enabled OR Google AI Studio API key
- Google Cloud credentials (if using Vertex AI)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Customer_Service_Agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Create .env file
cp .env.example .env

# For Vertex AI:
GOOGLE_GENAI_USE_VERTEXAI=TRUE

# For Google AI Studio:
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key
```

4. Authenticate with Google Cloud (if using Vertex AI):
```bash
gcloud auth application-default login
```

## Usage

### Interactive Mode (ADK Web UI)

Run the agent using ADK web interface:

```bash
adk web src/
```

Then open your browser to the provided URL (typically http://localhost:8000)

### API Server Mode

Run as an API server:

```bash
adk api_server src/
```

### Programmatic Usage

```python
from src.agents.supervisor import root_agent

# The root_agent is automatically discovered by ADK
# Use adk web or adk api_server to run the agent
```

## Agent Responsibilities

### Supervisor Agent
- Detects user language
- Classifies intent (knowledge_base, lodge_complaint, check_status)
- Delegates to appropriate sub-agent
- Manages session state

### KnowledgeBase Agent
- Handles general inquiries
- Multi-turn Q&A conversations
- RAG engine integration (placeholder)

### ComplaintFlow Agent
- Collects complaint data (Customer ID, Issue Type, Description)
- Translates to English
- Validates via TicketValidation Sequential Agent
- Confirms ticket creation

### StatusCheck Agent
- Extracts ticket ID
- Queries HubSpot API
- Returns formatted status

## State Management

ADK automatically manages session state:

- State is persisted across agent interactions
- Output schemas are automatically captured
- Sub-agents can access parent agent state
- Use callbacks for custom state management if needed

```python
# Define output schema for structured state
agent = LlmAgent(
    name="my_agent",
    output_schema=MyOutputSchema,
    ...
)
```

## Error Handling

### Recoverable Errors
- Handled within sub-agent
- Retry with backoff
- User informed naturally
- Agent maintains control

### Unrecoverable Errors
- Delegate back to Supervisor
- Professional error message
- Offer alternative actions

## Testing

Run unit tests:

```bash
pytest tests/
```

Run specific test:

```bash
pytest tests/test_supervisor.py -v
```

## Mock APIs

The system uses mock HubSpot APIs for prototyping:

- `mock_create_ticket()`: Simulates ticket creation
- `mock_check_status()`: Simulates status retrieval

Replace with real HubSpot API integration for production.

## Development

### Adding New Agents

1. Create agent file in `src/agents/`
2. Define system prompt in `src/prompts/`
3. Add Pydantic schemas if needed in `src/schemas/`
4. Register agent in supervisor or parent agent
5. Add unit tests in `tests/`

### Modifying Prompts

System prompts are in `src/prompts/`. Update prompts and test thoroughly before deployment.

## Production Deployment

1. Replace mock APIs with real integrations
2. Implement real RAG engine
3. Configure production credentials
4. Deploy to Vertex AI Agent Engine
5. Monitor and optimize

## License

[Your License]

## Support

[Your Support Information]
