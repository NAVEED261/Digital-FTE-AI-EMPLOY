# Troubleshooting AI/LLM Docker Services

## 25+ Battle-Tested Gotchas

### 1. GPU Not Detected in Container

**Symptom**: `torch.cuda.is_available() = False`, `CUDA device not found`

**Root Cause**: NVIDIA Container Toolkit not installed or runtime not configured

**Diagnosis**:
```bash
# Check 1: Toolkit installed
which nvidia-ctk  # Should exist

# Check 2: Docker daemon knows about nvidia runtime
docker info | grep nvidia  # Should show nvidia runtime

# Check 3: Test with cuda image
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi
# If this fails, GPU not accessible
```

**Fix**:
```bash
# Install toolkit
apt-get install nvidia-container-toolkit

# Configure Docker daemon
nvidia-ctk runtime configure --runtime=docker

# Restart Docker
systemctl restart docker

# Verify
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi
```

---

### 2. CUDA Version Mismatch

**Symptom**: `RuntimeError: CUDA version mismatch`, `cuBLAS version mismatch`

**Root Cause**: Base image CUDA version ≠ PyTorch CUDA version

**Diagnosis**:
```bash
# Check driver/CUDA version
nvidia-smi | grep "CUDA Version"
# e.g., CUDA Version: 12.1

# Check PyTorch CUDA version in container
docker run --gpus all my-app python -c "import torch; print(torch.version.cuda)"
# e.g., 12.4 or 11.8

# These don't match!
```

**Fix**:
```dockerfile
# Match CUDA versions
# If driver supports CUDA 12.1, use:
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

# Verify
docker run --gpus all my-app python -c "import torch; print(f'CUDA: {torch.version.cuda}')"
# Now matches nvidia-smi output
```

**CUDA Compatibility Reference**:
- nvidia/cuda:12.0 → pytorch:2.2.0-cuda12.1
- nvidia/cuda:12.1 → pytorch:2.2.0-cuda12.1
- nvidia/cuda:11.8 → pytorch:2.2.0-cuda11.8
- TensorFlow: tensorflow:latest-gpu

---

### 3. Out of Memory (OOM) Errors

**Symptom**: Container killed suddenly, `Killed` in logs, no error message

**Root Cause**: GPU or system memory exhausted

**Diagnosis**:
```bash
# Check if killed (exit code 137 = SIGKILL)
docker ps -a | grep my-app  # Shows "Exited (137)"

# Check Docker logs
docker logs my-app | tail -20  # Usually says "Killed"

# Monitor memory during run
docker stats my-app  # Watch MEM USAGE and GPU VRAM

# Check system memory
free -h
nvidia-smi  # Check GPU memory usage
```

**Fixes**:
```dockerfile
# Fix 1: Set memory allocation config
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512

# Fix 2: Use float16 instead of float32 (50% memory)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16  # Instead of default float32
)

# Fix 3: Set resource limits
docker run --gpus all -m 16g my-app python app.py

# Fix 4: Use quantization (GGUF, GPTQ, AWQ)
# See model-optimization.md for details
```

**docker-compose.yml:**
```yaml
services:
  llm-api:
    deploy:
      resources:
        limits:
          memory: 32g  # Prevent unbounded memory growth
    environment:
      - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512
      - MALLOC_TRIM_THRESHOLD_=128000
```

---

### 4. Health Check Timeout (Service Keeps Restarting)

**Symptom**: Container restarts every 30s, logs show "unhealthy"

**Root Cause**: Model loading takes longer than startup probe timeout

**Diagnosis**:
```bash
# Check health check status
docker inspect my-app | grep -A 10 "Health"

# View logs during startup
docker logs -f my-app

# Measure model loading time
docker run --gpus all my-app python -c "
import time
start = time.time()
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained('model-name')
print(f'Loaded in {time.time() - start:.1f}s')
"
# e.g., "Loaded in 45.2s"
```

**Fix**:
```dockerfile
# Increase startup probe timeout
HEALTHCHECK --interval=10s --timeout=5s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
    # start-period should be > model loading time

# Or in docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 120s  # 2 minutes for large models
```

---

### 5. Shared Memory Exhaustion (DataLoader Deadlock)

