# Advanced Pytest Fixtures

## Fixture Scopes

```python
@pytest.fixture(scope="session")
def expensive_resource():
    """Created once per session, shared across all tests."""
    resource = setup_expensive_resource()
    yield resource
    teardown_expensive_resource(resource)

@pytest.fixture(scope="module")
def module_level_db():
    """Created once per module."""
    db = create_test_database("module")
    yield db
    db.close()

@pytest.fixture(scope="function")  # Default
def function_level_data():
    """Created for each test function (default)."""
    data = {"value": 123}
    yield data

@pytest.fixture(scope="class")
def class_level_setup():
    """Created once per test class."""
    setup = initialize_class_setup()
    yield setup
    cleanup_class_setup()
```

## Indirect Parametrization

```python
@pytest.fixture
def user(request):
    """Create user based on parametrized request."""
    user_type = request.param
    if user_type == "admin":
        return User(role="admin", is_active=True)
    elif user_type == "user":
        return User(role="user", is_active=True)
    else:
        return User(role="user", is_active=False)

@pytest.mark.parametrize("user", ["admin", "user", "inactive"], indirect=True)
def test_user_types(user):
    """Test different user types."""
    assert user is not None
```

## Fixture Request Object

```python
@pytest.fixture
def setup(request):
    """Access test metadata via request object."""
    # Current test function
    test_func = request.function

    # Test class (if in class)
    test_class = request.cls

    # Parameter names and values
    param = request.param if hasattr(request, "param") else None

    # Additional fixtures this test depends on
    depends_on = request.fixturenames

    # Config object
    config = request.config

    return {
        "test_func": test_func,
        "test_class": test_class,
        "param": param
    }
```

## Fixture Auto-use

```python
@pytest.fixture(autouse=True)
def reset_database(db_session):
    """Automatically reset database before each test."""
    yield
    db_session.rollback()

@pytest.fixture(autouse=True)
def mock_external_api():
    """Automatically mock external API for all tests."""
    with patch('requests.get') as mock:
        mock.return_value.json.return_value = {"status": "ok"}
        yield mock
```

## Fixture Composition

```python
@pytest.fixture
def base_user_data():
    """Base user data."""
    return {"email": "test@example.com"}

@pytest.fixture
def admin_user_data(base_user_data):
    """Extend base user with admin role."""
    return {**base_user_data, "role": "admin"}

@pytest.fixture
def admin_user(admin_user_data, db_session):
    """Create admin user in database."""
    user = User(**admin_user_data)
    db_session.add(user)
    db_session.commit()
    return user
```

## Cleanup Patterns

```python
@pytest.fixture
def cleanup_after_test():
    """Cleanup using yield."""
    yield  # Test runs here
    # Cleanup happens after test completes
    cleanup_resources()

@pytest.fixture
def context_manager_cleanup():
    """Use context manager for cleanup."""
    with setup_temporary_file() as temp_file:
        yield temp_file
    # File is automatically cleaned up

@pytest.fixture
def request_finalizer(request):
    """Use request.addfinalizer for complex cleanup."""
    resource = setup_resource()

    def cleanup():
        teardown_resource(resource)

    request.addfinalizer(cleanup)
    return resource
```

## Parametrized Fixtures

```python
@pytest.fixture(params=[1, 2, 5])
def database_sizes(request):
    """Fixture that's parametrized."""
    size = request.param
    db = create_database_with_size(size)
    yield db
    db.close()

def test_query_performance(database_sizes):
    """Test runs 3 times with different database sizes."""
    results = database_sizes.query(Item).all()
    assert len(results) > 0
```

## Factory Fixtures

```python
@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    counter = 0

    def _create_user(email=None, role="user"):
        nonlocal counter
        counter += 1
        return User(
            id=counter,
            email=email or f"user{counter}@example.com",
            role=role
        )

    return _create_user

def test_multiple_users(user_factory):
    """Create multiple users with factory."""
    user1 = user_factory()
    user2 = user_factory(email="custom@example.com")
    admin = user_factory(role="admin")

    assert user1.email == "user1@example.com"
    assert user2.email == "custom@example.com"
    assert admin.role == "admin"
```

## Database Fixtures with Isolation

```python
@pytest.fixture
def isolated_db_session(db_engine):
    """Completely isolated database session."""
    connection = db_engine.connect()
    transaction = connection.begin()

    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def transactional_session(db_session):
    """Session that commits but rolls back after test."""
    yield db_session
    db_session.rollback()
```
