---
name: docker-ai-production
description: |
  Expert-level Docker for AI/LLM services with GPU support, model optimization, and production hardening.
  Use when containerizing AI agents, LLM inference services, model serving platforms, or GPU workloads.
  Includes UV integration, multi-stage builds, model layer caching, and NVIDIA runtime patterns.
version: 1.0.1
tags: [docker, ai, llm, gpu, containerization, production]
---

# Docker for AI/LLM Services: Production-Ready Patterns

## 🚀 Before You Start

**This section helps you prepare for AI containerization. Answer these questions first.**

### Prerequisites Checklist

Before proceeding, verify you have:

- [ ] **Docker** 20.10+ installed: `docker --version`
- [ ] **Docker daemon running**: `docker ps` (no errors)
- [ ] **Basic Docker knowledge**: Understand FROM, RUN, COPY, ENTRYPOINT
- [ ] **GPU available** (if needed): `nvidia-smi` works or planning GPU setup
- [ ] **HuggingFace account** (optional): Required for gated models (Llama 2, etc.)
- [ ] **Model access verified**: Can download/access your target model
- [ ] **Disk space**: At least 50GB free for large models (Llama 70B = 130GB)

**Not ready?** See:
- [references/gpu-runtime.md](references/gpu-runtime.md) for GPU setup
- [references/uv-integration.md](references/uv-integration.md) for dependency management

---

### Context Gathering: What's Your Situation?

**Step 1: Identify Your Use Case**

| Use Case | Real-Time? | Scale | Storage | Pattern |
|----------|-----------|-------|---------|---------|
| Chat API (like ChatGPT) | ✓ Yes | 100s concurrent | 7-20GB | Pattern 1 (FastAPI) |
| Batch Embeddings | No | 1000s items | 2-4GB | Pattern 3 (Batch) |
| Model Fine-tuning | No | Single/multi-GPU | 50-100GB | Pattern 2 (Training) |
| Inference Service | ✓ Yes | 10-100 concurrent | 50GB+ | Pattern 4+ |

**Your use case**: ______________________

**Step 2: GPU Resources**

- [ ] **No GPU** → Use CPU inference (slow, acceptable for batch/training)
- [ ] **1 GPU** (T4/RTX 3090) → Use vLLM or FastAPI (Pattern 1)
- [ ] **2-4 GPUs** (A6000/L40S) → Use vLLM with tensor parallelism
- [ ] **8+ GPUs** (A100) → Use vLLM distributed or Triton (Pattern 4)

**Your GPU count**: ______________________

**Step 3: Model Size**

| Model | Size | GPUs Needed | Recommended |
|-------|------|-------------|-------------|
| Llama 2 7B | 13GB | 1 T4 | ✓ FastAPI + GGUF |
| Llama 2 13B | 24GB | 1 A6000 | ✓ vLLM FP16 |
| Llama 2 70B | 130GB | 4-8 A100 | ✓ vLLM distributed |
| Mistral 7B | 13GB | 1 T4 | ✓ FastAPI + GGUF |

**Your model**: ______________________ **Size**: ______________________

---

### Quick Diagnosis: Which Pattern Do You Need?

**Answer these 3 questions to find your pattern:**

```
Question 1: What are you doing?
├─ Real-time inference (chat, API) → Question 2
├─ Batch processing (embeddings, classification) → PATTERN 3 (Batch Inference)
└─ Training / Fine-tuning → PATTERN 2 (Training Job)

Question 2: How many users/requests?
├─ < 10 concurrent → PATTERN 1 (FastAPI)
├─ 10-100 concurrent → PATTERN 1 (FastAPI + vLLM)
├─ 100+ concurrent → PATTERN 4 (Triton/TGI)
└─ Multi-region / complex → PATTERN 5 (Ray Serve)

Question 3: Do you have multiple GPUs?
├─ No → Use selected pattern as-is
└─ Yes → Add tensor parallelism (see references/model-optimization.md)
```

**Your pattern selection**: PATTERN _____

**Next step**: Scroll to your pattern below.

---