**Symptom**: DataLoader deadlock, workers hang, no error message

**Root Cause**: PyTorch DataLoader needs /dev/shm space for IPC

**Diagnosis**:
```bash
# Check shared memory usage
df /dev/shm  # Shows usage

# Run with workers
docker run my-app python -c "
from torch.utils.data import DataLoader
# If this hangs with workers > 0, it's shm exhaustion
"
```

**Fix**:
```bash
# Increase shared memory
docker run --shm-size=2gb my-app python app.py

# Or in docker-compose.yml
services:
  llm-api:
    shm_size: 2gb
```

---

### 6. Model Re-downloaded on Every Build

**Symptom**: Build takes 5-10 minutes every time, 10GB+ layers re-created

**Root Cause**: Model in wrong layer (before code layer) or no caching

**Fix**: See model-optimization.md for layer ordering

---

### 7. GPU Memory Leak

**Symptom**: Gradual memory increase over time, eventually OOM

**Root Cause**: Unclosed CUDA contexts or cached tensors

**Diagnosis**:
```bash
# Monitor GPU memory in loop
while true; do nvidia-smi | grep "MiB"; sleep 5; done
# Should be constant, not increasing
```

**Fix**:
```python
# Clear cache after batches
import torch
import gc

for batch in batches:
    output = model(batch)
    torch.cuda.empty_cache()  # Clear GPU memory
    gc.collect()  # Clear Python garbage

# Or use context manager
with torch.no_grad():
    output = model(batch)
torch.cuda.empty_cache()
```

---

### 8. Quantization Errors

**Symptom**: `ValueError: quantization not supported`, `RuntimeError: quantization failed`

**Root Cause**: Missing required library or model doesn't support quantization

**Diagnosis**:
```bash
# Check if llama-cpp-python installed
docker run my-app python -c "import llama_cpp"

# Check model format
# GGUF models need llama-cpp-python
# GPTQ models need auto-gptq
# AWQ models need autoawq
```

**Fix**:
```dockerfile
# For GGUF (llama.cpp)
RUN pip install llama-cpp-python

# For GPTQ
RUN pip install auto-gptq

# For AWQ
RUN pip install autoawq

# Use quantized model
# GGUF: https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF
# GPTQ: https://huggingface.co/TheBloke/Llama-2-7b-Chat-GPTQ
# AWQ: https://huggingface.co/TheBloke/Llama-2-7b-Chat-AWQ
```

---

### 9. Inference Timeout (504 Gateway Timeout)

**Symptom**: Requests timeout after 30-60 seconds, 504 error

**Root Cause**: Model inference takes longer than server timeout

**Fix**:
```dockerfile
# Increase Gunicorn timeout
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--timeout", "300", "app:app"]  # 5 minutes

# Or uvicorn directly
CMD ["uvicorn", "app:app", "--timeout-keep-alive", "120"]
```

**docker-compose.yml:**
```yaml
services:
  llm-api:
    environment:
      - GUNICORN_TIMEOUT=300
```

---

### 10. Multi-GPU Not Detected

**Symptom**: Only GPU 0 available, `cuda:1` not found

**Root Cause**: `NVIDIA_VISIBLE_DEVICES` not set correctly

**Fix**:
```dockerfile
ENV NVIDIA_VISIBLE_DEVICES=all  # Show all GPUs
```

**docker-compose.yml:**
```yaml
services:
  llm-api:
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all  # Allocate all GPUs
              capabilities: [gpu]
```

---

### 11. BuildKit Cache Not Working

**Symptom**: Docker builds entire image every time, no layer caching

**Root Cause**: Missing `--build-arg BUILDKIT_INLINE_CACHE=1`

**Diagnosis**:
```bash
# Check if BuildKit enabled
docker buildx version  # Should exist

# Check build output
docker build -t my-app . 2>&1 | grep "CACHED"
# If no "CACHED" messages, cache not working
```

**Fix**:
```bash
# Build with cache enabled
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t my-app:latest .

# Or enable in daemon.json
# "features": { "buildkit": true }

# Or use buildx
docker buildx build --build-arg BUILDKIT_INLINE_CACHE=1 -t my-app:latest .
```

---

### 12. Model Weights Corrupted

