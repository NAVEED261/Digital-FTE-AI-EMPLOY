# Model Artifact Optimization for Container Images

## Layer Caching: The Critical Pattern

### Why Layer Order Matters

Docker builds images in layers. Each instruction creates a new layer, and Docker caches each layer independently. If a layer hasn't changed since the last build, Docker uses the cached version.

**Bad Practice: Model changes invalidate all caches**
```dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY models/ /app/models/           # Layer 1: 10GB model (heavy)
COPY app/ /app/app/                 # Layer 2: Code (0.5MB)
RUN pip install -r requirements.txt # Layer 3: 500MB deps

# Problem: Edit app/main.py (0.1KB change) → Docker rebuilds ALL layers
# Cost: Re-downloads 10GB model, reinstalls 500MB deps = 5-10 min rebuild
```

**Good Practice: Models on final layer, code before**
```dockerfile
FROM python:3.11-slim
WORKDIR /app

RUN pip install -r requirements.txt # Layer 1: 500MB deps (cached)
COPY app/ /app/app/                 # Layer 2: Code (changes often, but small)
COPY models/ /app/models/           # Layer 3: 10GB model (changes rarely, cached)

# Benefit: Edit app/main.py → Docker rebuilds only layer 2 (1 sec)
# Model layer 3 is skipped (cached), only new code is copied
# Total rebuild: 1-2 seconds instead of 5-10 minutes
```

**Impact Calculation**:
- Standard build (model changes): 10 GB download + pip install = 10-15 min
- Optimized build (code changes): 1-2 sec (layer cache hit)
- **30-100x speedup** for development iterations

---

## Multi-Layer Model Loading Pattern

### Separating Model Downloading from Application Code

Instead of downloading the entire model during build, split into stages:

```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel as model-downloader

WORKDIR /tmp/models

# Install HuggingFace tools
RUN pip install huggingface-hub transformers

# Only download tokenizer (small, 100-500MB)
RUN python << 'EOF'
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer

model_name = "meta-llama/Llama-2-7b-chat-hf"

# Download tokenizer (triggers auth check)
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    trust_remote_code=True
)
EOF

# Stage 2: Download weights (largest, ~13GB for Llama-2-7B)
RUN python << 'EOF'
import torch
from transformers import AutoModelForCausalLM

model_name = "meta-llama/Llama-2-7b-chat-hf"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",  # Keep on CPU during download
    torch_dtype=torch.float16,  # FP16 = ~7GB instead of 13GB
    trust_remote_code=True
)
EOF

# Stage 3: Runtime (small, fast)
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Copy downloaded models from stage 2
COPY --from=model-downloader /root/.cache/huggingface /root/.cache/huggingface

# Copy application code (after models, so code changes don't re-download)
COPY app/ /app/app/
COPY config/ /app/config/

ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_OFFLINE=1  # Use cached models, no downloads at runtime

ENTRYPOINT ["python", "app/main.py"]
```

**Advantages**:
- Model downloaded once, reused across all containers
- Code changes don't re-trigger model downloads
- Clear separation of concerns (model layer vs code layer)

---

## BuildKit Cache Mounts: Advanced Layer Caching

### Problem: Installing Dependencies from Scratch Every Build

Standard Docker builds download all dependencies every time:

```dockerfile
# This installs from pip every single build (slow)
RUN pip install -r requirements.txt
```

### Solution: BuildKit Cache Mount

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

WORKDIR /app

# Mount persistent cache directory
# --mount=type=cache tells Docker to keep this directory between builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY app/ /app/app/
CMD ["python", "app/main.py"]
```

**Build this with:**
```bash
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t my-app:latest .
```

**Impact**:
- First build: 30 seconds (download all deps)
- Subsequent builds (unchanged requirements.txt): 1-2 seconds (cache hit)
- **15-20x speedup** for CI/CD pipelines

### BuildKit Cache for Model Downloads

```dockerfile
# syntax=docker/dockerfile:1.4

FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

WORKDIR /app

# Cache HuggingFace hub downloads
RUN --mount=type=cache,target=/root/.cache/huggingface \
    --mount=type=secret,id=hf_token \
    python << 'EOF'
import os
from huggingface_hub import login, hf_hub_download
from transformers import AutoModelForCausalLM

