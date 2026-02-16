---
name: kubernetes-ai-services
description: |
  Kubernetes for AI/LLM workloads with GPU scheduling, StatefulSets for model serving, custom autoscaling.
  Use when deploying AI agents, LLM inference services, RAG systems, or batch ML workloads to Kubernetes.
  Covers GPU node pools, PV/PVC for models, HPA with custom metrics, and AI-specific resilience patterns.
version: 1.0.1
tags: [kubernetes, ai, llm, gpu, statefulset, autoscaling, production]
---

# Kubernetes for AI/LLM Services: Production Patterns

## 🚀 Before You Deploy

**This section ensures your K8s cluster is ready for AI workloads.**

### Prerequisites Checklist

Before deploying, verify you have:

- [ ] **kubectl** installed: `kubectl version --client`
- [ ] **Kubernetes cluster** accessible: `kubectl cluster-info`
- [ ] **K8s version** 1.24+: `kubectl version | grep Server`
- [ ] **GPU support** (if needed): `kubectl get nodes -L nvidia.com/gpu`
- [ ] **StorageClass** defined: `kubectl get storageclass`
- [ ] **Container registry** access: Can push images
- [ ] **Persistent storage** available: 50GB+ (for model cache)
- [ ] **RBAC enabled**: `kubectl api-resources | grep role`

**Not ready?** See:
- [references/gpu-scheduling.md](references/gpu-scheduling.md) for GPU operator setup
- [references/persistent-storage-ai.md](references/persistent-storage-ai.md) for storage setup

---

### Context Gathering: Your K8s Setup

**Step 1: Cluster Type**

| Type | Best For | Example |
|------|----------|---------|
| **Local** (Minikube) | Development/testing | Single GPU dev machine |
| **Cloud** (EKS/GKE/AKS) | Production | Multi-region inference |
| **On-prem** | Controlled environment | Enterprise deployment |

**Your cluster**: ______________________

**Step 2: GPU Setup**

- [ ] **No GPUs** → Use CPU inference (slower, for testing)
- [ ] **Single GPU node** → Use Deployment + HPA
- [ ] **Multi-GPU nodes** → Use Deployment + tensor parallelism
- [ ] **GPU node pool** → Use nodeSelector + affinity

**Your GPU setup**: ______________________

**Step 3: Storage**

- [ ] **NFS** (shared) → For distributed inference
- [ ] **EBS/GCE disks** (cloud) → For cloud-native
- [ ] **Local storage** → For single-node testing
- [ ] **Object storage** (S3/GCS) → For model artifacts

**Your storage type**: ______________________

---

### Quick Diagnosis: Choose Your Pattern

**Answer these 2 questions to find your deployment pattern:**

```
Question 1: What's your workload?
├─ Real-time inference (chat, API) → Question 2
├─ Batch inference (embeddings, jobs) → PATTERN: Batch Job
└─ Model training → PATTERN: Training Job

Question 2: What scale?
├─ < 100 concurrent users → PATTERN 1: Simple Deployment
├─ 100-1000 concurrent → PATTERN 2: Deployment + HPA
├─ 1000+ concurrent / Multi-region → PATTERN 3: StatefulSet + Custom Scaling
└─ Multiple models / Complex inference → PATTERN 4: Triton Inference Server
```

**Your pattern**: PATTERN _____

---

### ✅ Success Metrics: Verify Deployment

After deploying, verify these metrics:

| Metric | Command | Expected |
|--------|---------|----------|
| **Pod is running** | `kubectl get pods -o wide` | STATUS = Running |
| **GPU allocated** | `kubectl describe pod <pod>` | nvidia.com/gpu: 1 present |
| **Model loads** | `kubectl logs <pod>` | "Model loaded" message |
| **Service accessible** | `kubectl get svc` | External-IP or port-forward works |
| **Health check passes** | `curl http://<service>/health` | `{"status": "ok"}` |
| **HPA working** | `kubectl get hpa` | TARGETS and MINPODS match |
| **Storage mounted** | `kubectl exec <pod> -- ls /models` | Model files visible |
| **No node pressure** | `kubectl describe nodes` | MemoryPressure: False |

---

## Quick Start

