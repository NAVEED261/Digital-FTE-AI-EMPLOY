# FastAPI Docker Integration Guide

Patterns and best practices for containerizing FastAPI applications, using your Task Management API as the reference.

## Your Task API Setup

**Current state:**
- Framework: FastAPI
- Database: SQLite (SQLModel ORM)
- Server: Uvicorn
- File: `main.py` with Task model and CRUD operations
- Endpoints: /docs, /health, /tasks, etc.

## Minimal FastAPI Dockerfile

### Simplest Approach

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t task-api:v1 .
docker run -p 8000:8000 task-api:v1
# Visit: http://localhost:8000/docs
```

## FastAPI-Specific Patterns

### 1. ASGI Application Exposure

FastAPI apps are ASGI applications. Docker should run:

```dockerfile
# Standard pattern
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Breakdown:**
- `uvicorn` = ASGI server
- `main:app` = module:app_variable (from main.py)
- `--host 0.0.0.0` = Listen on all interfaces (required for Docker)
- `--port 8000` = Port inside container

**Alternative (using gunicorn + uvicorn workers):**
```dockerfile
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 2. Port Configuration

**Your FastAPI app:**
```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="Task Management API")

@app.get("/")
async def root():
    return {"message": "Task API"}
```

**Dockerfile:**
```dockerfile
EXPOSE 8000    # Document the port
```

**Run with port mapping:**
```bash
docker run -p 8000:8000 task-api:v1
# -p <host>:<container>
# Access: http://localhost:8000
```

### 3. Environment Variables in FastAPI

**Your app should read from environment:**

```python
import os
from fastapi import FastAPI
from sqlalchemy import create_engine

# Read from environment with fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./tasks.db"
)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize database connection
    pass
```

**In Dockerfile:**
```dockerfile
ENV DATABASE_URL=sqlite:///tasks.db
# Or pass at runtime:
docker run -e DATABASE_URL=postgresql://user:pass@host/db task-api:v1
```

### 4. Health Check Endpoint

**Required for production:**

```python
# In main.py
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "task-api"
    }
```

**In Dockerfile:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1
```

### 5. Startup and Shutdown Events

**Handle container lifecycle:**

```python
import logging

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")
    # Initialize database, caches, etc.
    pass

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
    # Close database connections, cleanup
    pass
```

## Database Integration

### SQLite in Container

**Simple for development:**

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Data persists in container** (lost if container deleted):
```bash
docker run -v $(pwd):/app -p 8000:8000 task-api:v1
# SQLite file: /app/tasks.db (mounted volume)
# Changes appear on your local machine
```

### PostgreSQL with docker-compose

**For multi-container development:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://taskuser:taskpass@db:5432/tasks_db
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: taskpass
      POSTGRES_DB: tasks_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser"]
      interval: 10s

volumes:
  postgres_data:
```

**In main.py:**

```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./tasks.db"
)

# SQLAlchemy handles both SQLite and PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False,
    # SQLite-specific options
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
```

## Logging Configuration

### 1. Unbuffered Output

```dockerfile
ENV PYTHONUNBUFFERED=1
# Forces Python to write logs immediately to stdout
```

**Why:** Docker logs are captured from stdout/stderr. Buffering causes logs to appear delayed.

### 2. Uvicorn Access Logs

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--access-log"]
```

**View logs:**
```bash
docker logs -f container_id
# Shows: 2026-01-20 10:30:45 "GET /health HTTP/1.1" 200
```

### 3. Python Logging Configuration

```python
import logging
import sys

# Configure logging for container
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    logger.info("FastAPI application started")
```

## Static Files and Assets

### Serving Static Files

If your FastAPI app serves static files:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

**In Dockerfile:**
```dockerfile
COPY ./static ./static    # Copy static files
```

**With docker-compose volume:**
```yaml
volumes:
  - ./static:/app/static  # Development hot-reload
```

## CORS Configuration

### Allow Docker Network

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production:**
```python
import os

allow_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

```dockerfile
ENV ALLOWED_ORIGINS="https://example.com,https://app.example.com"
```

## Dependency Management

### requirements.txt for FastAPI

```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

**For PostgreSQL:**
```
psycopg2-binary>=2.9.9
```

**For async database:**
```
asyncpg>=0.29.0
```

### Dockerfile with requirements

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy and install requirements first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Development vs Production

### Development Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Include dev dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY . .

# Auto-reload on code changes
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
```

**Run with hot-reload:**
```bash
docker run -v $(pwd):/app -p 8000:8000 task-api:dev
# Changes to /app/*.py trigger reload
```

### Production Dockerfile

```dockerfile
# Multi-stage build
FROM python:3.13-slim AS builder

WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.13-slim

WORKDIR /app

# Security: non-root user
RUN useradd -m -u 1000 appuser
COPY --from=builder --chown=appuser:appuser \
  /root/.local /home/appuser/.local

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Testing FastAPI in Docker

### Run Tests in Container

```dockerfile
# In Dockerfile.test
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY . .

# Run pytest
CMD ["pytest", "-v"]
```

**Build and run:**
```bash
docker build -f Dockerfile.test -t task-api:test .
docker run --rm task-api:test
# Runs all tests in container
```

**Or in docker-compose:**
```yaml
services:
  tests:
    build:
      context: .
      dockerfile: Dockerfile.test
    volumes:
      - .:/app
```

```bash
docker-compose run --rm tests pytest -v
```

## Performance Optimization

### 1. Uvicorn Workers

**Single worker (default):**
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Multiple workers (for CPU-bound tasks):**
```dockerfile
# With gunicorn
CMD [
  "gunicorn",
  "main:app",
  "--workers", "4",
  "--worker-class", "uvicorn.workers.UvicornWorker",
  "--bind", "0.0.0.0:8000"
]
```

**Calculation:**
```
# workers = (2 × CPU_cores) + 1
# 4-core system: (2 × 4) + 1 = 9 workers
# But start with 4 and monitor
```

### 2. Async Context Management

```python
# Reuse database sessions efficiently
from contextlib import asynccontextmanager

engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global engine
    engine = create_engine(DATABASE_URL)
    yield
    # Shutdown
    engine.dispose()

app = FastAPI(lifespan=lifespan)
```

### 3. Resource Limits in docker-compose

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '0.5'         # Max 50% of 1 CPU
          memory: 512M        # Max 512MB RAM
        reservations:
          cpus: '0.25'        # Minimum 25% CPU
          memory: 256M        # Minimum 256MB RAM
```

## Troubleshooting

### Problem: "Address already in use" error

**Cause:** Port 8000 already in use on your machine

**Solutions:**
```bash
# Use different port in docker
docker run -p 8001:8000 task-api:v1

# Or kill the process using port 8000
# (Advanced, be careful)
```

### Problem: Cannot access http://localhost:8000

**Cause:** Multiple possibilities

**Debug:**
```bash
# Check if container is running
docker ps

# Check logs for errors
docker logs container_id

# Test from inside container
docker exec container_id curl http://127.0.0.1:8000/health
```

### Problem: Slow startup (>30 seconds)

**Cause:** Database migrations, imports, or initialization

**Solutions:**
```python
# Move heavy imports into startup event
@app.on_event("startup")
async def startup():
    # Import here, not at module level
    import heavy_module
```

```dockerfile
# Increase startup timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3
```

### Problem: "ModuleNotFoundError: No module named 'main'"

**Cause:** Wrong WORKDIR or COPY path

**Fix:**
```dockerfile
WORKDIR /app
COPY . .          # Copies everything to /app

# Verify:
# main.py should be at /app/main.py
```

## Complete Example: Task API Containerized

**Project structure:**
```
.
├── main.py              # FastAPI app
├── requirements.txt     # Dependencies
├── Dockerfile           # Production
├── docker-compose.yml   # Development
└── tasks.db             # SQLite (created at runtime)
```

**main.py (minimal):**
```python
from fastapi import FastAPI
from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

engine = create_engine(DATABASE_URL, echo=False)

app = FastAPI(title="Task Management API")

@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ... rest of your endpoints
```

**requirements.txt:**
```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
sqlalchemy>=2.0.0
```

**Dockerfile:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t task-api:latest .
docker run -p 8000:8000 task-api:latest
# Visit: http://localhost:8000/docs
```

## Key Takeaways

✓ **Expose ASGI app:** `CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]`
✓ **Health check:** Implement `/health` endpoint
✓ **Port mapping:** Run on 0.0.0.0 inside container
✓ **Environment variables:** Read from os.getenv()
✓ **Unbuffered output:** Set PYTHONUNBUFFERED=1
✓ **Database:** Handle both SQLite and PostgreSQL
✓ **Startup/shutdown:** Use lifespan for cleanup

## Next Steps

1. Containerize your Task API following patterns above
2. Test with `docker run -p 8000:8000 task-api:latest`
3. Add PostgreSQL with docker-compose
4. Implement health checks and logging
5. Move to Phase 3: Production optimization

---

**Created:** 2026-01-20 | **For:** FastAPI and Docker integration
