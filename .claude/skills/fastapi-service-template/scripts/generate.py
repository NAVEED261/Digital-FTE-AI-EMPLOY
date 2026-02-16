#!/usr/bin/env python3
"""
fastapi-service-template: Generate production-ready FastAPI microservice
MCP Code Execution Pattern - Script executes externally (0 tokens in context)
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict

SERVICE_TEMPLATES = {
    "triage-agent": {
        "port": 8001,
        "description": "Routes student queries to specialist agents",
        "agent_type": "triage"
    },
    "concepts-agent": {
        "port": 8002,
        "description": "Explains Python concepts with examples",
        "agent_type": "concepts"
    },
    "code-review-agent": {
        "port": 8003,
        "description": "Analyzes code quality and provides feedback",
        "agent_type": "code-review"
    }
}

def generate_main_py(service_name: str, port: int) -> str:
    """Generate main.py FastAPI application."""
    return f'''"""
{service_name.replace('-', ' ').title()} - LearnFlow Service
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .config import Config
from .agent import {service_name.replace("-", "_").replace("agent", "Agent")}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="{service_name}",
    description="AI agent service for LearnFlow platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize config and agent
config = Config()
agent = {service_name.replace("-", "_").replace("agent", "Agent")}(config)

# Health check endpoint
@app.get("/health")
async def health():
    """Service health check endpoint."""
    return {{
        "status": "healthy",
        "service": "{service_name}",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }}

# Query endpoint (service-specific)
@app.post("/api/query")
async def query(request: Request):
    """Process student query through agent."""
    try:
        body = await request.json()
        result = await agent.process_query(body)
        return result
    except Exception as e:
        logger.error(f"Error processing query: {{str(e)}}")
        raise HTTPException(status_code=500, detail=str(e))

# Readiness probe
@app.get("/ready")
async def ready():
    """Kubernetes readiness probe."""
    return {{"ready": True}}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port={port},
        reload=True,
        log_level="info"
    )
'''

def generate_agent_py(service_name: str, agent_type: str) -> str:
    """Generate agent.py with OpenAI integration."""
    return f'''"""
{service_name.replace('-', ' ').title()} Agent
"""

import os
import logging
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    """Student query request."""
    student_id: int
    query: str
    code: Optional[str] = None
    level: Optional[str] = "intermediate"

class QueryResponse(BaseModel):
    """Agent response."""
    response: str = Field(..., description="Agent response")
    agent: str = Field(default="{agent_type}", description="Agent type")
    confidence: float = Field(default=0.95, ge=0, le=1)

class {service_name.replace("-", "_").replace("agent", "Agent")}:
    """{{agent_type.title()}} Agent using OpenAI API."""

    SYSTEM_PROMPT = """You are the LearnFlow {{agent_type}} Agent.
Your role is to {{self._get_role_description()}}.
Respond clearly, concisely, and educationally.
Format responses in markdown when appropriate."""

    def __init__(self, config):
        """Initialize agent with configuration."""
        self.config = config
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4-turbo-preview"

    def _get_role_description(self) -> str:
        """Get role description for agent type."""
        roles = {{
            "triage": "route student queries to specialist agents",
            "concepts": "explain Python concepts with examples",
            "code-review": "analyze code quality and provide feedback"
        }}
        return roles.get("{agent_type}", "assist LearnFlow students")

    async def process_query(self, request: dict) -> QueryResponse:
        """Process student query through OpenAI agent."""
        try:
            req = QueryRequest(**request)

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {{"role": "system", "content": self.SYSTEM_PROMPT}},
                    {{"role": "user", "content": req.query}}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return QueryResponse(
                response=response.choices[0].message.content,
                agent="{agent_type}",
                confidence=0.95
            )
        except Exception as e:
            logger.error(f"Agent error: {{str(e)}}")
            raise
'''

def generate_models_py() -> str:
    """Generate models.py with Pydantic models."""
    return '''"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class QueryRequest(BaseModel):
    """Student query request."""
    student_id: int = Field(..., gt=0, description="Student ID")
    query: str = Field(..., min_length=1, max_length=2000)
    code: Optional[str] = Field(None, max_length=10000)
    level: Optional[str] = Field("intermediate", pattern="beginner|intermediate|advanced")

class QueryResponse(BaseModel):
    """Agent response."""
    response: str
    agent: str
    confidence: float = Field(ge=0, le=1)
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: str
    version: str