```yaml
# Deploy LLM inference with GPU
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llm-inference
  template:
    metadata:
      labels:
        app: llm-inference
    spec:
      containers:
      - name: llm-api
        image: my-llm:latest
        resources:
          limits:
            nvidia.com/gpu: 1  # Require 1 GPU
            memory: 32Gi
          requests:
            nvidia.com/gpu: 1
            memory: 24Gi
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          failureThreshold: 60  # 5 min for model load
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: llm-inference
spec:
  selector:
    app: llm-inference
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

See [references/gpu-scheduling.md] for node setup | [references/custom-autoscaling.md] for scaling

---

## 🎯 Real-World K8s Deployment Scenarios

### Scenario 1: "Deploy Llama 2 7B Chat to EKS with auto-scaling"

**Setup:**
- Cluster: AWS EKS
- Model: Llama 2 7B (13GB)
- Users: 100-500 concurrent
- Cost: Minimize

**Solution (copy-paste):**
```bash
# 1. Create GPU node group (on EKS)
aws eks create-nodegroup \
  --cluster-name prod-cluster \
  --nodegroup-name gpu-nodes \
  --node-role arn:aws:iam::ACCOUNT:role/NodeInstanceRole \
  --subnets subnet-xxx \
  --instance-types g4dn.xlarge \
  --desired-size 2 \
  --min-size 1 \
  --max-size 5

# 2. Install GPU operator
helm repo add nvidia https://nvidia.github.io/k8s-device-plugin
helm install nvidia-gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator-system --create-namespace

# 3. Create PVC for models
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: llm-models
spec:
  accessModes:
    - ReadOnlyMany
  storageClassName: gp3
  resources:
    requests:
      storage: 50Gi
EOF

# 4. Deploy with HPA
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-chat
spec:
  replicas: 2
  selector:
    matchLabels:
      app: llm-chat
  template:
    metadata:
      labels:
        app: llm-chat
    spec:
      containers:
      - name: llm
        image: my-llm:latest
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
      nodeSelector:
        nvidia.com/gpu: "true"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-chat-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-chat
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
EOF

# 5. Expose service
kubectl expose deployment llm-chat --port=8000 --type=LoadBalancer
```

**Expected Results:**
- Startup: 2-3 min (cluster + pods)
- Throughput: 20-30 tokens/sec
- Concurrency: 100-200 users
- Cost: ~$0.50/hour (2x g4dn.xlarge) → auto-scales to $2.50/hour at peak
- Scales down to 1 node at night

---

### Scenario 2: "Batch embeddings for 10M documents on GKE"

**Setup:**
- Cluster: GCP GKE
- Model: sentence-transformers (90MB)
- Data: 10M documents
- Goal: 1M docs/day

**Solution:**
```bash
# Create Job manifest
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: embeddings-batch
spec:
  parallelism: 4
  completions: 100
  backoffLimit: 3
  template:
    spec:
      containers:
      - name: worker
        image: embeddings-worker:latest
        env:
        - name: BATCH_SIZE
          value: "1000"
        - name: INPUT_BUCKET
          value: gs://data-input
        - name: OUTPUT_BUCKET
          value: gs://data-output
        volumeMounts:
        - name: cache
          mountPath: /models
      volumes:
      - name: cache
        persistentVolumeClaim:
          claimName: model-cache
      restartPolicy: Never
EOF

# Monitor progress
kubectl logs -f -l job-name=embeddings-batch --all-pods=true
```

**Expected:**
- Speed: 100,000 docs/hour
- Time for 10M: 100 hours (4 parallel workers)
- Cost: ~$10 total (CPU only, no GPU needed)

---

### Scenario 3: "Production RAG system (FastAPI + Qdrant + LLM)"

**Architecture:**
```
Ingress → FastAPI pods (3) ↔ Qdrant StatefulSet (3) → LLM pods (2)
                                                       (with GPU)
```

**Solution:**
```bash
# 1. Deploy Qdrant (vector DB)
helm repo add qdrant https://qdrant.github.io/helm
helm install qdrant qdrant/qdrant \
  --set replicaCount=3 \
  --set persistence.enabled=true \
  --set persistence.size=200Gi

