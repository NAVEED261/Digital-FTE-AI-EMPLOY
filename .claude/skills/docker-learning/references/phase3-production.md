# Phase 3: Production Readiness (Weeks 6+)

Master security, optimization, and preparation for deployment to production environments.

## Mental Model: From Development to Production

### Key Differences

| Aspect | Development | Production |
|--------|-------------|-----------|
| Security | Less critical | Non-root user, minimal base |
| Size | Not important | <200MB optimized |
| Performance | Good enough | Optimized caching |
| Health checks | Optional | Required |
| Vulnerabilities | Tolerated | Scanned and fixed |
| Updates | Any time | Scheduled |
| Restart policy | Manual | Automatic |

## Security Best Practices

### 1. Run as Non-Root User

**Why:** Prevent container escape from gaining full system access

**Vulnerable (Development):**
```dockerfile
FROM python:3.13-slim
COPY . /app
WORKDIR /app
# Running as root (uid=0) ❌
CMD ["python", "main.py"]
```

**Secure (Production):**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

COPY . .

# Switch to non-root user
USER appuser

EXPOSE 8000
CMD ["python", "main.py"]
```

**Verify:**
```bash
docker run --rm myimage id
# Should output: uid=1000(appuser) gid=1000(appuser)
# NOT uid=0(root)
```

### 2. Minimize Base Image

**Large (18 MB+):**
```dockerfile
FROM python:3.13        # ~900MB (includes dev tools)
```

**Small (100+ MB):**
```dockerfile
FROM python:3.13-slim   # ~150MB (minimal)
```

**Minimal (50-100 MB):**
```dockerfile
FROM python:3.13-alpine # ~50MB (very minimal)
```

**Trade-offs:**
- `python:3.13`: Everything, largest
- `python:3.13-slim`: Essentials only, recommended
- `python:3.13-alpine`: Bare minimum, may need extra setup

### 3. Use Read-Only Root Filesystem

```dockerfile
VOLUME ["/tmp"]  # Allow temp writes
RUN mkdir -p /app && chown appuser:appuser /app
WORKDIR /app
USER appuser
```

Run with read-only root:
```bash
docker run --read-only --tmpfs /tmp myimage
# Root filesystem is read-only
# /tmp writable (temporary storage)
```

### 4. Don't Run Unnecessary Services

```dockerfile
# ❌ Wrong: Installing dev tools you don't need
RUN apt-get install -y gcc build-essential vim

# ✓ Right: Only install what you need
RUN apt-get install -y curl  # For health checks
```

## Image Optimization

### 1. Multi-Stage Builds

**Idea:** Build in one stage, run in another

**Development (Large):**
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt  # Includes dev dependencies
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
# Final image: 300MB+ (includes pip cache, build tools)
```

**Production (Optimized):**
```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml
# This stage: 500MB (includes pip cache, build tools)

# Stage 2: Runtime
FROM python:3.13-slim
WORKDIR /app

# Security: Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy only installed packages from builder
COPY --from=builder --chown=appuser:appuser \
  /usr/local/lib/python3.13/site-packages \
  /usr/local/lib/python3.13/site-packages

# Copy application code
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# Final image: 150-200MB (only runtime, no build tools)
```

### 2. Layer Caching Optimization

**Order matters:**
```dockerfile
FROM python:3.13-slim                   # Layer 1: Rarely changes (~150MB)

RUN apt-get update && apt-get install -y curl \
  && rm -rf /var/lib/apt/lists/*        # Layer 2: Rarely changes

RUN pip install --no-cache-dir -r requirements.txt
                                         # Layer 3: Sometimes changes (~50MB)

COPY . /app                              # Layer 4: Often changes (your code)
```

**Why this order?**
- Base image changes rarely → cache hit
- System packages change rarely → cache hit
- Python packages change sometimes → rebuild Layer 3+
- Your code changes often → rebuild Layer 4+

**If you change code:**
- Layer 1-2: Use cache ✓
- Layer 3-4: Rebuild only

**If you change requirements.txt:**
- Layer 1-3: Build fresh, Layer 4: Use cache

### 3. Cache Busting Strategies

```dockerfile
# Bad: Always rebuilds (cache busted)
RUN pip install -r requirements.txt
COPY . .

# Better: Cache reused if requirements.txt unchanged
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Best: Separate requirements by change frequency
COPY requirements-base.txt .
RUN pip install -r requirements-base.txt
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
```

### 4. .dockerignore File

Exclude unnecessary files from build context:

**File:** `.dockerignore`

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.git
.gitignore
.gitattributes
.dockerfile
docker-compose*.yml
.env
.venv
venv/
.pytest_cache
.mypy_cache
.idea
*.swp
*.swo
*~
.DS_Store
node_modules
```

**Impact:** Reduces build context sent to Docker daemon

## Health Checks and Readiness

### 1. Application Health Check

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1
```

**In your FastAPI app (main.py):**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/readiness")
async def readiness_check():
    # Check database connection
    try:
        # Verify database works
        db_session = get_db()
        return {"ready": True}
    except Exception:
        return {"ready": False, "error": "Database unavailable"}
