# CRUD Operations in FastAPI

> **Official Docs**: [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

## HTTP Methods Overview

| Method | CRUD | Typical Use | Idempotent |
|--------|------|-------------|------------|
| GET | Read | Retrieve resources | Yes |
| POST | Create | Create new resource | No |
| PUT | Update | Replace entire resource | Yes |
| PATCH | Update | Partial update | No |
| DELETE | Delete | Remove resource | Yes |

## Status Codes Reference

| Code | Name | When to Use |
|------|------|-------------|
| 200 | OK | GET, PUT, PATCH success |
| 201 | Created | POST success (resource created) |
| 204 | No Content | DELETE success (no body returned) |
| 400 | Bad Request | Malformed request syntax |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (duplicate) |
| 422 | Unprocessable Entity | Validation failed |
| 500 | Internal Server Error | Unexpected server error |

## Complete CRUD Implementation

```python
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select
from typing import Literal

router = APIRouter(prefix="/tasks", tags=["tasks"])

# CREATE - POST /tasks
@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session)
):
    """Create a new task."""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# READ (List) - GET /tasks
@router.get("/", response_model=list[TaskRead])
def list_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    status_filter: Literal["todo", "in_progress", "done"] | None = Query(
        None, alias="status", description="Filter by status"
    ),
    priority: Literal["low", "medium", "high", "urgent"] | None = None,
    session: Session = Depends(get_session)
):
    """List tasks with optional filtering and pagination."""
    query = select(Task)

    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority:
        query = query.where(Task.priority == priority)

    query = query.offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return tasks

# READ (Single) - GET /tasks/{task_id}
@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Get a single task by ID."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task

# UPDATE (Full) - PUT /tasks/{task_id}
@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update a task (partial update supported)."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    # Only update fields that were explicitly set
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task

# DELETE - DELETE /tasks/{task_id}
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Delete a task."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    session.delete(task)
    session.commit()
    # No return for 204 status
```

## Path Parameters

```python
from fastapi import Path

@router.get("/{task_id}")
def get_task(
    task_id: int = Path(..., gt=0, description="The task ID")
):
    ...
```

## Query Parameters

```python
from fastapi import Query
from typing import Literal

@router.get("/")
def list_tasks(
    # Required query param
    q: str = Query(..., min_length=1),

    # Optional with default
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),

    # Optional enum filter
    status: Literal["todo", "in_progress", "done"] | None = None,

    # List of values (?tag=a&tag=b)
    tags: list[str] | None = Query(None),

    # Alias for different query name
    sort_order: str = Query("asc", alias="order"),
):
    ...
```

## Pagination Pattern

### Offset-based Pagination

```python
@router.get("/", response_model=list[TaskRead])
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session)
):
    return session.exec(
        select(Task).offset(skip).limit(limit)
    ).all()
```

### Cursor-based Pagination (Better for Large Datasets)

```python
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    items: list[TaskRead]
    next_cursor: int | None
    has_more: bool

@router.get("/", response_model=PaginatedResponse)
def list_tasks(
    cursor: int | None = Query(None, description="Last seen ID"),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Task).order_by(Task.id)

    if cursor:
        query = query.where(Task.id > cursor)

    tasks = session.exec(query.limit(limit + 1)).all()

    has_more = len(tasks) > limit
    items = tasks[:limit]
    next_cursor = items[-1].id if items and has_more else None

    return PaginatedResponse(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more
    )
```

## Filtering Pattern

```python
@router.get("/", response_model=list[TaskRead])
def list_tasks(
    status: Literal["todo", "in_progress", "done"] | None = None,
    priority: Literal["low", "medium", "high", "urgent"] | None = None,
    search: str | None = Query(None, min_length=1),
    created_after: datetime | None = None,
    session: Session = Depends(get_session)
):
    query = select(Task)

    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if search:
        query = query.where(Task.title.contains(search))
    if created_after:
        query = query.where(Task.created_at >= created_after)

    return session.exec(query).all()
```

## Sorting Pattern

```python
from sqlmodel import asc, desc

@router.get("/", response_model=list[TaskRead])
def list_tasks(
    sort_by: Literal["created_at", "updated_at", "title", "priority"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    session: Session = Depends(get_session)
):
    query = select(Task)

    # Map field names to columns
    sort_columns = {
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
        "title": Task.title,
        "priority": Task.priority,
    }

    column = sort_columns[sort_by]
    if sort_order == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    return session.exec(query).all()
```

## Bulk Operations

### Bulk Create

```python
@router.post("/bulk", response_model=list[TaskRead], status_code=status.HTTP_201_CREATED)
def create_tasks_bulk(
    tasks: list[TaskCreate],
    session: Session = Depends(get_session)
):
    """Create multiple tasks at once."""
    if len(tasks) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 tasks per request"
        )

    db_tasks = [Task.model_validate(t) for t in tasks]
    session.add_all(db_tasks)
    session.commit()

    for task in db_tasks:
        session.refresh(task)

    return db_tasks
```

### Bulk Delete

```python
@router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT)
def delete_tasks_bulk(
    task_ids: list[int] = Query(..., min_length=1, max_length=100),
    session: Session = Depends(get_session)
):
    """Delete multiple tasks by ID."""
    statement = select(Task).where(Task.id.in_(task_ids))
    tasks = session.exec(statement).all()

    for task in tasks:
        session.delete(task)

    session.commit()
```

## Response Models

```python
from pydantic import BaseModel

# Use response_model for automatic serialization
@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    return task  # SQLModel object automatically converted to TaskRead

# For lists
@router.get("/", response_model=list[TaskRead])
def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()

# Exclude fields from response
@router.get("/", response_model=TaskRead, response_model_exclude={"internal_notes"})
def get_task(...):
    ...

# Include only specific fields
@router.get("/", response_model=TaskRead, response_model_include={"id", "title"})
def get_task(...):
    ...
```

## Action Endpoints (Beyond CRUD)

```python
# Mark task as complete
@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "done"
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task

# Assign task to user
@router.post("/{task_id}/assign/{user_id}", response_model=TaskRead)
def assign_task(
    task_id: int,
    user_id: int,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task.assignee_id = user_id
    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task
```

## Statistics Endpoint

```python
from pydantic import BaseModel
from sqlmodel import func

class TaskStats(BaseModel):
    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    completion_rate: float

@router.get("/stats/overview", response_model=TaskStats)
def get_task_stats(session: Session = Depends(get_session)):
    total = session.exec(select(func.count(Task.id))).one()

    # Count by status
    status_counts = session.exec(
        select(Task.status, func.count(Task.id))
        .group_by(Task.status)
    ).all()
    by_status = {status: count for status, count in status_counts}

    # Count by priority
    priority_counts = session.exec(
        select(Task.priority, func.count(Task.id))
        .group_by(Task.priority)
    ).all()
    by_priority = {priority: count for priority, count in priority_counts}

    # Calculate completion rate
    done_count = by_status.get("done", 0)
    completion_rate = (done_count / total * 100) if total > 0 else 0

    return TaskStats(
        total=total,
        by_status=by_status,
        by_priority=by_priority,
        completion_rate=round(completion_rate, 2)
    )
```