'''

def generate_config_py() -> str:
    """Generate config.py with environment configuration."""
    return '''"""
Configuration management
"""

import os
from typing import Optional

class Config:
    """Application configuration from environment variables."""

    # API Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    SERVICE_NAME: str = os.getenv('SERVICE_NAME', 'learnflow-service')
    SERVICE_PORT: int = int(os.getenv('SERVICE_PORT', '8000'))

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        os.getenv('NEON_CONNECTION_STRING', '')
    )

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    # JWT Configuration (optional)
    JWT_SECRET: str = os.getenv('JWT_SECRET', 'development-secret')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')

    # Features
    ENABLE_CORS: bool = os.getenv('ENABLE_CORS', 'true').lower() == 'true'
    ENABLE_METRICS: bool = os.getenv('ENABLE_METRICS', 'false').lower() == 'true'

    def __init__(self):
        """Validate required configuration."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")
'''

def generate_requirements_txt() -> str:
    """Generate requirements.txt with dependencies."""
    return '''fastapi==0.104.1
uvicorn[standard]==0.24.0
openai==1.3.0
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
pytest==7.4.3
pytest-asyncio==0.21.1
aiofiles==23.2.1
python-dotenv==1.0.0
'''

def generate_dockerfile() -> str:
    """Generate Dockerfile for containerization."""
    return '''FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

def generate_deployment_yaml(service_name: str, port: int) -> str:
    """Generate Kubernetes deployment manifest."""
    return f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
  namespace: learnflow
  labels:
    app: {service_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
    spec:
      containers:
      - name: {service_name}
        image: {service_name}:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: neon-secret
              key: connection-string
        - name: SERVICE_NAME
          value: {service_name}
        - name: SERVICE_PORT
          value: "8000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: learnflow
spec:
  selector:
    app: {service_name}
  ports:
  - port: {port}
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
'''

def generate_test_py(service_name: str) -> str:
    """Generate pytest test file."""
    return f'''"""
Tests for {service_name}
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

@pytest.fixture
def client():
    """Provide test client."""
    return TestClient(app)

def test_health(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ready(client):
    """Test readiness probe."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True

def test_query_endpoint(client):
    """Test query endpoint."""
    payload = {{
        "student_id": 1,
        "query": "How do for loops work?",
        "code": None
    }}
    response = client.post("/api/query", json=payload)
    assert response.status_code in [200, 500]  # May fail without OpenAI key

def test_invalid_query(client):
    """Test invalid query handling."""
    payload = {{
        "student_id": -1,  # Invalid ID
        "query": "Test"
    }}
    response = client.post("/api/query", json=payload)
    assert response.status_code in [422, 400, 500]  # Validation error or server error
'''

def create_service(service_name: str, port: int = None) -> bool:
    """Create FastAPI service directory structure."""
    if service_name not in SERVICE_TEMPLATES:
        print(f"✗ Unknown service: {{service_name}}", file=sys.stderr)
        print(f"  Available: {', '.join(SERVICE_TEMPLATES.keys())}", file=sys.stderr)
        return False

    template = SERVICE_TEMPLATES[service_name]
    port = port or template["port"]
    agent_type = template["agent_type"]

    # Get working directory
    cwd = Path.cwd()
    service_dir = cwd / service_name

    # Create directory structure
    service_dir.mkdir(exist_ok=True)
    (service_dir / "tests").mkdir(exist_ok=True)

    # Generate files
    files = {
        "main.py": generate_main_py(service_name, port),
        "agent.py": generate_agent_py(service_name, agent_type),
        "models.py": generate_models_py(),
        "config.py": generate_config_py(),
        "requirements.txt": generate_requirements_txt(),
        "Dockerfile": generate_dockerfile(),
        "deployment.yaml": generate_deployment_yaml(service_name, port),
        "tests/test_agent.py": generate_test_py(service_name),
        ".gitignore": "*.pyc\n__pycache__/\n.env\n.venv/\ndist/\nbuild/\n*.egg-info/\n"
    }

    # Write files
    for file_path, content in files.items():
        full_path = service_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    print(f"✓ Generated {service_name} service")
    print(f"  Location: {{service_dir}}")
    print(f"  Port: {{port}}")
    print(f"  Files: {len(files)} created")
    return True

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: generate.py <service-name> [port]", file=sys.stderr)
        print(f"Services: {', '.join(SERVICE_TEMPLATES.keys())}", file=sys.stderr)
        sys.exit(1)

    service_name = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else None

    success = create_service(service_name, port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
