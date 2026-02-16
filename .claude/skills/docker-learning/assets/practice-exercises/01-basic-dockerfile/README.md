# Exercise 01: Your First Dockerfile

## Overview

Create your first Dockerfile from scratch for a simple Python application.

## Objective

Learn the basic structure of a Dockerfile and how to containerize a simple application.

## What You'll Learn

- Dockerfile syntax (FROM, WORKDIR, COPY, RUN, CMD)
- Building images
- Running containers
- Basic debugging

## Instructions

1. **Ask the docker-learning-tutor agent:**
   ```
   "I want to start Exercise 01: Your First Dockerfile"
   ```

2. **Follow the guided walkthrough:**
   - Create a simple Python script
   - Write a Dockerfile from scratch
   - Build the image
   - Run it as a container
   - Test the output

3. **Success criteria:**
   - ✓ Dockerfile builds successfully
   - ✓ Container runs without errors
   - ✓ Output is visible in logs

## Example Solution

Your Dockerfile might look like:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY . .

CMD ["python", "main.py"]
```

## Next Steps

After completing:
- Move to Exercise 02: Multi-stage builds
- Or ask the tutor for clarification

## Need Help?

Ask the docker-learning-tutor agent:
- "Walk me through Exercise 01"
- "I'm stuck on creating a Dockerfile"
- "My container isn't running"

---

**Phase:** Foundation (Week 1) | **Difficulty:** Beginner