## ✅ Success Metrics: How Do You Know It Works?

After building your container, verify these metrics:

| Metric | Command | Expected |
|--------|---------|----------|
| **GPU accessible** | `docker run --gpus all my-app nvidia-smi` | NVIDIA-SMI output visible |
| **Model loads in time** | Check logs for model loading time | < 5 minutes startup |
| **Inference works** | Send test query to API | Response in < 30 sec |
| **Memory stable** | `docker stats my-app` (2 min) | Memory constant ± 5% |
| **Health check passes** | `curl http://localhost:8000/health` | `{"status": "ok"}` |
| **Image size reasonable** | `docker images my-app` | < 10GB (after optimization) |

---

## Quick Start

```bash
# Install NVIDIA runtime
apt install nvidia-container-toolkit && systemctl restart docker

# Test GPU access
docker run --gpus all nvidia/cuda:12.0 nvidia-smi

# Build with model caching
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t my-llm:latest .

# Run with GPU + shared memory
docker run --gpus all -it --shm-size=2gb my-llm:latest
```

See [references/gpu-runtime.md] for troubleshooting | [references/model-optimization.md] for layer patterns

---

## AI Service Dockerfile Patterns

### Pattern 1: FastAPI + LLM Inference (vLLM/TGI)

```dockerfile
# Stage 1: Build dependencies with UV
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy pyproject.toml and lock file
COPY pyproject.toml uv.lock* ./
RUN uv venv /app/.venv && \
    uv pip install -e . --python /app/.venv/bin/python

# Stage 2: Runtime (small)
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcublas-12-0 libnccl2 libcudnn8 && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code (AFTER venv, before model)
COPY app/ /app/app/
COPY config/ /app/config/

# Copy model artifact (heavy, on its own layer for caching)
COPY models/llama-2-7b-chat.gguf /app/models/

# Setup entrypoint
RUN /app/.venv/bin/pip install uvicorn gunicorn
ENV PATH="/app/.venv/bin:$PATH"

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--timeout", "120", "app.main:app"]
```

**Why this pattern:**
- **Stage 1 isolation**: Compiler toolchain not in final image (50% size reduction)
- **UV for speed**: 10-30x faster than pip for dependency resolution
- **Model on final layer**: Changes to code don't invalidate model cache
- **Health checks**: Start probe gives 60s for model loading
- **Gunicorn + UV**: Better multiprocess handling for high concurrency

### Pattern 2: Training Job (PyTorch with Checkpoints)

```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Install training dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential wget && rm -rf /var/lib/apt/lists/*

# Install UV and project dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.cargo/bin/uv venv /app/.venv
COPY pyproject.toml uv.lock* ./
RUN /root/.cargo/bin/uv pip install -e . --python /app/.venv/bin/python

# Copy training code
COPY train/ /app/train/
COPY config/ /app/config/

# Checkpoints volume (mounted from host/PVC)
VOLUME ["/app/checkpoints"]

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "train/finetune.py"]
```

### Pattern 3: Batch Inference (CPU or GPU)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git libffi-dev && rm -rf /var/lib/apt/lists/*

# Setup UV + venv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

COPY pyproject.toml uv.lock* ./
RUN /root/.cargo/bin/uv venv /app/.venv && \
    /root/.cargo/bin/uv pip install --no-cache-dir . --python /app/.venv/bin/python

COPY inference/ /app/inference/

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "inference/batch_embed.py"]
```

---

## Model Artifact Optimization

### Why Layer Ordering Matters

```dockerfile
# ❌ BAD: Model changes invalidate code cache
FROM python:3.11-slim
WORKDIR /app
COPY models/ /app/models/      # 10GB layer - heavy
COPY app/ /app/app/            # Light code layer
RUN pip install dependencies
CMD ["python", "app/main.py"]

# ✅ GOOD: Code changes don't invalidate model cache
FROM python:3.11-slim
WORKDIR /app
RUN pip install dependencies   # Layer 1: OS packages
COPY app/ /app/app/            # Layer 2: Code (changes often)
COPY models/ /app/models/      # Layer 3: Models (changes rarely)
CMD ["python", "app/main.py"]
```

**Impact**: Model layer cached locally = 10GB not re-downloaded on code changes

### Multi-Layer Model Loading

```dockerfile
FROM python:3.11

