---
name: building-fastapi-apps
description: |
  Build production-ready FastAPI applications from hello world to professional APIs.
  Use when creating REST APIs, implementing authentication, database integration,
  testing, middleware, streaming, or agent integration patterns. Covers Pydantic v2
  models, SQLModel ORM, JWT auth, SSE streaming, and OpenAI Agents SDK integration.
triggers:
  - FastAPI
  - REST API
  - API endpoint
  - Pydantic model
  - SQLModel
  - JWT authentication
  - SSE streaming
  - OpenAI Agents
  - pytest FastAPI
  - CRUD operations
  - dependency injection
  - middleware
---

# Building FastAPI Applications

Production-grade FastAPI development from hello world to professional APIs.

## Quick Start

### Hello World (3 lines)
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}
```

Run: `uvicorn main:app --reload`

### Production Project Structure
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + lifespan
│   ├── config.py            # Settings with pydantic-settings
│   ├── database.py          # Engine + session dependency
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLModel
│   │   └── task.py          # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py          # Pydantic request/response models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Login, signup, token refresh
│   │   └── tasks.py         # CRUD endpoints
│   ├── services/
│   │   └── auth.py          # Password hashing, JWT logic
│   └── middleware/
│       └── timing.py        # Request timing middleware
├── tests/
│   ├── conftest.py          # Fixtures
│   └── test_tasks.py        # API tests
├── .env                     # Secrets (gitignored)
├── .gitignore
├── pyproject.toml
└── README.md
```

## Core Patterns

### 1. Application Setup with Lifespan
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    app.state.db_pool = create_pool()
    yield
    # Shutdown: Cleanup
    await app.state.db_pool.close()

app = FastAPI(
    title="My API",
    version="1.0.0",
    lifespan=lifespan
)
```

### 2. Pydantic Models: Literal vs Enum
```python
from typing import Literal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

# Literal: Best for simple, fixed values (better OpenAPI docs)
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    priority: Literal["low", "medium", "high"] = "medium"
    model_config = ConfigDict(extra="forbid")  # Reject unknown fields

# Enum: Best when you need the enum elsewhere in code
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
```

### 3. CRUD Operations with Status Codes
```python
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
```

### 4. Dependency Injection Pattern
```python
from functools import lru_cache
from fastapi import Depends
from sqlmodel import Session
from .config import Settings

# Cached settings (loaded once)
@lru_cache
def get_settings() -> Settings:
    return Settings()

# Session with cleanup (yield dependency)
def get_session():
    with Session(engine) as session:
        yield session

# Dependency chain: admin requires current_user
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return decode_token(token)

def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user
```

### 5. Database with SQLModel + Neon
```python
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=255)
    status: str = Field(default="todo")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Neon PostgreSQL connection
DATABASE_URL = "postgresql://user:pass@host.neon.tech/db?sslmode=require"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### 6. JWT Authentication
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_user_by_id(user_id)
```

### 7. Middleware Pattern
```python
import time
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

# Timing middleware
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],  # Never use ["*"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8. SSE Streaming
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import asyncio

async def event_generator():
    for i in range(10):
        yield {"event": "message", "data": f"Count: {i}"}
        await asyncio.sleep(1)

@app.get("/stream")
async def stream_events():
    return EventSourceResponse(event_generator())
```

### 9. Agent Integration (OpenAI Agents SDK)
```python
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Weather in {city}: Sunny, 72°F"

agent = Agent(
    name="weather-agent",
    instructions="You help users check weather.",
    tools=[get_weather]
)

@app.post("/chat")
async def chat(message: str):
    result = await Runner.run(agent, message)
    return {"response": result.final_output}

# Streaming version
@app.get("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        async with Runner.run_streamed(agent, message) as stream:
            async for event in stream:
                if hasattr(event, "text"):
                    yield {"data": event.text}
    return EventSourceResponse(generate())
```

### 10. Pytest Testing
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()

# test_tasks.py
def test_create_task(client):
    response = client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 201
    assert response.json()["title"] == "Test"

@pytest.mark.parametrize("title,expected", [
    ("Valid", 201),
    ("", 422),
    ("x" * 300, 422),
])
def test_title_validation(client, title, expected):
    response = client.post("/tasks", json={"title": title})
    assert response.status_code == expected
```

## Decision Tree

### Which Database?
```
Development/Testing → SQLite (in-memory for tests)
Production (simple) → SQLite file
Production (scalable) → PostgreSQL/Neon
```

### Which Auth Pattern?
```
Internal API → API keys
User-facing API → JWT tokens
Third-party login → OAuth2 (Google, GitHub)
Enterprise SSO → OIDC
```

### Sync vs Async?
```
CPU-bound work → Sync (def)
I/O-bound (DB, HTTP) → Async (async def)
Mixed → Async with run_in_executor for CPU
```

### Response Format?
```
Single resource → Return object with response_model
Collection → Return list with List[Model]
Stream → EventSourceResponse
File → FileResponse or StreamingResponse
No content → status_code=204
```

## HTTP Status Codes Reference

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | GET, PUT success |
| 201 | Created | POST success |
| 204 | No Content | DELETE success |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Valid auth, no permission |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable | Validation failed |
| 500 | Server Error | Unexpected error |

## Common Commands

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Testing
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html

# Database
alembic revision --autogenerate -m "Add users table"
alembic upgrade head
```

## Dependencies (pyproject.toml)

```toml
[project]
dependencies = [
    "fastapi[standard]>=0.115.0",
    "sqlmodel>=0.0.22",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "pwdlib[argon2]>=0.2.0",
    "sse-starlette>=2.0.0",
    "openai-agents>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "httpx>=0.27.0",
]
```

## References Index

| Topic | File | Key Concepts |
|-------|------|--------------|
| Pydantic Models | `references/01-pydantic-models.md` | Field validation, Literal vs Enum, ConfigDict |
| CRUD Operations | `references/02-crud-operations.md` | HTTP methods, status codes, pagination |
| Error Handling | `references/03-error-handling.md` | HTTPException, custom handlers |
| Dependency Injection | `references/04-dependency-injection.md` | Depends, lru_cache, yield |
| Environment Config | `references/05-environment-config.md` | BaseSettings, .env, .gitignore |
| Database Integration | `references/06-database-integration.md` | SQLModel, Neon, sessions |
| User Management | `references/07-user-management.md` | Password hashing (pwdlib/Argon2) |
| JWT Authentication | `references/08-jwt-authentication.md` | OAuth2PasswordBearer, tokens |
| Middleware | `references/09-middleware-patterns.md` | Timing, CORS, logging |
| Lifespan Events | `references/10-lifespan-events.md` | asynccontextmanager, cleanup |
| Streaming (SSE) | `references/11-streaming-sse.md` | Async generators, EventSourceResponse |
| Agent Integration | `references/12-agent-integration.md` | function_tool, Runner.run_streamed |
| Pytest Testing | `references/13-pytest-testing.md` | TestClient, fixtures, conftest.py |

## Official Documentation

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