```

### 2. Monitor Health Status

```bash
# Check health
docker ps
# Look for STATUS: "Up X minutes (healthy)"

# View health check history
docker inspect container_id | grep -A 10 "Health"

# Manual health check
docker exec container_id curl http://127.0.0.1:8000/health
```

## Container Security Scanning

### Vulnerability Scanning with Trivy

Trivy scans for known vulnerabilities in dependencies.

**Install Trivy:**
```bash
# On Windows (PowerShell)
choco install trivy
# OR download from: https://github.com/aquasecurity/trivy/releases
```

**Scan built image:**
```bash
# Build image first
docker build -t task-api:prod .

# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image task-api:prod

# Scan with severity threshold
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --severity HIGH,CRITICAL task-api:prod
```

**Interpretation:**
- RED: Critical vulnerabilities (fix immediately)
- YELLOW: High vulnerabilities (fix soon)
- BLUE: Medium vulnerabilities (fix when possible)

### Fix Vulnerabilities

**Common sources:**
1. **Base image:** Update to latest patch
   ```dockerfile
   FROM python:3.13-slim      # Always pull latest
   ```

2. **Python packages:** Update requirements.txt
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

3. **System packages:** Update in Dockerfile
   ```dockerfile
   RUN apt-get update && apt-get install -y --only-upgrade <package>
   ```

## Logging and Monitoring

### 1. Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_obj)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

### 2. Graceful Shutdown

```python
import signal
import asyncio

async def shutdown_handler(signum, frame):
    logger.info("Received shutdown signal")
    # Close database connections
    # Finish in-flight requests
    exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

## Environment Configuration

### 1. Environment Variable Strategy

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///tasks.db"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
```

### 2. Secrets Management

**Never hardcode secrets:**
```dockerfile
# ❌ Wrong
ENV DATABASE_PASSWORD=secret123

# ✓ Right
# Pass at runtime:
docker run -e DATABASE_PASSWORD=$PASSWORD myimage
# Or use Docker secrets (for swarm mode)
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Health check endpoint implemented
- [ ] Logging configured
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] .dockerignore file created

### Image Building
- [ ] Build succeeds without warnings
- [ ] Image size < 300MB (preferably < 200MB)
- [ ] Runs as non-root user
- [ ] Health check works
- [ ] Security scan passes (no CRITICAL vulnerabilities)

### Configuration
- [ ] All secrets in environment variables (not in code)
- [ ] Database URL points to production database
- [ ] Logging configured for production
- [ ] Resource limits set (memory, CPU)

### Kubernetes/Container Orchestration (if applicable)
- [ ] Readiness probe configured
- [ ] Liveness probe configured
- [ ] Resource requests/limits set
- [ ] Graceful shutdown implemented

## Example: Production-Ready Task API

**Final Dockerfile:**
```dockerfile
# syntax=docker/dockerfile:1

# Builder stage
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install --upgrade pip uv
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

# Production stage
FROM python:3.13-slim
WORKDIR /app

# Install runtime dependencies (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

# Security: Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy dependencies from builder
COPY --from=builder --chown=appuser:appuser \
  /usr/local/lib/python3.13/site-packages \
  /usr/local/lib/python3.13/site-packages

# Copy application
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

# Graceful shutdown with proper signal handling
STOPSIGNAL SIGTERM

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--access-log"]
```

## Key Metrics for Production

### Image Size
```bash
docker images task-api:prod
# SIZE should be < 200MB
```

### Startup Time
```bash
docker run task-api:prod
# Should start in < 10 seconds
```

### Resource Usage
```bash
docker stats
# Monitor CPU and memory while running
# Should stay under allocated limits
```

## Exercises for Phase 3

### Exercise 3.1: Security Hardening
Implement non-root user and health checks in your Dockerfile.

### Exercise 3.2: Multi-Stage Build
Optimize your Dockerfile to use multi-stage builds.

### Exercise 3.3: Security Scanning
Build image and scan for vulnerabilities:
```bash
docker build -t task-api:prod .
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image task-api:prod
```

### Exercise 3.4: Measure Image Size
Compare sizes:
```bash
docker images task-api
# dev version vs prod version
```

## Key Takeaways

✓ **Non-root user** = Security best practice
✓ **Multi-stage builds** = Optimize image size
✓ **Health checks** = Monitor container health
✓ **Layer caching** = Faster builds
✓ **.dockerignore** = Reduce build context
✓ **Vulnerability scanning** = Find security issues
✓ **Environment variables** = Configure securely
✓ **Graceful shutdown** = Clean container termination

## Next Steps

After Phase 3:

1. ✓ Production-ready container image
2. ✓ Security hardened and scanned
3. ✓ Optimized for size and performance
4. ✓ Proper logging and monitoring
5. **Ready for:** Kubernetes deployment or cloud deployment

---

**Phase 3 Complete:** Production readiness mastery!
**Next:** Deploy to `containerizing-applications` for Helm charts or cloud deployment
