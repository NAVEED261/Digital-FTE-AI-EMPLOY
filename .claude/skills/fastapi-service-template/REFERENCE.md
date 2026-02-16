# fastapi-service-template Reference Guide

## Overview

The `fastapi-service-template` skill generates production-ready FastAPI microservices with:
- OpenAI Agents SDK integration
- Neon PostgreSQL connection
- Kubernetes deployment manifests
- Docker containerization
- pytest test suite
- Structured outputs with Pydantic

## Service Types

### Triage Agent

Routes student queries to specialist agents.

**Endpoint**: `POST /api/query`

**Request**:
```json
{
  "student_id": 1,
  "query": "How do for loops work?",
  "code": null
}
```

**Response**:
```json
{
  "agent": "concepts",
  "response": "For loops in Python...",
  "confidence": 0.95
}
```

### Concepts Agent

Explains Python concepts with examples.

**Endpoint**: `POST /api/explain`

**Request**:
```json
{
  "student_id": 1,
  "concept": "for loops",
  "level": "beginner"
}
```

**Response**:
```json
{
  "explanation": "A for loop repeats a block of code...",
  "examples": ["for i in range(5): print(i)"],
  "resources": ["Python.org tutorial"]
}
```

### Code Review Agent

Analyzes code quality and provides feedback.

**Endpoint**: `POST /api/review`

**Request**:
```json
{
  "student_id": 1,
  "code": "for i in range(10):\n    print(i)",
  "language": "python"
}
```

**Response**:
```json
{
  "quality_score": 8.5,
  "feedback": "Good loop usage. Consider adding comments.",
  "suggestions": ["Add docstring", "Use meaningful variable names"]
}
```

## Generation Workflow

### Step 1: Specify Service Requirements

Create `spec.md` for the service:

```bash
claude "Use /sp.specify to create triage-agent specification"
```

This creates:
- Service purpose and scope
- API contract
- Database interactions
- Model configuration

### Step 2: Plan Implementation

Create `plan.md`:

```bash
claude "Use /sp.plan for triage-agent"
```

This creates:
- Architecture decisions
- File structure
- Dependency list
- Deployment strategy

### Step 3: Generate Tasks

Create `tasks.md`:

```bash
claude "Use /sp.tasks for triage-agent"
```

This creates:
- Actionable implementation tasks
- Dependencies between tasks
- Testing checklist

### Step 4: Generate Service Code

```bash
claude "Use fastapi-service-template skill to generate triage-agent"
```

This creates complete service with all files.

### Step 5: Implement Agent Logic

Update `agent.py` with service-specific logic (Triage, Concepts, Code Review).

### Step 6: Deploy

```bash
kubectl apply -f triage-agent/deployment.yaml
```

## Customization

### Custom Agent Prompt

In generated `agent.py`, update the system prompt:

```python
TRIAGE_PROMPT = """
You are the LearnFlow Triage Agent. Route student queries to specialists:
- Concepts questions → concepts-agent
- Code review requests → code-review-agent
- Error debugging → debug-agent

Analyze query and return routing decision with confidence score.
"""
```

### Custom Models

Update `models.py` with service-specific fields:

```python
class ConceptsQuery(BaseModel):
    student_id: int
    concept: str
    level: Literal["beginner", "intermediate", "advanced"]
    context: Optional[str] = None
```

### Custom Endpoints

Add new endpoints to `main.py`:

```python
@app.post("/api/advanced-endpoint")
async def advanced(request: AdvancedRequest) -> AdvancedResponse:
    # Implementation
    pass
```

### Environment Variables

Edit `config.py` to add new configuration:

```python
CUSTOM_PARAM = os.getenv('CUSTOM_PARAM', 'default_value')
```

## Database Integration

### Connection Setup

Services auto-connect to Neon via `DATABASE_URL`:

```python
from sqlalchemy import create_engine

engine = create_engine(config.DATABASE_URL)
```

### Query Examples

```python
from sqlalchemy import text

# Store conversation
with engine.connect() as conn:
    conn.execute(
        text("""
        INSERT INTO conversations (student_id, agent_type, messages)
        VALUES (:student_id, :agent_type, :messages)
        """),
        {"student_id": 1, "agent_type": "concepts", "messages": "[]"}
    )
```

## OpenAI Agents SDK Integration

### Initialize Agent

```python
from openai import OpenAI

client = OpenAI(api_key=config.OPENAI_API_KEY)

agent = client.beta.agents.create(
    name="Triage Agent",
    instructions=TRIAGE_PROMPT,
    model="gpt-4-turbo-preview"
)
```

