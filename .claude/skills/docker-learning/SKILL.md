# docker-learning Skill

Comprehensive Docker learning system covering beginner to advanced concepts, using your FastAPI Task Management API as the learning vehicle.

## Quick Start

**1. Verify Docker installation:**
```bash
python .claude/skills/docker-learning/scripts/verify.py
```

**2. Start learning:**
Use the `docker-learning-tutor` agent:
```
"I want to learn Docker from scratch"
"Help me understand containers"
"How do I containerize my FastAPI app?"
```

**3. Complete exercises:**
Navigate to `.claude/skills/docker-learning/assets/practice-exercises/` and follow progressive exercises.

## Skill Structure

```
docker-learning/
├── SKILL.md                           # This file - quick reference
├── references/                        # Deep learning materials
│   ├── windows-installation.md        # Windows 10/11 setup guide
│   ├── phase1-foundation.md           # Containers, images, basic Dockerfile
│   ├── phase2-development.md          # docker-compose, volumes, networking
│   ├── phase3-production.md           # Security, optimization, K8s intro
│   ├── fastapi-integration.md         # Containerizing Python web apps
│   ├── docker-compose-guide.md        # Complete docker-compose reference
│   ├── networking-explained.md        # Container networking deep dive
│   ├── volumes-and-storage.md         # Data persistence patterns
│   └── troubleshooting-guide.md       # Common errors and solutions
├── scripts/                           # Utility scripts
│   ├── verify.py                      # Verify Docker installation
│   ├── dockerfile-analyzer.py         # Analyze Dockerfile best practices
│   └── practice-validator.py          # Validate practice exercises
└── assets/practice-exercises/         # Hands-on exercises
    ├── 01-basic-dockerfile/           # Your first Dockerfile
    ├── 02-multi-stage-build/          # Optimize with multi-stage
    ├── 03-fastapi-container/          # Containerize your Task API (main.py)
    ├── 04-compose-fastapi-db/         # Add PostgreSQL with docker-compose
    ├── 05-volumes-persistence/        # Data persistence
    └── 06-production-ready/           # Security hardening
```

## Learning Path

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Understand containers and build basic Dockerfile

**Key Concepts:**
- Containers vs VMs (lightweight process isolation)
- Docker architecture (client, daemon, registry)
- Images vs Containers (blueprint vs running instance)
- Basic commands: `docker run`, `docker ps`, `docker logs`, `docker exec`
- Writing a basic Dockerfile

**Your First Dockerfile:**
```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Exercises:**
- 01-basic-dockerfile: Build your first container
- 02-multi-stage-build: Optimize image size

**Checkpoint:** Can you containerize Task API and access it via http://localhost:8000/docs?

### Phase 2: Development (Weeks 3-5)
**Goal:** Use Docker for full-stack development with docker-compose

**Key Concepts:**
- Multi-stage builds for optimization
- docker-compose orchestration
- Volumes for data persistence and hot-reload
- Networks for service communication
- Environment variables and .env files

**Multi-Container Setup Example:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/tasks
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: tasks
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s

volumes:
  postgres_data:
```

**Exercises:**
- 03-fastapi-container: Containerize Task API
- 04-compose-fastapi-db: Run Task API + PostgreSQL
- 05-volumes-persistence: Implement data persistence

**Checkpoint:** Can you run `docker-compose up` and access both API and database?

### Phase 3: Production (Weeks 6+)
**Goal:** Build secure, optimized containers for deployment

**Key Concepts:**
- Security: non-root users, minimal base images
- Health checks and restart policies
- Image optimization (multi-stage, .dockerignore)
- Container security scanning
- Kubernetes concepts introduction

**Production-Ready Pattern:**
```dockerfile
# syntax=docker/dockerfile:1

# Builder stage
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

# Production stage
FROM python:3.13-slim
WORKDIR /app

# Security: non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Exercise:**
- 06-production-ready: Security hardening of Task API container

**Checkpoint:** Can you build a container <200MB with security scanning?

**Graduation:** Ready for `containerizing-applications` skill (existing)

## Key Concepts Quick Reference

### Container vs VM
| Aspect | Container | VM |
|--------|-----------|-----|
| Size | 10-100 MB | 1-5 GB |
| Startup | Seconds | Minutes |
| Isolation | Process-level | Full OS |
| Resource use | Minimal | High |
| Use case | Development, deployment | Legacy apps |

### Dockerfile Instructions
```dockerfile
FROM image             # Base image (required, first)
WORKDIR /path         # Set working directory
COPY src dest         # Copy from host to container
RUN command           # Execute command in layer
ENV KEY value         # Set environment variable
EXPOSE 8000           # Document exposed ports
USER appuser          # Set running user
CMD ["cmd"]           # Default container command
HEALTHCHECK ...       # Define health check
```

### Docker Commands Cheat Sheet
```bash
# Image operations
docker build -t name:tag .           # Build image
docker images                        # List images
docker rmi image_id                  # Remove image
docker tag old_name new_name         # Tag image