# 2. Deploy FastAPI (CPU)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-api
  template:
    metadata:
      labels:
        app: rag-api
    spec:
      containers:
      - name: api
        image: rag-fastapi:latest
        env:
        - name: QDRANT_HOST
          value: qdrant
        - name: QDRANT_PORT
          value: "6333"
        - name: LLM_SERVICE
          value: llm-service:8000
        resources:
          requests:
            cpu: 1
            memory: 2Gi
          limits:
            cpu: 2
            memory: 4Gi
---
apiVersion: v1
kind: Service
metadata:
  name: rag-api
spec:
  type: LoadBalancer
  selector:
    app: rag-api
  ports:
  - port: 8000
    targetPort: 8000
EOF

# 3. Deploy LLM (GPU)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: llm-service
  template:
    metadata:
      labels:
        app: llm-service
    spec:
      containers:
      - name: llm
        image: my-llm:latest
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
      nodeSelector:
        nvidia.com/gpu: "true"
---
apiVersion: v1
kind: Service
metadata:
  name: llm-service
spec:
  clusterIP: None
  selector:
    app: llm-service
  ports:
  - port: 8000
EOF
```

**Expected:**
- Query latency: 500-1000ms (RAG + LLM)
- Concurrency: 50-100 users
- Throughput: 10-20 responses/second

---

## 📊 K8s Pattern Selection Table

| Pattern | Workload | Complexity | Cost | Scale | When to Use |
|---------|----------|-----------|------|-------|------------|
| **1: Simple Deployment** | Chat API | Low | Low | < 100 users | Testing, small scale |
| **2: Deployment + HPA** | Chat API | Medium | Medium | 100-1000 users | Production, dynamic load |
| **3: StatefulSet** | Multi-model | High | High | 1000+ users | Large scale, distributed |
| **4: Triton** | Multi-model | Very High | Very High | Enterprise | Complex inference graphs |
| **5: Batch Job** | Embeddings/batch | Low | Low | One-time | Scheduled processing |
| **6: RAG Stack** | RAG system | Very High | High | Enterprise | Full AI application |

---

## GPU Resource Management in Kubernetes

### GPU Node Pool Setup

**Step 1: Label GPU nodes**
```bash
# Check for GPUs
kubectl get nodes -L nvidia.com/gpu

# Manually add GPU labels if missing
kubectl label nodes <node-name> nvidia.com/gpu=true
```

**Step 2: Taint GPU nodes (optional, for dedicated use)**
```bash
kubectl taint nodes gpu-node-1 nvidia-gpu=true:NoSchedule
```

**Step 3: Verify GPU operator**
```bash
kubectl get daemonset -n nvidia-gpu-operator
# Should show:
# nvidia-device-plugin-daemonset
# nvidia-driver-daemon
```

### Requesting GPUs in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: llm-inference
spec:
  containers:
  - name: llm-api
    image: my-llm:latest
    resources:
      limits:
        nvidia.com/gpu: 1  # Must equal requests
      requests:
        nvidia.com/gpu: 1  # Guaranteed allocation
  nodeSelector:
    nvidia.com/gpu: "true"  # Schedule on GPU nodes
  tolerations:  # If tainted
  - key: nvidia-gpu
    operator: Equal
    value: "true"
    effect: NoSchedule
```

**Critical**: `limits.nvidia.com/gpu` must equal `requests.nvidia.com/gpu` for QoS Guaranteed

### Multi-GPU Support

```yaml
# Request multiple GPUs
resources:
  limits:
    nvidia.com/gpu: 4  # Get all 4 GPUs
  requests:
    nvidia.com/gpu: 4

# Environment variables automatically set:
# NVIDIA_VISIBLE_DEVICES=0,1,2,3
# CUDA_VISIBLE_DEVICES=0,1,2,3
```

---

## StatefulSets for Model Serving

### Pattern: Triton Inference Server with Persistent Models

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: triton-inference
spec:
  serviceName: triton-inference  # Headless service
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
        podAntiAffinity:  # Spread replicas across nodes
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
          name: grpc
        - containerPort: 8001
          name: metrics
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: 16Gi
          requests:
            nvidia.com/gpu: 1
            memory: 12Gi
        volumeMounts:
        - name: model-repository
          mountPath: /models
        startupProbe:
          httpGet:
            path: /v2/health/ready
            port: 8000
          failureThreshold: 60
          periodSeconds: 5
  volumeClaimTemplates:  # PVC per replica
  - metadata:
      name: model-repository
    spec:
      accessModes: ["ReadOnlyMany"]  # Read-only, shared cache
      storageClassName: fast-nvme
      resources:
        requests:
          storage: 100Gi