### Use Agent

```python
@app.post("/api/query")
async def query(request: QueryRequest) -> QueryResponse:
    response = client.beta.agents.process(
        agent_id=agent.id,
        input=request.query
    )
    return QueryResponse(
        response=response.text,
        agent="triage"
    )
```

## Kubernetes Deployment

### Build Docker Image

```bash
cd <service-name>
docker build -t <service-name>:latest .
docker push <registry>/<service-name>:latest
```

### Deploy to Cluster

```bash
kubectl apply -f <service-name>/deployment.yaml
kubectl apply -f <service-name>/service.yaml
```

### Verify Deployment

```bash
kubectl get pods -n learnflow
kubectl logs deployment/<service-name> -n learnflow
kubectl port-forward service/<service-name> 8001:8000 -n learnflow
```

## Testing

### Run Unit Tests

```bash
cd <service-name>
pytest tests/ -v
```

### Test Health Endpoint

```bash
curl http://localhost:8001/health
```

### Test Agent Endpoint

```bash
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "query": "How do loops work?"}'
```

### Load Testing

```bash
pip install locust

# Create locustfile.py with load test scenarios
locust -f locustfile.py --host=http://localhost:8001
```

## Performance Optimization

### Connection Pooling

Use pgBouncer for PostgreSQL connection pooling:

```python
# In config.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

### Response Caching

Add caching for frequently-requested concepts:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_concept_explanation(concept: str) -> str:
    # Expensive operation cached
    pass
```

### Async Processing

Use async/await for non-blocking operations:

```python
@app.post("/api/async-query")
async def async_query(request: QueryRequest) -> QueryResponse:
    # Non-blocking OpenAI call
    response = await client.beta.agents.async_process(...)
    return QueryResponse(response=response)
```

## Monitoring and Logging

### Application Logging

Logs go to stdout (captured by Kubernetes):

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Processing query for student {student_id}")
logger.error(f"Error in agent: {str(e)}")
```

### Prometheus Metrics

Add monitoring:

```python
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
response_time = Histogram('response_seconds', 'Response time')

@app.post("/api/query")
@response_time.time()
async def query(request: QueryRequest):
    request_count.inc()
    # Implementation
```

### Health Check

Endpoint returns service health:

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "triage-agent",
        "timestamp": datetime.now().isoformat()
    }
```

## Dapr Integration (Tier 2)

If deploying with Dapr service mesh:

### Add Dapr Annotations

```yaml
# In deployment.yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "triage-agent"
  dapr.io/app-port: "8000"
```

### Use Dapr State Management

```python
from dapr.clients import DaprClient

with DaprClient() as d:
    d.save_state(
        store_name="statestore",
        key="student_1_session",
        value=session_data
    )
```

### Use Dapr Pub/Sub

```python
# Subscribe to events
@app.post("/query-routed")
async def on_query_routed(event: dict):
    # Process routed query
    pass
```

## Troubleshooting

### Service won't start

Check logs:
```bash
kubectl logs deployment/<service-name> -n learnflow
```

Common causes:
- Missing environment variables
- Database connection failure
- OpenAI API key invalid
- Port already in use

### 502 Bad Gateway

Check service health:
```bash
kubectl exec -it pod/<service-name> -- curl http://localhost:8000/health
```

### Database connection timeout

Verify Neon connection string and network:
```bash
psql "$NEON_CONNECTION_STRING"
```

## Security Best Practices

1. **Environment Variables**: Never commit secrets (API keys, connection strings)
2. **Input Validation**: Pydantic automatically validates all inputs
3. **CORS**: Restrict cross-origin requests in production
4. **Rate Limiting**: Add rate limiting for public endpoints
5. **Authentication**: Implement OAuth/JWT for production

## Scaling Considerations

### Horizontal Scaling

Services scale independently:

```bash
kubectl scale deployment/<service-name> --replicas=3 -n learnflow
```

### Load Balancing

Kubernetes Service automatically load-balances across replicas.

### Database Scaling

Neon handles connection pooling and autoscaling.

## Migration Path

### From Template to Custom Service

1. Start with generated template
2. Implement service-specific agent logic
3. Add custom endpoints as needed
4. Deploy to Kubernetes
5. Monitor and optimize based on usage

### From HTTP to Event-Driven

When ready to scale to Tier 2:
1. Keep HTTP endpoints for now
2. Add Kafka consumer alongside
3. Gradually migrate to event-driven
4. Remove HTTP endpoints when Kafka ready
