# Exercise 02: Multi-Stage Builds

## Overview

Learn to optimize Dockerfile using multi-stage builds to reduce image size.

## Objective

Create a multi-stage Dockerfile that separates build and runtime stages.

## What You'll Learn

- Multi-stage build patterns
- Image size optimization
- Reducing final image footprint
- Understanding build vs runtime dependencies

## Instructions

1. **Ask the docker-learning-tutor agent:**
   ```
   "I want to learn Exercise 02: Multi-stage builds"
   ```

2. **Follow the guided walkthrough:**
   - Copy your Dockerfile from Exercise 01
   - Restructure as multi-stage build
   - Compare image sizes (before vs after)
   - Understand layer separation

3. **Success criteria:**
   - ✓ Dockerfile has 2+ FROM statements
   - ✓ Uses COPY --from= to copy from builder stage
   - ✓ Final image significantly smaller than Exercise 01
   - ✓ Container still runs correctly

## Pattern

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
RUN pip install -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim
COPY --from=builder /usr/local/lib /usr/local/lib
COPY . .
CMD ["python", "main.py"]
```

## Next Steps

After completing:
- Move to Exercise 03: Containerize your Task API
- Compare sizes: `docker images`

## Need Help?

Ask the docker-learning-tutor agent:
- "Explain multi-stage builds"
- "How do I use COPY --from="
- "Why is my image still large?"

---

**Phase:** Foundation (Week 2) | **Difficulty:** Beginner-Intermediate
