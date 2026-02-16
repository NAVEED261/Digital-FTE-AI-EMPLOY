# Pytest Testing for FastAPI

> **Official Docs**: [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Installation

```bash
pip install pytest pytest-cov httpx
```

## Basic TestClient Usage

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

## conftest.py Setup

Create `tests/conftest.py` for shared fixtures:

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.database import get_session

# In-memory test database
@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with database override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
```

## Testing CRUD Operations

### Test Create

```python
def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "priority": "high"}
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert data["status"] == "todo"  # Default
    assert "id" in data
    assert "created_at" in data

def test_create_task_minimal(client):
    """Test creating task with only required fields."""
    response = client.post("/tasks", json={"title": "Minimal"})
    assert response.status_code == 201
    assert response.json()["title"] == "Minimal"
```

### Test Read

```python
def test_get_task(client):
    # Create first
    create_response = client.post("/tasks", json={"title": "Test"})
    task_id = create_response.json()["id"]

    # Then get
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test"

def test_get_nonexistent_task(client):
    response = client.get("/tasks/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_list_tasks(client):
    # Create multiple tasks
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})

    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2
```

### Test Update

```python
def test_update_task(client):
    # Create
    create_response = client.post("/tasks", json={"title": "Original"})
    task_id = create_response.json()["id"]

    # Update
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