WORKDIR /app

# Layer 1: Base libraries (rarely changes)
RUN pip install torch transformers

# Layer 2: Download small model index
RUN mkdir -p /app/models && \
    python -c "from transformers import AutoTokenizer; \
    AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-hf')"

# Layer 3: Download weights (LARGEST, rarely changes)
RUN python -c "from transformers import AutoModelForCausalLM; \
    AutoModelForCausalLM.from_pretrained('meta-llama/Llama-2-7b-hf', \
    device_map='cpu', torch_dtype=torch.float16)"

COPY app/ /app/app/
CMD ["python", "app/main.py"]
```

### Model Compression for Smaller Images

**GGUF Format** (LLaMA C++ Backend):
```dockerfile
FROM python:3.11

WORKDIR /app

# Use pre-quantized GGUF (2-4GB vs 15GB FP32)
RUN apt-get install -y --no-install-recommends wget && \
    wget https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf \
    -O /app/models/llama-2-7b.gguf

RUN pip install llama-cpp-python

COPY app/ /app/app/
CMD ["python", "app/main.py"]
```

**Benefits**:
- **Size**: 2-4 GB vs 15 GB (FP32) or 7-8 GB (FP16)
- **Speed**: Comparable to FP16 due to optimized quantization
- **Memory**: Fits on consumer GPUs

See [references/model-optimization.md] for advanced patterns: layer caching, BuildKit cache mounts, sharding

---

## 🎯 Real-World Scenarios: Copy-Paste Solutions

**Choose your scenario to get a complete, production-ready solution:**

### Scenario 1: "I have Llama 2 7B, 1 GPU, need a chat API"

**Your setup:**
- Model: Llama 2 7B Chat (13GB)
- Hardware: 1 Tesla T4 GPU
- Load: 5-20 concurrent users
- Goal: ChatGPT-like API

**Solution:**
```dockerfile
# Use this Dockerfile directly (from Pattern 1)
FROM python:3.11-slim as builder
WORKDIR /app
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"
COPY pyproject.toml uv.lock* ./
RUN /root/.cargo/bin/uv venv /opt/venv && \
    /root/.cargo/bin/uv pip install vllm transformers --python /opt/venv/bin/python

FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY app/ /app/
COPY models/llama-2-7b-chat.gguf /app/models/
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "/app/models/llama-2-7b-chat.gguf", "--gpu-memory-utilization", "0.9"]
```

**Expected Performance:**
- Startup: 30-60 seconds
- Throughput: 20-30 tokens/second
- Memory: 10-12GB GPU + 4GB CPU
- Concurrency: 10-20 users

**Verify with:**
```bash
docker build -t llama2-chat .
docker run --gpus all -p 8000:8000 llama2-chat
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Llama-2-7b-chat","messages":[{"role":"user","content":"Hello"}]}'
```

---

### Scenario 2: "I need to embed 1M documents with Sentence Transformers"

**Your setup:**
- Task: Embeddings (not streaming)
- Model: sentence-transformers/all-MiniLM-L6-v2 (90MB)
- Load: 10,000 documents/minute
- Goal: Batch processing

**Solution:**
```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app
RUN pip install sentence-transformers torch

COPY embedding_job.py /app/
COPY data/ /app/data/

CMD ["python", "embedding_job.py"]
```

**embedding_job.py:**
```python
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')

sentences = open('/app/data/documents.txt').readlines()
embeddings = model.encode(sentences, batch_size=128, show_progress_bar=True)

# Save embeddings (numpy or Qdrant)
import numpy as np
np.save('/app/output/embeddings.npy', embeddings)
```

**Run:**
```bash
docker build -t embedder .
docker run --gpus all -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output embedder
```

**Expected Performance:**
- Throughput: 1000-5000 docs/sec
- Memory: 2GB GPU + 4GB CPU
- Time for 1M docs: 3-10 minutes

---

### Scenario 3: "Fine-tune Llama on custom data with 8 GPUs"

**Your setup:**
- Task: LoRA fine-tuning
- Model: Llama 2 7B
- Hardware: 8 A100 80GB GPUs
- Data: 100K examples

**Solution:**
```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