# Login with token from secret
if os.path.exists('/run/secrets/hf_token'):
    with open('/run/secrets/hf_token', 'r') as f:
        token = f.read().strip()
    login(token=token)

# Download model (cached in /root/.cache/huggingface)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    torch_dtype="auto",
    device_map="auto"
)
EOF

COPY app/ /app/app/
CMD ["python", "app/main.py"]
```

**Build with secret:**
```bash
docker build \
    --secret hf_token=/path/to/token \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t my-llm:latest .
```

---

## Model Compression Strategies

### Strategy 1: GGUF Quantization (2-4 GB)

**What is GGUF?**
- Format optimized for inference (not training)
- Quantized to INT4 or INT5 (75% size reduction)
- Optimized for CPU and small GPUs
- Used by llama.cpp backend

**Advantages**:
- Size: 2-4 GB vs 15 GB (FP32)
- Speed: Comparable to FP16 due to optimized kernels
- Compatibility: Works on consumer GPUs (8GB VRAM)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Use pre-quantized GGUF (TheBloke maintains these)
RUN apt-get install -y --no-install-recommends wget && \
    mkdir -p /app/models && \
    wget -O /app/models/llama-2-7b-q4.gguf \
    https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf

RUN pip install llama-cpp-python

COPY app/ /app/app/
CMD ["python", "app/main.py"]
```

**Sizes:**
- Llama 2 7B FP32: 13.5 GB
- Llama 2 7B FP16: 6.7 GB
- Llama 2 7B Q5_K_M (GGUF): 4.5 GB
- Llama 2 7B Q4_K_M (GGUF): 3.8 GB
- **Reduction: 72% smaller**

### Strategy 2: GPTQ Quantization (3-5 GB)

**What is GPTQ?**
- Post-training quantization method
- Maintains more accuracy than naive INT4
- Good for inference on GPU

**Dockerfile:**
```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

RUN pip install auto-gptq transformers

# Download pre-quantized GPTQ model
RUN python << 'EOF'
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig

model_name = "TheBloke/Llama-2-7B-Chat-GPTQ"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto"
)
EOF

COPY app/ /app/app/
ENV TRANSFORMERS_CACHE=/app/models
CMD ["python", "app/main.py"]
```

### Strategy 3: AWQ Quantization (3-4 GB)

**What is AWQ?**
- Better accuracy than GPTQ at same quantization level
- Faster inference
- Newer, fewer model variants available

**Dockerfile:**
```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

RUN pip install autoawq transformers

RUN python << 'EOF'
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_name = "TheBloke/Llama-2-7B-Chat-AWQ"
model = AutoAWQForCausalLM.from_quantized(
    model_name,
    device_map="auto"
)
EOF

COPY app/ /app/app/
CMD ["python", "app/main.py"]
```

---

## Advanced: Model Sharding and Distributed Loading

### Sharding Pattern: Split Large Models Across Multiple GPUs

For models >40GB (Llama 2 70B, Mistral 7x8B MoE):

```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

WORKDIR /app

RUN pip install vllm accelerate

# Use vLLM for distributed inference
RUN python << 'EOF'
from vllm import LLM

# Automatically shards across available GPUs
model = LLM(
    model="meta-llama/Llama-2-70b-chat-hf",
    tensor_parallel_size=4,  # Split across 4 GPUs
    dtype="float16"
)
EOF

COPY app/ /app/app/
ENV VLLM_TENSOR_PARALLEL_SIZE=4

EXPOSE 8000
CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "meta-llama/Llama-2-70b-chat-hf", \
     "--tensor-parallel-size", "4"]
```

### Alternative: Pipeline Parallelism

For extremely large models or specific architectures:

```python
# In application code
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b",
    device_map={
        # Layer 0-15 on GPU 0
        "transformer.h.0": 0,
        "transformer.h.1": 0,
        "transformer.h.2": 0,
        # ... continue mapping
        "transformer.h.31": 3,
        "lm_head": 3
    },
    torch_dtype=torch.float16
)
```

---

## Lazy Loading: Download on First Use

### Problem: Long startup time if downloading model during container start

```dockerfile
# ❌ Bad: Model downloads at container startup (can be 5-10 minutes)
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

COPY app/ /app/app/

# This will run when container starts, blocking health checks
CMD ["python", "app/main.py"]  # Loads model here
```

