# AI Observability on Kubernetes

This reference covers Prometheus metrics, DCGM GPU monitoring, SLO/SLI definition, and Grafana dashboards for AI workloads.

## Prometheus Metrics for AI Services

### Application Metrics (FastAPI)

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Create metrics
requests_total = Counter(
    'inference_requests_total',
    'Total inference requests',
    ['model', 'status']
)

request_duration_seconds = Histogram(
    'inference_request_duration_seconds',
    'Request latency',
    ['model'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

queue_depth = Gauge(
    'inference_queue_depth',
    'Current queue depth',
    ['model']
)

tokens_generated = Counter(
    'inference_tokens_generated_total',
    'Total tokens generated',
    ['model']
)

# In FastAPI endpoint
@app.post("/generate")
async def generate(prompt: str, model: str = "llama-2-7b"):
    with request_duration_seconds.labels(model=model).time():
        try:
            output = model.generate(prompt)
            requests_total.labels(model=model, status="success").inc()
            tokens_generated.labels(model=model).inc(len(output.split()))
            return {"text": output}
        except Exception as e:
            requests_total.labels(model=model, status="error").inc()
            raise

# Expose metrics on separate port
start_http_server(8001)
```

### Service Monitor (Prometheus Scraping)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: llm-inference
spec:
  selector:
    matchLabels:
      app: llm-inference
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

---

## GPU Metrics (NVIDIA DCGM)

### DCGM Exporter Pod

Already installed with GPU operator:

```bash
# Check DCGM exporter
kubectl get pods -n gpu-operator-system | grep dcgm

# Access metrics
kubectl port-forward -n gpu-operator-system \
  $(kubectl get pod -n gpu-operator-system -l app=dcgm-exporter -o jsonpath='{.items[0].metadata.name}') \
  9400:9400

# View GPU metrics
curl http://localhost:9400/metrics | grep -i gpu
```

### Key GPU Metrics

| Metric | Meaning |
|--------|---------|
| `DCGM_FI_DEV_GPU_UTIL` | GPU utilization % |
| `DCGM_FI_DEV_GPU_TEMP` | GPU temperature °C |
| `DCGM_FI_DEV_FB_FREE` | Free GPU memory |
| `DCGM_FI_DEV_SM_CLOCK` | GPU core clock MHz |
| `DCGM_FI_DEV_POWER_USAGE` | Power consumption W |
| `DCGM_FI_DEV_XID_ERRORS` | GPU errors (X-class) |

### Prometheus Scrape Config

```yaml
scrape_configs:
- job_name: dcgm
  metrics_path: /metrics
  static_configs:
  - targets: ['gpu-operator-system/dcgm-exporter:9400']
```

---

## Key SLI (Service Level Indicators)

### Availability (Uptime)

```promql
# Query: Uptime percentage last 30 days
(1 - (increase(kube_pod_container_status_restarts_total[30d]) / 30)) * 100

# Target: ≥99.5% (< 3.6 hours downtime/month)
```

### Latency (Response Time)

```promql
# Query: P95 latency
histogram_quantile(0.95, inference_request_duration_seconds)

# Target: <500ms for LLM, <100ms for embeddings
```

### Throughput (Requests/sec)

```promql
# Query: Requests per second
rate(inference_requests_total[5m])

# Target: ≥20 req/s per pod
```

### Error Rate

```promql
# Query: Error rate
(increase(inference_requests_total{status="error"}[5m]) /
 increase(inference_requests_total[5m])) * 100

# Target: <0.1%
```

### GPU Utilization

```promql
# Query: Average GPU util
avg(DCGM_FI_DEV_GPU_UTIL)

# Target: ≥70% (ensure cost efficiency)
```

---

## SLO (Service Level Objective) Definition

### Example: LLM Inference Service

```yaml
# Save as prometheus-rules-ai.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ai-slo
spec:
  groups:
  - name: ai-slo
    interval: 30s
    rules:
    # Availability SLO: 99.5%
    - record: slo:availability:30d
      expr: |
        (1 - (increase(kube_pod_container_status_restarts_total[30d]) / 30)) * 100

    # Latency SLO: P95 < 500ms
    - record: slo:latency:p95
      expr: |
        histogram_quantile(0.95, inference_request_duration_seconds)

    # Throughput SLO: ≥20 req/s
    - record: slo:throughput:5m
      expr: |
        rate(inference_requests_total[5m])

    # Error rate SLO: <0.1%
    - record: slo:error_rate:5m
      expr: |
        (increase(inference_requests_total{status="error"}[5m]) /
         increase(inference_requests_total[5m])) * 100

    # Alert: SLO breaches
    - alert: SLOBreached
      for: 5m
      expr: |
        (slo:latency:p95 > 500) or
        (slo:error_rate:5m > 0.1) or
        (slo:throughput:5m < 20)
      annotations:
        summary: "SLO breached"
```

---

## Grafana Dashboard

### Create Custom Dashboard

**JSON for LLM Inference Dashboard**:

```json
{
  "dashboard": {
    "title": "LLM Inference Metrics",
    "panels": [
      {
        "title": "Request Latency (P95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, inference_request_duration_seconds)"
        }],
        "yaxes": [{"format": "ms"}]
      },
      {
        "title": "Requests per Second",
        "targets": [{
          "expr": "rate(inference_requests_total[1m])"
        }]
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "(increase(inference_requests_total{status=\"error\"}[5m]) / increase(inference_requests_total[5m])) * 100"
        }],
        "yaxes": [{"format": "percent"}]
      },
      {
        "title": "GPU Utilization",
        "targets": [{
          "expr": "avg(DCGM_FI_DEV_GPU_UTIL)"
        }],
        "yaxes": [{"format": "percent"}]
      },
      {
        "title": "GPU Memory Usage",
        "targets": [{
          "expr": "DCGM_FI_DEV_FB_FREE / 1024"
        }],
        "yaxes": [{"format": "bytes"}]
      },
      {
        "title": "Queue Depth",
        "targets": [{
          "expr": "inference_queue_depth"
        }]
      }
    ]
  }
}
```

---

## Alert Rules

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ai-alerts
spec:
  groups:
  - name: ai-alerts
    rules:
    # High latency
    - alert: HighLatency
      for: 5m
      expr: histogram_quantile(0.95, inference_request_duration_seconds) > 1
      annotations:
        summary: "P95 latency > 1s ({{ $value }}s)"

    # High error rate
    - alert: HighErrorRate
      for: 5m
      expr: |
        (increase(inference_requests_total{status="error"}[5m]) /
         increase(inference_requests_total[5m])) > 0.01
      annotations:
        summary: "Error rate > 1% ({{ $value }}%)"

    # GPU overheating
    - alert: GPUOverheating
      for: 2m
      expr: DCGM_FI_DEV_GPU_TEMP > 80
      annotations:
        summary: "GPU temperature > 80°C"

    # GPU memory full
    - alert: GPUMemoryFull
      expr: DCGM_FI_DEV_FB_FREE < 1024
      annotations:
        summary: "GPU memory < 1GB free"

    # Pod restarting frequently
    - alert: PodRestarting
      for: 10m
      expr: rate(kube_pod_container_status_restarts_total[1h]) > 0.01
      annotations:
        summary: "Pod restarting > 1/100 per hour"

    # GPU errors
    - alert: GPUErrors
      expr: DCGM_FI_DEV_XID_ERRORS > 0
      annotations:
        summary: "GPU X-class errors detected"
```