---
apiVersion: v1
kind: Service
metadata:
  name: triton-inference
spec:
  clusterIP: None  # Headless
  selector:
    app: triton
  ports:
  - port: 8000
    targetPort: 8000
    name: grpc
```

**Why StatefulSets**:
- **Stable hostnames**: triton-inference-0, triton-inference-1 (useful for debugging)
- **Persistent cache**: PVC attached to each replica
- **Ordered deployments**: Controlled rollout
- **Pod identity**: Each replica has unique identity

---

## Persistent Storage for Large Models

### PVC for Shared Model Cache (ReadOnlyMany)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: llm-model-cache
spec:
  accessModes:
  - ReadOnlyMany  # Multiple pods read-only
  storageClassName: fast-nvme
  resources:
    requests:
      storage: 500Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference
spec:
  replicas: 5
  template:
    spec:
      initContainers:
      - name: download-model  # Runs before main container
        image: model-downloader:latest
        volumeMounts:
        - name: models
          mountPath: /models
        env:
        - name: HF_HOME
          value: /models
        command:
        - sh
        - -c
        - |
          # Only download if not already there
          [ -d /models/llama-2-7b ] || \
          huggingface-cli download meta-llama/Llama-2-7b-chat-hf --local-dir /models/llama-2-7b
      containers:
      - name: llm-api
        image: my-llm:latest
        volumeMounts:
        - name: models
          mountPath: /models
          readOnly: true  # Read-only access
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: llm-model-cache
```

### Populate Cache (One-Time Job)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: populate-model-cache
spec:
  template:
    spec:
      containers:
      - name: download
        image: python:3.11
        volumeMounts:
        - name: models
          mountPath: /models
        command:
        - sh
        - -c
        - |
          pip install huggingface-hub transformers
          huggingface-cli download meta-llama/Llama-2-70b-chat-hf \
            --local-dir /models/llama-2-70b
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: llm-model-cache
      restartPolicy: Never
```

---

## Custom Autoscaling for AI Workloads

### HPA with Custom Metrics (Queue Depth)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: llm-api
        env:
        - name: QUEUE_DEPTH_METRIC  # App exports this metric
          value: "inference_queue_depth"
---
apiVersion: autoscaling.custom.io/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-inference-autoscale
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: inference_queue_depth  # Custom metric
      target:
        type: AverageValue
        averageValue: "10"  # Target queue depth per pod
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

### KEDA for Advanced Metrics

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: llm-inference-scaler
spec:
  scaleTargetRef:
    name: llm-inference
  minReplicaCount: 2
  maxReplicaCount: 20
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      metricName: inference_queue_depth
      query: |
        avg(inference_queue_depth{pod="llm-inference"})
      threshold: "10"
  - type: cpu
    metadata:
      type: Utilization
      value: "80"  # Fallback to CPU at 80%
```

---

## Health Checks for Large Model Loading

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: llm-inference
spec:
  containers:
  - name: llm-api
    image: my-llm:latest
    ports:
    - containerPort: 8000
    startupProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 0  # Check immediately
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 120  # 10 minutes (120 * 5s)
      successThreshold: 1
    readinessProbe:
      httpGet:
        path: /ready
        port: 8000
      initialDelaySeconds: 0
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 3
      successThreshold: 1
    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 120
      periodSeconds: 30
      timeoutSeconds: 5
      failureThreshold: 3
```

**Application code:**
```python
from fastapi import FastAPI

app = FastAPI()

model = None
model_loading = False

@app.on_event("startup")
async def load_model():
    global model, model_loading
    model_loading = True
    model = load_llm_model()  # Can take 5-10 minutes
    model_loading = False

@app.get("/health")
def health():
    # Startup probe: returns 200 once model loads
    return {"status": "ok"} if model else {"status": "loading"}

@app.get("/ready")
def ready():
    # Readiness probe: only ready after health + inference test
    if not model or model_loading:
        raise HTTPException(status_code=503)
    return {"status": "ready"}
