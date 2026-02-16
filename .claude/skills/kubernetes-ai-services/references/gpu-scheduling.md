# GPU Scheduling and Resource Management in Kubernetes

## NVIDIA GPU Operator Installation

### Prerequisites
- Kubernetes 1.16+
- NVIDIA GPU nodes (Tesla, Quadro, RTX, etc.)
- Helm 3+

### Install Steps

```bash
# Add NVIDIA Helm repo
helm repo add nvidia https://nvidia.github.io/k8s-device-plugin
helm repo update

# Install GPU operator
helm install gpu-operator nvidia/gpu-operator \
    --namespace gpu-operator-system \
    --create-namespace \
    --set driver.enabled=true \
    --set toolkit.enabled=true

# Verify installation
kubectl get daemonset -n gpu-operator-system
# Should show:
# nvidia-device-plugin-daemonset
# nvidia-driver-daemon
# nvidia-dcgm-exporter (monitoring)
```

### Verify GPU Access

```bash
# Check nodes have GPU
kubectl get nodes -L nvidia.com/gpu
# Output: all GPU nodes should have nvidia.com/gpu=true

# Test GPU from pod
kubectl run gpu-test --image=nvidia/cuda:12.0-base --rm -it -- nvidia-smi
# Should show GPU info

# Permanent test pod
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: gpu-test
spec:
  containers:
  - name: cuda-test
    image: nvidia/cuda:12.0-runtime
    command: ["nvidia-smi"]
  nodeSelector:
    nvidia.com/gpu: "true"
EOF

kubectl logs gpu-test
```

---

## GPU Request/Limit Patterns

### Pattern 1: Single GPU Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: single-gpu
spec:
  containers:
  - name: app
    image: my-llm:latest
    resources:
      limits:
        nvidia.com/gpu: 1  # Require exactly 1 GPU
      requests:
        nvidia.com/gpu: 1  # Reserve 1 GPU
  nodeSelector:
    nvidia.com/gpu: "true"  # Only schedule on GPU nodes
```

### Pattern 2: Multi-GPU Pod

```yaml
resources:
  limits:
    nvidia.com/gpu: 4  # Use all 4 GPUs
  requests:
    nvidia.com/gpu: 4

# Environment variables set automatically:
# NVIDIA_VISIBLE_DEVICES=0,1,2,3
# CUDA_VISIBLE_DEVICES=0,1,2,3
```

### Pattern 3: GPU Fraction (MIG or Time-Slicing)

```yaml
# For NVIDIA A100 MIG mode or GPU time-slicing
resources:
  limits:
    nvidia.com/gpu: "0.25"  # 25% of GPU time
  requests:
    nvidia.com/gpu: "0.25"
```

---

## Node Affinity and GPU Scheduling

### GPU Node Pool Isolation

```bash
# Label GPU nodes
kubectl label nodes gpu-node-1 gpu-type=tesla-t4
kubectl label nodes gpu-node-2 gpu-type=tesla-a100

# Taint GPU nodes (prevent non-GPU workloads)
kubectl taint nodes gpu-node-1 gpu=true:NoSchedule
```

### Pod Configuration with Affinity

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference-t4
spec:
  template:
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: gpu-type
                operator: In
                values:
                - tesla-t4  # Only T4 GPUs
      tolerations:
      - key: gpu
        operator: Equal
        value: "true"
        effect: NoSchedule
      containers:
      - name: llm-api
        image: my-llm:latest
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
```

### Pod-to-Pod Affinity

```yaml
# Spread inference pods across different GPU nodes
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - llm-inference
        topologyKey: kubernetes.io/hostname  # Spread across nodes
```

---

## GPU Monitoring and Metrics

### NVIDIA DCGM Exporter

```bash
# Already installed with GPU operator
# Exposes metrics on port 9400

# Port-forward to Prometheus
kubectl port-forward -n gpu-operator-system \
    $(kubectl get pod -n gpu-operator-system -l app=dcgm-exporter -o jsonpath='{.items[0].metadata.name}') \
    9400:9400

# View metrics
curl localhost:9400/metrics | grep -i gpu
```

### Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: gpu-metrics
spec:
  selector:
    matchLabels:
      app: dcgm-exporter
  endpoints:
  - port: metrics
    interval: 30s
```

---

## Cloud-Specific GPU Setup

### AWS EKS with GPU Nodes

```bash
# Create node group with GPU
eksctl create nodegroup \
    --cluster my-cluster \
    --name gpu-nodes \
    --instance-types g4dn.xlarge \
    --nodes 3 \
    --node-type on-demand

# Verify GPU nodes
kubectl get nodes -L node.kubernetes.io/instance-type
```

### GCP GKE with GPU Nodes

```bash
# Create node pool with GPU
gcloud container node-pools create gpu-pool \
    --cluster my-cluster \
    --machine-type n1-standard-4 \
    --accelerator type=nvidia-tesla-t4,count=1 \
    --num-nodes 3

# Install GPU drivers
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
```

### Azure AKS with GPU Nodes

```bash
# Create node pool with GPU
az aks nodepool add \
    --resource-group myResourceGroup \
    --cluster-name myAKSCluster \
    --name gpunodepool \
    --node-vm-size Standard_NC6s_v3 \
    --node-count 3

# Verify
kubectl get nodes -L accelerator=nvidia-tesla-v100
```

---

## Troubleshooting GPU Issues

### GPU Not Visible in Pod

**Diagnosis**:
```bash
# Check operator status
kubectl get daemonset -n gpu-operator-system

# Check node labels
kubectl get nodes --show-labels | grep gpu

# Check pod request
kubectl describe pod <pod> | grep -A 3 "Limits"
```

**Fixes**:
```bash
# Reinstall GPU operator
helm uninstall gpu-operator -n gpu-operator-system
helm install gpu-operator nvidia/gpu-operator ...

# Manually label nodes
kubectl label nodes <node> nvidia.com/gpu=true --overwrite

# Verify pod scheduling
kubectl get events -n <namespace>
```

### GPU Memory Issues

```bash
# Check GPU memory per pod
nvidia-smi -q -d MEMORY | grep -A 5 "Memory"

# Monitor pod GPU usage
kubectl exec <pod> -- nvidia-smi --query-gpu=memory.used,memory.total --format=csv

# Set memory limits (application-level)
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512
```

---

## Reference

- **NVIDIA GPU Operator**: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/
- **Kubernetes GPU Scheduling**: https://kubernetes.io/docs/tasks/manage-gpus/
- **NVIDIA DCGM**: https://developer.nvidia.com/dcgm
