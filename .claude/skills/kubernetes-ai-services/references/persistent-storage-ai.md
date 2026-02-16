# Persistent Storage for AI Workloads

This reference covers PV/PVC patterns, model caching, cloud storage integration, and snapshots for AI services.

## PV/PVC Pattern (Model Caching)

### Create Storage Class

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ai-models
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
reclaimPolicy: Retain  # Keep volume when PVC deleted
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer  # Bind when pod scheduled
```

### Create PVC for Models

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: llm-models
spec:
  accessModes:
    - ReadOnlyMany  # Multiple pods can read (read-only)
  storageClassName: ai-models
  resources:
    requests:
      storage: 100Gi  # Size for model + cache
```

### Pod: Mount Model PVC

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference
spec:
  replicas: 3
  template:
    spec:
      initContainers:
      - name: download-model
        image: python:3.11
        command:
        - python
        - -c
        - |
          from transformers import AutoModel
          # Download model (uses cache)
          model = AutoModel.from_pretrained(
              "meta-llama/Llama-2-7b",
              cache_dir="/models"
          )
        volumeMounts:
        - name: models
          mountPath: /models
        env:
        - name: HF_HOME
          value: /models
      containers:
      - name: llm-api
        image: my-llm:latest
        volumeMounts:
        - name: models
          mountPath: /models
          readOnly: true  # Read-only after download
        env:
        - name: HF_HOME
          value: /models
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: llm-models
```

---

## Cloud Object Storage (S3/GCS)

### Mount S3 with s3fs

```dockerfile
FROM python:3.11
RUN apt-get update && apt-get install -y s3fs
RUN pip install awscli
WORKDIR /app
COPY app.py .
ENTRYPOINT ["python", "app.py"]
```

### Pod with S3 Mount

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: llm-s3-mount
spec:
  serviceAccountName: s3-accessor
  initContainers:
  - name: mount-s3
    image: python:3.11
    command:
    - bash
    - -c
    - |
      apt-get update && apt-get install -y s3fs
      mkdir -p /data
      s3fs my-models /data \
        -o endpoint=s3.amazonaws.com \
        -o url=https://s3.amazonaws.com \
        -o allow_other \
        -o uid=1000 \
        -o gid=1000 \
        -o use_cache=/tmp
    volumeMounts:
    - name: cache
      mountPath: /tmp
  containers:
  - name: inference
    image: my-llm:latest
    volumeMounts:
    - name: s3-mount
      mountPath: /models
  volumes:
  - name: cache
    emptyDir: {}
  - name: s3-mount
    emptyDir: {}
```

### Simpler: Use S3 Directly in Code

```python
import boto3
from transformers import AutoModel

s3_client = boto3.client('s3')

# Download model from S3
s3_client.download_file(
    'my-models',
    'llama-2-7b.tar.gz',
    '/tmp/model.tar.gz'
)

# Extract and load
import tarfile
tarfile.open('/tmp/model.tar.gz').extractall('/tmp')
model = AutoModel.from_pretrained('/tmp/llama-2-7b')
```

---

## Init Container Pattern (Lazy Load)

Download model at pod startup (avoids long image builds):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference
spec:
  replicas: 2
  template:
    spec:
      initContainers:
      - name: download-model
        image: huggingface/transformers-cli:latest
        args:
        - transformers-cli
        - download
        - meta-llama/Llama-2-7b
        volumeMounts:
        - name: model-cache
          mountPath: /root/.cache/huggingface
        env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: huggingface-token
              key: token
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
      containers:
      - name: api
        image: my-llm:latest
        volumeMounts:
        - name: model-cache
          mountPath: /root/.cache/huggingface
          readOnly: true
      volumes:
      - name: model-cache
        emptyDir:
          sizeLimit: 100Gi
```

---

## StatefulSet with Persistent Volume

For distributed training or stateful inference:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: distributed-training
spec:
  serviceName: training-service
  replicas: 4
  template:
    spec:
      containers:
      - name: trainer
        image: my-training:latest
        volumeMounts:
        - name: checkpoint
          mountPath: /checkpoints
  volumeClaimTemplates:
  - metadata:
      name: checkpoint
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ai-models
      resources:
        requests:
          storage: 100Gi
```

Result: Each pod gets `distributed-training-0`, `distributed-training-1`, etc., with separate 100Gi volumes.

---

## Volume Snapshots (Backup/Restore)

### Create Snapshot

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: llm-models-backup-v1
spec:
  volumeSnapshotClassName: ai-models-snapshot
  source:
    persistentVolumeClaimName: llm-models
```

### Restore from Snapshot

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: llm-models-restored
spec:
  dataSource:
    name: llm-models-backup-v1
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadOnlyMany
  storageClassName: ai-models
  resources:
    requests:
      storage: 100Gi
```

---

## Model Caching Strategy

### Shared Cache (NFS)

All pods share model cache:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs-model-cache
spec:
  accessModes:
    - ReadWriteMany  # Multiple pods read/write
  storageClassName: nfs
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
      containers:
      - name: api
        image: my-llm:latest
        volumeMounts:
        - name: shared-cache
          mountPath: /models
      volumes:
      - name: shared-cache
        persistentVolumeClaim:
          claimName: nfs-model-cache
```

**Benefit**: Download once, use in 5 pods. **Downside**: NFS can bottleneck under high load.

### Local Cache (Each Pod)

Each pod has its own cache:

```yaml
volumeMounts:
- name: local-cache
  mountPath: /models
volumes:
- name: local-cache
  emptyDir:
    sizeLimit: 100Gi
```

**Benefit**: No network contention. **Downside**: Download repeated per pod, slower startup.

---

## Cost Optimization

### Cleanup Old Models

```bash
# List PVCs with their sizes
kubectl get pvc -A

# Delete unused PVC
kubectl delete pvc old-model-cache
```

### Archive Models to S3

```bash
# Backup model PVC to S3
kubectl exec <pod> -- tar czf - /models | \
  aws s3 cp - s3://model-backups/llama-2-7b.tar.gz

# Restore from S3
kubectl exec <pod> -- bash -c \
  'aws s3 cp s3://model-backups/llama-2-7b.tar.gz - | tar xzf - -C /'
```

---

## Troubleshooting

### PVC Stuck in Pending

```bash
# Check why PVC not binding
kubectl describe pvc llm-models

# Check StorageClass
kubectl get sc

# Check available disk
kubectl describe nodes
```

### Model Files Disappear

```bash
# Check if init container completed
kubectl describe pod llm-inference-0 | grep -A 20 "Init Containers"

# View init container logs
kubectl logs llm-inference-0 -c download-model

# Check volume mount path
kubectl exec llm-inference-0 -- ls -lah /models
```

### Slow Model Loading

```bash
# Check disk I/O
kubectl top node
kubectl top pod -A --containers

# Use faster storage class
kubectl edit sc ai-models
# Change to SSD (gp3 with higher IOPS)
```

---

## References

- [Kubernetes PV Docs](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [EBS CSI Driver](https://github.com/kubernetes-sigs/aws-ebs-csi-driver)
- [NFS CSI](https://github.com/kubernetes-csi/csi-driver-nfs)
- [S3 CSI](https://github.com/aws-samples/amazon-s3-csi-driver)
