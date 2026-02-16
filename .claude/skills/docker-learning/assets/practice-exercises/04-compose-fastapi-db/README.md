# Exercise 04: Multi-Container Setup with docker-compose

## Objective

Learn to orchestrate multiple containers using docker-compose. Set up your FastAPI application with a PostgreSQL database and understand service communication.

## What You'll Learn

- Creating docker-compose.yml files
- Multi-container orchestration
- Service networking (how containers talk to each other)
- Volume management for data persistence
- Health checks and depends_on
- Environment variables for configuration

## Getting Started

### Prerequisites

- Docker Desktop installed
- Completed Exercise 03 (basic containerization)
- Your main.py, requirements.txt, and Dockerfile

### Files in This Exercise

```
04-compose-fastapi-db/
├── docker-compose.yml      # Multi-container configuration
├── README.md              # This file
├── Dockerfile             # (copy from exercise 03)
├── main.py                # (copy from project root)
└── requirements.txt       # (copy from project root)
```

## Step 1: Prepare Your Files

Copy necessary files to this directory:

```bash
# From project root
cp main.py .claude/skills/docker-learning/assets/practice-exercises/04-compose-fastapi-db/
cp requirements.txt .claude/skills/docker-learning/assets/practice-exercises/04-compose-fastapi-db/

# Copy Dockerfile from exercise 03
cp .claude/skills/docker-learning/assets/practice-exercises/03-fastapi-container/Dockerfile \
   .claude/skills/docker-learning/assets/practice-exercises/04-compose-fastapi-db/
```

## Step 2: Update requirements.txt

Ensure PostgreSQL driver is included:

```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
sqlalchemy>=2.0.0
pydantic>=2.0.0
psycopg2-binary>=2.9.9
```

Add if missing: `psycopg2-binary>=2.9.9`

## Step 3: Update Your Application

Your `main.py` needs to read DATABASE_URL from environment:

```python
import os
from sqlalchemy import create_engine

# Read database URL from environment, fallback to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./tasks.db"
)

# Create engine (works with both SQLite and PostgreSQL)
engine = create_engine(DATABASE_URL, echo=False)

# ... rest of your code

# Make sure you have a health check endpoint:
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Key points:**
- `os.getenv("DATABASE_URL", "sqlite://...")` reads from docker-compose environment
- The fallback allows running locally without docker-compose
- PostgreSQL connection string: `postgresql://user:pass@host:port/database`

## Step 4: Review docker-compose.yml

Study the provided configuration:

```yaml
version: '3.8'

services:
  api:
    build: .                    # Build from Dockerfile
    environment:
      DATABASE_URL: postgresql://taskuser:taskpass@db:5432/tasks_db
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: taskpass
      POSTGRES_DB: tasks_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser"]
      interval: 10s
```

**Key sections:**
- `services:` - Define each container
- `build: .` - Build API from Dockerfile
- `image: postgres:16-alpine` - Use existing PostgreSQL image
- `environment:` - Pass configuration to containers
- `depends_on:` - Start order and health conditions
- `volumes:` - Persist database data
- `healthcheck:` - Monitor service health

## Step 5: Start Services

Navigate to this exercise directory and start:

```bash
cd .claude/skills/docker-learning/assets/practice-exercises/04-compose-fastapi-db

# Start all services in foreground (you'll see logs)
docker-compose up

# Expected output:
# Creating task-api ... done
# Creating task-db ... done
# task-api    | INFO:     Uvicorn running on http://0.0.0.0:8000
# task-db     | LOG: database system is ready to accept connections
```

**Keep this terminal open!** Both services are running.

## Step 6: Verify Services Are Running

In another terminal:

```bash
# List running services
docker-compose ps

# Expected:
# NAME       IMAGE              STATUS      PORTS
# task-api   task-api:latest    Up 2 mins   0.0.0.0:8000->8000/tcp
# task-db    postgres:16-alpine Up 2 mins   0.0.0.0:5432->5432/tcp
```

## Step 7: Test the API

Test your containerized application with PostgreSQL backend:

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Get all tasks
curl http://localhost:8000/tasks
# Expected: [] (empty list, or existing tasks)

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Docker", "description": "Complete exercise 04"}'

# Get tasks again
curl http://localhost:8000/tasks
# Should show your new task

# Visit in browser
# http://localhost:8000/docs - Swagger UI
# http://localhost:8000/health - Health check
```

## Step 8: View Logs

```bash
# All service logs
docker-compose logs

# Follow all logs
docker-compose logs -f

# Just API logs
docker-compose logs -f api

# Just database logs
docker-compose logs -f db
```

## Step 9: Access the Database

Test database connectivity:

```bash
# Connect to PostgreSQL from host
docker-compose exec db psql -U taskuser -d tasks_db

