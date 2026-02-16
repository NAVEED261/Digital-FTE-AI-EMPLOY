# Troubleshooting AI Workloads on Kubernetes

This reference covers 30+ battle-tested K8s + AI issues with symptoms, root causes, and fixes.

## Quick Diagnosis Matrix

| Symptom | Probable Causes | First Check |
|---------|-----------------|------------|
| Pod won't start | Image pull, resource limit, init container | `kubectl describe pod` |
| Pod starts but slow | Model loading timeout | `kubectl logs -f <pod>` |
| GPU not detected | Driver missing, device plugin | `kubectl exec <pod> -- nvidia-smi` |
| OOM killed | Model too big, batch size | `kubectl describe pod` → Limits |
| Inference timeout | Queue backed up, model hanging | `kubectl logs <pod>` + `kubectl top pod` |
| Can't connect to service | DNS/network policy | `kubectl exec <pod> -- nslookup` |
| HPA not scaling | Metrics not flowing | `kubectl describe hpa` |
| Cost explosion | Too many replicas, high GPU | `kubectl top nodes -l gpu=true` |

---

## Issue 1: ImagePullBackOff

**Symptom**: Pod stuck in `ImagePullBackOff` for 10+ minutes

**Root Cause**: Image can't be pulled from registry

**Diagnosis**:
```bash
kubectl describe pod llm-inference-0
# Look for: Failed to pull image "my-llm:latest": image not found
```

**Fix**:
```bash
# 1. Verify image exists
docker images | grep my-llm
# Not there? Build it: docker build -t my-llm:latest .

# 2. Push to registry
docker tag my-llm:latest myregistry.azurecr.io/my-llm:latest
docker push myregistry.azurecr.io/my-llm:latest

# 3. Add imagePullSecret to pod
kubectl create secret docker-registry myregsecret \
  --docker-server=myregistry.azurecr.io \
  --docker-username=username \
  --docker-password=password

# 4. Update deployment
kubectl patch deployment llm-inference -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"myregsecret"}]}}}}'
```

---

## Issue 2: CrashLoopBackOff on Startup

**Symptom**: Pod restarts every 10 seconds

**Root Cause**: Startup error in application code

**Diagnosis**:
```bash
kubectl logs llm-inference-0 --previous
# Look for: ModuleNotFoundError, FileNotFoundError, OOM
```

**Fix** (depends on error):
```bash
# Missing dependency
# Update Dockerfile: pip install transformers torch

# Model file not found
# Use init container to download model

# Memory issues
kubectl set resources deployment llm-inference --limits=memory=32Gi --requests=memory=24Gi
```

---

## Issue 3: Pod Pending (Can't Schedule)

**Symptom**: Pod in `Pending` state, never transitions to `Running`

**Root Cause**: Insufficient resources or affinity mismatch

**Diagnosis**:
```bash
kubectl describe pod llm-inference-0 | grep -A 5 "Events"
# Will show: 0/3 nodes are available (1 node GPU, 2 insufficient memory)
```

**Fix** (check each):
```bash
# 1. Check GPU availability
kubectl get nodes -L nvidia.com/gpu

# 2. If no GPUs, install GPU operator
helm install nvidia-gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator-system --create-namespace

# 3. Check memory
kubectl describe nodes | grep -A 5 "Allocatable"

# 4. Reduce pod requests or add nodes
kubectl set resources deployment llm-inference --requests=memory=16Gi

# 5. Check affinity constraints
kubectl get pod llm-inference-0 -o yaml | grep -A 20 "affinity"
```

---

## Issue 4: Model Never Loads (Startup Probe Timeout)

**Symptom**: Pod runs but startup probe fails after 300 seconds (5 min)

**Root Cause**: Model download taking too long

**Diagnosis**:
```bash
kubectl describe pod llm-inference-0 | grep -A 20 "Conditions"
# Startup: False (Probe Timeout)

# Check what's happening
kubectl logs llm-inference-0 | tail -50
# Should see download progress
```

**Fix**:
```bash
# 1. Increase startup probe timeout
# failureThreshold * periodSeconds = total timeout
# Current: 60 * 5 = 300s. Need 10 min? Use 120 * 5 = 600s

kubectl patch deployment llm-inference --type merge -p '
{
  "spec":{
    "template":{
      "spec":{
        "containers":[{
          "name":"llm-api",
          "startupProbe":{
            "failureThreshold":120
          }
        }]
      }
    }
  }
}'

# 2. Or: Pre-download model in init container
# See: persistent-storage-ai.md reference
```