WORKDIR /app
RUN pip install transformers peft bitsandbytes peft trl

COPY train.py /app/
COPY data/ /app/data/
VOLUME ["/app/checkpoints"]

CMD ["torchrun", "--nproc_per_node=8", "train.py"]
```

**train.py:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import get_peft_model, LoraConfig
from trl import SFTTrainer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b")
peft_config = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, task_type="CAUSAL_LM")
model = get_peft_model(model, peft_config)

trainer = SFTTrainer(
    model=model,
    args=TrainingArguments(
        output_dir="/app/checkpoints",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        save_steps=500,
    ),
    train_dataset=load_dataset("data/train.json"),
)

trainer.train()
```

**Run:**
```bash
docker build -t llama-finetune .
docker run --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/checkpoints:/app/checkpoints \
  llama-finetune
```

**Expected Performance:**
- Training speed: 2000-3000 tokens/sec
- Time for 100K examples: 6-12 hours
- Checkpoint size: 100MB (LoRA only)
- GPU memory: 70GB per GPU

---

### Scenario 4: "Deploy multiple models (Triton) with auto-scaling"

See [references/inference-patterns.md](references/inference-patterns.md) for Triton Dockerfile + Kubernetes setup in kubernetes-ai-services skill.

---

## Pattern Comparison: Quick Selection Table

| Pattern | Use Case | Throughput | Latency | Setup Complexity | When to Use |
|---------|----------|-----------|---------|------------------|------------|
| **1: FastAPI** | Chat/streaming | 20-50 tok/s | 50-100ms | Low | < 100 users, streaming needed |
| **2: vLLM** | High throughput | 100-300 tok/s | 20-50ms | Medium | 100+ users, no streaming |
| **3: TGI** | HF optimized | 80-200 tok/s | 30-80ms | Medium | HF models, simple setup |
| **4: Triton** | Multi-model | Variable | 10-50ms | High | 5+ models, complex inference |
| **5: Batch Job** | Embeddings/classification | 1K-10K items/s | N/A | Low | Non-streaming, bulk processing |
| **6: Ray Serve** | Distributed | 100-500 tok/s | 20-100ms | Very High | Extreme scale, multi-node |

---

## GPU and NVIDIA Runtime Configuration

### Step 1: Install NVIDIA Container Toolkit

```bash
# Ubuntu 22.04 LTS (Jammy)
curl https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl https://nvidia.github.io/libnvidia-container/ubuntu22.04/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null

apt-get update && apt-get install -y nvidia-container-toolkit
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker
```

### Step 2: Test GPU Access

```bash
# Verify NVIDIA runtime is registered
docker info | grep nvidia

# Test with nvidia/cuda image
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi

# Test with PyTorch
docker run --rm --gpus all pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel \
    python -c "import torch; print(torch.cuda.is_available())"
```

### Step 3: Configure GPU Access in docker-compose

```yaml
version: '3.8'
services:
  llm-inference:
    image: my-llm:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    shm_size: 2gb  # For PyTorch DataLoader
    ports:
      - "8000:8000"
```

### CUDA Version Matching (Critical)

```dockerfile
# Get base image CUDA version
docker run --rm nvidia/cuda:12.0-base nvidia-smi | grep CUDA

# Install matching PyTorch
# CUDA 12.0: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel
# CUDA 11.8: pytorch/pytorch:2.2.0-cuda11.8-cudnn8-devel

# Test mismatch detection
docker run --rm -it my-llm python -c \
    "import torch; assert torch.version.cuda == '12.1', 'CUDA mismatch!'"
```

See [references/gpu-runtime.md] for CUDA compatibility matrix, troubleshooting, and cloud GPU patterns (AWS/GCP/Azure)

---

## docker-compose for AI Services

