# Exercise 05: Volumes and Data Persistence

## Overview

Learn to use volumes for data persistence across container restarts.

## Objective

Implement named volumes and bind mounts in docker-compose to persist application data.

## What You'll Learn

- Named volumes vs bind mounts
- Data persistence strategies
- Volume permissions and ownership
- Data backup and migration

## Instructions

1. **Ask the docker-learning-tutor agent:**
   ```
   "I want to learn Exercise 05: Volumes and persistence"
   ```

2. **Follow the guided walkthrough:**
   - Start with Exercise 04 docker-compose setup
   - Add named volumes
   - Test data persistence across restarts
   - Explore bind mounts for development

3. **Success criteria:**
   - ✓ Create a task in the API
   - ✓ Stop containers with docker-compose down
   - ✓ Start containers again with docker-compose up
   - ✓ Task still exists (persisted!)

## Volume Types

**Named Volumes (Production):**
```yaml
volumes:
  postgres_data:

services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

**Bind Mounts (Development):**
```yaml
services:
  api:
    volumes:
      - ./src:/app/src  # Local directory -> container
```

## Testing Persistence

```bash
# Create data
docker-compose up -d
curl -X POST http://localhost:8000/tasks -d ...

# Verify
curl http://localhost:8000/tasks

# Stop
docker-compose down

# Start again
docker-compose up -d

# Data should still exist!
curl http://localhost:8000/tasks
```

## Next Steps

After completing:
- Move to Exercise 06: Production hardening
- Learn advanced networking patterns

## Need Help?

Ask the docker-learning-tutor agent:
- "How do volumes work?"
- "Named volumes vs bind mounts?"
- "Why did my data disappear?"

---

**Phase:** Development (Week 4) | **Difficulty:** Intermediate
