"""
Complete working example of database integration patterns
Demonstrates SQLModel, Neon connection, Session management, and CRUD operations
"""

from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy import func

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Log SQL queries
)


def create_db_and_tables():
    """Create all database tables on startup"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency that provides a database session"""
    with Session(engine) as session:
        yield session


# ============================================================================
# MODELS (SQLModel Table Definitions)
# ============================================================================

class TaskBase(SQLModel):
    """Shared fields for all task schemas"""
    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: str = Field(default="todo")  # "todo", "in_progress", "done"
    priority: str = Field(default="medium")  # "low", "medium", "high", "urgent"
    due_date: Optional[datetime] = None


class Task(TaskBase, table=True):
    """Database model with auto-managed timestamps"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for POST requests (no id, timestamps)"""
    pass


class TaskUpdate(SQLModel):
    """Schema for PUT requests (all fields optional)"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskRead(TaskBase):
    """Schema for GET responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(title="Task Management API")


@app.on_event("startup")
def on_startup():
    """Initialize database on app startup"""
    create_db_and_tables()


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

# CREATE - POST
@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(
    task_create: TaskCreate,
    session: Session = Depends(get_session)
):
    """Create a new task"""
    task = Task(**task_create.dict())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# READ - GET All
@app.get("/tasks", response_model=List[TaskRead])
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    """List tasks with pagination and filtering"""
    query = session.query(Task)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    tasks = query.offset(skip).limit(limit).all()
    return tasks


# READ - GET Single
@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Get a single task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# UPDATE - PUT
@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update a task"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only provided fields
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    # Auto-update timestamp
    task.updated_at = datetime.utcnow()

    # Handle status transitions
    if task_update.status == "done" and task.status != "done":
        task.completed_at = datetime.utcnow()
    elif task_update.status != "done" and task.completed_at is not None:
        task.completed_at = None

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# DELETE - DELETE
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Delete a task"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()


# ============================================================================
# SPECIAL OPERATIONS
# ============================================================================

@app.post("/tasks/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Mark task as completed"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "done"
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.get("/tasks/stats/overview")
def get_task_stats(session: Session = Depends(get_session)):
    """Get comprehensive task statistics"""
    total = session.query(func.count(Task.id)).scalar()

    by_status = session.query(
        Task.status,
        func.count(Task.id).label("count")
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


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================================
# TO RUN THIS EXAMPLE
# ============================================================================
# 1. Install dependencies:
#    pip install fastapi sqlmodel uvicorn
#
# 2. Run the app:
#    uvicorn complete_example:app --reload
#
# 3. Visit:
#    - http://localhost:8000/docs (Swagger UI)
#    - http://localhost:8000/redoc (ReDoc)
#
# 4. Test endpoints:
#    curl -X POST http://localhost:8000/tasks \
#      -H "Content-Type: application/json" \
#      -d '{"title": "Test Task", "priority": "high"}'
#
#    curl http://localhost:8000/tasks
#
#    curl http://localhost:8000/tasks/1
#
#    curl -X PUT http://localhost:8000/tasks/1 \
#      -H "Content-Type: application/json" \
#      -d '{"status": "in_progress"}'
#
#    curl -X DELETE http://localhost:8000/tasks/1