### LLM Inference Stack

```yaml
version: '3.8'

services:
  # LLM Inference Service (GPU)
  llm-api:
    build: .
    image: llm-inference:latest
    container_name: llm-api
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      - MODEL_PATH=/models/llama-2-7b.gguf
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']  # GPU 0
              capabilities: [gpu]
    volumes:
      - ./models:/models:ro
      - ./config:/app/config:ro
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    shm_size: 2gb
    restart: unless-stopped

  # Vector Database (for RAG)
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant-db
    environment:
      - QDRANT_API_KEY=test-key
    volumes:
      - qdrant-data:/qdrant/storage
    ports:
      - "6333:6333"
    restart: unless-stopped

  # Redis (for caching/queue)
  redis:
    image: redis:7-alpine
    container_name: redis-cache
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    restart: unless-stopped

  # Monitoring (Prometheus)
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

volumes:
  qdrant-data:
  redis-data:
  prometheus-data:
```

**Usage:**
```bash
# Start all services
docker-compose up -d

# Monitor inference service
docker-compose logs -f llm-api

# Check resource usage
docker stats llm-api

# Stop everything
docker-compose down
```

---

## Production Hardening for AI Services

### 1. Non-Root User + GPU Access

```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Create non-root user
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Install dependencies
RUN pip install fastapi uvicorn torch

COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser models/ /app/models/

# Use non-root user
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**GPU Note**: Non-root users can access GPU if group membership is correct:
```bash
docker run --gpus all --user 1000:1000 my-llm nvidia-smi
# Works because container runtime adds necessary capabilities
```

### 2. Resource Limits

```yaml
# docker-compose.yml
services:
  llm-api:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 16g
          # GPU limit (count, not VRAM)
        reservations:
          cpus: '2'
          memory: 12g
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      # Prevent OOM: Set PyTorch memory fraction
      - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512
```

### 3. OOM Prevention

```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512 \
    TORCH_HOME=/cache/torch \
    HF_HOME=/cache/huggingface \
    TRANSFORMERS_CACHE=/cache/huggingface/models

WORKDIR /app

# Pre-allocate cache volumes
RUN mkdir -p /cache && \
    pip install torch transformers

COPY app/ /app/app/
COPY models/ /app/models/

EXPOSE 8000
CMD ["python", "app/main.py"]
```

### 4. Security Scanning

```bash
# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image my-llm:latest

# Build SBOM (Software Bill of Materials)
pip install cyclonedx-bom
cyclonedx-bom -o sbom.xml

# Check secrets in image
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image --secret-scan my-llm:latest
```

---

## UV Package Manager Integration

### Why UV for AI Services

```bash
# Dependency resolution
# pip: 30-45 seconds
# UV: 2-5 seconds
# 10-20x faster!

# Installation from lock file
# pip: Variable performance
# UV: Consistent, reproducible builds
```

### Multi-Stage Build with UV

```dockerfile
# Stage 1: Dependency builder (smallest possible)
FROM python:3.11-slim as builder

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.cargo/bin/uv venv /opt/venv

# Copy only dependency specs
COPY pyproject.toml uv.lock* ./

# Lock file doesn't exist? Create it:
RUN /root/.cargo/bin/uv lock --no-cache || true

# Install dependencies
RUN /root/.cargo/bin/uv pip install --python /opt/venv/bin/python -e .

# Stage 2: Runtime (final image, no build tools)
FROM python:3.11-slim

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY app/ /app/app/
COPY models/ /app/models/

CMD ["python", "app/main.py"]
```

### Using Private PyPI Registries

```dockerfile
# Use BuildKit secrets for secure token passing
# docker build --secret pip_token=/run/secrets/pip_token .

FROM python:3.11-slim

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.cargo/bin/uv venv /opt/venv

# Mount secret at build time
RUN --mount=type=secret,id=pip_token \
    /root/.cargo/bin/uv pip config set global.index-url "https://token:$(cat /run/secrets/pip_token)@private.pypi.org/simple" && \
    /root/.cargo/bin/uv pip install -e . --python /opt/venv/bin/python