---

## Issue 5: GPU Not Detected in Pod

**Symptom**: Pod runs but `nvidia-smi` returns "No devices found"

**Root Cause**: GPU not allocated, driver issue, or environment variable

**Diagnosis**:
```bash
kubectl exec llm-inference-0 -- nvidia-smi
# Returns: No devices found

# Check pod GPU request
kubectl describe pod llm-inference-0 | grep -A 2 "nvidia.com/gpu"
# Should see: limits: nvidia.com/gpu: 1
```

**Fix**:
```bash
# 1. Check if GPU allocated
kubectl describe pod llm-inference-0 | grep -A 5 "Allocate"

# 2. Verify GPU operator is running
kubectl get daemonset -n gpu-operator-system

# 3. Check node GPU labels
kubectl get nodes -L nvidia.com/gpu

# 4. If no labels, manually add
kubectl label nodes gpu-node-1 nvidia.com/gpu=true

# 5. Add nodeSelector to pod
kubectl patch deployment llm-inference -p '
{
  "spec":{
    "template":{
      "spec":{
        "nodeSelector":{"nvidia.com/gpu":"true"}
      }
    }
  }
}'
```

---

## Issue 6: OOMKilled (Out of Memory)

**Symptom**: Pod killed with exit code 137 or "OOMKilled" status

**Root Cause**: Memory request too low for model

**Diagnosis**:
```bash
kubectl describe pod llm-inference-0 | grep -i "OOM"
# Shows: OOMKilled=true

# Check memory usage at time of death
kubectl top pod llm-inference-0 --containers
# May show high usage before crash
```

**Fix**:
```bash
# 1. Increase memory limit
kubectl set resources deployment llm-inference \
  --limits=memory=40Gi \
  --requests=memory=32Gi

# 2. Or: Use quantized model (smaller)
# GGUF: 7B model = 4GB (vs 14GB full precision)
# GPTQ: 7B model = 3.5GB

# 3. Or: Reduce batch size
# Env var: BATCH_SIZE=4 (vs 16)
```

---

## Issue 7: Inference Timeout (Pod Hangs)

**Symptom**: Inference request hangs forever or times out after 30s

**Root Cause**: Model stuck, queue backed up, or deadlock

**Diagnosis**:
```bash
# Check if pod responsive
kubectl exec llm-inference-0 -- curl http://localhost:8000/health

# Check logs for warnings
kubectl logs llm-inference-0 | grep -i "warning\|error\|hang"

# Check if inference queue is full
kubectl logs llm-inference-0 | grep "queue"

# Check GPU status
kubectl exec llm-inference-0 -- nvidia-smi
# GPU util should be high (>50%) if inferencing
```

**Fix**:
```bash
# 1. Increase timeout in client
# FastAPI: response_timeout=300

# 2. Scale up pods to reduce queue
kubectl scale deployment llm-inference --replicas=5

# 3. Or: Use HPA to auto-scale
kubectl apply -f hpa.yaml  # See references/custom-autoscaling.md

# 4. Or: Reduce batch size to process faster
kubectl set env deployment llm-inference BATCH_SIZE=4
```

---

## Issue 8: HPA Not Scaling (Desired == Current)

**Symptom**: HPA shows `Desired: 2, Current: 2` but load is high

**Root Cause**: Metrics not flowing, threshold too high, or resource limit

**Diagnosis**:
```bash
kubectl describe hpa llm-inference-hpa
# Check "Metrics" section - should show current values

# If "unknown" or "unavaialable"
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1 | jq .
# If 404: Prometheus Adapter not installed
```

**Fix**:
```bash
# 1. Install Prometheus Adapter
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  --namespace monitoring

# 2. Check metric target
kubectl describe hpa | grep "Target:"
# Should show: "80% CPU" or custom metric value

# 3. Check current metric
kubectl get hpa llm-inference-hpa -A -w
# Watch for metric values updating

# 4. Verify Prometheus is scraping
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visit http://localhost:9090 and query metric
```

---

## Issue 9: Pod Evicted (Node Pressure)

