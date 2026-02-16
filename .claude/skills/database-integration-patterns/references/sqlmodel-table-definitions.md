# SQLModel Table Definitions

## Basic Table Structure

```python
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    """Complete task model with all patterns"""
    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Required fields with constraints
    title: str = Field(
        index=True,  # Index for filtering
        max_length=255,
        description="Task title"
    )

    # Optional fields
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Detailed description"
    )

    # Enum-like fields (use string type)
    status: str = Field(default="todo")  # Values: "todo", "in_progress", "done"
    priority: str = Field(default="medium")  # Values: "low", "medium", "high", "urgent"

    # DateTime fields with auto-management
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Created timestamp (immutable)"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last modified timestamp (auto-updated)"
    )
    due_date: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Set when status changes to 'done'"
    )
```

## Table Naming Conventions

```python
from sqlalchemy import Table

class User(SQLModel, table=True):
    # SQLModel uses lowercase table name by default: "user"
    __tablename__ = "users"  # Override if needed
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
```

## Field Constraints and Validation

### String Fields

```python
class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Length constraints
    title: str = Field(max_length=200)  # Enforced at DB level

    # Email format (client-side validation in FastAPI)
    email: str = Field(regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")

    # Required vs optional
    name: str  # NOT NULL constraint
    slug: Optional[str] = None  # NULL allowed

    # Indexed fields (for filtering)
    category: str = Field(index=True)  # Creates database index
```

### Numeric Fields

```python
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Integer constraints
    quantity: int = Field(ge=0)  # >= 0
    rating: int = Field(ge=1, le=5)  # Between 1-5

    # Float/Decimal for money (use str type to avoid float precision issues)
    price: str = Field(max_length=10)  # Store as "99.99" or use Decimal

    # Boolean
    is_active: bool = Field(default=True)
```

### DateTime Fields

```python
from datetime import datetime, timedelta

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Timestamp with auto-generation
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Future date field
    starts_at: datetime
    ends_at: Optional[datetime] = None

    # Calculated field (not stored, computed at runtime)
    # duration: timedelta  # This won't store in DB, use in Python only
```

## Relationships (One-to-Many)

```python
from typing import List

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Relationship field (not stored in this table)
    posts: List["Post"] = []

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    # Foreign key
    author_id: int = Field(foreign_key="author.id")

    # Relationship field (loaded on demand)
    author: Optional[Author] = None
```

## Unique Constraints

```python
from sqlalchemy import Column, String, UniqueConstraint

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)  # Unique constraint
    email: str = Field(unique=True)

    # Or use SQLAlchemy constraint
    __table_args__ = (
        UniqueConstraint("username", "email", name="uq_user_email"),
    )
```

## Indexes for Performance

```python
from sqlalchemy import Index

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Single column index
    user_id: int = Field(index=True)  # Speeds up WHERE user_id = X
    status: str = Field(index=True)  # Speeds up filtering
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True  # For date range queries
    )

    # Composite index (multiple columns)
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
    )
```

## Timestamps with Auto-Management

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    # Created timestamp (set once, never changes)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Set at creation, never modified"
    )

    # Updated timestamp (auto-updated on every PUT)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Updated on every modification"
    )

    # Completion timestamp (only set when status changes)
    completed_at: Optional[datetime] = None
```

### Auto-Management in API Endpoints

```python
from fastapi import HTTPException
from sqlmodel import Session, select

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Not found")

    # Update fields
    task_data = task_update.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)

    # Auto-update timestamp (don't manually set this!)
    task.updated_at = datetime.utcnow()

    # If status changed to "done", set completed_at
    if task_update.status == "done" and task.status != "done":
        task.completed_at = datetime.utcnow()
    elif task_update.status != "done" and task.status == "done":
        task.completed_at = None  # Clear if reverted from done

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## Best Practices

1. **Use `Optional` for nullable fields**: `Optional[str] = None`
2. **Index frequently-filtered columns**: `status`, `user_id`, `created_at`
3. **Use Field descriptions**: Helps auto-generate API documentation
4. **Set reasonable defaults**: `status: str = Field(default="active")`
5. **Never manually update `updated_at`**: Let the endpoint logic handle it
6. **Validate at DB level**: Use `max_length`, `ge`, `le` on Field
7. **Use immutable `created_at`**: Never allow client to set this
8. **Handle datetime in UTC**: Always use `datetime.utcnow()`, never `.now()`