FROM python:3.11-slim
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY app/ /app/app/
CMD ["python", "app/main.py"]
```

**Usage:**
```bash
docker build \
  --secret pip_token=/path/to/token \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  -t my-llm:latest .
```

See [references/uv-integration.md] for performance benchmarks, lock file management, and dependency pinning strategies

---

## Battle-Tested AI Gotchas

| Issue | Symptoms | Cause | Fix |
|-------|----------|-------|-----|
| **GPU not found** | `torch.cuda.is_available() = False` | NVIDIA runtime not installed | `apt install nvidia-container-toolkit && docker restart` |
| **CUDA version mismatch** | `RuntimeError: CUDA version doesn't match` | Base image CUDA ≠ PyTorch CUDA | Check `nvidia-smi \| grep CUDA` and match in Dockerfile FROM |
| **OOM during inference** | Container killed, no error logs | GPU memory exhausted | Set `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512` |
| **Model re-download on build** | Slow build, 10GB+ layers | Model in code/requirements layer | Move model COPY to final layer |
| **Health check timeout** | Container restarts every 30s | Model loading takes >30s startup probe | Set `start_period: 60s` or higher |
| **Shared memory exhaustion** | DataLoader deadlock, no error | PyTorch DataLoader needs /dev/shm | Add `shm_size: 2gb` in docker-compose |
| **GPU memory leak** | Gradual memory increase, crashes | Unclosed CUDA contexts | Run `torch.cuda.empty_cache()` after batches |
| **Quantization errors** | `ValueError: quantization not supported` | GGUF/GPTQ requires specific library | Check `llama-cpp-python` or `auto-gptq` installed |
| **Inference timeout** | 504 Gateway Timeout | Model inference >120s | Increase Gunicorn `--timeout` parameter |
| **Multi-GPU not detected** | Only GPU 0 visible in container | Missing `NVIDIA_VISIBLE_DEVICES=all` | Set in docker-compose environment |
| **BuildKit cache ignored** | Docker builds full image every time | Missing `--build-arg BUILDKIT_INLINE_CACHE=1` | Use: `docker build --build-arg BUILDKIT_INLINE_CACHE=1 .` |
| **Model weights corrupted** | Checksum mismatch during download | Incomplete download in earlier build layer | Clear cache: `docker builder prune` |
| **Permissions denied in volume** | `Permission denied: /models/model.bin` | File owned by root, container runs as user | Use `--chown=appuser:appuser` in COPY |
| **Network timeout downloading model** | HuggingFace Hub timeout | No internet in build context | Pre-download: `huggingface-hub download` before docker build |
| **pip conflicts with torch** | `ERROR: pip's dependency resolver does not currently take into account` | pip can't resolve PyTorch+transformers | Use UV for faster, cleaner resolution |
| **Startup probe failing** | 503 Service Unavailable immediately | Model loading not complete before first probe | Increase `start_period` to 120s-300s for large models |
| **GPU sharing between containers** | Both containers get same GPU | No device isolation configured | Set `device_ids: ['0']` per service |
| **High memory on cold start** | Spike to 16GB when loading model | No streaming/lazy loading | Use `device_map='cpu'` initially, then to GPU |
| **GGUF inference slow** | 2-3 tokens/sec instead of 10-20 | GGUF missing quantization or wrong backend | Use Q4 or Q5 quantization, verify llama-cpp |
| **Docker layer cache mismatch** | Different build results locally vs CI | System Python vs venv versions | Always use `--platform=linux/amd64` in CI |

**Debugging Commands**:
```bash
# Check GPU inside container
docker run --gpus all my-llm nvidia-smi

# Inspect image layers
docker history my-llm:latest

# Check OOM errors
docker logs --tail=100 my-llm 2>&1 | grep -i "killed\|oom"

# Profile memory usage
docker run --gpus all --cap-add=SYS_PTRACE my-llm python -m memory_profiler app.py

# Check startup probe status
docker inspect my-llm | grep -A 10 "Healthcheck"
```

