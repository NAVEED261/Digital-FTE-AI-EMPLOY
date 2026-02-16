# Custom Autoscaling for AI Workloads

This reference covers horizontal pod autoscaling (HPA) with custom metrics, KEDA for advanced triggers, and cost optimization.

## HPA Basics

### Metric-Based Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  minReplicas: 2        # Always have 2 for HA
  maxReplicas: 10       # Don't exceed GPU quota
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Target 70% CPU
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80  # Target 80% memory
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30    # Quick scale-up
      policies:
      - type: Percent
        value: 100                       # Double replicas
        periodSeconds: 30
    scaleDown:
      stabilizationWindowSeconds: 300   # Wait 5 min before down
      policies:
      - type: Percent
        value: 50                        # Reduce by 50%
        periodSeconds: 60
```

---

## Custom Metrics (Prometheus Adapter)

Custom metrics scale based on application-specific signals (queue depth, latency, throughput).

### Install Prometheus Adapter

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  --namespace monitoring \
  --values values.yaml
```

### values.yaml
```yaml
prometheus:
  url: http://prometheus-server
  port: 80

rules:
- seriesQuery: 'inference_queue_depth{pod=".*llm.*"}'
  resources:
    template: <<.Resource>>
  name:
    matches: "^(.*)"
    as: "inference_queue_depth"
  metricsQuery: 'avg(<<.Series>>{<<.LabelMatchers>>})'
```

### Application Code (Prometheus Metrics)

```python
from prometheus_client import Counter, Gauge, start_http_server
import queue

# Create metrics
queue_depth = Gauge('inference_queue_depth', 'Queue depth for inference requests')
requests_total = Counter('inference_requests_total', 'Total inference requests')
inference_latency = Histogram('inference_latency_seconds', 'Latency of inference')

# Background thread to update metrics
request_queue = queue.Queue(maxsize=100)

def update_metrics():
    while True:
        queue_depth.set(request_queue.qsize())
        time.sleep(10)

# In FastAPI app
@app.post("/generate")
async def generate(prompt: str):
    requests_total.inc()
    try:
        with inference_latency.time():
            # Inference code
            result = model.generate(prompt)
        return result
    except queue.Full:
        raise HTTPException(status_code=503, detail="Queue full")

# Start metrics server
start_http_server(8001)  # Separate port for metrics
```

### HPA with Custom Metric

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-queue-based-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Pods
    pods:
      metric:
        name: inference_queue_depth
      target:
        type: AverageValue
        averageValue: "10"  # Target 10 items per pod
  - type: Pods
    pods:
      metric:
        name: inference_latency_seconds
      target:
        type: AverageValue
        averageValue: "0.5"  # Target 500ms latency
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Percent
        value: 100  # Aggressive scale-up
        periodSeconds: 30
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 25   # Conservative scale-down
        periodSeconds: 60
```

---

## KEDA (Advanced Event Triggers)

KEDA scales based on external systems (queues, databases, HTTP endpoints).

### Install KEDA

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm install keda kedacore/keda --namespace keda --create-namespace
```

### AWS SQS Trigger

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: inference-queue-scaler
spec:
  scaleTargetRef:
    name: llm-inference
  minReplicaCount: 2
  maxReplicaCount: 20
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.us-west-2.amazonaws.com/123456/inference-jobs
      queueLength: "5"  # Scale up if >5 messages per pod
      awsRegion: "us-west-2"
      identityOwner: "operator"  # Use operator's IAM role
```

### Kafka Trigger

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-inference-scaler
spec:
  scaleTargetRef:
    name: llm-inference
  minReplicaCount: 2
  maxReplicaCount: 20
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka:9092
      consumerGroup: inference-group
      topic: inference-requests
      lagThreshold: "100"  # Scale if lag > 100 messages
      offsetResetPolicy: "latest"
```

### Prometheus Trigger (Custom)

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: prometheus-scaling
spec:
  scaleTargetRef:
    name: llm-inference
  minReplicaCount: 2
  maxReplicaCount: 20
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      metricName: inference_requests_pending
      query: |
        sum(rate(inference_requests_total{status="pending"}[30s]))
      threshold: "50"  # Scale when >50 req/s pending
```

---

## Vertical Pod Autoscaling (VPA)

Automatically adjusts CPU/memory requests based on actual usage.

### Install VPA

```bash
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

### VPA Policy

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: llm-inference-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  updatePolicy:
    updateMode: "auto"  # Automatic updates (requires PodDisruptionBudget)
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: 500m
        memory: 4Gi
      maxAllowed:
        cpu: 4
        memory: 32Gi
      controlledResources:
      - cpu
      - memory
```

---

## Cluster Autoscaler

Automatically adds/removes nodes based on pending pods.

### AWS EKS

```bash
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm install cluster-autoscaler autoscaler/cluster-autoscaler \
  --namespace kube-system \
  --set autoDiscovery.clusterName=my-cluster \
  --set awsUseStaticInstanceList=false
```

### GCP GKE

```bash
# Enable in cluster creation
gcloud container clusters create my-cluster \
  --enable-vertical-pod-autoscaling \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 20
```

---

## Cost Optimization

### Pod Disruption Budget (PDB)

Ensure ≥1 pod running during maintenance:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: llm-inference-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: llm-inference
```

### Spot/Preemptible Node Scaling

Use cheaper spot instances for non-critical workloads:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference
spec:
  template:
    spec:
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: cloud.google.com/gke-preemptible
                operator: In
                values:
                - "true"  # Prefer preemptible nodes
      tolerations:
      - key: cloud.google.com/gke-preemptible
        operator: Equal
        value: "true"
        effect: NoSchedule
```

### Scheduled Scaling (Down at night)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-inference-scheduled
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  minReplicas: 1  # Scale down to 1 at night
  maxReplicas: 20
  metrics: [...]
---
# CronJob to scale down at night
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-down-night
spec:
  schedule: "0 20 * * *"  # 8 PM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: kubectl
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - kubectl patch hpa llm-inference-hpa -p '{"spec":{"minReplicas":1}}'
          restartPolicy: OnFailure
---
# CronJob to scale up in morning
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-up-morning
spec:
  schedule: "0 6 * * *"  # 6 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: kubectl
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - kubectl patch hpa llm-inference-hpa -p '{"spec":{"minReplicas":2}}'
          restartPolicy: OnFailure
```

---

## Scaling Best Practices

| Scenario | Strategy | Config |
|----------|----------|--------|
| **Real-time API** | CPU/Memory + custom metrics | HPA, queue depth, latency |
| **Batch processing** | Queue length | KEDA SQS/Kafka |
| **Variable load** | Cost optimization + PDB | Scheduled scaling + spot nodes |
| **Multi-region** | Global load balancing | DNS failover + regional HPA |
| **GPU workloads** | Conservative scaling | Long stabilization window |

---

## Monitoring Scaling

```bash
# Watch HPA status
kubectl describe hpa llm-inference-hpa

# View scaling events
kubectl get events --field-selector involvedObject.name=llm-inference-hpa

# Check Prometheus metrics
kubectl exec prometheus-pod -- \
  curl localhost:9090/api/v1/query?query=keda_scaler_active
```

---

## References

- [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Adapter](https://github.com/kubernetes-sigs/prometheus-adapter)
- [KEDA](https://keda.sh/)
- [VPA](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
