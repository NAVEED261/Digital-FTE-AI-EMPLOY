---
name: fastapi-service-template
description: Generate complete FastAPI microservice from template
version: 1.0.0
cross-agent: claude-code,goose
token-cost: 150
---

# Generate FastAPI Microservice Template

Creates production-ready FastAPI microservice with OpenAI Agents SDK integration, Kubernetes deployment, and pytest configuration.

## When to Use

Use this skill when you need to:
- Create new FastAPI microservice for LearnFlow
- Generate Triage, Concepts, or Code Review agent service
- Create service with database connection and OpenAI integration
- Generate Kubernetes deployment manifests
- Setup pytest for service testing

## Usage

```bash
claude "Use fastapi-service-template skill to generate <service-name>"
```

## Parameters

- **service-name**: Name of service (triage-agent, concepts-agent, code-review-agent)
- **port**: Port number (8001, 8002, 8003) - auto-assigned if not specified
- **include-tests**: Include pytest tests (default: true)
- **include-docker**: Include Dockerfile (default: true)
- **include-k8s**: Include Kubernetes manifests (default: true)

## Output

Creates directory with complete service:

```
<service-name>/
├── main.py                 # FastAPI app with health check
├── agent.py               # OpenAI Agents SDK integration
├── models.py              # Pydantic models for request/response
├── config.py              # Environment configuration
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── deployment.yaml        # Kubernetes deployment
├── service.yaml           # Kubernetes service
└── tests/
    └── test_agent.py      # Pytest tests
```

## Examples

Generate Triage Agent:
```bash
claude "Use fastapi-service-template skill to generate triage-agent"
```

Generate Concepts Agent on port 8002:
```bash
claude "Use fastapi-service-template skill to generate concepts-agent with port=8002"
```

Generate Code Review Agent without tests:
```bash
claude "Use fastapi-service-template skill to generate code-review-agent with include-tests=false"
```

## Generated Files

### main.py
FastAPI application with:
- `/health` GET endpoint (service health check)
- `/api/query` POST endpoint (agent-specific)
- Logging and error handling
- OpenAI API integration
- Database connection

### agent.py
OpenAI Agents SDK wrapper:
- Agent initialization
- Structured outputs with Pydantic
- Prompt engineering for specific agent type
- Response formatting

### models.py
Pydantic data models:
- QueryRequest (student query input)
- QueryResponse (agent response)
- AgentConfig (configuration)

### config.py
Environment configuration:
- OpenAI API key loading
- Database connection setup
- Service port and host
- Logging configuration

### requirements.txt
Python dependencies:
- fastapi
- uvicorn
- openai
- psycopg2-binary
- pydantic
- pytest

### Dockerfile
Multi-stage Docker build:
- Python 3.11 base image
- Dependency caching
- Non-root user
- Health check

### Kubernetes Manifests
- Deployment with resource limits
- Service for discovery
- ConfigMap for configuration
- Dapr annotations (if Tier 2)

## Validation

Generated service should:
- [ ] Run with `python main.py`
- [ ] Respond to `/health` GET request
- [ ] Accept `/api/query` POST requests
- [ ] Return structured JSON responses
- [ ] Connect to PostgreSQL (if configured)
- [ ] Tests pass: `pytest tests/`
- [ ] Docker builds: `docker build -t service:latest .`

---

**See [REFERENCE.md](./REFERENCE.md) for customization and advanced options.**
