# Phase 1: Docker Foundation (Weeks 1-2)

Master the fundamental concepts of Docker: containers, images, and how to build your first Dockerfile.

## Mental Model: Containers Explained

### What is a Container?

Think of a Docker container like a lightweight box containing everything your application needs to run:
- Application code
- Runtime (Python 3.13)
- Dependencies (libraries)
- Configuration
- System libraries needed

**Key difference from virtual machines:**
- VM: Full operating system + application (1-5 GB each)
- Container: Just application + minimal OS layer (10-100 MB)

### Docker Architecture

```
Your Computer (Windows)
└── Docker Desktop
    ├── WSL 2 (Linux kernel)
    └── Docker Daemon
        ├── Image 1 (blueprint)
        ├── Image 2 (blueprint)
        └── Containers (running instances)
            ├── Container 1 (Task API)
            └── Container 2 (Database)
```

**Key Components:**
- **Docker Client:** Commands you run (`docker run`, `docker build`)
- **Docker Daemon:** Runs in background, manages containers
- **Docker Registry:** Docker Hub, stores images for sharing
- **Images:** Blueprints (like a recipe)
- **Containers:** Running instances (like a meal made from recipe)

## Core Concepts

### 1. Images vs Containers

**Image (Blueprint):**
```
FROM python:3.13-slim
RUN pip install fastapi
COPY main.py .
CMD ["python", "main.py"]
```
- Static, doesn't change
- Stored on disk
- Can be shared
- Made of layers

**Container (Running Instance):**
```
├── Read-only image layers
└── Writable container layer (changes here)
```
- Running process
- Uses memory
- Changes are isolated
- Can be started/stopped
- Can be deleted (changes lost)

### 2. Layers and Caching

Every line in a Dockerfile creates a layer:

```dockerfile
FROM python:3.13-slim         # Layer 1 (base image)
RUN pip install fastapi       # Layer 2 (dependencies)
COPY main.py .                # Layer 3 (code)
```

**Image size = Sum of all layers**

**Caching:** If you change line 3, Docker rebuilds layers 3+ but reuses layers 1-2 (faster!)

**Optimization:** Put lines that change rarely at the top
```dockerfile
FROM python:3.13-slim         # Rarely changes
RUN pip install fastapi       # Sometimes changes
COPY main.py .                # Often changes (local edits)
```

### 3. Ports and Networking

**Exposing ports:**
```dockerfile
EXPOSE 8000  # Document that app uses port 8000
```

**Port mapping (when running):**
```bash
docker run -p 8000:8000 task-api
# Syntax: -p <host-port>:<container-port>
# Host port 8000 → Container port 8000
# Access: http://localhost:8000
```

**Multiple ports:**
```bash
docker run -p 8000:8000 -p 5432:5432 my-app
# Port 8000: FastAPI
# Port 5432: PostgreSQL
```

## Your First Dockerfile

### Simple Dockerfile for Task API

Create: `Dockerfile` (in your project root)

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

**Line by line:**
- `FROM python:3.13-slim` - Start with Python 3.13 (slim = smaller size)
- `WORKDIR /app` - Set working directory (like `cd /app`)
- `COPY requirements.txt .` - Copy requirements to container
- `RUN pip install...` - Install Python dependencies
- `COPY . .` - Copy your code to container
- `EXPOSE 8000` - Document that app listens on port 8000
- `CMD [...]` - Default command to run

### Building Your Image

```bash
# Navigate to your project
cd C:\Users\xpert\OneDrive\Desktop\CLOUD_NATIVE_AI-400\ai-400-project-1

# Build the image
docker build -t task-api:v1 .
# -t = tag (name:version)
# . = build context (current directory)
```

Expected output:
```
[1/5] FROM python:3.13-slim          # Pulling base image
[2/5] WORKDIR /app                   # Creating directory
[3/5] COPY requirements.txt .         # Copying file
[4/5] RUN pip install...             # Installing packages
[5/5] COPY . .                        # Copying code

Successfully built task-api:v1
```

### Running Your Container

```bash
# Run the container
docker run -p 8000:8000 task-api:v1

# In another terminal, test it:
curl http://localhost:8000/docs
# Should see Swagger UI

curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

**Control flow:**
- Keep the above terminal running
- In another terminal, you can run curl/browser commands
- `Ctrl+C` in the container terminal stops it

### Viewing Running Containers

In another terminal:
```bash
docker ps
# Shows: CONTAINER ID, IMAGE, STATUS, PORTS

# Example output:
# CONTAINER ID   IMAGE           STATUS      PORTS
# a1b2c3d4e5f6   task-api:v1     Up 2 mins   0.0.0.0:8000->8000/tcp
```

## Essential Docker Commands

### Building Images

```bash
# Build from Dockerfile in current directory
docker build -t myimage:v1 .

# Build from specific Dockerfile
docker build -f Dockerfile.prod -t myimage:prod .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.13 -t myimage .
```

### Running Containers

```bash
# Run in foreground (you see logs)
docker run -p 8000:8000 task-api:v1

# Run in background (detached)
docker run -d -p 8000:8000 task-api:v1

# Run with name
docker run -d --name my-api -p 8000:8000 task-api:v1

# Run with environment variable
docker run -e DATABASE_URL="sqlite:///tasks.db" task-api:v1

