# UV Package Manager for Docker AI Services

## UV vs pip: Performance Comparison

| Operation | pip | UV | Speedup |
|-----------|-----|-----|---------|
| Dependency resolution | 30-60s | 2-5s | **10-30x** |
| First install | 45-90s | 5-10s | **10-15x** |
| Lock file generation | Variable | <5s | **15-30x** |
| CI build (cold cache) | 3-5 min | 30-60s | **5-10x** |
| CI build (warm cache) | 2-3 min | 2-5s | **20-60x** |

**Bottom line**: UV = 10-30x faster dependency resolution, perfect for Docker builds

---

## Basic Dockerfile Pattern with UV

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.11-slim as builder

WORKDIR /app

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy dependency specs
COPY pyproject.toml uv.lock* ./

# Install with BuildKit cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /opt/venv && \
    uv pip install -e . --python /opt/venv/bin/python

# Runtime: small, no build tools
FROM python:3.11-slim

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY app/ /app/app/
COPY models/ /app/models/

CMD ["python", "app/main.py"]
```

**Key features**:
- UV installed from pre-built binary (1 second)
- BuildKit cache mount for pip cache (reuses across builds)
- Final image only contains runtime venv

---

## pyproject.toml with Dependency Pinning

**For reproducible AI services:**

```toml
[project]
name = "llm-inference"
version = "1.0.0"
description = "Production LLM Inference API"
dependencies = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "torch==2.1.1",
    "transformers==4.34.1",
    "pydantic==2.5.0",
]

[project.optional-dependencies]
gpu = [
    "accelerate==0.24.1",
    "bitsandbytes==0.41.2.post2",
]

dev = [
    "pytest==7.4.3",
    "pytest-asyncio==0.21.1",
    "black==23.11.0",
]

[tool.uv]
python-version = "3.11"
allow-insecure = []  # Reject insecure packages
prerelease = "if-necessary"  # Don't use prereleases unless required
```

**Lock file (uv.lock)**: Generated via `uv lock`, checked into git for reproducibility

```bash
# Generate lock file
uv lock

# Install from lock (deterministic)
uv pip install --from-lock uv.lock
```

---

## Dockerfile with GPU Dependencies

```dockerfile
# syntax=docker/dockerfile:1.4

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime as builder

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

COPY pyproject.toml uv.lock* ./

# Install PyTorch is already in base image
# Install additional GPU deps with UV
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install accelerate bitsandbytes --python /opt/python/bin/python

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app/ /app/app/
CMD ["python", "app/main.py"]
```

---

## UV with Private PyPI Registry

**Using BuildKit secrets for secure token passing:**

```bash
# Create token file
echo "your-private-token" > /run/secrets/pip_token

# Build with secret
docker build \
    --secret pip_token=/run/secrets/pip_token \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t my-app:latest .
```

**Dockerfile:**
```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.11-slim as builder

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock* ./

# Mount secret, use it temporarily
RUN --mount=type=secret,id=pip_token \
    --mount=type=cache,target=/root/.cache/uv \
    bash -c 'TOKEN=$(cat /run/secrets/pip_token) && \
    uv pip config set global.index-url "https://token:${TOKEN}@private.pypi.org/simple" && \
    uv pip install -e . --python /opt/venv/bin/python'

# Secret is not in final image
FROM python:3.11-slim
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY app/ /app/
CMD ["python", "app/main.py"]
```

---

## UV with HuggingFace Token

**For gated models (Llama 2, Mistral, etc.):**

```dockerfile
# syntax=docker/dockerfile:1.4

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel as downloader

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

RUN --mount=type=secret,id=hf_token \
    --mount=type=cache,target=/root/.cache/huggingface \
    bash -c 'HF_TOKEN=$(cat /run/secrets/hf_token) && \
    uv pip install transformers huggingface-hub && \
    python << EOF
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
os.environ["HF_TOKEN"] = "$HF_TOKEN"
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-chat-hf",
    device_map="cpu"
)
EOF'

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime
COPY --from=downloader /root/.cache/huggingface /root/.cache/huggingface
ENV HF_HOME=/root/.cache/huggingface
WORKDIR /app
COPY app/ /app/
CMD ["python", "app/main.py"]
```

**Build:**
```bash
docker build \
    --secret hf_token=$HF_TOKEN \
    -t my-llm:latest .
