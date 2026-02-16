# syntax=docker/dockerfile:1
# Exercise 03: Containerize Your FastAPI Task API
#
# Goal: Create a Dockerfile that packages your Task Management API
#
# Instructions:
# 1. Review this Dockerfile structure
# 2. Make sure your requirements.txt is in the project root
# 3. Build: docker build -t task-api:v1 .
# 4. Run: docker run -p 8000:8000 task-api:v1
# 5. Test: curl http://localhost:8000/health

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
# (do this before copying code for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Document the port your app uses
EXPOSE 8000

# Health check (optional, but recommended)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
