# Database Integration with SQLModel

> **Official Docs**: [SQLModel Docs](https://sqlmodel.tiangolo.com/)

## Installation

```bash
pip install sqlmodel
# For PostgreSQL (Neon)
pip install psycopg2-binary
# or async
pip install asyncpg
```

## SQLModel Table Definition

```python
from datetime import datetime
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    """Task database model."""
    __tablename__ = "tasks"  # Optional: explicit table name

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: str = Field(default="todo", index=True)
    priority: str = Field(default="medium")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
```

## Engine Setup

### SQLite (Development)

```python
from sqlmodel import create_engine, SQLModel

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL statements
    connect_args={"check_same_thread": False}  # Required for SQLite
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### PostgreSQL / Neon (Production)

```python
from sqlmodel import create_engine

# Neon connection string format
DATABASE_URL = "postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Disable in production
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
)
```

## Session Management

### Sync Session Dependency

```python
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

# Usage
@app.get("/tasks")
def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()
```

### Session with Transaction Control

```python
def get_session():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
```

## CRUD Operations

### Create

```python
from sqlmodel import Session

@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)  # Load generated fields (id, created_at)
    return db_task
```

### Read Single

```python
@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)  # Get by primary key
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### Read List with Filters

```python
from sqlmodel import select

@app.get("/tasks", response_model=list[TaskRead])
def list_tasks(
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    session: Session = Depends(get_session)
):
    query = select(Task)

    if status:
        query = query.where(Task.status == status)

    query = query.offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return tasks
```

### Update

```python
@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update fields that were set in the request
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Delete

```python
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
```

## Auto-managed Timestamps

```python
from datetime import datetime
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

    # Set once on creation
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Updated on every change
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Set when status becomes "done"
    completed_at: datetime | None = None

# In update endpoint:
def update_task(task_id: int, task_update: TaskUpdate, session: Session):
    task = session.get(Task, task_id)

    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    # Auto-update timestamp
    task.updated_at = datetime.utcnow()

    # Auto-set completed_at when done
    if task_update.status == "done" and not task.completed_at:
        task.completed_at = datetime.utcnow()
    elif task_update.status != "done":
        task.completed_at = None  # Clear if reverting from done

    session.commit()
    return task
```

## Relationships

### One-to-Many

```python
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Relationship: User has many tasks
    tasks: list["Task"] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

    # Foreign key
    owner_id: int | None = Field(default=None, foreign_key="user.id")

    # Relationship: Task belongs to User
    owner: User | None = Relationship(back_populates="tasks")
```

### Many-to-Many

```python
class TaskTagLink(SQLModel, table=True):
    """Association table for Task-Tag many-to-many."""
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)

class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    tasks: list["Task"] = Relationship(
        back_populates="tags",
        link_model=TaskTagLink
    )

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

    tags: list[Tag] = Relationship(
        back_populates="tasks",
        link_model=TaskTagLink
    )
```

## Query Patterns

### Filtering

```python
from sqlmodel import select

# Single condition
query = select(Task).where(Task.status == "todo")

# Multiple conditions (AND)
query = select(Task).where(
    Task.status == "todo",
    Task.priority == "high"
)

# OR conditions
from sqlmodel import or_
query = select(Task).where(
    or_(Task.priority == "high", Task.priority == "urgent")
)

# IN clause
query = select(Task).where(Task.status.in_(["todo", "in_progress"]))

# LIKE
query = select(Task).where(Task.title.contains("urgent"))

# Comparison
query = select(Task).where(Task.created_at >= some_date)
```

### Sorting

```python
from sqlmodel import asc, desc

# Ascending
query = select(Task).order_by(asc(Task.created_at))

# Descending
query = select(Task).order_by(desc(Task.created_at))

# Multiple columns
query = select(Task).order_by(desc(Task.priority), asc(Task.created_at))
```

### Aggregations

```python
from sqlmodel import func, select

# Count
count = session.exec(select(func.count(Task.id))).one()

# Group by
query = select(Task.status, func.count(Task.id)).group_by(Task.status)
results = session.exec(query).all()  # [("todo", 5), ("done", 3)]
```

### Joins

```python
# Explicit join
query = select(Task, User).join(User).where(User.id == 1)

# Select with relationship loaded
query = select(Task).options(selectinload(Task.owner))
```

## Connection Pooling

```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Connections to keep open
    max_overflow=10,       # Extra connections when pool exhausted
    pool_timeout=30,       # Seconds to wait for connection
    pool_recycle=1800,     # Recycle connections after 30 min
    pool_pre_ping=True,    # Test connections before use
)
```

## Neon PostgreSQL Setup

### Connection String

```python
# Format for Neon
DATABASE_URL = "postgresql://[user]:[password]@[host]/[database]?sslmode=require"

# Example
DATABASE_URL = "postgresql://myuser:mypass@ep-cool-rain-123456.us-east-2.aws.neon.tech/mydb?sslmode=require"
```

### Full Setup

```python
# database.py
from sqlmodel import SQLModel, Session, create_engine
from functools import lru_cache

@lru_cache
def get_engine():
    from .config import get_settings
    settings = get_settings()

    return create_engine(
        settings.database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=settings.debug,
    )

def create_db_and_tables():
    SQLModel.metadata.create_all(get_engine())

def get_session():
    with Session(get_engine()) as session:
        yield session
```

### Environment Configuration

```bash
# .env
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/db?sslmode=require
```

## Async Database (Optional)

```python
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Async engine (note: postgresql+asyncpg)
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
async_engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(async_engine, class_=AsyncSession)

async def get_async_session():
    async with async_session() as session:
        yield session

# Async endpoint
@app.get("/tasks")
async def list_tasks(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Task))
    return result.all()
```

## Testing with In-Memory Database

```python
# conftest.py
import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
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
```

## Common Patterns

### Soft Delete

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    deleted_at: datetime | None = None  # Soft delete marker

# Soft delete
def soft_delete_task(task_id: int, session: Session):
    task = session.get(Task, task_id)
    task.deleted_at = datetime.utcnow()
    session.commit()

# Query excludes deleted
query = select(Task).where(Task.deleted_at.is_(None))
```

### Optimistic Locking

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    version: int = Field(default=1)  # Version for optimistic locking

def update_task(task_id: int, task_update: TaskUpdate, session: Session):
    task = session.get(Task, task_id)

    # Check version matches
    if task.version != task_update.version:
        raise HTTPException(status_code=409, detail="Resource was modified")

    task.version += 1  # Increment version
    # ... apply updates
    session.commit()
```

### Bulk Insert

```python
def bulk_create_tasks(tasks: list[TaskCreate], session: Session):
    db_tasks = [Task.model_validate(t) for t in tasks]
    session.add_all(db_tasks)
    session.commit()
    return db_tasks
```
