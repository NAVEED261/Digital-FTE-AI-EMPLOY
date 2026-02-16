# Observability: Logging, Metrics, and Tracing

## The Three Pillars

| Pillar | Purpose | Tools | Example |
|--------|---------|-------|---------|
| **Logs** | Record events that happened | ELK Stack, Loki, CloudWatch | "User login failed: invalid password" |
| **Metrics** | Quantify system behavior | Prometheus, Grafana, CloudWatch | CPU usage: 45%, Requests/sec: 1000 |
| **Traces** | Show request flow across services | Jaeger, Zipkin, DataDog | Request path: API → OrderService → Database |

---

## 1. Structured Logging

### FastAPI with JSON Logs
```python
# logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging():
    formatter = JSONFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger

# In main.py
from logging_config import setup_logging
logger = setup_logging()
```

### Log with Trace Context
```python
import uuid
import contextvars
from fastapi import Request

trace_id_var = contextvars.ContextVar('trace_id', default=None)

@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    trace_id_var.set(trace_id)

    # Log request start
    logger.info("Request started", extra={
        "trace_id": trace_id,
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host,
    })

    response = await call_next(request)

    # Log request end
    logger.info("Request completed", extra={
        "trace_id": trace_id,
        "status": response.status_code,
    })

    response.headers["X-Trace-ID"] = trace_id
    return response
```

### Centralized Logging with Loki
```yaml
# docker-compose for local Loki
version: '3.8'
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
    command: -config.file=/etc/loki/local-config.yaml

  promtail:  # Log collector
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yaml:/etc/promtail/config.yaml
    command: -config.file=/etc/promtail/config.yaml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
```

---

## 2. Metrics Collection (Prometheus)

### Expose Prometheus Metrics in FastAPI
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request
import time

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

active_requests = Gauge(
    'http_requests_in_progress',
    'Number of active HTTP requests'
)

database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'table', 'status']
)

# Middleware to track metrics
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    active_requests.inc()
    start = time.time()

    response = await call_next(request)

    duration = time.time() - start
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    active_requests.dec()
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Track database operations
def track_db_operation(operation: str, table: str, success: bool):
    status = "success" if success else "error"
    database_queries_total.labels(
        operation=operation,
        table=table,
        status=status
    ).inc()
```

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'order-service'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'product-service'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/metrics'

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

### Docker Compose for Prometheus + Grafana
```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
```

### Sample Grafana Queries (PromQL)
```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, http_request_duration_seconds)

# Error rate percentage
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# CPU usage per pod (Kubernetes)
sum(rate(container_cpu_usage_seconds_total[5m])) by (pod_name)
```

---

## 3. Distributed Tracing (Jaeger)

### Enable Tracing in FastAPI
```python
from jaeger_client import Config
from jaeger_client.config import DEFAULT_REPORTING_PORT
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# Initialize Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(jaeger_exporter)
)

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Auto-instrument database
SQLAlchemyInstrumentor().instrument(engine=engine)

# Auto-instrument HTTP client
HTTPXClientInstrumentor().instrument()

# Manual span creation
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.get("/order/{order_id}")
async def get_order(order_id: int):
    with tracer.start_as_current_span("get_order") as span:
        span.set_attribute("order_id", order_id)
        # Fetch order
        span.add_event("order_retrieved")
        return order
```

### Docker Compose for Jaeger
```yaml
version: '3.8'
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "6831:6831/udp"  # Jaeger agent
      - "16686:16686"    # Jaeger UI
    environment:
      COLLECTOR_ZIPKIN_HOST_PORT: ":9411"
```

### Kubernetes Jaeger Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:latest
        ports:
        - containerPort: 6831
          protocol: UDP
        - containerPort: 16686
          protocol: TCP
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 1Gi

---
apiVersion: v1
kind: Service
metadata:
  name: jaeger
  namespace: monitoring
spec:
  selector:
    app: jaeger
  ports:
  - port: 6831
    protocol: UDP
  - port: 16686
    name: ui
```

---

## 4. Alerting (Prometheus + AlertManager)

### Alert Rules
```yaml
# alert-rules.yml
groups:
  - name: service-alerts
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value | humanizePercentage }}"

    - alert: HighLatency
      expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
      for: 5m
      annotations:
        summary: "High latency detected"

    - alert: ServiceDown
      expr: up{job="order-service"} == 0
      for: 2m
      annotations:
        summary: "Service is down"

    - alert: PodCrashLooping
      expr: rate(kube_pod_container_status_restarts_total[15m]) > 0.1
      annotations:
        summary: "Pod is crash looping"
```

### AlertManager Configuration
```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  receiver: 'team-slack'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

receivers:
  - name: 'team-slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

---

## 5. Dashboard Example (Grafana)

### Service Health Dashboard
```json
{
  "dashboard": {
    "title": "Microservice Health",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~'5..'}[5m])"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "Database Connection Pool Usage",
        "targets": [
          {
            "expr": "sqlalchemy_pool_checkedin"
          }
        ]
      }
    ]
  }
}
```

---

## Key Observability Practices

1. **Correlation IDs**: Propagate `X-Trace-ID` across all services
2. **Health Checks**: Implement `/health/live` and `/health/ready`
3. **Resource Limits**: Define requests and limits for all containers
4. **Retention**: Set log, metric, and trace retention policies
5. **Sampling**: Sample traces to reduce storage (e.g., 10% in prod)
6. **Alerts on SLO**: Alert when approaching error budget limits
7. **Dashboard per Service**: Make observability data visible to teams