# Container operations
docker run -p 8000:8000 image:tag    # Run container
docker ps                            # List running containers
docker ps -a                         # List all containers
docker logs container_id             # View container logs
docker exec -it container_id bash    # Enter container shell
docker stop container_id             # Stop running container
docker rm container_id               # Remove container

# docker-compose
docker-compose up                    # Start services
docker-compose up -d                 # Start in background
docker-compose logs -f               # View logs
docker-compose ps                    # List services
docker-compose down                  # Stop and remove services
```

### Common Patterns

**Health Check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1
```

**Non-Root User (Security):**
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

**Multi-Stage Build (Optimization):**
```dockerfile
FROM python:3.13-slim AS builder
# Build stage
RUN pip install -r requirements.txt

FROM python:3.13-slim
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
# Production stage
```

**Volume Mount for Development:**
```bash
docker run -v $(pwd):/app -p 8000:8000 task-api:latest
# Changes to local files reflected immediately
```

## FastAPI Task API Integration

Your containerization journey uses the real Task Management API:

**File:** `main.py` (Task model, CRUD operations, SQLite database)

**Current endpoints:**
- `GET /docs` - Interactive API documentation
- `GET /health` - Health check endpoint
- `POST /tasks` - Create task
- `GET /tasks` - List tasks
- `GET /tasks/{id}` - Get task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

**Docker phases:**
1. **Phase 1:** Run with SQLite inside container
2. **Phase 2:** Add PostgreSQL via docker-compose
3. **Phase 3:** Security hardening and optimization

## Utility Scripts

### verify.py - Verify Docker Installation
```bash
python .claude/skills/docker-learning/scripts/verify.py
```

Checks:
- Docker installed (version 24.0+)
- Docker daemon running
- docker-compose available
- WSL 2 enabled (Windows)
- Container runtime healthy

### dockerfile-analyzer.py - Best Practices Analysis
```bash
python .claude/skills/docker-learning/scripts/dockerfile-analyzer.py Dockerfile
```

Reports:
- Syntax directive presence
- Base image choice
- Security (USER directive)
- Health checks
- Cache optimization

### practice-validator.py - Exercise Validation
```bash
python .claude/skills/docker-learning/scripts/practice-validator.py 03-fastapi-container
```

Validates:
- Dockerfile exists
- Required instructions present
- Builds successfully
- Runs without errors

## Common Windows Issues & Solutions

**Issue:** WSL 2 not enabled
**Solution:** See `references/windows-installation.md` for WSL 2 setup

**Issue:** File path issues (C:\ to /c/)
**Solution:** Docker Desktop handles mapping automatically; use forward slashes

**Issue:** Line ending issues (CRLF vs LF)
**Solution:** Set `core.autocrlf=input` in git config for Dockerfile

**Issue:** Permission denied running docker
**Solution:** Add user to docker group (see Windows setup guide)

## Next Steps

1. **Read:** `references/windows-installation.md` (complete Windows setup)
2. **Verify:** Run `scripts/verify.py` to confirm Docker installation
3. **Start Phase 1:** Ask docker-learning-tutor "I want to learn Docker"
4. **Complete exercises:** 01 → 02 → 03 → 04 → 05 → 06
5. **Advance:** Graduate to `containerizing-applications` skill for Helm/Kubernetes

## Learning Resources

- **References:** 9 detailed guides covering all aspects
- **Exercises:** 6 progressive, hands-on practice exercises
- **Scripts:** 3 utility scripts for verification and validation
- **Tutor:** Interactive `docker-learning-tutor` agent for guidance
- **Your Project:** Real Task Management API for learning

## Success Metrics

You're ready for the next level when you can:
- ✓ Write Dockerfile from scratch without reference
- ✓ Optimize image size using multi-stage builds
- ✓ Use docker-compose for multi-service development
- ✓ Implement volumes and networks correctly
- ✓ Explain container security concepts
- ✓ Troubleshoot common Docker errors
- ✓ Deploy containerized app to cloud

## Integration with Existing Skills

**Learning progression:**
```
docker-learning (Phase 1-2: Beginner → Intermediate)
    ↓
docker-learning (Phase 3) + containerizing-applications (Advanced)
    ↓
deploying-cloud-k8s or operating-k8s-local (Kubernetes)
```

**Related skills:**
- `containerizing-applications` - Advanced production patterns
- `scaffolding-fastapi-dapr` - Microservices architecture
- `deploying-postgres-k8s` - Production database setup
- `operating-k8s-local` - Local Kubernetes development

---

**Created by:** Claude Code | **Last Updated:** 2026-01-20
