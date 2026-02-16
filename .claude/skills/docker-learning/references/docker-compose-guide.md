# Docker Compose Complete Reference Guide

Comprehensive guide to docker-compose for multi-container development.

## Quick Reference

### Installation

```bash
# Already included with Docker Desktop
docker-compose --version
# Docker Compose version 2.x.x
```

### File Format

**File:** `docker-compose.yml` or `docker-compose.yaml`

```yaml
version: '3.8'           # Compose file format version

services:               # Define containers
  service_name:
    image: image:tag    # Or build: .
    ports:
      - "8000:8000"
    environment:
      KEY: value
    volumes:
      - ./local:/container/path
    networks:
      - app-network

volumes:               # Define volumes
  volume_name:

networks:              # Define networks
  app-network:
```

## Complete Services Configuration

### Minimal Service

```yaml
services:
  myapp:
    image: python:3.13
```

### Full Service Configuration

```yaml
services:
  myapp:
    # Image (option 1)
    image: python:3.13

    # OR Build (option 2)
    build: .
    build:
      context: .
      dockerfile: Dockerfile
      args:
        PYTHON_VERSION: 3.13

    # Container name
    container_name: my-container

    # Port mapping
    ports:
      - "8000:8000"           # host:container
      - "127.0.0.1:8001:8000" # host:host_ip:container

    # Expose ports (internal only, no mapping)
    expose:
      - 8000

    # Environment variables
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      DEBUG: "true"
      NODE_ENV: development

    # OR load from file
    env_file: .env
    env_file:
      - .env
      - .env.production

    # Working directory
    working_dir: /app

    # Mount volumes
    volumes:
      - ./src:/app/src              # Bind mount
      - named_volume:/data          # Named volume
      - /var/run/docker.sock:/var/run/docker.sock  # Socket

    # Commands
    command: python main.py
    command:
      - python
      - main.py

    # Entrypoint
    entrypoint: /bin/bash
    entrypoint:
      - /bin/bash
      - -c

    # Networks
    networks:
      - app-network
      - monitoring

    # Depends on
    depends_on:
      - db
      - cache

    # More detailed depends_on with conditions
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

    # Restart policy
    restart: unless-stopped
    # Options: no, always, on-failure, unless-stopped

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    # Logging
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

    # User
    user: "1000:1000"

    # Security options
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

    # Read-only root filesystem
    read_only: true
    tmpfs:
      - /tmp
      - /run

    # Labels
    labels:
      app: myapp
      version: "1.0.0"
```

## Networks

### Default Network

```yaml
services:
  api:
    # Automatically on 'default' network
    image: python:3.13
  db:
    # Also on 'default' network
    image: postgres:16
# Services can reach each other via service name
```

### Custom Network

```yaml
networks:
  app-network:
    driver: bridge
  monitoring-network:
    driver: bridge

services:
  api:
    networks:
      - app-network
  db:
    networks:
      - app-network
  prometheus:
    networks:
      - monitoring-network
# api and db can reach each other
# prometheus isolated from api/db
```

### Network Isolation

```yaml
networks:
  frontend:
  backend:

services:
  web:
    networks:
      - frontend
  api:
    networks:
      - frontend
      - backend
  db:
    networks:
      - backend
# web can only reach api
# api can reach both web and db
# db can only reach api
```

## Volumes

### Named Volume

```yaml
volumes:
  postgres_data:
    # Created and managed by Compose
    # Persists between container restarts

  postgres_data:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
```

### Bind Mount

```yaml
services:
  app:
    volumes:
      - ./local:/app          # Relative path
      - /absolute/local:/app  # Absolute path
      - ${PWD}:/app           # Use environment variable
```

### Volume Permissions

```yaml
services:
  app:
    volumes:
      - ./data:/app/data:ro   # Read-only
      - ./src:/app/src:rw     # Read-write (default)
```

## Environment Variables

### Inline Definition

```yaml
services:
  app:
    environment:
      DATABASE_URL: postgresql://localhost/mydb
      DEBUG: "true"
      LOG_LEVEL: INFO
```

### From File

```yaml
services:
  app:
    env_file: .env
    # .env file in same directory as docker-compose.yml
```

### Multiple Files

```yaml
services:
  app:
    env_file:
      - .env
      - .env.override
      - .env.${ENVIRONMENT}  # Use ${} to reference env vars
```

### Docker Compose Variables

Use `${VARIABLE_NAME}`:

```yaml
# docker-compose.yml
services:
  app:
    image: myapp:${VERSION}
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
```

**In .env file:**
```
VERSION=1.0.0
DB_USER=admin
DB_PASSWORD=secret
DB_NAME=myapp
```

**Or from shell:**
```bash
VERSION=2.0.0 docker-compose up
```

## Common Patterns

### FastAPI + PostgreSQL

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      PYTHONUNBUFFERED: 1
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app
    networks:
      - app-network

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
```

### FastAPI + PostgreSQL + Redis

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      REDIS_URL: redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Multiple Environments

**docker-compose.yml (shared):**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "${PORT}:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
```