# Run interactively (enter shell)
docker run -it ubuntu bash
```

### Viewing Containers and Images

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List images
docker images

# View container details
docker inspect container_id

# View image details
docker inspect image_id
```

### Container Lifecycle

```bash
# View logs
docker logs container_id
docker logs -f container_id        # Follow (tail -f)
docker logs --tail 10 container_id # Last 10 lines

# Stop running container
docker stop container_id

# Start stopped container
docker start container_id

# Remove container
docker rm container_id

# Remove image
docker rmi image_id

# Execute command in running container
docker exec container_id ps aux
docker exec -it container_id bash  # Interactive shell
```

### Cleaning Up

```bash
# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune

# Remove all unused objects (containers, images, volumes)
docker system prune

# Remove everything (be careful!)
docker system prune --all
```

## Common Patterns

### Pattern 1: Health Checks

Add health check to Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1
```

Check health:
```bash
docker ps
# STATUS shows: "Up 2 minutes (healthy)" or "Up 2 minutes (unhealthy)"
```

### Pattern 2: Tagging Images

```bash
# Tag image with version
docker build -t task-api:v1.0.0 .
docker build -t task-api:latest .

# Tag existing image
docker tag task-api:v1.0.0 task-api:stable

# Multiple tags from one build
docker build -t task-api:v1.0.0 -t task-api:latest -t task-api:stable .
```

### Pattern 3: Environment Variables

**In Dockerfile:**
```dockerfile
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///tasks.db
```

**At runtime:**
```bash
docker run -e DATABASE_URL="sqlite:///tasks.db" task-api:v1
```

### Pattern 4: Volumes (Basic)

**Mount local directory to container:**
```bash
# Map current directory to /app in container
docker run -v $(pwd):/app -p 8000:8000 task-api:v1

# Any files you change locally appear immediately in container
```

## Troubleshooting Phase 1

### Problem: "No such file or directory: 'main.py'"

**Cause:** Dockerfile is in wrong directory or COPY paths are incorrect

**Check:**
```bash
# Verify you're in project root
ls main.py requirements.txt

# Fix: Edit Dockerfile COPY lines if files are in subdirectory
COPY src/main.py .  # If main.py is in src/
```

### Problem: "pip install failed"

**Cause:** Package name typo or incompatible version

**Check:**
```bash
# Build with verbose output
docker build --progress=plain -t task-api:v1 .

# Check requirements.txt for typos
cat requirements.txt
```

### Problem: "Cannot assign requested address" on port 8000

**Cause:** Port already in use by another process

**Solutions:**
```bash
# Kill other process using port 8000
# Option 1: Use different port
docker run -p 8001:8000 task-api:v1

# Option 2: Find and kill process using 8000
# (Advanced, use with caution)
```

### Problem: Container exits immediately

**Cause:** Application crashed or exited

**Debug:**
```bash
docker run -it task-api:v1 bash
# You're now inside the container, can run commands manually
# Try: python main.py
# See what error occurs
```

## Learning Exercises

### Exercise 1.1: Build Your First Image
```bash
# Navigate to your project
cd C:\Users\xpert\OneDrive\Desktop\CLOUD_NATIVE_AI-400\ai-400-project-1

# Build the image
docker build -t task-api:v1 .

# Verify it was created
docker images | grep task-api
```

**Expected:** Image `task-api:v1` appears in list

### Exercise 1.2: Run Your Container
```bash
# Run the container
docker run -p 8000:8000 task-api:v1

# In another terminal, test endpoints
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

curl http://localhost:8000/docs
# Should return HTML (Swagger UI)
```

**Expected:** API responds with health status and Swagger UI

### Exercise 1.3: View Logs
```bash
# In the running container terminal:
# You should see logs like:
# INFO:     Uvicorn running on http://0.0.0.0:8000

# Press Ctrl+C to stop container
```

**Expected:** See startup logs, container stops cleanly

### Exercise 1.4: Inspect Container
```bash
# In another terminal while container runs:
docker ps
# Note the CONTAINER ID

docker logs <CONTAINER_ID>
# Should show same logs you saw in terminal

docker exec <CONTAINER_ID> ls /app
# Should list files in container /app directory
```

**Expected:** Can view logs and list files in container

## Key Takeaways

✓ **Container** = Lightweight application package
✓ **Image** = Blueprint (Dockerfile) → Built image
✓ **Dockerfile** = Instructions to build image (like recipe)
✓ **`docker build`** = Create image from Dockerfile
✓ **`docker run`** = Start container from image
✓ **`docker ps`** = See running containers
✓ **`docker logs`** = View container output
✓ **Port mapping** = `-p host:container` connects ports
✓ **Layers** = Each Dockerfile line creates a layer (affects size)
✓ **Caching** = Unchanged layers rebuild instantly

## Next Steps

After completing Phase 1 exercises:

1. ✓ Can build a Dockerfile from scratch
2. ✓ Can run container and access it via browser
3. ✓ Can view logs and inspect containers
4. ✓ Understand image vs container vs Dockerfile
5. **Ready for Phase 2:** Multi-container with docker-compose

---

**Phase 1 Complete:** You understand Docker fundamentals!
**Next:** `references/phase2-development.md` - docker-compose and multi-container orchestration
