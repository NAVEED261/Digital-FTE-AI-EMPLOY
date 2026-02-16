---
name: todo-task-manager
description: |
  Use when building task management applications with CRUD operations for tasks, priorities, and status tracking.
  Also use for implementing task filtering, sorting, completion tracking, and simple task workflows.
  NOT when building complex project management systems (use project-management-tools for that).
---

# ToDo Task Manager

A simple task management system for tracking, organizing, and completing tasks. This skill provides patterns for building task management features with priority levels, status tracking, and efficient task queries.

## Quick Start: Task Models

```python
# app/models/task.py
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(SQLModel, table=True):
    """Task model for database."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, index=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Relationship
    owner: "User" = Relationship(back_populates="tasks")

class TaskCreate(SQLModel):
    """Schema for creating task."""
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskUpdate(SQLModel):
    """Schema for updating task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

class TaskRead(SQLModel):
    """Schema for reading task."""
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    user_id: int
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

## Core Patterns

### 1. Task CRUD Operations

```python
# app/crud/tasks.py
from datetime import datetime
from sqlmodel import Session, select
from app.models import Task, TaskStatus, TaskPriority
from app.schemas import TaskCreate, TaskUpdate

def get_task(session: Session, task_id: int, user_id: int) -> Task:
    """Get task by ID (user-owned)."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    return session.exec(statement).first()

def get_user_tasks(
    session: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> list[Task]:
    """Get all tasks for user."""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(Task.priority.desc(), Task.created_at.desc())
    )
    return session.exec(statement).all()

def create_task(
    session: Session,
    task_create: TaskCreate,
    user_id: int
) -> Task:
    """Create new task."""
    task = Task(
        **task_create.dict(),
        user_id=user_id
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def update_task(
    session: Session,
    db_task: Task,
    task_update: TaskUpdate
) -> Task:
    """Update task."""
    update_data = task_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # If status changed to DONE, set completed_at
    if update_data.get("status") == TaskStatus.DONE:
        update_data["completed_at"] = datetime.utcnow()
    elif update_data.get("status") != TaskStatus.DONE:
        update_data["completed_at"] = None

    for key, value in update_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def delete_task(session: Session, task_id: int, user_id: int) -> bool:
    """Delete task."""
    task = get_task(session, task_id, user_id)
    if not task:
        return False
    session.delete(task)
    session.commit()
    return True

def complete_task(session: Session, task_id: int, user_id: int) -> Task:
    """Mark task as complete."""
    task = get_task(session, task_id, user_id)
    if task:
        task.status = TaskStatus.DONE
        task.completed_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
    return task
```

### 2. Task Filtering and Sorting

```python
# app/crud/tasks.py (continued)
from sqlalchemy import desc, asc

def get_tasks_by_status(
    session: Session,
    user_id: int,
    status: TaskStatus
) -> list[Task]:
    """Get tasks filtered by status."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.status == status
    )
    return session.exec(statement).all()

def get_tasks_by_priority(
    session: Session,
    user_id: int,
    priority: TaskPriority
) -> list[Task]:
    """Get tasks filtered by priority."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.priority == priority
    )
    return session.exec(statement).all()

def get_overdue_tasks(session: Session, user_id: int) -> list[Task]:
    """Get overdue tasks."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.status != TaskStatus.DONE,
        Task.due_date < datetime.utcnow()
    )
    return session.exec(statement).all()

def get_tasks_sorted(
    session: Session,
    user_id: int,
    sort_by: str = "priority",
    reverse: bool = False
) -> list[Task]:
    """Get tasks with custom sorting."""
    sort_field = {
        "priority": Task.priority,
        "created": Task.created_at,
        "due_date": Task.due_date,
        "status": Task.status
    }.get(sort_by, Task.priority)

    order = desc(sort_field) if reverse else asc(sort_field)

    statement = select(Task).where(
        Task.user_id == user_id
    ).order_by(order)

    return session.exec(statement).all()

def search_tasks(
    session: Session,
    user_id: int,
    query: str
) -> list[Task]:
    """Search tasks by title or description."""
    statement = select(Task).where(
        Task.user_id == user_id,
        (Task.title.ilike(f"%{query}%") |
         Task.description.ilike(f"%{query}%"))
    )
    return session.exec(statement).all()
```

### 3. API Endpoints

```python
# app/api/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models import Task, TaskStatus, TaskPriority, User
from app.schemas import TaskCreate, TaskRead, TaskUpdate
from app.api.deps import get_current_user, get_session
from app.crud import tasks as crud_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create new task."""
    return crud_tasks.create_task(session, task_in, current_user.id)

@router.get("/", response_model=list[TaskRead])
def list_tasks(
    skip: int = 0,
    limit: int = 50,
    status: TaskStatus = None,
    priority: TaskPriority = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List user's tasks with optional filters."""
    if status:
        return crud_tasks.get_tasks_by_status(session, current_user.id, status)
    if priority:
        return crud_tasks.get_tasks_by_priority(session, current_user.id, priority)
    return crud_tasks.get_user_tasks(session, current_user.id, skip, limit)

@router.get("/overdue", response_model=list[TaskRead])
def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get user's overdue tasks."""
    return crud_tasks.get_overdue_tasks(session, current_user.id)

@router.get("/search", response_model=list[TaskRead])
def search_tasks(
    q: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Search tasks by title or description."""
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters"
        )
    return crud_tasks.search_tasks(session, current_user.id, q)

@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get specific task."""
    task = crud_tasks.get_task(session, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update task."""
    task = crud_tasks.get_task(session, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return crud_tasks.update_task(session, task, task_in)

@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Mark task as complete."""
    task = crud_tasks.complete_task(session, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete task."""
    success = crud_tasks.delete_task(session, task_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
```

### 4. Task Statistics

```python
# app/crud/tasks.py (continued)
from sqlalchemy import func

def get_task_statistics(session: Session, user_id: int) -> dict:
    """Get task statistics for user."""
    # Total tasks
    total = session.query(func.count(Task.id)).filter(
        Task.user_id == user_id
    ).scalar()

    # By status
    by_status = {}
    for status in TaskStatus:
        count = session.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.status == status
        ).scalar()
        by_status[status.value] = count

    # By priority
    by_priority = {}
    for priority in TaskPriority:
        count = session.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.priority == priority
        ).scalar()
        by_priority[priority.value] = count

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "completion_rate": (
            by_status.get(TaskStatus.DONE.value, 0) / total * 100
            if total > 0 else 0
        )
    }

@router.get("/stats", response_model=dict)
def get_statistics(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get task statistics."""
    return crud_tasks.get_task_statistics(session, current_user.id)
```

## Best Practices

1. **Use enums** for status and priority
2. **Add timestamps** for created_at and updated_at
3. **Track completion** with completed_at
4. **Support filtering** by status and priority
5. **Enable searching** for discoverability
6. **Implement sorting** by priority and date
7. **Use indexes** on frequently queried fields
8. **Enforce user isolation** - users can only see their tasks
9. **Soft deletes** - mark as deleted rather than removing
10. **Simple over complex** - avoid unnecessary features

## Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks Table
CREATE TABLE tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('todo', 'in_progress', 'done') DEFAULT 'todo',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    user_id INT NOT NULL,
    due_date DATETIME,
    completed_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_status (user_id, status),
    INDEX idx_user_priority (user_id, priority),
    INDEX idx_due_date (due_date)
);
```

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Task Management Best Practices](https://en.wikipedia.org/wiki/Task_management)
