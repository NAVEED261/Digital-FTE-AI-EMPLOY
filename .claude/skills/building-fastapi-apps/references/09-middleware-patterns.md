# Middleware Patterns in FastAPI

> **Official Docs**: [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)

## What is Middleware?

Middleware is code that runs before every request and after every response. Use it for:
- Request timing and logging
- CORS headers
- Authentication checks
- Request/response transformation
- Error handling

## Basic Middleware Pattern

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()

    # Process request
    response = await call_next(request)

    # Add timing header
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    return response
```

## Timing Middleware

```python
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """Log request timing and details."""
    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Duration: {duration:.4f}s"
    )

    # Add timing header
    response.headers["X-Process-Time"] = f"{duration:.4f}"

    return response
```

## CORS Middleware

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Production: Specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://www.myapp.com",
        "http://localhost:3000",  # Development only
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

### CORS Configuration Options

| Option | Description |
|--------|-------------|
| `allow_origins` | List of allowed origins (never use `["*"]` with credentials) |
| `allow_credentials` | Allow cookies and auth headers |
| `allow_methods` | Allowed HTTP methods |
| `allow_headers` | Allowed request headers |
| `expose_headers` | Headers visible to browser JavaScript |
| `max_age` | Seconds to cache preflight response |

## Request Logging Middleware

```python
import logging
import uuid
from fastapi import Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests with unique ID."""
    # Generate request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Add to request state for use in endpoints
    request.state.request_id = request_id

    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"from {request.client.host}"
    )

    response = await call_next(request)

    # Add request ID to response
    response.headers["X-Request-ID"] = request_id

    # Log response
    logger.info(f"[{request_id}] Response: {response.status_code}")

    return response
```

## Error Handling Middleware

```python
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """Catch unhandled exceptions."""
    try:
        return await call_next(request)
    except Exception as e:
        # Log the full traceback
        logger.error(
            f"Unhandled error: {e}\n{traceback.format_exc()}"
        )

        # Return generic error (don't leak details)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
```

## Authentication Middleware

```python
from fastapi import Request, HTTPException
from jose import jwt, JWTError

# Paths that don't require authentication
PUBLIC_PATHS = ["/", "/health", "/auth/login", "/auth/signup", "/docs", "/openapi.json"]

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Verify JWT token for protected routes."""
    path = request.url.path

    # Skip auth for public paths
    if any(path.startswith(p) for p in PUBLIC_PATHS):
        return await call_next(request)

    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing authentication"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.state.user_id = payload.get("sub")
    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    return await call_next(request)
```

## Rate Limiting Middleware

```python
from collections import defaultdict
import time
from fastapi import Request
from fastapi.responses import JSONResponse

# Simple in-memory rate limiter (use Redis in production)
request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 100  # requests
WINDOW_SECONDS = 60  # per minute

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Limit requests per IP address."""
    client_ip = request.client.host
    now = time.time()

    # Remove old requests outside window
    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if now - t < WINDOW_SECONDS
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
            headers={"Retry-After": str(WINDOW_SECONDS)}
        )

    request_counts[client_ip].append(now)

    response = await call_next(request)

    # Add rate limit headers
    remaining = RATE_LIMIT - len(request_counts[client_ip])
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    return response
```

## Request Body Logging (Debug Only)

```python
import json
from fastapi import Request

@app.middleware("http")
async def log_request_body(request: Request, call_next):
    """Log request body for debugging (disable in production!)."""
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        if body:
            try:
                body_json = json.loads(body)
                logger.debug(f"Request body: {json.dumps(body_json, indent=2)}")
            except json.JSONDecodeError:
                logger.debug(f"Request body (raw): {body[:500]}")

    return await call_next(request)
```

## Custom BaseHTTPMiddleware

For more complex middleware, extend `BaseHTTPMiddleware`:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class CustomMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, some_config: str = "default"):
        super().__init__(app)
        self.some_config = some_config

    async def dispatch(self, request: Request, call_next) -> Response:
        # Before request
        request.state.custom_value = self.some_config

        response = await call_next(request)

        # After response
        response.headers["X-Custom-Header"] = self.some_config

        return response

# Add to app
app.add_middleware(CustomMiddleware, some_config="my-value")
```

## Middleware Execution Order

Middleware executes in reverse order of registration:

```python
app = FastAPI()

@app.middleware("http")
async def middleware_a(request, call_next):
    print("A: before")
    response = await call_next(request)
    print("A: after")
    return response

@app.middleware("http")
async def middleware_b(request, call_next):
    print("B: before")
    response = await call_next(request)
    print("B: after")
    return response

# Output for a request:
# B: before
# A: before
# (endpoint executes)
# A: after
# B: after
```

## GZip Compression Middleware

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

app.add_middleware(
    GZipMiddleware,
    minimum_size=500  # Only compress responses > 500 bytes
)
```

## Trusted Host Middleware

```python
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["myapp.com", "*.myapp.com"]
)
```

## HTTPS Redirect Middleware

```python
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Redirect all HTTP to HTTPS
app.add_middleware(HTTPSRedirectMiddleware)
```

## Complete Production Middleware Stack

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Order matters: Last added = first executed

# 1. Trusted hosts (security)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["myapp.com", "*.myapp.com", "localhost"]
)

# 2. CORS (before any processing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=500)

# 4. Custom timing/logging
@app.middleware("http")
async def timing_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response

# 5. Request ID tracking
@app.middleware("http")
async def request_id_middleware(request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

## Testing Middleware

```python
from fastapi.testclient import TestClient

def test_cors_headers(client):
    response = client.options(
        "/tasks",
        headers={"Origin": "https://myapp.com"}
    )
    assert "Access-Control-Allow-Origin" in response.headers

def test_timing_header(client):
    response = client.get("/health")
    assert "X-Process-Time" in response.headers

def test_request_id_generated(client):
    response = client.get("/health")
    assert "X-Request-ID" in response.headers

def test_request_id_preserved(client):
    response = client.get(
        "/health",
        headers={"X-Request-ID": "test-123"}
    )
    assert response.headers["X-Request-ID"] == "test-123"
```