**Symptom**: `Checkpoint format not supported`, `unexpected key in state_dict`

**Root Cause**: Incomplete download in earlier build layer, corrupted file

**Diagnosis**:
```bash
# Check file size
ls -lh /models/model.bin  # Seems too small?

# Check checksum
sha256sum /models/model.bin > model.sha256
```

**Fix**:
```bash
# Clear Docker build cache
docker builder prune -a

# Force re-download
docker build --no-cache -t my-app:latest .

# Verify download completeness
docker run my-app python -c "
import torch
model = torch.load('/models/model.bin')
print('Model loaded successfully')
"
```

---

### 13. Permission Denied in Volume

**Symptom**: `Permission denied: /models/model.bin`, `PermissionError`

**Root Cause**: File owned by root, container runs as different user

**Fix**:
```dockerfile
# Use --chown flag
COPY --chown=appuser:appuser models/ /app/models/

# Or run as root (less secure)
USER root

# Or change permissions
RUN chmod -R 755 /app/models
```

---

### 14. Network Timeout Downloading Model

**Symptom**: `Connection timeout`, `ReadTimeoutError` during model download

**Root Cause**: No internet in build context, network issues, HuggingFace Hub timeout

**Fix**:
```dockerfile
# Pre-download model before Docker build
# Local machine:
huggingface-cli download meta-llama/Llama-2-7b-chat-hf \
    --local-dir ./model-cache

# Then in Dockerfile
COPY model-cache /app/models
ENV TRANSFORMERS_OFFLINE=1  # Use cached, no downloads
```

---

### 15. pip Conflicts with torch

**Symptom**: `ERROR: pip's dependency resolver does not currently take into account`

**Root Cause**: pip can't resolve PyTorch + transformers + other deps

**Fix**: Use UV instead of pip
```dockerfile
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.cargo/bin/uv pip install -e . --python /opt/venv/bin/python
# UV resolves 10x faster and cleaner
```

---

### 16. Startup Probe Failing Immediately

**Symptom**: 503 Service Unavailable on first request, before model loads

**Root Cause**: Readiness probe checks before startup probe completes

**Fix**:
```dockerfile
# Use startup probe instead of readiness for model loading
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

**Or in Kubernetes**:
```yaml
startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 0  # Check immediately
  periodSeconds: 5
  failureThreshold: 60    # Allow 300 seconds (60 * 5s)
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 10
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 60
  periodSeconds: 30
```

---

### 17. GPU Sharing Between Containers

**Symptom**: Multiple containers use same GPU, poor performance

**Root Cause**: No device isolation configured

**Fix**:
```yaml
services:
  llm-api-1:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']  # Specific GPU 0
              capabilities: [gpu]

  llm-api-2:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['1']  # Different GPU 1
              capabilities: [gpu]
```

---

### 18. High Memory on Cold Start

**Symptom**: Startup spike to 16GB+ immediately

**Root Cause**: Loading entire model to GPU at once

**Fix**:
```python
# Use device_map for progressive loading
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",  # Spreads model across devices
    torch_dtype=torch.float16
)
```

---

### 19. GGUF Inference Slow

**Symptom**: 2-3 tokens/sec instead of 10-20

**Root Cause**: GGUF using wrong quantization or backend

**Fix**:
```python
# Verify quantization method
from llama_cpp import Llama
model = Llama("model.gguf", n_gpu_layers=-1)  # Use GPU
# Check loaded message: "ngl: 35" means GPU layers loaded

# Use higher quantization
# Q5_K_M faster than Q4_K_M
# Q4_K_M most compact
```

---

### 20. Different Build Results Locally vs CI

**Symptom**: Builds fine locally, fails in GitHub Actions

**Root Cause**: Architecture mismatch (arm64 vs amd64), different Python versions

**Fix**:
```bash
# Always specify platform
docker build --platform=linux/amd64 -t my-app:latest .

# In GitHub Actions
- name: Build image
  run: |
    docker build --platform=linux/amd64 \
      --build-arg BUILDKIT_INLINE_CACHE=1 \
      -t my-app:latest .
```

---

### 21. Model Cache Invalidated by env vars

**Symptom**: Model re-downloaded even with cache

**Root Cause**: Environment variables change between builds

**Fix**:
```dockerfile
# Don't embed paths in RUN commands if they change
# Instead, use ENV only for runtime