```

---

## Deployment Patterns

### Canary Deployment (Progressive Rollout)

```yaml
apiVersion: fluxcd.io/v1beta1
kind: Kustomization
metadata:
  name: llm-inference
spec:
  targetNamespace: production
  serviceAccountName: flux
  sourceRef:
    kind: GitRepository
    name: flux-system
  path: ./k8s/llm-inference
  interval: 1m0s
  retryInterval: 1m0s
  timeout: 5m0s
  validation: client
  postBuild:
    substitute:
      canary_replicas: "1"  # Start with 1 replica
      stable_replicas: "4"  # Keep 4 stable
---
# Blue-green deployment
apiVersion: v1
kind: Service
metadata:
  name: llm-inference
spec:
  selector:
    version: blue  # Point to blue deployment initially
  ports:
  - port: 8000
    targetPort: 8000
```

### Batch Inference Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-embeddings
spec:
  parallelism: 4  # 4 parallel workers
  completions: 100  # Wait for 100 completions
  backoffLimit: 3
  template:
    spec:
      containers:
      - name: embedding-worker
        image: embedding-service:latest
        env:
        - name: BATCH_SIZE
          value: "32"
        - name: INPUT_BUCKET
          value: s3://data-input/
        - name: OUTPUT_BUCKET
          value: s3://data-output/
        resources:
          limits:
            gpu: 1
            memory: 16Gi
      restartPolicy: Never
```

---

## ConfigMaps and Secrets

### Model Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-config
data:
  model_name: meta-llama/Llama-2-70b-chat-hf
  model_dtype: float16
  max_tokens: 4096
  temperature: "0.7"
---
apiVersion: v1
kind: Secret
metadata:
  name: llm-credentials
type: Opaque
stringData:
  HF_TOKEN: <base64-encoded-token>
  API_KEY: <api-key>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference
spec:
  template:
    spec:
      containers:
      - name: llm-api
        envFrom:
        - configMapRef:
            name: llm-config
        - secretRef:
            name: llm-credentials
```

---

## Kubernetes Security for AI Deployments

### Pod Security Policy

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted-ai
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'secret'
    - 'persistentVolumeClaim'
  hostNetwork: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  fsGroup:
    rule: 'RunAsAny'
```

### Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: llm-inference-deny-all
spec:
  podSelector:
    matchLabels:
      app: llm-inference
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:  # Allow to PVC
        matchLabels:
          pvc: model-cache
  - to:  # Allow DNS
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
```

---

## Debugging AI Workloads

### Check GPU Allocation

```bash
# View GPU nodes and capacity
kubectl get nodes -L nvidia.com/gpu

# Check GPU usage per pod
kubectl top pod -A | grep -i gpu

# Inspect pod GPU request/limits
kubectl describe pod llm-inference-0 | grep -A 5 "Limits\|Requests"

# Check if GPU is actually allocated
kubectl exec llm-inference-0 -- nvidia-smi
```

### Model Loading Issues

```bash
# Check startup probe status
kubectl describe pod llm-inference-0 | grep -A 10 "Conditions"

# View logs during startup
kubectl logs llm-inference-0 --previous  # If crashed

# Check model cache PVC
kubectl get pvc
kubectl exec <pod> -- ls -lah /models

# Verify model exists
kubectl exec llm-inference-0 -- python -c \
  "from transformers import AutoModelForCausalLM; \
   model = AutoModelForCausalLM.from_pretrained('/models/llama-2-7b')"
```

### Performance Issues

```bash
# Check resource usage
kubectl top pod llm-inference-0 --containers

# Check if requests are being queued
kubectl logs llm-inference-0 | grep "queue_depth"

# View HPA status
kubectl describe hpa llm-inference-autoscale

# Check pending pods
kubectl get pods -o wide | grep Pending
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy with GPU | `kubectl apply -f deployment-gpu.yaml` |
| Check GPU status | `kubectl top pod -A` |
| View HPA scaling | `kubectl describe hpa <name>` |
| Get pod logs | `kubectl logs <pod> -c <container>` |
| Exec into pod | `kubectl exec -it <pod> -- /bin/bash` |
| Debug startup | `kubectl describe pod <pod> | grep Conditions` |

---

## 🔧 Troubleshooting Decision Tree

**Follow this decision tree to resolve common K8s AI deployment issues:**

