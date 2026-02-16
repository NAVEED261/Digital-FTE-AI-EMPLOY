# Session Management with FastAPI

## Yield-Based Dependency Injection

### Basic Pattern

```python
from fastapi import Depends, FastAPI
from sqlmodel import Session, create_engine

app = FastAPI()
engine = create_engine("sqlite:///./tasks.db")

def get_session():
    """Dependency that provides a database session"""
    with Session(engine) as session:
        yield session
        # Cleanup happens after endpoint returns
```

### Using in Endpoints

```python
from fastapi import HTTPException

@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    """Session is auto-created and auto-closed after endpoint returns"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

**How it works:**
1. FastAPI calls `get_session()` before endpoint
2. `yield session` provides session to endpoint
3. Endpoint runs with session
4. `with` block exits, session closes
5. Any open transaction commits (on success) or rolls back (on error)

## Transaction Management

### Auto-Commit Pattern

SQLModel uses auto-commit by default with `Session`:

```python
@app.post("/tasks", status_code=201)
def create_task(task_create: TaskCreate, session: Session = Depends(get_session)):
    task = Task.from_orm(task_create)
    session.add(task)
    session.commit()  # Explicit commit
    session.refresh(task)  # Reload to get DB-generated values
    return task
```

### Manual Transaction Control

```python
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404)

    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    # Explicit transaction control
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

## Error Handling & Rollback

### Automatic Rollback on Exception

```python
def get_session():
    """Auto-rollback on exception"""
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

@app.post("/tasks")
def create_task(task_create: TaskCreate, session: Session = Depends(get_session)):
    # If this raises an exception, session.rollback() is called automatically
    task = Task(**task_create.dict())
    session.add(task)
    session.commit()
    return task
```

### Explicit Error Handling

```python
from sqlalchemy.exc import IntegrityError

@app.post("/tasks")
def create_task(task_create: TaskCreate, session: Session = Depends(get_session)):
    try:
        task = Task(**task_create.dict())
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=422, detail="Duplicate task")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error")
```

## Query Patterns

### Simple Query

```python
@app.get("/tasks")
def list_tasks(session: Session = Depends(get_session)):
    # Query all tasks
    tasks = session.query(Task).all()
    return tasks
```

### Query with Filter

```python
@app.get("/tasks/by-status/{status}")
def get_tasks_by_status(status: str, session: Session = Depends(get_session)):
    tasks = session.query(Task).filter(Task.status == status).all()
    return tasks
```

### Query with Pagination

```python
from fastapi import Query

@app.get("/tasks")
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session)
):
    tasks = session.query(Task).offset(skip).limit(limit).all()
    return tasks
```

### Query with Multiple Filters

```python
from typing import Optional

@app.get("/tasks")
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = session.query(Task)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    return query.all()
```

## Read vs Detached Objects

### Issue: Session Expiration

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    return task  # ✅ Works: session still open

# Outside the endpoint, this fails:
task = get_task(1)
print(task.title)  # ❌ Error: DetachedInstanceError (session closed)
```

### Solution 1: Refresh Before Return

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    session.refresh(task)  # Load all lazy fields
    return task  # ✅ Now detached but data is loaded
```

### Solution 2: Use Response Models

```python
from sqlmodel import SQLModel

class TaskRead(SQLModel):
    id: int
    title: str
    status: str

@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    return task  # ✅ FastAPI converts to TaskRead schema
```

## Relationship Loading

### Lazy Loading (Default)

```python
class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author_id: int = Field(foreign_key="author.id")
    author: Optional[Author] = None

@app.get("/posts/{post_id}")
def get_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    # author is NOT loaded yet
    print(post.author)  # ❌ Error: DetachedInstanceError (relationship not loaded)
    return post
```

### Eager Loading with Relationship

```python
from sqlalchemy.orm import selectinload

@app.get("/posts/{post_id}")
def get_post(post_id: int, session: Session = Depends(get_session)):
    post = session.query(Post)\
        .options(selectinload(Post.author))\
        .filter(Post.id == post_id)\
        .first()
    # author IS loaded in same query
    return post  # ✅ Safe to access post.author
```

## Context Manager Patterns

### For Multiple Operations

```python
@app.post("/tasks/bulk")
def create_multiple_tasks(tasks_data: List[TaskCreate], session: Session = Depends(get_session)):
    """Create multiple tasks in one session"""
    tasks = []
    try:
        for task_data in tasks_data:
            task = Task(**task_data.dict())
            session.add(task)
            tasks.append(task)

        session.commit()  # Commit all at once
        for task in tasks:
            session.refresh(task)
        return tasks
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500)
```

### For Manual Session Management

```python
@app.post("/tasks/advanced")
def create_with_manual_session():
    """Manually create session (less common, use Depends instead)"""
    with Session(engine) as session:
        task = Task(title="Test")
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
```

## Testing Session Setup

```python
import pytest
from sqlmodel import create_engine, Session

@pytest.fixture
def test_engine():
    """In-memory test database"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def test_session(test_engine):
    """Test session"""
    with Session(test_engine) as session:
        yield session

@pytest.fixture
def test_client(test_session):
    """FastAPI test client with overridden session"""
    def get_session_override():
        return test_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_create_task(test_client):
    response = test_client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 201
```

## Performance Considerations

1. **Connection pooling**: Use `pool_size`, `max_overflow` (see neon-connection-setup.md)
2. **Lazy vs eager loading**: Use `selectinload()` to prevent N+1 queries
3. **Batch operations**: Use one session for multiple creates
4. **Index frequently-filtered columns**: `status`, `user_id`, `created_at`
5. **Use `.scalars()` for single column queries**: Faster than full objects
