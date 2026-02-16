# Phase 2: Development Workflows (Weeks 3-5)

Master docker-compose, multi-container orchestration, volumes, and networking for development.

## Mental Model: From Single to Multi-Container

### Phase 1 → Phase 2

**Phase 1 (Single container):**
```bash
docker run -p 8000:8000 task-api:v1
# Your API with SQLite database inside container
# Limitation: Can't easily use separate database
```

**Phase 2 (Multi-container with docker-compose):**
```yaml
services:
  api:
    image: task-api:v1
  db:
    image: postgres:16
```
```bash
docker-compose up
# Two services: API and PostgreSQL
# They communicate via network
# Better separation of concerns
```

### Why Multi-Container?

| Aspect | Single Container | Multi-Container |
|--------|-----------------|-----------------|
| Services | Everything in one | Each service separate |
| Database | SQLite (file-based) | PostgreSQL (production) |
| Scaling | Can't scale database | Can scale each service |
| Development | Realistic | Production-like |
| Updates | Rebuild everything | Update services independently |

## Docker Compose Fundamentals

### What is docker-compose?

A tool to define and run multi-container Docker applications using a YAML file.

**File:** `docker-compose.yml` or `docker-compose.yaml`

**Structure:**
```yaml
version: '3.8'           # API version

services:               # Define each service
  api:
    # Configuration for API service
  db:
    # Configuration for database service

volumes:               # Define shared storage
  postgres_data:
    # Database persistence

networks:              # Define networks (optional, compose creates default)
  # Network configuration
```

### Your Task API with PostgreSQL

**File:** `docker-compose.yml` (in project root)

```yaml
version: '3.8'

services:
  # FastAPI application
  api:
    build: .                          # Build from Dockerfile in current directory
    container_name: task-api          # Container name for reference
    ports:
      - "8000:8000"                   # Map port 8000
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/tasks
      PYTHONUNBUFFERED: 1             # Python output buffering
    depends_on:
      db:
        condition: service_healthy    # Wait for database health check
    volumes:
      - .:/app                        # Mount local code (hot-reload)
    networks:
      - app-network                   # Custom network

  # PostgreSQL database
  db:
    image: postgres:16                # Use official PostgreSQL image
    container_name: task-db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: tasks
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - app-network

volumes:
  postgres_data:                      # Named volume for persistence

networks:
  app-network:                        # Custom network
    driver: bridge
```

## Key Concepts

### 1. Services

Each service = one container definition

```yaml
services:
  api:                    # Service name
    image: python:3.13    # Use existing image
    # OR
    build: .              # Build from Dockerfile
    ports:
      - "8000:8000"       # Port mapping
    environment:
      VAR: value          # Environment variables
    depends_on:
      - db                # Start after db
    volumes:
      - .:/app            # Volume mounts
```

### 2. Networking

Services can communicate using service names!

```yaml
services:
  api:
    environment:
      DATABASE_URL: postgresql://db:5432/tasks
      # Uses service name 'db' as hostname
  db:
    # Accessible from api as 'db:5432'
```

**Docker Compose creates internal network:**
- `api` service can reach `db` at `db:5432`
- `db` service can reach `api` at `api:8000`
- Both isolated from outside (unless exposed with ports)

### 3. Volumes

**Named volume (persists data):**
```yaml
volumes:
  postgres_data:           # Volume definition

services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
      # Syntax: volume_name:container_path
```

**Bind mount (local directory):**
```yaml
services:
  api:
    volumes:
      - .:/app
      # Syntax: local_path:container_path
      # Changes in ./ appear immediately in /app
```

### 4. Environment Variables

```yaml
services:
  api:
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/tasks
      DEBUG: "true"
```

**Access in your Python code:**
```python
import os
database_url = os.getenv("DATABASE_URL")
# Gets: postgresql://user:pass@db:5432/tasks
```

### 5. Health Checks

```yaml
services:
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]  # Command to check health
      interval: 10s                                # Check every 10s
      timeout: 5s                                  # Timeout in 5s
      retries: 5                                   # Max 5 failures before unhealthy
      start_period: 10s                            # Wait 10s before first check
```

### 6. Depends On

```yaml
services:
  api:
    depends_on:
      db:                    # Wait for db service
        condition: service_healthy  # Wait for health check to pass
```

## Docker Compose Commands

### Basic Operations

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up api

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers, volumes, networks
docker-compose down -v

# Restart services
docker-compose restart
```

### Viewing Status

```bash
# List running services
docker-compose ps

# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs api

# Follow logs (tail -f style)
docker-compose logs -f api

# View last 10 lines
docker-compose logs --tail=10 api
```

### Execution

```bash
# Run command in running service
docker-compose exec api ls /app

# Interactive shell
docker-compose exec -it api bash

# Run command without service running (creates temporary container)
docker-compose run --rm api python -c "print('hello')"
```

### Building

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build api

# Build and don't use cache
docker-compose build --no-cache
```

## Real Example: Task API + PostgreSQL

### Step 1: Verify Your Dockerfile

Your `Dockerfile` should work with PostgreSQL:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Update requirements.txt

Add PostgreSQL driver:
```
fastapi>=0.104.1
uvicorn>=0.24.0
sqlmodel>=0.0.14
psycopg2-binary>=2.9.9    # PostgreSQL driver
pydantic>=2.0.0
sqlalchemy>=2.0.0
```

### Step 3: Create docker-compose.yml