```

---

## Dependency Management Best Practices

### 1. Pin All Transitive Dependencies

```bash
# Generate full lock file with all transitive deps
uv lock --all-extras

# This includes:
# - Direct dependencies from pyproject.toml
# - All transitive (indirect) dependencies
# - Exact versions for reproducibility
```

### 2. Separate Runtime and Development Dependencies

```toml
[project.optional-dependencies]
gpu = ["accelerate", "bitsandbytes"]  # Runtime, GPU-specific
dev = ["pytest", "black", "mypy"]     # Development only

[tool.uv]
# Exclude dev deps from production build
exclude-groups = ["dev"]
```

**Dockerfile:**
```dockerfile
# Only install runtime + gpu deps, skip dev
RUN uv pip install -e . --extras gpu --python /opt/venv/bin/python
```

### 3. Version Constraints for Stability

```toml
# Too loose: may break in future
dependencies = ["torch", "transformers"]

# Better: pin major.minor
dependencies = ["torch==2.1.*", "transformers==4.34.*"]

# Best: pin exact for reproducibility
dependencies = ["torch==2.1.1", "transformers==4.34.1"]

# For development, allow minor updates
dev-dependencies = ["pytest>=7.0,<8.0"]
```

---

## Conditional Dependencies by Platform

```toml
[project.optional-dependencies]
# GPU support (CUDA 12.1)
cuda12 = [
    "torch[cuda12]==2.1.1",
    "accelerate==0.24.1",
]

# GPU support (CUDA 11.8)
cuda11 = [
    "torch[cuda11]==2.1.1",
    "accelerate==0.24.1",
]

# CPU only
cpu = [
    "torch[cpu]==2.1.1",
]
```

**Build for specific platform:**
```dockerfile
# Build for CUDA 12.1
RUN uv pip install -e ".[cuda12]" --python /opt/venv/bin/python

# Build for CPU
RUN uv pip install -e ".[cpu]" --python /opt/venv/bin/python
```

---

## UV in CI/CD Pipelines

### GitHub Actions with UV Caching

```yaml
name: Build Docker Image

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Cache UV cache directory
      - uses: actions/cache@v3
        with:
          path: ~/.cache/uv
          key: uv-${{ hashFiles('**/uv.lock') }}
          restore-keys: uv-

      - name: Build image
        run: |
          docker build \
            --build-arg BUILDKIT_INLINE_CACHE=1 \
            -t my-app:latest .

      - name: Push to registry
        run: docker push my-app:latest
```

### Local CI Simulation

```bash
# Simulate CI build (cold cache)
docker builder prune -f  # Clear cache
docker build -t my-app:latest .  # First build (slow)
docker build -t my-app:latest .  # Second build (fast, uses cache)
```

---

## Troubleshooting UV in Docker

### Issue: "uv: command not found"

```dockerfile
# ❌ Installation doesn't persist
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# Binary is in /root/.cargo/bin but PATH not updated

# ✅ Correct approach
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="/root/.cargo/bin:$PATH"' >> ~/.bashrc
ENV PATH="/root/.cargo/bin:$PATH"
```

### Issue: "uv: version mismatch"

```bash
# Check uv version
uv --version

# Update to latest
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: "Cache mount permission denied"

```dockerfile
# ❌ Wrong: cache mount in wrong directory
RUN uv pip install -e . --target /app/lib

# ✅ Correct: use standard pip cache location
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e . --python /opt/venv/bin/python
```

---

## Reference

- **UV Documentation**: https://docs.astral.sh/uv/
- **UV GitHub**: https://github.com/astral-sh/uv
- **pyproject.toml Standard**: https://peps.python.org/pep-0621/
