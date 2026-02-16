# FastAPI Production Patterns

## Service Template

```python
# main.py - FastAPI microservice boilerplate
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
import json
from uuid import uuid4
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
SERVICE_NAME = os.getenv("SERVICE_NAME", "api-service")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
SHUTDOWN_TIMEOUT = int(os.getenv("SHUTDOWN_TIMEOUT", 30))

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

# Graceful shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"{SERVICE_NAME} starting up")
    yield
    # Shutdown - wait for pending requests
    logger.info(f"{SERVICE_NAME} shutting down, waiting {SHUTDOWN_TIMEOUT}s")
    await asyncio.sleep(SHUTDOWN_TIMEOUT)
    logger.info(f"{SERVICE_NAME} shutdown complete")

app = FastAPI(
    title=SERVICE_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# Middleware for trace IDs
@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid4()))
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

# Structured logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    log_data = {
        "timestamp": time.time(),
        "service": SERVICE_NAME,
        "trace_id": request.state.trace_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": int(duration * 1000),
        "client": request.client.host if request.client else None
    }
    logger.info(json.dumps(log_data))
    return response

# Health checks
@app.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe - is the service running?"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe - is the service ready to handle traffic?"""
    try:
        # Check database connectivity
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")

# Metrics endpoint (Prometheus)
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from time import time

request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'path'])

@app.get("/metrics")
async def metrics():
    return generate_latest()

# Example endpoints
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: float

@app.post("/items", tags=["items"])
async def create_item(item: Item):
    """Create a new item"""
    logger.info(f"Creating item: {item.name}")
    # TODO: Save to database
    return {"id": 1, "name": item.name, "price": item.price}

@app.get("/items/{item_id}", tags=["items"])
async def get_item(item_id: int):
    """Get item by ID"""
    # TODO: Fetch from database
    return {"id": item_id, "name": "Sample Item", "price": 99.99}

# Error handling
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "trace_id": request.state.trace_id}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=LOG_LEVEL.lower(),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
```

## Key Patterns

### 1. Configuration Management
- Never hardcode configuration
- Use environment variables for all settings
- Validate on startup
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str
    database_url: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Database Connection Pooling
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # connections in pool
    max_overflow=10,       # extra connections allowed
    pool_pre_ping=True,    # test connections before use
    pool_recycle=3600      # recycle connections after 1 hour
)
```

### 3. Dependency Injection (Database Sessions)
```python
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items")
async def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = DatabaseItem(**item.dict())
    db.add(db_item)
    db.commit()
    return db_item
```

### 4. Async Client for Downstream Services
```python
import httpx

async def call_downstream_service(service_url: str, trace_id: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            service_url,
            headers={"X-Trace-ID": trace_id}
        )
        response.raise_for_status()
        return response.json()
```

### 5. Error Handling with Context
```python
from enum import Enum

class ErrorCode(str, Enum):
    ITEM_NOT_FOUND = "ITEM_NOT_FOUND"
    INVALID_INPUT = "INVALID_INPUT"
    DATABASE_ERROR = "DATABASE_ERROR"

class APIError(HTTPException):
    def __init__(self, code: ErrorCode, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail={
            "code": code.value,
            "message": message
        })

@app.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise APIError(
            ErrorCode.ITEM_NOT_FOUND,
            f"Item {item_id} not found",
            status_code=404
        )
    return item
```

### 6. Request/Response Models with Validation
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)
    description: Optional[str] = None

    @validator('name')
    def name_must_be_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Name must be alphanumeric')
        return v

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy ORM compatibility
```

### 7. Service-to-Service Communication with Retries
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_with_retry(url: str, trace_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"X-Trace-ID": trace_id},
            timeout=5.0
        )
        response.raise_for_status()
        return response.json()
```

## Dependencies (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
prometheus-client==0.19.0
httpx==0.25.1
tenacity==8.2.3
python-json-logger==2.0.7
```

## Testing

```python
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_item():
    response = client.post("/items", json={"name": "Test", "price": 19.99})
    assert response.status_code == 200
    assert response.json()["name"] == "Test"

def test_get_item():
    response = client.get("/items/1")
    assert response.status_code == 200

def test_health_check():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"
```

## Running Locally

```bash
# Development
uvicorn main:app --reload --log-level debug

# Production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