```
PROBLEM: Pod won't start
├─ Status: ImagePullBackOff
│  └─ Fix: Push image to registry, check imagePullSecrets
├─ Status: Pending
│  ├─ Check: kubectl describe pod (Node affinity/taint issue?)
│  ├─ No GPU available? → Check GPU operator, node labels
│  └─ Insufficient resources? → Add nodes or reduce replicas
├─ Status: CrashLoopBackOff
│  └─ Fix: kubectl logs <pod> → Check startup errors
│  └─ Common: Model download timeout → Increase startupProbe.failureThreshold

PROBLEM: Pod starts but inference fails
├─ GPU not detected
│  ├─ Check: kubectl exec <pod> -- nvidia-smi
│  ├─ Returns error? → GPU driver issue (verify gpu-operator)
│  └─ Returns devices? → App not using GPU correctly
├─ Model takes too long to load
│  ├─ Check: kubectl logs <pod> | grep "loading\|progress"
│  ├─ Timeout? → Increase startupProbe.failureThreshold (120 = 10 min)
│  └─ Hangs? → Check PVC mounted, model file exists
├─ Inference runs but slow
│  ├─ Check: kubectl top pod --containers (GPU util?)
│  ├─ GPU idle? → Model not using GPU (code issue)
│  └─ GPU busy? → Normal, check latency requirements

PROBLEM: HPA not scaling
├─ Check: kubectl describe hpa <name>
├─ Status: "unknown" metrics?
│  └─ Fix: Install Prometheus Adapter (if using custom metrics)
├─ Status: Desired = Replicas?
│  ├─ CPU-based scaling? → Verify current CPU > threshold
│  └─ Custom metrics? → Check metric value in Prometheus
├─ Not scaling up fast enough?
│  └─ Fix: Reduce stabilizationWindowSeconds (default 300s)

PROBLEM: Storage issues
├─ PVC stuck in Pending
│  └─ Fix: Check StorageClass, check cloud quota
├─ Model files missing
│  ├─ Check: kubectl exec <pod> -- ls /models
│  ├─ Empty? → Init container failed, check logs
│  └─ Fix: kubectl describe pod (init container section)
├─ Permission denied on PVC
│  └─ Fix: Check fsGroup in pod spec, PVC file ownership

PROBLEM: Memory/OOM issues
├─ Pod evicted (OOMKilled)
│  ├─ Check: kubectl describe pod | grep OOMKilled
│  ├─ Fix: Increase memory limit
│  └─ Or: Reduce batch size, model quantization
├─ Node memory pressure
│  └─ Check: kubectl describe nodes | grep MemoryPressure
│  └─ Fix: Add nodes, reduce pod replicas, enable memory limits

PROBLEM: Networking/connectivity
├─ Service unreachable
│  ├─ Check: kubectl get svc, kubectl get ep
│  ├─ No endpoints? → Pods not matching selector labels
│  └─ Fix: Verify app port = service.targetPort
├─ DNS resolution fails
│  └─ Fix: kubectl run debug --image=nicolaka/netshoot -- nslookup qdrant
├─ Network policy blocking traffic
│  └─ Check: kubectl get networkpolicies
│  └─ Fix: Add ingress rules for required services
```

---

## ✅ Production Readiness Checklist

**Use this checklist before deploying AI services to production:**

### Phase 1: Pre-Cluster (Before any K8s work)

- [ ] **Cluster planned**: EKS/GKE/AKS selected, region chosen, cost estimated
- [ ] **GPU quota verified**: Enough GPUs available (check cloud limits)
- [ ] **Storage provisioned**: 50GB+ for model cache, snapshots enabled
- [ ] **Registry ready**: Can push/pull images (ECR/GCR/ACR)
- [ ] **Monitoring decided**: Prometheus + Grafana, cloud native, or custom
- [ ] **DNS planned**: Ingress domain, TLS certificate (if external)

### Phase 2: Cluster Preparation

