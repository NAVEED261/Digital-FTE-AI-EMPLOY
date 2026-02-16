---
name: testing-with-pytest
description: |
  Use when writing unit tests, integration tests, or end-to-end tests in Python.
  Also use for implementing test fixtures, mocking, parametrization, async testing, or coverage analysis.
  NOT when using other testing frameworks (unittest, nose) or testing non-Python code.
---

# Testing with Pytest

Pytest is a powerful, flexible Python testing framework that enables writing simple tests yet scales to support complex functional testing. This skill covers both core testing patterns and advanced techniques.

## Quick Start: Test File Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_models.py           # Database model tests
├── test_api.py              # API endpoint tests
├── test_services.py         # Business logic tests
├── integration/
│   ├── conftest.py          # Integration-specific fixtures
│   └── test_workflows.py    # End-to-end workflows
└── fixtures/
    ├── users.py             # User fixtures
    ├── items.py             # Item fixtures
    └── db.py                # Database fixtures
```

## Core Patterns

### 1. Basic Test Structure

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    """Test user creation endpoint."""
    response = client.post(
        "/api/v1/users/",
        json={"email": "user@example.com", "password": "secure123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"

def test_get_user_not_found():
    """Test 404 for non-existent user."""
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
```

### 2. Fixtures - Reusable Test Data

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import User

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_user(db_session):
    """Create sample user for tests."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def client(db_session):
    """Create test client with database session."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api.deps import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
```

### 3. Parametrization - Testing Multiple Cases

```python
import pytest

@pytest.mark.parametrize("email,password,expected_status", [
    ("valid@example.com", "secure123", 201),
    ("invalid@", "short", 422),
    ("", "password", 422),
    ("user@example.com", "", 422),
])
def test_user_creation_variants(email, password, expected_status, client):
    """Test user creation with various inputs."""
    response = client.post(
        "/api/v1/users/",
        json={"email": email, "password": password}
    )
    assert response.status_code == expected_status

# Parametrize with fixtures
@pytest.mark.parametrize("user_fixture", [
    pytest.param("sample_user", id="with_user"),
    pytest.param("admin_user", id="with_admin"),
])
def test_user_deletion(request, user_fixture, client):
    """Test deletion with different user roles."""
    user = request.getfixturevalue(user_fixture)
    response = client.delete(f"/api/v1/users/{user.id}")
    assert response.status_code == 204
```

### 4. Markers - Organizing Tests

```python
# tests/conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "database: marks tests that require database"
    )

# tests/test_api.py
@pytest.mark.slow
def test_complex_calculation():
    """This test is marked as slow."""
    pass

@pytest.mark.integration
def test_full_workflow(client, db_session):
    """Full integration test."""
    pass

@pytest.mark.database
def test_user_save(db_session):
    """Test database save operation."""
    pass

# Run with: pytest -m "not slow"
# Run with: pytest -m "integration"
```

### 5. Mocking with unittest.mock

```python
from unittest.mock import patch, MagicMock
import pytest

@pytest.fixture
def mock_email_service():
    """Mock email service."""
    with patch('app.services.email.send_email') as mock:
        mock.return_value = True
        yield mock

def test_send_notification(mock_email_service, client):
    """Test endpoint that sends email."""
    response = client.post(
        "/api/v1/notifications/send/",
        json={"user_id": 1, "message": "Hello"}
    )
    assert response.status_code == 200
    # Verify email was called
    mock_email_service.assert_called_once()

@patch('requests.get')
def test_external_api_call(mock_get):
    """Mock external API calls."""
    mock_get.return_value.json.return_value = {"data": "success"}

    result = fetch_external_data()

    assert result["data"] == "success"
    mock_get.assert_called_once()
```

## Advanced Patterns

### 1. Async Testing

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_endpoint():
    """Test async endpoint."""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/")
        assert response.status_code == 200

@pytest.fixture
async def async_client():
    """Async test client."""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_with_async_client(async_client):
    """Test using async client fixture."""
    response = await async_client.post(
        "/items/",
        json={"name": "test"}
    )
    assert response.status_code == 201
```

### 2. Database Transaction Isolation

```python
@pytest.fixture
def db_transaction(db_session):
    """Rollback all changes after test."""
    try:
        yield db_session
    finally:
        db_session.rollback()

def test_user_creation_rollback(db_transaction):
    """Test that changes are rolled back."""
    user = User(email="test@example.com")
    db_transaction.add(user)
    db_transaction.commit()
    assert user.id is not None

# After test completes, transaction is rolled back
```

### 3. Factory Fixtures