Save as `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: task-api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://taskuser:taskpass@db:5432/tasks_db
      PYTHONUNBUFFERED: 1
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app
    networks:
      - app-network
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    container_name: task-db
    environment:
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: taskpass
      POSTGRES_DB: tasks_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### Step 4: Update Your Code

Update `main.py` to use PostgreSQL:

```python
import os
from sqlalchemy import create_engine
from sqlmodel import Session, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./tasks.db"  # Fallback for local development
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "check_same_thread": False
    } if "sqlite" in DATABASE_URL else {}
)
```

### Step 5: Run Multi-Container Setup

```bash
# Navigate to project
cd C:\Users\xpert\OneDrive\Desktop\CLOUD_NATIVE_AI-400\ai-400-project-1

# Start all services
docker-compose up

# In another terminal, verify both are running
docker-compose ps

# Test the API
curl http://localhost:8000/health

# View logs
docker-compose logs -f api
```

### Step 6: Access PostgreSQL

From your Python code, use `db:5432` as hostname:

```python
# In environment variable (docker-compose.yml)
DATABASE_URL: postgresql://taskuser:taskpass@db:5432/tasks_db
                                           ^^  this is the service name
```

From inside api container:
```bash
docker-compose exec api psql -h db -U taskuser -d tasks_db
```

## Best Practices for Development

### 1. Use .dockerignore

Create `.dockerignore` to exclude unnecessary files:

```
__pycache__
*.pyc
.git
.gitignore
.env
.venv
venv/
.pytest_cache
.coverage
*.egg-info
.DS_Store
__pycache__
node_modules
```

This reduces build time and image size.

### 2. Environment Variables Strategy

**Local development (.env file):**
```
DATABASE_URL=postgresql://taskuser:taskpass@db:5432/tasks_db
DEBUG=true
```

**Use in docker-compose:**
```yaml
env_file:
  - .env
```

### 3. Hot-Reload for Development

Mount code as volume:
```yaml
services:
  api:
    volumes:
      - .:/app
```

**Note:** FastAPI auto-reloads when code changes (if DEBUG=true)

### 4. Database Migrations

When changing models, apply migrations:
```bash
# Run alembic migration
docker-compose exec api alembic upgrade head

# Or manually create tables
docker-compose exec api python -c "from main import engine; SQLModel.metadata.create_all(engine)"
```

## Networking Deep Dive

### Service Discovery

```yaml
services:
  api:
    environment:
      # Use service name as hostname
      DB_HOST: db
      DB_PORT: 5432
      # Compose creates DNS entry: db → db container IP
```

### Port Exposure

```yaml
services:
  db:
    ports:
      - "5432:5432"
      # Left (5432) = host port (your machine)
      # Right (5432) = container port (inside container)
      # Accessible from: localhost:5432 (from your machine)
      # Accessible from: db:5432 (from other containers)
```

### Custom Networks

```yaml
networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  api:
    networks:
      - app-network
    # Only containers in app-network can reach api
```

## Troubleshooting Phase 2

### Problem: "db service unhealthy"

**Cause:** Database not starting or health check failing

**Debug:**
```bash
docker-compose logs db
# Look for PostgreSQL startup errors

docker-compose exec db pg_isready -U taskuser
# Test health check manually
```

### Problem: "Cannot connect to database"

**Cause:** Wrong hostname, credentials, or database doesn't exist

**Check:**
```bash
# Verify service is running
docker-compose ps

# Check connection string
echo $DATABASE_URL
# Should be: postgresql://taskuser:taskpass@db:5432/tasks_db

# Test from api container
docker-compose exec api python -c "import os; print(os.getenv('DATABASE_URL'))"
```

### Problem: "Port 8000 already in use"

**Solution:**
```yaml
# In docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

Or kill the process using port 8000.

### Problem: "Volume data lost after docker-compose down"

**Cause:** Not using named volumes, using bind mounts instead

**Fix:**
```yaml
volumes:
  postgres_data:     # Named volume persists

services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Use named volume
```

## Exercises for Phase 2

### Exercise 2.1: Create docker-compose.yml
Create the `docker-compose.yml` file with API and PostgreSQL services.

### Exercise 2.2: Start Multi-Container Stack
```bash
docker-compose up
# Wait for both services to be healthy

docker-compose ps
# Should show both running

curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### Exercise 2.3: Test Database Connection
```bash
# From another terminal
docker-compose exec api python -c "from main import engine; print('Database connected!')"
```

### Exercise 2.4: View Logs
```bash
# See api logs
docker-compose logs api

# Follow db logs
docker-compose logs -f db

# See last 5 lines of both
docker-compose logs --tail=5
```

### Exercise 2.5: Scale Services (Optional)

Create another API instance:
```bash
docker-compose up --scale api=2 db=1
# Creates 2 API containers, 1 database
# (requires load balancer for production)
```

## Key Takeaways

✓ **docker-compose** = Define multi-container setup in YAML
✓ **services** = Each container in your application
✓ **networking** = Services reach each other via service names
✓ **volumes** = Persist data across container restarts
✓ **depends_on** = Control startup order
✓ **environment** = Pass variables to containers
✓ **healthcheck** = Monitor service health
✓ **docker-compose up** = Start all services
✓ **docker-compose logs** = View service output

## Next Steps

After Phase 2:

1. ✓ Can write docker-compose.yml files
2. ✓ Can run multi-container applications
3. ✓ Understand service networks and communication
4. ✓ Use volumes for data persistence
5. **Ready for Phase 3:** Production readiness

---

**Phase 2 Complete:** Multi-container development mastery!
**Next:** `references/phase3-production.md` - Security and optimization