# ❌ Bad
RUN export HF_HOME=/custom/path && \
    python download_model.py

# ✅ Good
ENV HF_HOME=/cache/huggingface
RUN mkdir -p $HF_HOME

# Then use ENV for runtime
ENTRYPOINT ["python", "app/main.py"]
```

---

### 22. Inference Crashes After 1000s Requests

**Symptom**: Service fine initially, crashes after hours/days

**Root Cause**: Memory leak or unclosed file handles

**Fix**:
```python
# Use context managers
with torch.no_grad():
    output = model(batch)

# Cleanup after batches
torch.cuda.empty_cache()
gc.collect()

# Monitor in production
import psutil
memory_percent = psutil.virtual_memory().percent
if memory_percent > 90:
    gc.collect()  # Aggressive cleanup
    torch.cuda.empty_cache()
```

---

### 23. Model Download Interrupted

**Symptom**: Model downloads as separate files, import fails

**Root Cause**: Network interrupted during multi-file download

**Fix**:
```bash
# Use resumable download
huggingface-cli download meta-llama/Llama-2-70b-chat-hf \
    --resume-download \
    --local-dir ./models

# Or in Docker with retries
RUN for i in 1 2 3; do \
  huggingface-cli download model-name && break || \
  (sleep 5 && continue); \
done
```

---

### 24. Triton Server Model Not Found

**Symptom**: `TRITONSERVER_ERROR_UNAVAILABLE_MODEL`

**Root Cause**: Model config incorrect or path wrong

**Fix**:
```bash
# Check model directory
docker exec triton ls -la /models/model_name/

# Should contain:
# - config.pbtxt (model configuration)
# - 1/ (version directory with actual model)

# Verify config syntax
docker run --rm -v $(pwd)/models:/models \
  nvcr.io/nvidia/tritonserver:24.02-py3 \
  tritonserver --model-repository=/models --model-control-mode=explicit
```

---

### 25. CUDA Out of Memory During Fine-tuning

**Symptom**: Fine-tuning crashes with OOM, inference works

**Root Cause**: Training requires gradients, double memory usage

**Fix**:
```python
# Gradient checkpointing
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    gradient_checkpointing=True,  # Trade speed for memory
    torch_dtype=torch.float16
)

# 8-bit optimizer
from bitsandbytes.optim import AdamW8bit
optimizer = AdamW8bit(model.parameters())

# Lower batch size
batch_size = 1  # Instead of 8

# Use LoRA (parameter-efficient fine-tuning)
from peft import get_peft_model, LoraConfig
config = LoraConfig(r=8, lora_alpha=16)
model = get_peft_model(model, config)
```

---

## Debugging Commands Quick Reference

```bash
# Check Docker/NVIDIA setup
docker info | grep nvidia
nvidia-smi
nvidia-ctk --version

# View image layers
docker history my-app:latest

# Check OOM in logs
docker logs my-app 2>&1 | grep -i "killed\|oom\|memory"

# Profile memory usage
docker run --cap-add=SYS_PTRACE my-app python -m memory_profiler app.py

# Check health check status
docker inspect my-app | grep -A 15 "Health"

# Monitor resource usage
docker stats --no-stream my-app

# Build without cache
docker build --no-cache -t my-app:latest .

# Build with verbose output
docker build -t my-app:latest . 2>&1 | head -50
```

---

## Quick Checklist Before Production

- [ ] GPU is detected: `docker run --gpus all my-app nvidia-smi`
- [ ] CUDA version matches: `torch.version.cuda` == driver cuda version
- [ ] Health checks pass: Container stays healthy for 5+ minutes
- [ ] Memory stable: `docker stats` shows constant memory usage
- [ ] Image size reasonable: `docker images` shows <10GB (after optimization)
- [ ] Non-root user: `docker run my-app id` shows non-zero UID
- [ ] Secrets not in image: `docker history my-app` has no tokens/keys
- [ ] Model loads in <60s: Startup probe times model loading
- [ ] Inference completes: Run a simple query, verify response
- [ ] No OOM: `docker logs` has no "Killed" messages