---

## Observability Stack Installation

### Prometheus + Grafana

```bash
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Expose Prometheus
kubectl port-forward -n monitoring svc/monitoring-prometheus 9090:9090

# Expose Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# Login: admin / prom-operator
```

---

## Cost Monitoring

```yaml
# Track pod costs
apiVersion: v1
kind: ConfigMap
metadata:
  name: pod-cost-model
data:
  # Spot instance costs (hourly)
  gpu-spot: "0.30"  # $ per hour
  cpu-spot: "0.03"
  # On-demand costs
  gpu-ondemand: "0.70"
  cpu-ondemand: "0.08"
---
# Calculate cost per pod
apiVersion: batch/v1
kind: CronJob
metadata:
  name: calculate-pod-costs
spec:
  schedule: "0 * * * *"  # Hourly
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cost-calculator
            image: python:3.11
            command:
            - python
            - -c
            - |
              import subprocess
              import json

              # Get pod resource usage
              pods = subprocess.run(
                  ["kubectl", "top", "pod", "-A", "--no-headers"],
                  capture_output=True, text=True
              ).stdout.strip().split('\n')

              total_cost = 0
              for pod in pods:
                  parts = pod.split()
                  cpu = float(parts[2].rstrip('m')) / 1000
                  mem = float(parts[3].rstrip('Mi')) / 1024
                  gpu_cost = 0.30 if 'gpu' in pod else 0
                  hourly_cost = (cpu * 0.08 + mem * 0.01 + gpu_cost)
                  total_cost += hourly_cost

              print(f"Total hourly cost: ${total_cost:.2f}")
          restartPolicy: OnFailure
```

---

## References

- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/grafana/)
- [NVIDIA DCGM](https://developer.nvidia.com/dcgm)
- [Google SLO Guide](https://sre.google/sre-book/service-level-objectives/)