**docker-compose.dev.yml (override):**
```yaml
services:
  api:
    volumes:
      - .:/app
    environment:
      DEBUG: "true"
```

**Use:**
```bash
docker-compose up                                    # Uses docker-compose.yml
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Commands Reference

### Lifecycle

| Command | Description |
|---------|-------------|
| `docker-compose up` | Create and start containers |
| `docker-compose up -d` | Start in background |
| `docker-compose stop` | Stop running containers |
| `docker-compose start` | Start stopped containers |
| `docker-compose restart` | Restart all services |
| `docker-compose pause` | Pause services |
| `docker-compose unpause` | Unpause services |
| `docker-compose down` | Stop and remove containers |
| `docker-compose down -v` | Remove containers and volumes |

### Status and Logs

| Command | Description |
|---------|-------------|
| `docker-compose ps` | List services |
| `docker-compose logs` | View logs all services |
| `docker-compose logs -f` | Follow logs all services |
| `docker-compose logs service_name` | Logs for one service |
| `docker-compose logs -f service_name` | Follow one service |
| `docker-compose logs --tail 10` | Last 10 lines |

### Build and Configuration

| Command | Description |
|---------|-------------|
| `docker-compose build` | Build all images |
| `docker-compose build service_name` | Build specific service |
| `docker-compose build --no-cache` | Build without cache |
| `docker-compose config` | Show merged configuration |

### Execute Commands

| Command | Description |
|---------|-------------|
| `docker-compose exec service_name command` | Run command in service |
| `docker-compose exec -it service_name bash` | Interactive shell |
| `docker-compose run --rm service_name command` | Run one-off command |
| `docker-compose run --rm service_name bash` | Run interactive bash |

### Maintenance

| Command | Description |
|---------|-------------|
| `docker-compose images` | List images |
| `docker-compose pull` | Pull latest images |
| `docker-compose push` | Push to registry |
| `docker-compose stats` | Container resource usage |
| `docker-compose events` | Stream events |
| `docker-compose validate` | Validate file |
| `docker-compose version` | Show version |

## Debugging

### View Configuration

```bash
# Show merged configuration
docker-compose config

# Show configuration for one service
docker-compose config --services

# Show specific service config
docker-compose config | grep -A 20 "api:"
```

### Check Status

```bash
# Detailed status
docker-compose ps

# Show only running
docker-compose ps --services --filter "status=running"

# Show container details
docker inspect <container_id>
```

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs api

# Last 50 lines
docker-compose logs --tail=50 api

# With timestamps
docker-compose logs --timestamps api

# Specific time range (if supported)
docker-compose logs api --since 1m  # Last 1 minute
```

### Test Services

```bash
# Execute command in running service
docker-compose exec api curl http://localhost:8000/health

# Test database
docker-compose exec db psql -U user -d mydb -c "SELECT 1;"

# Test Redis
docker-compose exec cache redis-cli ping
```

### Restart Service

```bash
# Restart specific service
docker-compose restart api

# Restart all services
docker-compose restart

# Force rebuild and restart
docker-compose up --build --force-recreate
```

## Best Practices

### 1. Use Named Volumes for Persistence

```yaml
volumes:
  postgres_data:    # Named volume
  # NOT: volume: ["/var/lib/postgresql/data:/data"]

services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### 2. Health Checks

```yaml
services:
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

services:
  api:
    depends_on:
      db:
        condition: service_healthy
```

### 3. Environment Variables

```yaml
# Don't hardcode passwords
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}

# Use .env file or pass at runtime
docker-compose up
# Reads from .env file

PASSWORD=secret docker-compose up
# Override at runtime
```

### 4. Resource Limits

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 5. Override Compose Files

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Troubleshooting

### Compose File Issues

```bash
# Validate file
docker-compose config

# Show merged config
docker-compose config | less

# Specific validation errors
docker-compose up 2>&1 | head -20
```

### Service Issues

```bash
# Check if service is running
docker-compose ps

# Check logs
docker-compose logs service_name

# Test connectivity
docker-compose exec api curl http://db:5432
```

### Network Issues

```bash
# View networks
docker network ls

# Inspect network
docker network inspect <network_id>

# Test from one service to another
docker-compose exec api ping db
docker-compose exec api curl http://db:5432
```

### Volume Issues

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect <volume_name>

# Check disk usage
docker system df
```

## Key Takeaways

✓ `docker-compose.yml` defines multi-container application
✓ `services:` define each container
✓ `networks:` define how services communicate
✓ `volumes:` define persistent storage
✓ `environment:` pass configuration
✓ `depends_on:` control startup order
✓ `healthcheck:` monitor service health
✓ `docker-compose up` starts all services
✓ `docker-compose logs` view output
✓ `docker-compose exec` run commands in services

---

**Last Updated:** 2026-01-20 | **For:** Docker Compose 3.8+