def test_partial_update(client):
    """Test updating only some fields."""
    create_response = client.post(
        "/tasks",
        json={"title": "Test", "priority": "low"}
    )
    task_id = create_response.json()["id"]

    # Update only priority
    response = client.put(
        f"/tasks/{task_id}",
        json={"priority": "high"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test"  # Unchanged
    assert response.json()["priority"] == "high"  # Updated
```

### Test Delete

```python
def test_delete_task(client):
    # Create
    create_response = client.post("/tasks", json={"title": "To Delete"})
    task_id = create_response.json()["id"]

    # Delete
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent(client):
    response = client.delete("/tasks/99999")
    assert response.status_code == 404
```

## Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("title,expected_status", [
    ("Valid Title", 201),
    ("", 422),  # Empty string
    ("x" * 256, 422),  # Too long
])
def test_title_validation(client, title, expected_status):
    response = client.post("/tasks", json={"title": title})
    assert response.status_code == expected_status

@pytest.mark.parametrize("priority", ["low", "medium", "high", "urgent"])
def test_valid_priorities(client, priority):
    response = client.post(
        "/tasks",
        json={"title": "Test", "priority": priority}
    )
    assert response.status_code == 201
    assert response.json()["priority"] == priority

@pytest.mark.parametrize("invalid_priority", ["invalid", "LOW", "1", ""])
def test_invalid_priorities(client, invalid_priority):
    response = client.post(
        "/tasks",
        json={"title": "Test", "priority": invalid_priority}
    )
    assert response.status_code == 422
```

## Testing Authentication

### Auth Fixtures

```python
# conftest.py
@pytest.fixture
def auth_headers(client):
    """Create user and return auth headers."""
    # Signup
    client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })

    # Login
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "SecurePass123!"
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client, session):
    """Create admin user and return auth headers."""
    from app.models import User

    # Create admin user directly in DB
    admin = User(
        email="admin@example.com",
        name="Admin",
        is_admin=True
    )
    admin.set_password("AdminPass123!")
    session.add(admin)
    session.commit()

    # Login
    response = client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "AdminPass123!"
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Auth Tests

```python
def test_protected_route_without_auth(client):
    response = client.get("/me")
    assert response.status_code == 401

def test_protected_route_with_auth(client, auth_headers):
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_admin_route_as_user(client, auth_headers):
    response = client.get("/admin/users", headers=auth_headers)
    assert response.status_code == 403

def test_admin_route_as_admin(client, admin_headers):
    response = client.get("/admin/users", headers=admin_headers)
    assert response.status_code == 200

def test_invalid_token(client):
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/me", headers=headers)
    assert response.status_code == 401
```

## Testing Filtering and Pagination

```python
def test_filter_by_status(client):
    # Create tasks with different statuses
    client.post("/tasks", json={"title": "Todo 1", "status": "todo"})
    client.post("/tasks", json={"title": "Done 1", "status": "done"})
    client.post("/tasks", json={"title": "Todo 2", "status": "todo"})

    # Filter
    response = client.get("/tasks?status=todo")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert all(t["status"] == "todo" for t in tasks)

def test_pagination(client):
    # Create 10 tasks
    for i in range(10):
        client.post("/tasks", json={"title": f"Task {i}"})

    # Get first page
    response = client.get("/tasks?skip=0&limit=5")
    assert len(response.json()) == 5

    # Get second page
    response = client.get("/tasks?skip=5&limit=5")
    assert len(response.json()) == 5

def test_pagination_limits(client):
    # Test max limit
    response = client.get("/tasks?limit=200")
    assert response.status_code == 422  # Exceeds max

    # Test negative skip
    response = client.get("/tasks?skip=-1")
    assert response.status_code == 422
```

## Testing Timestamps

```python
import time

def test_created_at_set(client):
    response = client.post("/tasks", json={"title": "Test"})
    assert "created_at" in response.json()
    assert response.json()["created_at"] is not None

def test_updated_at_changes(client):
    # Create
    create_response = client.post("/tasks", json={"title": "Test"})
    task_id = create_response.json()["id"]
    original_updated = create_response.json()["updated_at"]

    # Wait briefly
    time.sleep(0.01)

    # Update
    update_response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated"}
    )
    new_updated = update_response.json()["updated_at"]

    assert new_updated != original_updated

def test_completed_at_set_on_done(client):
    # Create
    create_response = client.post("/tasks", json={"title": "Test"})
    task_id = create_response.json()["id"]
    assert create_response.json()["completed_at"] is None

    # Mark done
    response = client.put(
        f"/tasks/{task_id}",
        json={"status": "done"}
    )
    assert response.json()["completed_at"] is not None
```

## Testing Error Cases

```python
def test_validation_error_format(client):
    response = client.post("/tasks", json={})  # Missing required title
    assert response.status_code == 422

    data = response.json()
    assert "detail" in data
    # Check error structure
    assert any("title" in str(e) for e in data["detail"])

def test_extra_fields_rejected(client):
    """Test that extra fields are rejected with extra='forbid'."""
    response = client.post(
        "/tasks",
        json={"title": "Test", "unknown_field": "value"}
    )
    assert response.status_code == 422

def test_wrong_type(client):
    response = client.post(
        "/tasks",
        json={"title": 123}  # Should be string
    )
    assert response.status_code == 422
```

## Async Test Support

```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
```

## Testing with Database Fixtures

```python
@pytest.fixture
def sample_tasks(session):
    """Create sample tasks for testing."""
    from app.models import Task

    tasks = [
        Task(title="Task 1", status="todo", priority="high"),
        Task(title="Task 2", status="in_progress", priority="medium"),
        Task(title="Task 3", status="done", priority="low"),
    ]

    for task in tasks:
        session.add(task)
    session.commit()

    return tasks

def test_with_sample_data(client, sample_tasks):
    response = client.get("/tasks")
    assert len(response.json()) == 3
```

## Code Coverage

Run with coverage:

```bash
# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Coverage Configuration (pyproject.toml)

```toml
[tool.coverage.run]
source = ["app"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

## Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── test_health.py       # Health check tests
├── test_tasks.py        # Task CRUD tests
├── test_auth.py         # Authentication tests
├── test_users.py        # User management tests
├── test_validation.py   # Input validation tests
└── test_integration.py  # End-to-end workflows
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_tasks.py

# Run specific test
pytest tests/test_tasks.py::test_create_task

# Run tests matching pattern
pytest -k "create"

# Stop on first failure
pytest -x

# Run failed tests from last run
pytest --lf

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## Complete Test Example

```python
# tests/test_tasks.py
import pytest
from fastapi.testclient import TestClient


class TestCreateTask:
    """Tests for task creation."""

    def test_create_with_all_fields(self, client):
        response = client.post("/tasks", json={
            "title": "Complete project",
            "description": "Finish the FastAPI project",
            "priority": "high"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete project"
        assert data["description"] == "Finish the FastAPI project"
        assert data["priority"] == "high"
        assert data["status"] == "todo"

    def test_create_minimal(self, client):
        response = client.post("/tasks", json={"title": "Simple"})
        assert response.status_code == 201

    @pytest.mark.parametrize("invalid_data,error_field", [
        ({}, "title"),  # Missing required
        ({"title": ""}, "title"),  # Empty
        ({"title": "x" * 300}, "title"),  # Too long
        ({"title": "Test", "priority": "invalid"}, "priority"),
    ])
    def test_validation_errors(self, client, invalid_data, error_field):
        response = client.post("/tasks", json=invalid_data)
        assert response.status_code == 422
        assert error_field in str(response.json())


class TestListTasks:
    """Tests for task listing."""

    def test_empty_list(self, client):
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_with_tasks(self, client, sample_tasks):
        response = client.get("/tasks")
        assert len(response.json()) == len(sample_tasks)

    def test_filter_by_status(self, client, sample_tasks):
        response = client.get("/tasks?status=done")
        tasks = response.json()
        assert all(t["status"] == "done" for t in tasks)

    def test_pagination(self, client, sample_tasks):
        response = client.get("/tasks?skip=1&limit=1")
        assert len(response.json()) == 1


class TestIntegration:
    """End-to-end workflow tests."""

    def test_full_task_lifecycle(self, client):
        # Create
        create_resp = client.post("/tasks", json={"title": "Lifecycle Test"})
        assert create_resp.status_code == 201
        task_id = create_resp.json()["id"]

        # Read
        get_resp = client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 200

        # Update
        update_resp = client.put(
            f"/tasks/{task_id}",
            json={"status": "done"}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "done"

        # Delete
        delete_resp = client.delete(f"/tasks/{task_id}")
        assert delete_resp.status_code == 204

        # Verify deleted
        verify_resp = client.get(f"/tasks/{task_id}")
        assert verify_resp.status_code == 404
```
