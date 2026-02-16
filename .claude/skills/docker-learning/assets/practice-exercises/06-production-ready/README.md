# Exercise 06: Production-Ready Hardening

## Overview

Learn to build secure, optimized containers for production deployment.

## Objective

Implement security best practices and performance optimizations in your Dockerfile.

## What You'll Learn

- Running containers as non-root user
- Multi-stage build optimization
- Security vulnerability scanning
- Health checks and graceful shutdown
- Image size optimization
- Production configuration patterns

## Instructions

1. **Ask the docker-learning-tutor agent:**
   ```
   "I want to learn Exercise 06: Production hardening"
   ```

2. **Follow the guided walkthrough:**
   - Start with your Task API Dockerfile
   - Add non-root user
   - Implement multi-stage build
   - Add health checks
   - Scan for vulnerabilities
   - Optimize image size

3. **Success criteria:**
   - ✓ Dockerfile uses non-root user (uid != 0)
   - ✓ Multi-stage build present
   - ✓ Health check implemented
   - ✓ Image size < 200MB
   - ✓ Vulnerability scan passes (no CRITICAL)
   - ✓ Container runs cleanly

## Production Dockerfile Pattern

```dockerfile
# syntax=docker/dockerfile:1

# Builder
FROM python:3.13-slim AS builder
RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --system --no-cache

# Runtime
FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /usr/local/lib /usr/local/lib
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Verification

```bash
# Build
docker build -t task-api:prod .

# Check size
docker images task-api:prod
# Should be < 200MB

# Check user
docker run --rm task-api:prod id
# Should NOT be uid=0 (root)

# Scan vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image task-api:prod
```

## Next Steps

After completing:
- You're ready for production deployment!
- Graduate to containerizing-applications skill
- Learn Kubernetes or cloud deployment
- Deploy to production environment

## Need Help?

Ask the docker-learning-tutor agent:
- "How do I run as non-root user?"
- "How do I scan for vulnerabilities?"
- "Why is my image so large?"
- "What's a healthcheck?"

---

**Phase:** Production (Week 6+) | **Difficulty:** Advanced

## Congratulations! 🎉

You've completed all Docker learning exercises and are ready for production deployment!
