# Production Security for AI Services in Docker

## Non-Root User with GPU Access

**Pattern: Run as non-root while accessing GPU**

```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Create non-root user
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser && \
    mkdir -p /app && chown -R appuser:appuser /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn torch

COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser models/ /app/models/

# Run as non-root user
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Verification:**
```bash
# Container runs as user 1000
docker run my-app:latest id
# uid=1000(appuser) gid=1000(appuser)

# GPU still accessible (container runtime handles capabilities)
docker run --gpus all my-app:latest nvidia-smi
# Should work fine even with non-root user
```

**Why this works**: Docker container runtime automatically grants necessary GPU capabilities regardless of user ID

---

## Secrets Management

### Pattern 1: BuildKit Secrets (Recommended)

```dockerfile
# syntax=docker/dockerfile:1.4

FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

WORKDIR /app

# Mount secrets at build time
RUN --mount=type=secret,id=hf_token \
    --mount=type=secret,id=pip_token \
    bash -c '
    HF_TOKEN=$(cat /run/secrets/hf_token)
    PIP_TOKEN=$(cat /run/secrets/pip_token)

    pip config set global.index-url "https://token:${PIP_TOKEN}@private.pypi.org/simple"

    python -c "
    import os
    os.environ[\"HF_TOKEN\"] = \"${HF_TOKEN}\"
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(
        \"meta-llama/Llama-2-70b-chat-hf\"
    )
    "
    '

FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
COPY --from=builder /root/.cache /root/.cache
WORKDIR /app
COPY app/ /app/
CMD ["python", "app/main.py"]
```

**Build with secrets:**
```bash
docker build \
    --secret hf_token=$HF_TOKEN_FILE \
    --secret pip_token=$PIP_TOKEN_FILE \
    -t my-app:latest .
```

**Benefits**:
- Secrets not visible in image layers
- Secrets not in git history
- Secrets only mounted during build, not in final image

### Pattern 2: Environment Variables from Docker Secrets (Runtime)

```yaml
# docker-compose.yml
version: '3.8'

services:
  llm-api:
    image: my-app:latest
    environment:
      - HF_HOME=/cache/huggingface
    secrets:
      - hf_token
      - api_key
    volumes:
      - huggingface_cache:/cache/huggingface:ro

secrets:
  hf_token:
    file: ./secrets/hf_token.txt
  api_key:
    file: ./secrets/api_key.txt
```

**In application code:**
```python
import os
with open('/run/secrets/hf_token', 'r') as f:
    hf_token = f.read().strip()
```

### Pattern 3: Kubernetes Secrets

```yaml
# kubernetes secret
apiVersion: v1
kind: Secret
metadata:
  name: llm-credentials
type: Opaque
data:
  HF_TOKEN: <base64-encoded-token>
  API_KEY: <base64-encoded-key>
```

**In Pod:**
```yaml
env:
  - name: HF_TOKEN
    valueFrom:
      secretKeyRef:
        name: llm-credentials
        key: HF_TOKEN
```

---

## Image Scanning and Vulnerability Detection

### Trivy Image Scanning

```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image
trivy image my-app:latest

# High severity vulnerabilities only
trivy image --severity HIGH,CRITICAL my-app:latest

# Generate SBOM (Software Bill of Materials)
trivy image --format cyclonedx --output sbom.json my-app:latest

# Exit with error if critical found
trivy image --exit-code 1 --severity CRITICAL my-app:latest
```

**In CI/CD:**
```yaml
# .github/workflows/build.yml
- name: Scan image
  run: |
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy image my-app:latest
```

### Snyk Container Scanning

```bash
# Install Snyk
npm install -g snyk

# Scan image
snyk container test my-app:latest

# Test Dockerfile
snyk test --file=Dockerfile
```

---

## Supply Chain Security (SBOM)

### Generate SBOM with cyclonedx-bom

```bash
# Install
pip install cyclonedx-bom

# Generate from pip freeze
pip freeze > requirements.txt
cyclonedx-bom -i requirements.txt -o sbom.xml

# Generate from poetry
cyclonedx-bom pyproject.toml -o sbom.xml

# Generate in JSON format
cyclonedx-bom -i requirements.txt -o sbom.json -f json
```

### Include SBOM in Docker Image

```dockerfile
FROM python:3.11-slim

RUN pip install cyclonedx-bom
COPY pyproject.toml requirements.txt ./

RUN pip freeze > /tmp/requirements.txt && \
    cyclonedx-bom -i /tmp/requirements.txt -o /app/sbom.xml

# Metadata label
LABEL org.opencontainers.image.sbom=/app/sbom.xml

COPY app/ /app/
CMD ["python", "app/main.py"]
```

### Verify SBOM in Image

```bash
# Extract SBOM from image
docker inspect my-app:latest | grep sbom

# Or extract directly
docker run --rm my-app:latest cat /app/sbom.xml
```

---

## Signing and Verification

### Docker Content Trust (DCT)

```bash
# Enable DCT
export DOCKER_CONTENT_TRUST=1

# Generate signing keys
docker trust key generate my-key

# Sign and push image
docker push my-app:latest
# Creates signature in Notary

# Verify signed image
docker pull my-app:latest
# Verifies signature before running
```

### Cosign (CNCF Alternative)

```bash
# Install
wget https://github.com/sigstore/cosign/releases/latest/download/cosign-linux
chmod +x cosign

# Sign image
cosign sign --key cosign.key my-app:latest

# Verify signature
cosign verify --key cosign.pub my-app:latest

# In Kubernetes policy
kubectl apply -f - <<EOF
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredimagesigned
spec:
  validation:
    openAPIV3Schema:
      type: object
EOF
```

---

## Resource Limits and OOM Prevention

### Docker Compose Resource Limits

```yaml
services:
  llm-api:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 32g
          # GPU limit (count, not VRAM)
        reservations:
          cpus: '4'
          memory: 24g
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512
      - MALLOC_TRIM_THRESHOLD_=128000
```

### Memory Monitoring

```bash
# Real-time memory usage
docker stats my-app

# Check OOM status
docker inspect my-app | grep -i oom

# View container logs for OOM events
docker logs my-app 2>&1 | grep -i "killed\|oom"
```

---

## Network Security

### Dockerfile

```dockerfile
# Non-root user
USER appuser

# No network access (if not needed)
# This requires SecurityContext in K8s:
# securityContext:
#   capabilities:
#     drop:
#       - NET_RAW

# Limited network (only HTTP/HTTPS)
# Use network policy in K8s instead
```

### docker-compose.yml

```yaml
services:
  llm-api:
    networks:
      - internal  # Isolated network
    expose:
      - 8000      # Don't expose to host by default
    ports:
      - "127.0.0.1:8000:8000"  # Bind to localhost only

  # Optional: nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "8000:80"
    networks:
      - internal
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro

networks:
  internal:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.enable_ip_masquerade: 'true'
```

---

## Kubernetes Pod Security

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
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
    seLinuxOptions:
      level: "s0:c123,c456"
  supplementalGroups:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: false
```

### Deployment with Security Context

```yaml
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
      serviceAccountName: llm-inference
      securityContext:
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: llm-api
        image: my-app:latest
        imagePullPolicy: Always
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "32Gi"
            cpu: "8"
          requests:
            nvidia.com/gpu: 1
            memory: "24Gi"
            cpu: "4"
        volumeMounts:
          - name: tmp
            mountPath: /tmp
          - name: cache
            mountPath: /cache
      volumes:
        - name: tmp
          emptyDir: {}
        - name: cache
          emptyDir: {}
```

---

## Audit Logging

### Application-level logging

```python
import logging
import json

# JSON logging for ELK/Splunk
class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'user_id': getattr(record, 'user_id', 'unknown'),
            'model': getattr(record, 'model', 'unknown'),
            'request_id': getattr(record, 'request_id', 'unknown'),
        })

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Usage
logger.info('Model inference completed', extra={
    'user_id': user_id,
    'model': model_name,
    'request_id': request_id,
    'tokens': token_count,
})
```

### Kubernetes audit logging

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["pods", "services"]
    omitStages:
      - RequestReceived
  - level: Metadata
    resources:
      - group: ""
        resources: ["pods/log", "pods/status"]
```

---

## Reference

- **Trivy**: https://aquasecurity.github.io/trivy/
- **Docker Content Trust**: https://docs.docker.com/engine/security/trust/
- **Cosign**: https://docs.sigstore.dev/cosign/overview/
- **SBOM Standard**: https://cyclonedx.org/
- **Pod Security Standards**: https://kubernetes.io/docs/concepts/security/pod-security-standards/
