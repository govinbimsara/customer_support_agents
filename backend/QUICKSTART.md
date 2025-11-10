# Quick Start Guide

Get the trilingual customer service system running in 5 minutes.

## Prerequisites

- Python 3.10+
- Google Cloud Project with Vertex AI enabled OR Google AI Studio API key
- Google Cloud credentials (if using Vertex AI)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# For Vertex AI:
GOOGLE_GENAI_USE_VERTEXAI=TRUE

# For Google AI Studio:
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key
```

### 3. Authenticate with Google Cloud (if using Vertex AI)

```bash
gcloud auth application-default login
```

### 4. Run ADK Web Interface

```bash
adk web src/
```

Open your browser to http://localhost:8000

## Test Scenarios

### Scenario 1: Knowledge Base Query (English)
```
You: What are your business hours?
Agent: [Responds with information from knowledge base]
```

### Scenario 2: Lodge Complaint (Sinhala)
```
You: මට පැමිණිල්ලක් ඉදිරිපත් කිරීමට අවශ්‍යයි
Agent: [Collects customer ID, issue type, description]
Agent: [Creates ticket and confirms]
```

### Scenario 3: Check Status (Tamil)
```
You: டிக்கெட் HUB-12345 இன் நிலையை சரிபார்க்கவும்
Agent: [Retrieves and displays ticket status]
```

## Project Structure

```
src/
├── agents/          # All agent implementations
├── schemas/         # Pydantic models
├── tools/           # Mock APIs
├── prompts/         # System prompts
├── config/          # Settings
└── app.py           # Entry point
```

## Common Commands

```bash
# Run ADK web interface
adk web src/

# Run as API server
adk api_server src/

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_supervisor.py -v
```

## Troubleshooting

### Issue: Authentication Error
**Solution:** Run `gcloud auth application-default login`

### Issue: Module Not Found
**Solution:** Ensure you're in the project root and dependencies are installed

### Issue: API Quota Exceeded
**Solution:** Check your Vertex AI quotas in Google Cloud Console

## Next Steps

1. ✅ System is running
2. 📝 Test all three languages
3. 🔧 Refine system prompts
4. 🧪 Implement unit tests
5. 🚀 Deploy to production

## Support

- See `README.md` for detailed documentation
- See `IMPLEMENTATION_SUMMARY.md` for architecture details
- Check `notebooks/prototype_testing.ipynb` for examples

## Quick Reference

**Supported Languages:**
- English
- Sinhala (සිංහල)
- Tamil (தமிழ்)

**Supported Intents:**
- `knowledge_base` - General inquiries
- `lodge_complaint` - File complaints
- `check_status` - Check ticket status

**Mock APIs:**
- HubSpot ticket creation
- HubSpot status check
- RAG knowledge base (placeholder)

---

**You're all set! Start chatting with the agent in any supported language.**