**Symptom**: Pod evicted, status shows `Evicted`, reason: `NodeMemoryPressure`

**Root Cause**: Node running out of memory, pod got kicked off

**Diagnosis**:
```bash
kubectl describe pod llm-inference-0 | grep -i "evicted"

# Check node status
kubectl describe nodes | grep -A 5 "Conditions"
# Should show: MemoryPressure: True
```

**Fix**:
```bash
# 1. Delete evicted pods
kubectl delete pods --field-selector status.phase=Failed -A

# 2. Add more nodes
# EKS: aws ec2 describe-instances --filters "Name=tag:eks:nodegroup-name,Values=gpu-nodes"
# Then scale node group

# 3. Or: Reduce pod memory requests
kubectl set resources deployment llm-inference --requests=memory=24Gi

# 4. Or: Enable memory limits
# Deployment already has limits, but check kubelet --max-pods=110
```

---

## Issue 10: Service Unreachable (Connection Refused)

**Symptom**: `curl http://llm-inference:8000/health` → Connection refused

**Root Cause**: Pod not ready, service has no endpoints, wrong port

**Diagnosis**:
```bash
# Check service has endpoints
kubectl get endpoints llm-inference

# Check pod is running
kubectl get pods -l app=llm-inference

# Check port matching
kubectl get svc llm-inference -o yaml | grep -A 5 "ports"
kubectl get pod llm-inference-0 -o yaml | grep -A 5 "ports"
```

**Fix**:
```bash
# 1. Port mismatch
# Service port=8000, container port=9000 → Fix container port

# 2. Pod not ready
kubectl logs llm-inference-0
# Fix startup issue (see Issue 2)

# 3. Readiness probe failing
# Container ready but probe says not ready
kubectl describe pod llm-inference-0 | grep "Readiness"
# Fix: /ready endpoint should return 200 when app ready

# 4. Test with port-forward
kubectl port-forward svc/llm-inference 8000:8000
curl http://localhost:8000/health
```

---

## Issue 11: Network Policy Blocking

**Symptom**: Pod can't connect to Qdrant (vector DB)

**Root Cause**: Network policy denying egress

**Diagnosis**:
```bash
# From pod, try to connect
kubectl exec llm-inference-0 -- curl qdrant:6333
# Returns: Connection timed out (typical network policy issue)

# Check network policies
kubectl get networkpolicies
kubectl describe networkpolicy allow-api-to-qdrant
```

**Fix**:
```yaml
# Add egress rule to allow Qdrant traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-qdrant
spec:
  podSelector:
    matchLabels:
      app: llm-inference
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: qdrant
    ports:
    - protocol: TCP
      port: 6333
```

---

## Issue 12: Inference Latency Spike

**Symptom**: Normally 100ms, suddenly jumping to 500ms+

**Root Cause**: Model swap, memory fragmentation, or CPU contention

**Diagnosis**:
```bash
# Check GPU memory fragmentation
kubectl exec llm-inference-0 -- nvidia-smi

# Check CPU contention
kubectl top pod -A | grep -v llm
# Is something else using CPU?

# Check model changed
kubectl logs llm-inference-0 | tail | grep "loading"
```

**Fix**:
```bash
# 1. Restart pod to defrag GPU memory
kubectl delete pod llm-inference-0

# 2. Check if node CPU oversubscribed
kubectl top nodes
# If >80% CPU, reduce other workloads

# 3. Use node affinity to avoid mixed workloads
# Add: nodeSelector: {workload: ai}
```

---

## Issue 13: GPU Memory Leak

**Symptom**: Free GPU memory decreases every request, eventually hits OOM

**Root Cause**: Model or request handling not releasing memory

**Diagnosis**:
```bash
# Monitor GPU memory
watch -n 1 'kubectl exec llm-inference-0 -- nvidia-smi | grep -A 5 "Processes"'

# Check Python memory
kubectl exec llm-inference-0 -- python -c \
  "import torch; print(torch.cuda.memory_allocated() / 1e9)"
```

**Fix** (Python code):
```python
# Clear cache after each inference
import torch

@app.post("/generate")
async def generate(prompt: str):
    try:
        with torch.no_grad():  # Disable gradient tracking
            output = model.generate(prompt)

        # Clear cache
        torch.cuda.empty_cache()

        return {"text": output}
    finally:
        torch.cuda.empty_cache()  # Even on error
```