```python
import pytest
from factory import Factory, Faker
from app.models import User, Item

class UserFactory(Factory):
    class Meta:
        model = User

    email = Faker("email")
    username = Faker("user_name")
    is_active = True

class ItemFactory(Factory):
    class Meta:
        model = Item

    title = Faker("sentence")
    description = Faker("text")
    user = factory.SubFactory(UserFactory)

@pytest.fixture
def user_factory():
    """Factory for creating users."""
    return UserFactory

def test_with_factory(user_factory, db_session):
    """Test using factory-boy."""
    user = user_factory.create()
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

### 4. Coverage Analysis

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html

# Generate coverage badge
coverage-badge -o coverage.svg

# Show coverage report
coverage report --precision=2
```

### 5. Custom Assertions

```python
import pytest

@pytest.fixture
def assert_helpers():
    """Custom assertion helpers."""
    class AssertHelpers:
        @staticmethod
        def has_required_fields(data, fields):
            for field in fields:
                assert field in data, f"Missing field: {field}"

        @staticmethod
        def is_valid_uuid(value):
            import uuid
            try:
                uuid.UUID(str(value))
                return True
            except ValueError:
                return False

    return AssertHelpers()

def test_response_structure(client, assert_helpers):
    """Test response has required structure."""
    response = client.get("/api/v1/items/1")
    data = response.json()
    assert_helpers.has_required_fields(data, ["id", "name", "created_at"])
```

### 6. Exception Testing

```python
import pytest

def test_invalid_input_raises():
    """Test that invalid input raises exception."""
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email("not-an-email")

def test_database_error():
    """Test database error handling."""
    with pytest.raises(DatabaseError):
        db.query(User).filter(User.id == "invalid").first()
```

### 7. Fixtures with Dependencies

```python
@pytest.fixture
def authenticated_user(sample_user, client):
    """Get authenticated user with token."""
    response = client.post(
        "/api/v1/login/",
        json={"email": sample_user.email, "password": "password"}
    )
    token = response.json()["access_token"]
    return {"user": sample_user, "token": token}

def test_protected_endpoint(authenticated_user, client):
    """Test protected endpoint with authentication."""
    token = authenticated_user["token"]
    response = client.get(
        "/api/v1/profile/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### 8. Performance Testing

```python
import pytest
import time

@pytest.mark.slow
def test_query_performance(db_session):
    """Test that query completes within time limit."""
    start = time.time()
    items = db_session.query(Item).all()
    elapsed = time.time() - start

    assert elapsed < 0.5, f"Query took {elapsed}s, expected < 0.5s"

# Use pytest-benchmark for profiling
def test_algorithm_performance(benchmark):
    """Benchmark algorithm performance."""
    result = benchmark(expensive_function, arg1, arg2)
    assert result is not None
```

### 9. Snapshot Testing

```python
# pip install pytest-snapshot
def test_api_response_snapshot(client, snapshot):
    """Test API response matches snapshot."""
    response = client.get("/api/v1/items/1")
    snapshot.assert_match(response.json())

# Update snapshots: pytest --snapshot-update
```

### 10. Integration Tests

```python
# tests/integration/test_workflow.py
@pytest.mark.integration
def test_complete_user_workflow(client, db_session):
    """Test complete user workflow."""
    # Create user
    response = client.post(
        "/api/v1/users/",
        json={"email": "user@example.com", "password": "secure123"}
    )
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Login
    response = client.post(
        "/api/v1/login/",
        json={"email": "user@example.com", "password": "secure123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create item as authenticated user
    response = client.post(
        "/api/v1/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Item"}
    )
    assert response.status_code == 201
```

## Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    database: marks tests that require database
```

### conftest.py Patterns

```python
# tests/conftest.py
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment."""
    import os
    os.environ["ENV"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

## Best Practices

1. **Use descriptive test names** - `test_create_user_with_valid_email` not `test_1`
2. **Arrange-Act-Assert pattern** - Setup, execute, verify
3. **One assertion per test** (when possible) - Easier to debug
4. **DRY with fixtures** - Reuse setup code
5. **Mock external dependencies** - Keep tests fast and isolated
6. **Parametrize variations** - Test multiple cases efficiently
7. **Clear error messages** - Use custom assertions for clarity
8. **Test edge cases** - Empty inputs, None, boundaries
9. **Isolate tests** - No dependencies between tests
10. **Use markers** - Organize and filter tests effectively

## Common Commands

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_create_user

# Run with output
pytest -v

# Run with coverage
pytest --cov=app

# Run specific marker
pytest -m "not slow"

# Run with multiple workers (parallel)
pytest -n auto

# Show print statements
pytest -s

# Debug with pdb
pytest --pdb
```

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Pytest Plugins](https://docs.pytest.org/en/latest/plugins.html)
