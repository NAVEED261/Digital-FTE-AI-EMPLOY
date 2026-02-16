# StatefulSets for AI Model Serving

This reference covers when to use StatefulSets, persistent cache patterns, distributed inference, and comparison with Deployments.

## StatefulSet vs Deployment

| Feature | Deployment | StatefulSet |
|---------|-----------|------------|
| **Pod Identity** | Random (app-abc123) | Stable (app-0, app-1, app-2) |
| **Network Identity** | Cluster service | Headless service (DNS) |
| **Storage** | Shared or none | Per-pod persistent volumes |
| **Scaling** | Unordered | Ordered (0→1→2) |
| **Rolling Update** | Parallel | Sequential |
| **Use Case** | Simple APIs | Stateful apps, inference servers |

---

## When to Use StatefulSet

### ✅ Use StatefulSet When

1. **Each pod needs persistent storage** (e.g., model cache, inference state)
2. **Pods have network identity** (e.g., Triton replicas need DNS names)
3. **Ordered deployment matters** (e.g., set up primary before replicas)
4. **Distributed inference** with model parallelism across pods

### ❌ Use Deployment When

1. All pods are interchangeable (simple LLM API)
2. No persistent state needed
3. Fast scaling up/down is critical
4. Single model, high throughput

---

## Pattern 1: Model Serving with Local Cache

StatefulSet where each pod maintains its own persistent model cache:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: triton-inference
spec:
  clusterIP: None  # Headless service for DNS
  selector:
    app: triton
  ports:
  - port: 8000
    targetPort: 8000
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: triton-inference
spec:
  serviceName: triton-inference  # Must match headless service
  replicas: 3
  selector:
    matchLabels:
      app: triton
  template:
    metadata:
      labels:
        app: triton
    spec:
      affinity:
        podAntiAffinity:  # Spread across nodes
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - triton
              topologyKey: kubernetes.io/hostname
      containers:
      - name: triton
        image: nvcr.io/nvidia/tritonserver:24.02-py3
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: model-cache
          mountPath: /models
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
        startupProbe:
          httpGet:
            path: /v2/health/ready
            port: 8000
          failureThreshold: 60
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: model-cache
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ai-models
      resources:
        requests:
          storage: 100Gi
```

**Result**: Creates `triton-inference-0`, `triton-inference-1`, `triton-inference-2` with separate volumes, each with DNS name `triton-inference-0.triton-inference.default.svc.cluster.local`.

---

## Pattern 2: Distributed Inference (Tensor Parallelism)

Multiple pods cooperate to serve a single large model using tensor parallelism:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: distributed-llm
spec:
  serviceName: distributed-llm
  replicas: 4  # 4 GPUs for 1 model
  selector:
    matchLabels:
      app: llm
  template:
    metadata:
      labels:
        app: llm
    spec:
      containers:
      - name: llm
        image: my-distributed-llm:latest
        ports:
        - containerPort: 8000
        env:
        - name: RANK
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: WORLD_SIZE
          value: "4"
        - name: MASTER_ADDR
          value: distributed-llm-0.distributed-llm
        - name: MASTER_PORT
          value: "29500"
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          failureThreshold: 120
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: distributed-llm
spec:
  clusterIP: None
  selector:
    app: llm
  ports:
  - port: 8000
  - port: 29500  # PyTorch distributed communication
```

**Application code** (PyTorch):

```python
import torch.distributed as dist
from fastapi import FastAPI

app = FastAPI()

# Initialize distributed
dist.init_process_group("nccl")
rank = dist.get_rank()
world_size = dist.get_world_size()

# Load model with tensor parallelism
from transformers import AutoModel
model = AutoModel.from_pretrained("meta-llama/Llama-2-70b")
model = model.to(f"cuda:{rank}")

# Shard model across GPUs
from fairscale.nn import auto_wrap
model = auto_wrap(model)

@app.post("/generate")
async def generate(prompt: str):
    output = model.generate(prompt)
    # Automatically synchronized across ranks
    return {"text": output}
```

---

## Pattern 3: Ordered Rollout (Setup Primary First)

Scale up/down in order:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: llm-cluster
spec:
  serviceName: llm-cluster
  replicas: 3
  podManagementPolicy: Ordered  # Default
  selector:
    matchLabels:
      app: llm
  template:
    metadata:
      labels:
        app: llm
    spec:
      containers:
      - name: llm
        image: my-llm:latest
        env:
        - name: POD_ORDINAL
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
```

**Startup order**: `llm-cluster-0` → `llm-cluster-1` → `llm-cluster-2`
**Shutdown order**: `llm-cluster-2` → `llm-cluster-1` → `llm-cluster-0`

---

## Headless Service + StatefulSet

```bash
# Query pod directly by name
curl http://triton-inference-0.triton-inference:8000/v2/models

# Query via load balancer (any pod)
curl http://triton-inference:8000/v2/models  # ERROR! No IP

# Use individual pod DNS
nslookup triton-inference-0.triton-inference.default.svc.cluster.local
# Returns: 10.0.0.5
```

---

## Scaling StatefulSet

```bash
# Scale up to 5 replicas
kubectl scale sts triton-inference --replicas=5

# Monitor scaling
kubectl get pods -w -l app=triton

# Scale down (removes in reverse order)
kubectl scale sts triton-inference --replicas=2
```

---

## Updates and Rollouts

### Rolling Update (Default)

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2  # Only update pods >= 2
```

Example: `partition: 2` means only update `triton-2, triton-3, ...` (keep `triton-0, triton-1` stable).

### OnDelete Strategy

```yaml
spec:
  updateStrategy:
    type: OnDelete
```

Pods only update when manually deleted. Useful for state-aware apps.

---

## Monitoring StatefulSet

```bash
# Check pod ordinals and status
kubectl get pods -l app=triton -o custom-columns=NAME:.metadata.name,STATUS:.status.phase

# Check PVC binding
kubectl get pvc -l app=triton

# Check pod readiness
kubectl describe pod triton-inference-0 | grep Ready

# Monitor resource usage
kubectl top pod -l app=triton --containers
```

---

## Cleanup and Deletion

```bash
# Delete StatefulSet and keep pods (manual cleanup)
kubectl delete sts triton-inference --cascade=orphan

# Delete StatefulSet and associated pods
kubectl delete sts triton-inference

# Delete PVC after removing StatefulSet
kubectl delete pvc -l app=triton
```

---

## Troubleshooting

### Pod Stuck in Pending

```bash
# Check why pod can't schedule
kubectl describe pod triton-inference-0

# Common causes:
# 1. PVC pending (StorageClass issue)
# 2. GPU not available
# 3. Affinity rules preventing scheduling
```

### Pod Not Ready

```bash
# Check startup probe
kubectl describe pod triton-inference-0 | grep -A 10 "Conditions"

# View logs
kubectl logs triton-inference-0

# Check mount
kubectl exec triton-inference-0 -- ls /models
```

### Network Connectivity

```bash
# Verify headless service
kubectl get svc triton-inference

# Test DNS from pod
kubectl exec triton-inference-0 -- nslookup triton-inference.default.svc.cluster.local

# Test inter-pod communication
kubectl exec triton-inference-0 -- ping triton-inference-1.triton-inference
```

---

## References

- [Kubernetes StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
- [PyTorch Distributed](https://pytorch.org/docs/stable/distributed.html)
- [Fairscale for Distributed Training](https://fairscale.readthedocs.io/)
