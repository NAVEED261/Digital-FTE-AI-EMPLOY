# CRUD Operations

## Create (POST)

### Simple Create

```python
from fastapi import HTTPException
from sqlmodel import Session

@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(task_create: TaskCreate, session: Session = Depends(get_session)):
    """Create a new task"""
    task = Task.from_orm(task_create)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Create with Validation

```python
from pydantic import ValidationError

@app.post("/tasks", status_code=201)
def create_task(task_create: TaskCreate, session: Session = Depends(get_session)):
    """Validate before creating"""
    try:
        task = Task(**task_create.dict())
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### Create with Default Values

```python
from datetime import datetime

class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"  # Default

@app.post("/tasks", status_code=201)
def create_task(task_create: TaskCreate, session: Session = Depends(get_session)):
    # Auto-managed fields (don't set manually)
    task = Task(
        title=task_create.title,
        description=task_create.description,
        priority=task_create.priority,
        status="todo",  # Default status
        # created_at, updated_at auto-set by Field(default_factory=datetime.utcnow)
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Bulk Create

```python
@app.post("/tasks/bulk")
def create_multiple_tasks(tasks_data: List[TaskCreate], session: Session = Depends(get_session)):
    """Create multiple tasks efficiently"""
    tasks = [Task(**task_data.dict()) for task_data in tasks_data]

    try:
        session.add_all(tasks)
        session.commit()

        # Refresh all to get IDs and timestamps
        for task in tasks:
            session.refresh(task)

        return tasks
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

## Read (GET)

### Get Single Item

```python
@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    """Get task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### List All Items

```python
@app.get("/tasks", response_model=List[TaskRead])
def list_tasks(session: Session = Depends(get_session)):
    """Get all tasks"""
    tasks = session.query(Task).all()
    return tasks
```

### List with Pagination

```python
from fastapi import Query

@app.get("/tasks", response_model=List[TaskRead])
def list_tasks(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Records to return"),
    session: Session = Depends(get_session)
):
    """Get paginated task list"""
    tasks = session.query(Task).offset(skip).limit(limit).all()
    return tasks
```

### List with Filtering

```python
from typing import Optional

@app.get("/tasks")
def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    session: Session = Depends(get_session)
):
    """Get tasks with optional filters"""
    query = session.query(Task)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    return query.all()
```

### List with Sorting

```python
@app.get("/tasks")
def list_tasks(
    sort_by: str = Query("created_at", regex="^(created_at|priority|title)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    session: Session = Depends(get_session)
):
    """Get tasks sorted by field"""
    query = session.query(Task)

    # Map column names
    column_map = {
        "created_at": Task.created_at,
        "priority": Task.priority,
        "title": Task.title,
    }

    if order == "desc":
        query = query.order_by(column_map[sort_by].desc())
    else:
        query = query.order_by(column_map[sort_by].asc())

    return query.all()
```

### Search

```python
@app.get("/tasks/search")
def search_tasks(
    q: str = Query(..., min_length=1),
    session: Session = Depends(get_session)
):
    """Search tasks by title or description"""
    tasks = session.query(Task).filter(
        (Task.title.contains(q)) | (Task.description.contains(q))
    ).all()
    return tasks
```

## Update (PUT)

### Full Update

```python
class TaskUpdate(SQLModel):
    title: str
    description: Optional[str] = None
    status: str
    priority: str

@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update entire task"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update all fields
    update_data = task_update.dict()
    for key, value in update_data.items():
        setattr(task, key, value)

    # Auto-update timestamp (do NOT manually set this)
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Partial Update (PATCH)

```python
class TaskUpdate(SQLModel):
    """All fields optional for PATCH"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

@app.patch("/tasks/{task_id}", response_model=TaskRead)
def partial_update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update only provided fields"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update fields that were provided
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    # Auto-update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Update with State Transitions

```python
@app.put("/tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    new_status: str,
    session: Session = Depends(get_session)
):
    """Update status with automatic state management"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = new_status
    task.updated_at = datetime.utcnow()

    # Auto-set completed_at when status changes to "done"
    if new_status == "done":
        task.completed_at = datetime.utcnow()
    elif task.status != "done":
        # Clear completed_at if reverting from "done"
        task.completed_at = None

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Conditional Update (Optimistic Locking)

```python
from datetime import datetime

@app.put("/tasks/{task_id}")
def update_task_with_version(
    task_id: int,
    task_update: TaskUpdate,
    updated_at: str,  # Previous version timestamp
    session: Session = Depends(get_session)
):
    """Prevent concurrent updates"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check version matches
    if task.updated_at.isoformat() != updated_at:
        raise HTTPException(status_code=409, detail="Task was modified")

    # Update
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## Delete (DELETE)

### Simple Delete

```python
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """Delete a task"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
```

### Delete with Cascade

```python
# In Task model, use delete cascade
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    # In related model:
    subtasks: List["Subtask"] = Field(back_populates="task")

class Subtask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id", ondelete="CASCADE")
    task: Task = Field(back_populates="subtasks")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """Delete task and cascade to subtasks"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)  # Subtasks deleted automatically
    session.commit()
```

### Soft Delete (Mark as Deleted)

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    is_deleted: bool = Field(default=False)  # Soft delete flag

@app.delete("/tasks/{task_id}", status_code=204)
def soft_delete_task(task_id: int, session: Session = Depends(get_session)):
    """Mark task as deleted without removing from DB"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_deleted = True
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()

@app.get("/tasks")
def list_active_tasks(session: Session = Depends(get_session)):
    """Only return non-deleted tasks"""
    tasks = session.query(Task).filter(Task.is_deleted == False).all()
    return tasks
```

### Bulk Delete

```python
@app.delete("/tasks/bulk")
def delete_multiple_tasks(task_ids: List[int], session: Session = Depends(get_session)):
    """Delete multiple tasks"""
    try:
        session.query(Task).filter(Task.id.in_(task_ids)).delete()
        session.commit()
        return {"deleted": len(task_ids)}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

## Aggregation & Statistics

### Count

```python
@app.get("/tasks/count")
def count_tasks(session: Session = Depends(get_session)):
    """Get total task count"""
    from sqlalchemy import func
    count = session.query(func.count(Task.id)).scalar()
    return {"total": count}
```

### Group By

```python
@app.get("/tasks/stats")
def task_stats(session: Session = Depends(get_session)):
    """Get task counts by status"""
    from sqlalchemy import func

    results = session.query(
        Task.status,
        func.count(Task.id).label("count")
    ).group_by(Task.status).all()

    return {
        "by_status": {status: count for status, count in results}
    }
```

### Complex Aggregations

```python
@app.get("/tasks/overview")
def task_overview(session: Session = Depends(get_session)):
    """Get comprehensive task statistics"""
    from sqlalchemy import func

    total = session.query(func.count(Task.id)).scalar()
    by_status = session.query(
        Task.status,
        func.count().label("count")
    ).group_by(Task.status).all()

    completed = session.query(func.count(Task.id))\
        .filter(Task.completed_at.isnot(None)).scalar()

    completion_rate = (completed / total * 100) if total > 0 else 0

    return {
        "total": total,
        "by_status": {status: count for status, count in by_status},
        "completed": completed,
        "completion_rate": f"{completion_rate:.1f}%"
    }
```