### Solution: Pre-download in image, lazy-load in app

```dockerfile
# ✅ Good: Pre-cache model in image, load quickly at startup
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime as downloader

RUN python << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
# This runs during build, not runtime
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")
EOF

FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

COPY --from=downloader /root/.cache/huggingface /root/.cache/huggingface

WORKDIR /app
COPY app/ /app/app/

ENV TRANSFORMERS_OFFLINE=1  # Don't try to download, use cached
HEALTHCHECK --interval=10s --timeout=5s --start-period=60s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app/main.py"]
```

**app/main.py:**
```python
from fastapi import FastAPI
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

model = None
tokenizer = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    # Load from cache (fast, 1-10 seconds)
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-chat-hf",
        device_map="auto",
        torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-2-7b-chat-hf"
    )

@app.get("/health")
def health():
    return {"status": "ok" if model else "loading"}

@app.post("/generate")
def generate(prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=100)
    return {"result": tokenizer.decode(outputs[0])}
```

---

## Measuring Image Size Impact

### Docker Image Size Analysis

```bash
# See all layers and their sizes
docker history my-llm:latest
# Output:
# IMAGE               CREATED             CREATED BY                                      SIZE
# abc123              2 minutes ago       /bin/sh -c #(nop) CMD ["python" "app/main.py"]   0B
# def456              2 minutes ago       /bin/sh -c COPY app/ /app/app/ -- 0.5MB
# ghi789              5 minutes ago       /bin/sh -c COPY models/ /app/models/ -- 3.8GB
# jkl012              10 minutes ago      /bin/sh -c pip install pytorch --  2.1GB
# mno345              (base)              (base layer)                                      1.5GB

# Size of final image
docker images my-llm:latest
# REPOSITORY  TAG     IMAGE ID     SIZE
# my-llm      latest  abc123       7.8GB

# Size of uncompressed layers
docker inspect my-llm:latest | grep -A5 "Layers"
```

### Dockerfile Size Optimization Checklist

- [ ] **Base image size**: Use slim or alpine variants (`python:3.11-slim` = 150MB vs `python:3.11` = 900MB)
- [ ] **Multi-stage builds**: Remove build tools from final image (50-70% reduction)
- [ ] **RUN cleanup**: Delete apt/pip caches (`apt-get clean && rm -rf /var/lib/apt/lists/*`)
- [ ] **Combine RUN**: Merge multiple RUN commands (reduces layers)
- [ ] **Model quantization**: Use GGUF/GPTQ (60-75% reduction)
- [ ] **Layer ordering**: Models on final layer for cache efficiency
- [ ] **BuildKit cache**: Use `--mount=type=cache` for deps (rebuild speedup)
- [ ] **Remove unused files**: Delete example code, documentation

---

## Performance Benchmark: Model Loading Times

| Format | Size | Load Time (GPU) | Load Time (CPU) | Inference Speed |
|--------|------|-----------------|-----------------|-----------------|
| FP32 | 13.5 GB | 30-60s | 5-10 min | Baseline (100%) |
| FP16 | 6.7 GB | 15-30s | 2-5 min | ~100% |
| GGUF Q4 | 3.8 GB | 5-10s | 30-60s | 80-90% |
| GGUF Q5 | 4.5 GB | 8-12s | 60-90s | 90-95% |
| GPTQ | 3.5 GB | 10-15s | N/A | 95-99% |
| AWQ | 3.4 GB | 8-12s | N/A | 95-99% |

**Recommendation for Production**:
- GPU inference (A100/L40S): **FP16** or **GPTQ** (best speed/size)
- GPU inference (T4/RTX): **GGUF Q4** (fits in 8GB VRAM)
- CPU inference: **GGUF Q4** (only viable option)
- Training: **FP16** (no quantization, need gradients)

---

## Reference

- **GGUF Format**: https://github.com/ggerganov/ggml/blob/master/docs/gguf.md
- **TheBloke Models**: https://huggingface.co/TheBloke
- **GPTQ Explained**: https://arxiv.org/abs/2210.17323
- **AWQ Explained**: https://arxiv.org/abs/2306.00978
- **Transformers Quantization**: https://huggingface.co/docs/transformers/quantization
