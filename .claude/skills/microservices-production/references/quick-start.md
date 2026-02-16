# Quick Start: Building a Production Microservice

## 5-Minute Overview

1. **Choose a Framework**: FastAPI (Python), Go, or Node.js
2. **Write Service Code**: Use boilerplate from `references/fastapi-patterns.md`
3. **Containerize**: Use `Dockerfile.fastapi` from `assets/`
4. **Deploy Locally**: Test with `docker-compose.yml` from `assets/`
5. **Deploy to Kubernetes**: Use `bootstrap-k8s.py` script
6. **Add Monitoring**: Use `setup-monitoring.py` script

---

## Step-by-Step: Build Order Service

### 1. Create FastAPI Service

```python
# main.py
from fastapi import FastAPI
from healthchecks import HealthHandler

app = FastAPI(title="order-service")

# Add middleware for tracing and metrics
# Add health checks endpoints
# Add business logic endpoints
```

See `references/fastapi-patterns.md` for complete example.

### 2. Create Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

Or copy from `assets/Dockerfile.fastapi`.

### 3. Build and Test Locally

```bash
# Build image
docker build -t order-service:v1 .

# Run with docker-compose
cd assets
docker-compose up

# Test service
curl http://localhost:8000/health/live
curl http://localhost:8000/orders
```

### 4. Deploy to Kubernetes

```bash
# Generate K8s manifests
python scripts/bootstrap-k8s.py \
  --service order-service \
  --image myrepo/order-service:v1 \
  --namespace microservices

# Apply manifests
kubectl apply -f k8s/

# Verify deployment
kubectl get pods -n microservices
kubectl logs deployment/order-service -n microservices
```

### 5. Setup Monitoring

```bash
# Generate monitoring manifests
python scripts/setup-monitoring.py \
  --services order-service product-service

# Apply monitoring
kubectl apply -f monitoring/

# Access dashboards
kubectl port-forward -n monitoring service/grafana 3000:3000
kubectl port-forward -n monitoring service/jaeger 16686:16686
```

---

## Common Tasks

### Add a New Endpoint

```python
@app.post("/orders")
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Validate input
    # Save to database
    # Publish event
    return {"id": 1, "status": "created"}
```

### Call Another Service

```python
import httpx

async def get_product(product_id: int, trace_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://product-service:8000/products/{product_id}",
            headers={"X-Trace-ID": trace_id}
        )
        return response.json()
```

### Publish an Event

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# In your endpoint
producer.send('orders', value={
    "event_type": "order.created",
    "order_id": 123,
    "timestamp": datetime.utcnow().isoformat()
})
```

### Consume Events

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'orders',
    bootstrap_servers=['kafka:9092'],
    group_id='notification-service'
)

for message in consumer:
    event = json.loads(message.value)
    if event['event_type'] == 'order.created':
        # Send notification
        pass
```

### Enable Distributed Tracing

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider

jaeger_exporter = JaegerExporter(agent_host_name="jaeger", agent_port=6831)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(jaeger_exporter)
)

# Services are auto-instrumented; just access Jaeger UI
```

### Implement Circuit Breaker

See `references/advanced-patterns.md` for CircuitBreaker class.

```python
from circuit_breaker import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@app.get("/protected-call")
async def protected():
    try:
        result = await breaker.call(downstream_service.get_data)
        return result
    except Exception:
        return {"error": "Service unavailable", "fallback": []}
```

---

## Debugging Production Issues

### Pod is Crashing

```bash
# Check logs
kubectl logs deployment/order-service -n microservices

# Check events
kubectl describe pod <pod-name> -n microservices

# Check resource limits
kubectl top pods -n microservices
```

### High Latency

```bash
# Query P95 latency in Prometheus
histogram_quantile(0.95, http_request_duration_seconds)

# Check distributed traces in Jaeger
# Look for slow database queries or downstream calls
```

### High Error Rate

```bash
# Query error rate
rate(http_requests_total{status=~"5.."}[5m])

# Check logs with trace context
kubectl logs deployment/order-service -n microservices | grep ERROR
```

### Database Connection Issues

```bash
# Check connection pool metrics
sqlalchemy_pool_checkedin

# Check database query performance
# Add slow query logging to PostgreSQL
```

---

## Production Deployment Checklist

Before pushing to production:

- [ ] All endpoints have request/response validation
- [ ] Health checks return correct status
- [ ] Structured logging with correlation IDs
- [ ] Metrics exposed at `/metrics`
- [ ] Service-to-service calls have timeouts and retries
- [ ] Database connections use connection pooling
- [ ] Secrets managed via Kubernetes Secrets or Vault
- [ ] Resource requests/limits configured
- [ ] HPA configured for auto-scaling
- [ ] Network policies restrict traffic
- [ ] Distributed tracing enabled
- [ ] Alerts configured for SLOs
- [ ] Runbooks documented for common issues
- [ ] Load testing completed
- [ ] Graceful shutdown tested

---

## Reference Files

- **fastapi-patterns.md**: Complete FastAPI service template with patterns
- **kubernetes-deployment.md**: K8s manifests and deployment strategies
- **observability-setup.md**: Logging, metrics, tracing configuration
- **advanced-patterns.md**: Service mesh, event-driven, security patterns

## Scripts

- **bootstrap-k8s.py**: Generate Kubernetes manifests
- **setup-monitoring.py**: Generate monitoring stack manifests

## Assets

- **Dockerfile.fastapi**: Production Dockerfile for FastAPI
- **docker-compose.yml**: Local development environment