# Inside psql:
\dt                  # List tables
SELECT * FROM task;  # Query tasks (if table exists)
\q                   # Quit

# Or test connection from API
docker-compose exec api python -c \
  "from main import engine; print('Connected to DB successfully')"
```

## Step 10: Stop Services

```bash
# In the terminal where docker-compose is running
# Press Ctrl+C

# Or in another terminal
docker-compose stop

# Remove containers and keep volumes (for next run)
docker-compose down

# Remove everything including data
docker-compose down -v
```

## Understanding Service Communication

### Network Magic

Docker Compose creates a network where:
- Service `db` is accessible at `db:5432` from the API container
- Service `api` is accessible at `api:8000` from other containers
- Hostname = service name

### How It Works

```
main.py:
  DATABASE_URL = "postgresql://taskuser:taskpass@db:5432/tasks_db"
                                                 ^^  service name
                                                     (Docker DNS resolves to IP)
```

Docker resolves `db` to the PostgreSQL container's IP automatically!

## Data Persistence

### After docker-compose up

- Tasks you create are stored in PostgreSQL
- Data is in the `postgres_data` volume

### After docker-compose down

- Containers are removed
- Data persists in volume (safe!)
- Run `docker-compose up` again - same data

### After docker-compose down -v

- Everything is deleted, including data
- Start fresh next time

## Variations to Try

### Run in Background

```bash
docker-compose up -d
# -d = detached (background)

# View logs
docker-compose logs -f

# Stop
docker-compose stop
```

### Scale Services (optional)

```bash
# Advanced: run multiple API instances
docker-compose up --scale api=2 db=1

# Requires load balancer (not set up here)
```

### Override Ports

Create `docker-compose.override.yml`:
```yaml
services:
  api:
    ports:
      - "8001:8000"  # Use different port
```

Then: `docker-compose up` automatically applies overrides

### Use Different PostgreSQL Version

Edit docker-compose.yml:
```yaml
db:
  image: postgres:15-alpine  # Change version
```

## Success Criteria

You've completed this exercise when:

- ✓ docker-compose up starts both API and database
- ✓ docker-compose ps shows both services running
- ✓ Health endpoint responds: `curl http://localhost:8000/health`
- ✓ Can create tasks via API
- ✓ Tasks persist when restarting containers
- ✓ Can connect to database: `docker-compose exec db psql...`
- ✓ Can view logs for both services
- ✓ Can cleanly stop with Ctrl+C or docker-compose stop

## Troubleshooting

### "db service unhealthy"

**Cause:** PostgreSQL didn't start or health check failing

**Fix:**
```bash
# View database logs
docker-compose logs db

# Check health manually
docker-compose exec db pg_isready -U taskuser
```

### "Cannot connect to database"

**Cause:** Wrong credentials or DATABASE_URL not set

**Fix:**
```python
# In main.py, verify:
DATABASE_URL = os.getenv("DATABASE_URL", "...")
# Should match docker-compose environment

# Check in running container:
docker-compose exec api python -c \
  "import os; print(os.getenv('DATABASE_URL'))"
```

### "Port 8000 already in use"

**Cause:** Another service using port 8000

**Fix:**
```yaml
# In docker-compose.yml
ports:
  - "8001:8000"  # Use different port
```

Then: `curl http://localhost:8001/health`

### "Volume permission denied"

**Cause:** Volume ownership issues (rare)

**Fix:**
```bash
# Stop and remove (keeps volume)
docker-compose down

# Try again
docker-compose up
```

### Slow startup

**Cause:** PostgreSQL initialization takes time

**Fix:** Wait 10+ seconds after `docker-compose up` before testing

## Next Steps

After completing this exercise:

1. ✓ You understand multi-container orchestration
2. ✓ You can use docker-compose for development
3. ✓ You understand service networking
4. ✓ You can persist data with volumes

**Next:** Exercise 05 - Advanced volumes and networking patterns

## Learning Points

- **docker-compose.yml**: Configuration file for multi-container apps
- **services**: Define each container (api, db, etc.)
- **build vs image**: Build from Dockerfile or use existing image
- **environment**: Configuration variables
- **depends_on**: Control startup order
- **healthcheck**: Monitor container health
- **volumes**: Persistent data storage
- **networks**: Service-to-service communication
- **Service naming**: Use service name as hostname
- **docker-compose up**: Start all services
- **docker-compose logs**: View service output
- **docker-compose ps**: List running services

## Additional Resources

- **Phase 2 Reference:** `../../../references/phase2-development.md`
- **docker-compose Guide:** `../../../references/docker-compose-guide.md`
- **FastAPI Integration:** `../../../references/fastapi-integration.md`

---

**Exercise 04 Complete!** You've orchestrated a full development stack! 🎉