---

## Issue 14: PVC Not Mounting

**Symptom**: Pod hangs at init container, PVC not bound

**Root Cause**: StorageClass missing, quota exceeded, or other storage issue

**Diagnosis**:
```bash
kubectl get pvc llm-models
# Status: Pending (not bound)

kubectl describe pvc llm-models
# Events section shows why not binding
```

**Fix**:
```bash
# 1. Check StorageClass exists
kubectl get sc
# If not: Install EBS CSI or NFS provisioner

# 2. Check cloud storage quota
# AWS: Check EBS volume quota in account
# GCP: Check persistent disk quota

# 3. Manual PV creation
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolume
metadata:
  name: llm-models-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: manual
  hostPath:
    path: /mnt/data  # Local node path
EOF

# 4. Update PVC to use manual SC
kubectl patch pvc llm-models -p '{"spec":{"storageClassName":"manual"}}'
```

---

## 30+ More Issues (Quick Reference)

| # | Issue | Symptom | Quick Fix |
|----|-------|---------|-----------|
| 15 | Model file missing | "FileNotFoundError: /models/model.pt" | Check PVC mounted, init container completed |
| 16 | CUDA version mismatch | "Illegal instruction (core dumped)" | Rebuild image with matching CUDA version |
| 17 | GPU driver version mismatch | "CUDA driver older than runtime" | Update GPU operator to latest version |
| 18 | Batch size too large | "CUDA out of memory" | Reduce BATCH_SIZE env var, restart pod |
| 19 | No disk space | "Write error, no space" | Check node disk usage, clean docker cache |
| 20 | Certificate expired | "SSL: Certificate verify failed" | Renew TLS cert, kubectl patch secret |
| 21 | DNS resolution failure | "Name or service not known" | Check CoreDNS running, test with nslookup |
| 22 | StatefulSet pod identity issue | "Pod names random, not ordered" | Verify serviceName matches headless service |
| 23 | Pod not communicating | "Connection refused between pods" | Check network policy, verify nodeSelector |
| 24 | ConfigMap not mounted | "Env var undefined" | Verify ConfigMap exists, pod restarts after create |
| 25 | Secret not mounted | "HF token invalid" | Check secret exists, verify pod restart |
| 26 | Affinity pod anti-affinity too strict | "Can't scale past 2 pods" | Loosen weight in podAntiAffinity |
| 27 | Node selector wrong label | "Pod pending, node has label" | Check node label key/value exactly |
| 28 | Readiness probe too strict | "Pod never goes Ready" | Implement /ready endpoint or remove probe |
| 29 | Resource quota exceeded | "Pod rejected: exceeded quota" | Check namespace resourcequota, increase |
| 30 | Docker image too large | "Pod pulls image for 20 min" | Use multi-stage build, remove layer bloat |
| 31 | Model quantization broken | "Output values all zeros" | Verify quantized model is valid GGUF/GPTQ |
| 32 | Multi-GPU kernel unavailable | "GPU 1 & 2 not visible together" | Upgrade NVIDIA driver, check GPU fabric |
| 33 | Timeout on health check | "Liveness probe failed" | Increase probe timeout, check /health endpoint |
| 34 | Request timeout in proxy | "Request timed out (504)" | Increase Ingress timeout, check backend latency |

---

## Production Readiness Checklist

Before going live, verify:

- [ ] All pods reach `Ready` status
- [ ] GPU detected on all pods (`nvidia-smi` works)
- [ ] Model loads and inference works (`curl /generate`)
- [ ] HPA scaling works (load test, watch replicas)
- [ ] Network policies don't block needed traffic
- [ ] Logging aggregated (Loki/ELK)
- [ ] Metrics flowing to Prometheus
- [ ] Alerts configured
- [ ] Backup/restore tested
- [ ] Disaster recovery documented

---

## References

- [Kubernetes Debugging](https://kubernetes.io/docs/tasks/debug-application-cluster/)
- [NVIDIA Kubernetes Docs](https://docs.nvidia.com/datacenter/cloud-native/kubernetes/)
- [Troubleshooting Guide](https://kubernetes.io/docs/tasks/debug-application-cluster/determine-reason-pod-failure/)
