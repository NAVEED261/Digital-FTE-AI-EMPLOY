# Exercise 03: Containerize Your FastAPI Task API

## Objective

Learn to containerize a Python FastAPI application by creating a Dockerfile and running it as a Docker container.

## What You'll Learn

- Creating a Dockerfile for FastAPI applications
- Building Docker images
- Running containers with port mapping
- Testing containerized applications
- Health checks in Docker

## Getting Started

### Prerequisites

- Docker Desktop installed and running
- Python 3.13+
- Your Task Management API (main.py)
- requirements.txt with FastAPI and dependencies

### Files in This Exercise

```
03-fastapi-container/
├── Dockerfile          # Your container blueprint
└── README.md          # This file
```

## Step 1: Prepare Your Code

Ensure you have:

1. **main.py** - Your FastAPI application with Task model
2. **requirements.txt** - Your Python dependencies

Copy these files from your project root to this directory:

```bash
# From project root
cp main.py .claude/skills/docker-learning/assets/practice-exercises/03-fastapi-container/
cp requirements.txt .claude/skills/docker-learning/assets/practice-exercises/03-fastapi-container/
```

Or update the Dockerfile to reference the files in your project root.

## Step 2: Review the Dockerfile

Study the provided `Dockerfile`:

```dockerfile
FROM python:3.13-slim      # Start with Python 3.13
WORKDIR /app               # Set working directory
COPY requirements.txt .    # Copy dependencies list
RUN pip install...         # Install packages
COPY . .                   # Copy your code
EXPOSE 8000                # Document port
CMD ["uvicorn", ...]       # Run the app
```

**Key points:**
- `FROM` sets the base image (Python runtime)
- `WORKDIR` sets `/app` as the working directory
- `COPY requirements.txt` first (won't change often)
- `RUN pip install` installs dependencies
- `COPY . .` copies your application code
- `EXPOSE 8000` documents the port
- `CMD` specifies how to run your app

## Step 3: Build the Image

Navigate to this exercise directory and build:

```bash
cd .claude/skills/docker-learning/assets/practice-exercises/03-fastapi-container

# Build the image
docker build -t task-api:v1 .

# Expected output:
# [1/5] FROM python:3.13-slim
# [2/5] WORKDIR /app
# [3/5] COPY requirements.txt .
# [4/5] RUN pip install...
# [5/5] COPY . .
# Successfully built task-api:v1
```

**Options:**
```bash
# Build with progress
docker build --progress=plain -t task-api:v1 .

# Build without cache (force fresh install)
docker build --no-cache -t task-api:v1 .
```

## Step 4: List Your Image

Verify the image was created:

```bash
docker images

# Look for:
# REPOSITORY   TAG    IMAGE ID      CREATED        SIZE
# task-api     v1     a1b2c3d4e5f6  5 seconds ago  150MB
```

## Step 5: Run the Container

Start your containerized application:

```bash
# Run in foreground (you'll see logs)
docker run -p 8000:8000 task-api:v1

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Keep this terminal open!** Your app is running. Open another terminal for the next steps.

## Step 6: Test the Application

In another terminal, test your containerized app:

```bash
# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Test API documentation
curl http://localhost:8000/docs
# Expected: HTML for Swagger UI (or visit in browser)

# Test task endpoints (example)
curl http://localhost:8000/tasks
# Should return your tasks as JSON
```

**Or in browser:**
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Swagger UI: http://localhost:8000/redoc

## Step 7: View Container Details

In yet another terminal, inspect the running container:

```bash
# List running containers
docker ps

# Shows:
# CONTAINER ID   IMAGE         STATUS      PORTS
# a1b2c3d4e5f6   task-api:v1   Up 2 mins   0.0.0.0:8000->8000/tcp

# View logs
docker logs -f <CONTAINER_ID>

# See the same logs you see in the running terminal
```

## Step 8: Stop the Container

When done testing:

```bash
# In the terminal where the container is running
# Press Ctrl+C to stop it

# Or in another terminal
docker stop <CONTAINER_ID>

# Verify it stopped
docker ps
# Should not show the container anymore
```

## Variations to Try

### Run in Background

```bash
docker run -d -p 8000:8000 --name my-api task-api:v1
# -d = detached (background)
# --name my-api = give it a name

# View logs
docker logs -f my-api

# Stop it
docker stop my-api
```

### Run with Volume Mount

```bash
docker run -v $(pwd):/app -p 8000:8000 task-api:v1
# -v mounts local directory to /app in container
# Changes to local files appear in container
```

### Different Port

```bash
docker run -p 8001:8000 task-api:v1
# Host port 8001 -> Container port 8000
# Access at http://localhost:8001/docs
```

### With Environment Variable

```bash
docker run -e DEBUG=true -p 8000:8000 task-api:v1
# -e sets environment variable
# Access with: os.getenv("DEBUG")
```

## Success Criteria

You've completed this exercise when:

- ✓ Dockerfile builds without errors
- ✓ Image is created: `docker images | grep task-api`
- ✓ Container runs: `docker run -p 8000:8000 task-api:v1`
- ✓ Health endpoint responds: `curl http://localhost:8000/health`
- ✓ API documentation is accessible: `http://localhost:8000/docs`
- ✓ Can create/read/update/delete tasks in container
- ✓ Can stop container cleanly with Ctrl+C

## Troubleshooting

### "docker build" fails with permission denied

**Cause:** Docker Desktop daemon not running

**Fix:**
```bash
# Open Docker Desktop
# Wait 30 seconds for daemon startup
# Try again
```

### "Cannot assign requested address" on port 8000

**Cause:** Port 8000 in use by another process

**Fix:**
```bash
docker run -p 8001:8000 task-api:v1
# Use different port
```

### "No such file or directory: main.py"

**Cause:** main.py not in same directory as Dockerfile

**Fix:**
```bash
# Copy files to exercise directory
cp ../../../../../../main.py .
cp ../../../../../../requirements.txt .

# OR update COPY in Dockerfile:
# COPY ../../../../../../main.py .
```

### Container starts but API not responding

**Cause:** Application error or wrong port

**Fix:**
```bash
# Check logs
docker logs <CONTAINER_ID>

# Look for error messages and fix in main.py
```

### Image size too large (>300MB)

**Cause:** Caching pip packages

**Fix:**
```dockerfile
# Already done in provided Dockerfile:
RUN pip install --no-cache-dir -r requirements.txt
```

## Next Steps

After completing this exercise:

1. ✓ You can containerize Python FastAPI apps
2. ✓ You understand Dockerfile structure
3. ✓ You can build and run containers

**Next:** Move to Exercise 04 - Add PostgreSQL with docker-compose

## Learning Points

- **FROM**: Base image (Python runtime)
- **WORKDIR**: Set container working directory
- **COPY**: Add files to container
- **RUN**: Execute commands during build
- **EXPOSE**: Document container port
- **CMD**: Default command when container starts
- **docker build**: Create image from Dockerfile
- **docker run**: Start container from image
- **Port mapping**: `-p host:container`
- **Health checks**: Monitor container health

## Additional Resources

- **Phase 1 Reference:** `../../../references/phase1-foundation.md`
- **FastAPI Integration:** `../../../references/fastapi-integration.md`
- **Full Dockerfile Reference:** Docker docs (search: "Dockerfile reference")

---

**Exercise 03 Complete!** You've containerized your first FastAPI application! 🎉