- [ ] **Cluster deployed**: 1.24+ K8s version verified
- [ ] **GPU operator installed**: `kubectl get daemonset -n gpu-operator-system` returns 3 daemonsets
- [ ] **GPU verified**: `kubectl get nodes -L nvidia.com/gpu` shows GPU nodes
- [ ] **GPU test pod**: `kubectl run gpu-test --image=nvidia/cuda:12.0 -- nvidia-smi` returns GPU info
- [ ] **StorageClass created**: Default SC exists for models (`kubectl get sc`)
- [ ] **PVC tested**: Create test PVC, verify it binds
- [ ] **RBAC configured**: Roles created for CI/CD, operators, monitoring
- [ ] **Network policies reviewed**: Understand Ingress/egress rules
- [ ] **Backup configured**: PVC snapshots enabled for production models

### Phase 3: Deployment Preparation

- [ ] **Image optimized**: Multi-stage build, model caching, <5GB size
- [ ] **Image scanned**: Trivy/Snyk scan passed, CVE review
- [ ] **Health checks defined**: /health, /ready endpoints implemented
- [ ] **Startup probe tuned**: failureThreshold accounts for model load time
- [ ] **Resources right-sized**: requests/limits set, QoS Guaranteed for GPU
- [ ] **GPU allocation**: Verified limits == requests (critical for QoS)
- [ ] **PVC claim created**: Model storage PVC exists, accessible
- [ ] **Init container tested**: Model download/setup works locally
- [ ] **Env vars reviewed**: No secrets in deployment, ConfigMap/Secrets used
- [ ] **HPA configured**: minReplicas >= 2 for HA, maxReplicas <= available GPU quota
- [ ] **Metrics provider ready**: Prometheus Adapter for custom metrics (if needed)

### Phase 4: Deployment Phase

- [ ] **Dry-run succeeds**: `kubectl apply -f manifest.yaml --dry-run`
- [ ] **YAML validated**: No syntax errors, all required fields present
- [ ] **Namespace created**: `kubectl create namespace prod`
- [ ] **Secrets deployed**: Registry secrets, HF tokens, API keys
- [ ] **ConfigMaps deployed**: Model config, feature flags
- [ ] **Deployment applied**: `kubectl apply -f manifest.yaml`
- [ ] **Pods running**: `kubectl get pods -w` shows all Running
- [ ] **Init containers completed**: Check pod events, no errors
- [ ] **Model loaded**: Check logs, "Model loaded" message appears
- [ ] **Health checks passing**: `kubectl describe pod | grep Conditions`
- [ ] **Service endpoints ready**: `kubectl get ep` shows pod IPs
- [ ] **Ingress configured**: LoadBalancer/Ingress accessible

### Phase 5: Post-Deployment

- [ ] **Smoke test passed**: `curl http://service:8000/health` returns 200
- [ ] **Inference works**: Test actual inference with test data
- [ ] **Metrics flowing**: Pod metrics visible in `kubectl top pod`
- [ ] **Custom metrics ready**: Prometheus has app metrics
- [ ] **HPA scaling tested**: Manually increase load, verify pods scale up
- [ ] **Graceful shutdown tested**: SIGTERM handling, in-flight requests complete
- [ ] **Log aggregation working**: Logs visible in centralized logging system
- [ ] **Alerts configured**: Critical thresholds set (high memory, pod restart, latency)
- [ ] **Performance baseline**: Document p50/p95/p99 latency, throughput
- [ ] **Cost tracking**: Resource requests tracked, GPU hours monitored
- [ ] **Runbook created**: How to restart, scale, rollback, access pods
- [ ] **Disaster recovery tested**: Can recover from PVC loss, node failure

---

## 📅 How to Keep This Skill Updated

**K8s and AI frameworks evolve quickly. Use this schedule to stay current:**

### Monthly (1 hour)

- [ ] **Check K8s releases**: https://github.com/kubernetes/kubernetes/releases
  - New GPU features? Check release notes for gpu-related changes
  - Security patches? Update cluster version if critical
- [ ] **Check NVIDIA GPU Operator**: https://github.com/NVIDIA/gpu-operator/releases
  - New CUDA version support? Update install instructions
  - New GPU models? Add to gpu-scheduling.md
- [ ] **Check inference frameworks**: vLLM, TGI, Triton release notes
  - New features? Update inference-patterns.md with examples

### Quarterly (2 hours)

- [ ] **Run verification script**: `python scripts/verify.py`
  - All checks passing? If not, update installation steps
- [ ] **Test example scenarios**: Deploy Llama 2 example to test cluster
  - Works as documented? If not, update references
  - Latency/cost expectations still accurate?
