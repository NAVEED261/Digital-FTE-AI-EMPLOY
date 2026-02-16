# Lifespan Events in FastAPI

> **Official Docs**: [FastAPI Lifespan](https://fastapi.tiangolo.com/advanced/events/)

## What is Lifespan?

Lifespan manages code that runs:
- **Startup**: Before the app starts accepting requests
- **Shutdown**: After the app stops accepting requests

Use for:
- Database connection pools
- HTTP client sessions
- Machine learning model loading
- Cache initialization
- Background task cleanup

## Basic Lifespan Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: runs before app starts
    print("Starting up...")
    yield
    # Shutdown: runs after app stops
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

## Using app.state for Shared Resources

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create shared resources
    app.state.http_client = httpx.AsyncClient()

    yield

    # Shutdown: Cleanup
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

# Access in endpoints
@app.get("/external")
async def fetch_external(request: Request):
    client = request.app.state.http_client
    response = await client.get("https://api.example.com/data")
    return response.json()
```

## Database Pool Lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import QueuePool

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database engine with connection pool
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

    # Create tables
    SQLModel.metadata.create_all(engine)

    # Store engine in app state
    app.state.engine = engine

    print("Database pool initialized")
    yield

    # Shutdown: Dispose of connections
    engine.dispose()
    print("Database pool closed")

app = FastAPI(lifespan=lifespan)
```

## Multiple Resources

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx
import redis.asyncio as redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize all resources
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    app.state.redis = redis.from_url("redis://localhost")
    app.state.ml_model = load_ml_model("model.pkl")

    print("All resources initialized")
    yield

    # Cleanup all resources (in reverse order)
    del app.state.ml_model
    await app.state.redis.close()
    await app.state.http_client.aclose()

    print("All resources cleaned up")

app = FastAPI(lifespan=lifespan)
```

## Health Check Integration

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Mark app as not ready during startup
    app.state.ready = False

    # Initialize resources
    app.state.db = await create_db_pool()

    # Mark app as ready
    app.state.ready = True
    print("App ready to serve requests")

    yield

    # Mark as not ready during shutdown
    app.state.ready = False

    # Cleanup
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)

@app.get("/health/live")
def liveness():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

@app.get("/health/ready")
def readiness(request: Request):
    """Kubernetes readiness probe."""
    if not request.app.state.ready:
        raise HTTPException(status_code=503, detail="Not ready")
    return {"status": "ready"}
```

## Async vs Sync Lifespan

### Async (Recommended)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Can use async/await
    app.state.client = await create_async_client()
    yield
    await app.state.client.close()
```

### Sync (When Needed)

```python
from contextlib import contextmanager

@contextmanager
def lifespan(app: FastAPI):
    # Sync-only operations
    app.state.cache = create_sync_cache()
    yield
    app.state.cache.close()
```

## Error Handling in Lifespan

```python
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Startup
        app.state.db = await connect_to_database()
        logger.info("Database connected")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise  # App won't start if startup fails

    try:
        yield
    finally:
        # Shutdown always runs, even if there was an error
        try:
            await app.state.db.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
```

## Background Tasks with Lifespan

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task
    async def background_worker():
        while True:
            await process_queue()
            await asyncio.sleep(60)

    task = asyncio.create_task(background_worker())
    app.state.background_task = task

    yield

    # Cancel background task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
```

## Machine Learning Model Loading

```python
from contextlib import asynccontextmanager
import pickle

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML model (can be slow, only once at startup)
    print("Loading ML model...")
    with open("model.pkl", "rb") as f:
        app.state.model = pickle.load(f)
    print("Model loaded")

    yield

    # Cleanup (if needed)
    del app.state.model

app = FastAPI(lifespan=lifespan)

@app.post("/predict")
async def predict(data: PredictionInput, request: Request):
    model = request.app.state.model
    result = model.predict(data.features)
    return {"prediction": result}
```

## Dependency Injection with Lifespan Resources

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

# Dependency to get the client
def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

# Use in endpoints
@app.get("/fetch")
async def fetch_data(client: httpx.AsyncClient = Depends(get_http_client)):
    response = await client.get("https://api.example.com")
    return response.json()
```

## Testing with Lifespan

```python
import pytest
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager

# Test lifespan that uses mocks
@asynccontextmanager
async def test_lifespan(app: FastAPI):
    app.state.db = MockDatabase()
    app.state.http_client = MockHTTPClient()
    yield
    # No cleanup needed for mocks

@pytest.fixture
def client():
    from main import app

    # Override lifespan for testing
    app.router.lifespan_context = test_lifespan

    with TestClient(app) as client:
        yield client

def test_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
```

## Graceful Shutdown Pattern

```python
import signal
import asyncio
from contextlib import asynccontextmanager

shutdown_event = asyncio.Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup signal handlers for graceful shutdown
    def handle_shutdown(signum, frame):
        shutdown_event.set()

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    # Start resources
    app.state.db = await create_pool()

    yield

    # Wait for in-flight requests (give them 10 seconds)
    print("Waiting for in-flight requests...")
    await asyncio.sleep(10)

    # Close resources
    await app.state.db.close()
    print("Shutdown complete")
```

## Complete Production Lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx
import redis.asyncio as redis
from sqlmodel import SQLModel, create_engine
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Production lifespan with all resources."""
    logger.info("Starting application...")

    # 1. Database
    try:
        engine = create_engine(settings.database_url)
        SQLModel.metadata.create_all(engine)
        app.state.engine = engine
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
        raise

    # 2. Redis cache
    try:
        app.state.redis = redis.from_url(settings.redis_url)
        await app.state.redis.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}")
        app.state.redis = None

    # 3. HTTP client for external APIs
    app.state.http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_connections=100)
    )
    logger.info("HTTP client initialized")

    # 4. Mark as ready
    app.state.ready = True
    logger.info("Application ready")

    yield

    # Shutdown
    logger.info("Shutting down...")
    app.state.ready = False

    await app.state.http_client.aclose()
    if app.state.redis:
        await app.state.redis.close()
    app.state.engine.dispose()

    logger.info("Shutdown complete")

app = FastAPI(lifespan=lifespan)
```