See [references/troubleshooting-ai.md] for 25+ additional gotchas with detailed debugging guides

---

## 🔧 Troubleshooting Decision Tree

**Container won't start or fails immediately?**

```
ERROR: Check these in order:

1. Does Docker see the image?
   ├─ docker images | grep my-app
   └─ If missing: Run `docker build -t my-app .`

2. Does it fail on GPU access?
   ├─ docker run --gpus all my-app nvidia-smi
   ├─ If fails: See [references/gpu-runtime.md] step 1-3
   └─ If passes: GPU is OK

3. Does model load successfully?
   ├─ Check logs: `docker logs <container_id>`
   ├─ Search for "Loaded" or "Loading"
   └─ If timeout: See [Battle-Tested Gotchas #4]

4. Does health check pass?
   ├─ curl http://localhost:8000/health
   ├─ If 503: Model still loading (normal)
   └─ If connection refused: Check EXPOSE port
```

---

## 📋 Production Readiness Checklist

**Use this before deploying to production:**

### Pre-Build Phase
- [ ] **Model access verified**: Can you download your model?
- [ ] **Disk space**: 50GB+ available?
- [ ] **Docker installed**: `docker --version` shows 20.10+?
- [ ] **GPU (if needed)**: `nvidia-smi` shows your GPUs?

### Build Phase
- [ ] **Build completes**: `docker build -t my-app .` succeeds?
- [ ] **Build time**: Reasonable (< 30 min)?
- [ ] **Image size**: `docker images my-app` shows < 20GB?

### Runtime Phase - Quick Tests
```bash
# Test 1: GPU accessible
docker run --gpus all my-app nvidia-smi

# Test 2: Model loads
docker run --gpus all my-app python -c \
  "from transformers import AutoModelForCausalLM; print('✓ Model loads')"

# Test 3: Health check
docker run --gpus all -d -p 8000:8000 my-app
sleep 120  # Wait for startup
curl http://localhost:8000/health
```

### Pre-Production Phase
- [ ] **Inference latency**: Single query takes < 30 sec?
- [ ] **Memory stable**: `docker stats my-app` shows stable memory after 5 min?
- [ ] **No OOM kills**: Logs show no "Killed" messages?
- [ ] **Concurrency test**: Handle 5+ concurrent requests?
- [ ] **Security scan**: `trivy image my-app` shows no critical?

### Deployment Phase
- [ ] **Image tagged with version**: `my-app:v1.0.0`?
- [ ] **Image pushed to registry**: `docker push my-app:v1.0.0`?
- [ ] **Kubernetes manifests ready** (if deploying): All YAML files validated?
- [ ] **Resource requests set**: CPU/memory/GPU defined in K8s?

### Post-Deployment Phase
- [ ] **Container stays healthy**: No restarts in first 24h?
- [ ] **Logs are clean**: No warnings or errors?
- [ ] **Monitoring in place**: Metrics being collected?
- [ ] **Alerts configured**: Email/Slack on failures?

---

## Image Optimization Checklist

- [ ] **Multi-stage build**: Separated builder and runtime stages
- [ ] **Dependencies before code**: RUN pip install before COPY app/
- [ ] **Models on final layer**: COPY models after code to preserve cache
- [ ] **Health checks**: HEALTHCHECK with appropriate timeout (120s+ for large models)
- [ ] **Non-root user**: USER statement before CMD
- [ ] **Resource limits**: CPU/memory/GPU reservations in docker-compose
- [ ] **OOM prevention**: `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512`
- [ ] **Shared memory**: `shm_size: 2gb` for PyTorch DataLoader
- [ ] **Build cache enabled**: `--build-arg BUILDKIT_INLINE_CACHE=1`
- [ ] **Security scanning**: `trivy image` passes critical/high checks
- [ ] **SBOM generated**: `cyclonedx-bom` for supply chain security
- [ ] **CUDA version match**: Verified via `nvidia-smi` vs `torch.version.cuda`
- [ ] **UV for dependencies**: No pip in production Dockerfile
- [ ] **Secrets not in image**: No HuggingFace tokens or API keys in layers
- [ ] **Image size <10GB**: For LLM + serving stack (after quantization)