- [ ] **Review Kubernetes docs**: https://kubernetes.io/docs/tasks/manage-gpus/
  - New GPU patterns? Add to SKILL.md
  - GPU sharing (MIG) best practices changed? Update gpu-scheduling.md
- [ ] **Check cloud provider GPU docs**:
  - AWS: https://aws.amazon.com/blogs/containers/ (GPU topics)
  - GCP: https://cloud.google.com/kubernetes-engine/docs/concepts/gpu (New instance types?)
  - Azure: https://docs.microsoft.com/en-us/azure/aks/ (New GPU SKUs?)

### Annually (4 hours)

- [ ] **Deep review of references**: Each reference file accuracy
- [ ] **Update version numbers**: K8s version, GPU operator version, Python versions
- [ ] **Test all examples**:
  - GPU node creation still works (cloud CLIs might change)
  - All manifests still valid YAML
  - Helm install commands still work
- [ ] **Review troubleshooting section**: Collect new issues from community
  - GitHub issues from k8s, GPU operator repos
  - Common production problems from your team

---

## Related Skills

- **[docker-ai-production](../docker-ai-production/SKILL.md)** — Containerize AI services
- **[deploying-cloud-k8s](../deploying-cloud-k8s/SKILL.md)** — Cloud K8s basics (EKS/GKE/AKS)
- **[operating-k8s-local](../operating-k8s-local/SKILL.md)** — Local K8s with Minikube
- **[building-fastapi-apps](../building-fastapi-apps/SKILL.md)** — API patterns for AI services
- **[building-rag-systems](../building-rag-systems/SKILL.md)** — RAG pipeline deployment

---

## 📚 References Index

| Topic | File | Coverage | Keep Updated | Official Docs |
|-------|------|----------|--------------|---------------|
| **GPU Scheduling** | [gpu-scheduling.md](references/gpu-scheduling.md) | GPU operator, NVIDIA runtime, node pools, cloud setup | Monthly | [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/) \| [K8s GPU Docs](https://kubernetes.io/docs/tasks/manage-gpus/) |
| **Model Serving** | [model-serving-architectures.md](references/model-serving-architectures.md) | Triton, vLLM, Ray Serve, KServe, Seldon, traffic splitting | Quarterly | [Triton Docs](https://docs.nvidia.com/deeplearning/triton-inference-server/) \| [KServe Docs](https://kserve.github.io/website/) |
| **Custom Autoscaling** | [custom-autoscaling.md](references/custom-autoscaling.md) | HPA, custom metrics, Prometheus Adapter, KEDA, cluster autoscaler | Quarterly | [K8s HPA Docs](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) \| [KEDA Docs](https://keda.sh/) |
| **StatefulSets** | [statefulsets-for-ai.md](references/statefulsets-for-ai.md) | When to use, persistent cache, distributed inference, headless services | Quarterly | [K8s StatefulSet Docs](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) |
| **Persistent Storage** | [persistent-storage-ai.md](references/persistent-storage-ai.md) | PV/PVC patterns, StorageClass, object storage mounting (S3/GCS), snapshots | Quarterly | [K8s PV Docs](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) \| [EBS CSI](https://github.com/kubernetes-sigs/aws-ebs-csi-driver) |
| **Observability** | [ai-observability.md](references/ai-observability.md) | Prometheus metrics, DCGM, ServiceMonitor, Grafana dashboards, SLO/SLI | Quarterly | [Prometheus Docs](https://prometheus.io/docs/) \| [DCGM Docs](https://developer.nvidia.com/dcgm) |
| **Troubleshooting** | [troubleshooting-ai-k8s.md](references/troubleshooting-ai-k8s.md) | 30+ K8s AI issues, symptoms, causes, debugging commands, fixes | Monthly | [K8s Debug Guide](https://kubernetes.io/docs/tasks/debug-application-cluster/) |

---

**Skill Metadata**:
- **Version**: 1.0.1
- **Last Updated**: February 2025
- **K8s Versions Tested**: 1.24, 1.25, 1.26, 1.27, 1.28, 1.29
- **GPU Operator Tested**: 24.3.0+
- **Status**: Production-Ready
- **Update Schedule**: Monthly checks, quarterly deep-dives, annual comprehensive review
