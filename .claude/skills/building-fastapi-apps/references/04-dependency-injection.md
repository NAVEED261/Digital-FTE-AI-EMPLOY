# Dependency Injection in FastAPI

> **Official Docs**: [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

## Basic Dependency

```python
from fastapi import Depends, Query

def common_parameters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return {"skip": skip, "limit": limit}

@app.get("/items/")
def list_items(params: dict = Depends(common_parameters)):
    return {"skip": params["skip"], "limit": params["limit"]}

@app.get("/users/")
def list_users(params: dict = Depends(common_parameters)):
    return {"skip": params["skip"], "limit": params["limit"]}
```

## Depends() Pattern

### Function Dependency

```python
from fastapi import Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session  # Cleanup happens after response

@app.get("/tasks")
def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()
```

### Class Dependency

```python
from fastapi import Depends, Query

class Pagination:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100)
    ):
        self.skip = skip
        self.limit = limit

@app.get("/tasks")
def list_tasks(
    pagination: Pagination = Depends(),  # No argument needed for classes
    session: Session = Depends(get_session)
):
    return session.exec(
        select(Task).offset(pagination.skip).limit(pagination.limit)
    ).all()
```

## @lru_cache for Configuration

Cache expensive operations that only need to run once:

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    model_config = {"env_file": ".env"}

@lru_cache  # Only loads settings once
def get_settings() -> Settings:
    return Settings()

@app.get("/info")
def get_info(settings: Settings = Depends(get_settings)):
    return {"debug": settings.debug}
```

### Cache Key Considerations

```python
# Bad: New instance every call (defeats caching)
@lru_cache
def get_settings(env: str = "prod"):  # Different args = different cache entries
    return Settings(_env_file=f".env.{env}")

# Good: Single cached instance
@lru_cache
def get_settings():
    return Settings()

# If you need multiple configs, use separate functions
@lru_cache
def get_prod_settings():
    return Settings(_env_file=".env.prod")

@lru_cache
def get_dev_settings():
    return Settings(_env_file=".env.dev")
```

## Yield Dependencies (Context Manager Pattern)

For resources that need cleanup:

```python
from contextlib import contextmanager

# Database session with cleanup
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()  # Commit on success
    except Exception:
        session.rollback()  # Rollback on error
        raise
    finally:
        session.close()  # Always close

# HTTP client with cleanup
async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client

# File handle with cleanup
def get_temp_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f
    os.unlink(f.name)  # Cleanup after response
```

### Async Yield Dependency

```python
async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
        await session.commit()
```

## Dependency Hierarchies (Chaining)

Build complex dependencies from simpler ones:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Level 1: Get token
def get_token(token: str = Depends(oauth2_scheme)) -> str:
    return token

# Level 2: Decode token to get user
def get_current_user(token: str = Depends(get_token)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Level 3: Verify user is active
def get_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user

# Level 4: Verify user is admin
def get_admin_user(user: User = Depends(get_active_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user

# Usage: Each endpoint gets appropriate level of access
@app.get("/public")
def public_route():
    return {"message": "Anyone can see this"}

@app.get("/profile")
def get_profile(user: User = Depends(get_current_user)):
    return user

@app.get("/dashboard")
def dashboard(user: User = Depends(get_active_user)):
    return {"message": f"Welcome {user.name}"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(get_admin_user)):
    # Only admins reach here
    db.delete(User, user_id)
```

## Testing with dependency_overrides

Override dependencies for testing:

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(test_session):
    def get_session_override():
        return test_session

    def get_current_user_override():
        return User(id=1, email="test@example.com", is_admin=True)

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()  # Clean up after test

# test_tasks.py
def test_create_task(client):
    response = client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 201

def test_admin_endpoint(client):
    # get_current_user_override returns admin user
    response = client.delete("/users/999")
    assert response.status_code in [200, 404]  # Not 403
```

## Router-Level Dependencies

Apply dependencies to all routes in a router:

```python
from fastapi import APIRouter, Depends

# All routes require authentication
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_user)]  # Applied to ALL routes
)

@router.get("/users")
def list_users():  # No need to add Depends(get_admin_user) here
    ...

@router.delete("/users/{user_id}")
def delete_user(user_id: int):  # Already protected by router dependency
    ...
```

## App-Level Dependencies

Apply to ALL routes in the app:

```python
app = FastAPI(
    dependencies=[Depends(verify_api_key)]  # Every route requires API key
)
```

## Dependency Factories

Create parameterized dependencies:

```python
def require_role(required_role: str):
    """Factory that creates a dependency requiring a specific role."""
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_checker

# Usage
@app.get("/manager-only")
def manager_route(user: User = Depends(require_role("manager"))):
    return {"message": f"Hello manager {user.name}"}

@app.get("/editor-only")
def editor_route(user: User = Depends(require_role("editor"))):
    return {"message": f"Hello editor {user.name}"}
```

## Multiple Dependencies in One Endpoint

```python
@app.post("/tasks")
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    # All three dependencies are injected
    db_task = Task.model_validate(task, update={"owner_id": user.id})
    session.add(db_task)
    session.commit()
    return db_task
```

## Background Task Dependency

```python
from fastapi import BackgroundTasks, Depends

def get_email_service():
    return EmailService()

@app.post("/users")
def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    email_service: EmailService = Depends(get_email_service),
    session: Session = Depends(get_session)
):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()

    # Send welcome email in background
    background_tasks.add_task(
        email_service.send_welcome,
        to=db_user.email,
        name=db_user.name
    )

    return db_user
```

## Dependency Execution Order

Dependencies execute in order they appear:

```python
@app.get("/example")
def example(
    first: str = Depends(dep_a),   # Executes 1st
    second: str = Depends(dep_b),  # Executes 2nd
    third: str = Depends(dep_c),   # Executes 3rd
):
    ...

# For yield dependencies, cleanup happens in REVERSE order:
# dep_c cleanup -> dep_b cleanup -> dep_a cleanup
```

## Common Dependency Patterns

### Request ID Tracking

```python
import uuid
from fastapi import Request

def get_request_id(request: Request) -> str:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return request_id

@app.get("/tasks")
def list_tasks(request_id: str = Depends(get_request_id)):
    logger.info(f"[{request_id}] Listing tasks")
    ...
```

### Rate Limiting

```python
from collections import defaultdict
import time

request_counts = defaultdict(list)

def rate_limiter(request: Request):
    client_ip = request.client.host
    now = time.time()

    # Remove requests older than 1 minute
    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if now - t < 60
    ]

    if len(request_counts[client_ip]) >= 100:
        raise HTTPException(status_code=429, detail="Too many requests")

    request_counts[client_ip].append(now)

@app.get("/api/data", dependencies=[Depends(rate_limiter)])
def get_data():
    ...
```

### Feature Flags

```python
def require_feature(feature_name: str):
    def checker(settings: Settings = Depends(get_settings)):
        if not getattr(settings, f"feature_{feature_name}", False):
            raise HTTPException(
                status_code=404,
                detail="Feature not available"
            )
    return checker

@app.get("/beta-feature", dependencies=[Depends(require_feature("beta"))])
def beta_feature():
    return {"message": "Welcome to the beta!"}
```