---

## Verification

```bash
# Run skill verification
cd .claude/skills/docker-ai-production
python scripts/verify.py
```

**Output**:
```
✓ Docker installed (v24.0.0)
✓ Docker daemon running
✓ NVIDIA Container Toolkit: v1.15.0
✓ UV installed: v0.4.0
✓ Skill structure validated (SKILL.md + 6 references + assets)
✓ All templates valid YAML
✓ All examples buildable
Ready for AI containerization!
```

---

## Related Skills

- **[docker-learning](../docker-learning/SKILL.md)** — Foundation (Containers, Images, Registries)
- **[containerizing-applications](../containerizing-applications/SKILL.md)** — General production patterns
- **[kubernetes-ai-services](../kubernetes-ai-services/SKILL.md)** — Deploy containerized AI to K8s
- **[building-fastapi-apps](../building-fastapi-apps/SKILL.md)** — API patterns for LLM services
- **[building-rag-systems](../building-rag-systems/SKILL.md)** — RAG pipeline containerization
- **[scaffolding-fastapi-dapr](../scaffolding-fastapi-dapr/SKILL.md)** — Event-driven AI microservices

---

## 📚 References Index

| Topic | File | Coverage | Keep Updated | Official Docs |
|-------|------|----------|--------------|---------------|
| **GPU Runtime** | [gpu-runtime.md](references/gpu-runtime.md) | NVIDIA toolkit, CUDA matching, cloud GPUs | Monthly | [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/) |
| **Model Optimization** | [model-optimization.md](references/model-optimization.md) | Layer caching, compression (GGUF/GPTQ/AWQ) | When tools release | [TheBloke Models](https://huggingface.co/TheBloke) |
| **Inference Patterns** | [inference-patterns.md](references/inference-patterns.md) | vLLM, TGI, Triton, TorchServe, Ray | Every 2-3 months | [vLLM Docs](https://docs.vllm.ai/) \| [TGI Docs](https://huggingface.co/docs/text-generation-inference/) |
| **UV Package Manager** | [uv-integration.md](references/uv-integration.md) | Lock files, private registries, performance | Monthly | [UV GitHub](https://github.com/astral-sh/uv) |
| **Production Security** | [production-security-ai.md](references/production-security-ai.md) | Non-root GPU, secrets, SBOM, supply chain | Quarterly | [Trivy](https://aquasecurity.github.io/trivy/) \| [Cosign](https://docs.sigstore.dev/cosign/) |
| **Troubleshooting** | [troubleshooting-ai.md](references/troubleshooting-ai.md) | 25+ production issues, debugging | As needed | See reference file links |

---

### 📌 How to Keep This Skill Updated

**This skill relies on tools that evolve frequently. Follow this schedule:**

1. **Monthly**: Check for NVIDIA driver/CUDA updates
   - Visit: https://docs.nvidia.com/cuda/
   - Update: `gpu-runtime.md` with new CUDA versions

2. **Every 2-3 months**: Check framework updates
   - vLLM: https://github.com/vllm-project/vllm/releases
   - TGI: https://github.com/huggingface/text-generation-inference/releases
   - Update: `inference-patterns.md` with new features

3. **Quarterly**: Review security and best practices
   - Check: https://owasp.org/ for security updates
   - Update: `production-security-ai.md`

4. **When you encounter new issues**: Add to troubleshooting
   - Document symptom, cause, fix
   - Update: `troubleshooting-ai.md`

---

## Quick Links

- **GPU Runtime**: [Install NVIDIA Toolkit](#gpu-and-nvidia-runtime-configuration)
- **Model Caching**: [Layer Ordering](#model-artifact-optimization)
- **docker-compose**: [Complete AI Stack](#docker-compose-for-ai-services)
- **Hardening**: [Security Checklist](#image-optimization-checklist)
- **Troubleshooting**: [Gotchas Table](#battle-tested-ai-gotchas)

**Version**: 1.0.0 | **Last Updated**: 2024 | **Status**: Production-Ready
