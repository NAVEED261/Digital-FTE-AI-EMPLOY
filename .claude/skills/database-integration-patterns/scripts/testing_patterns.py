"""
Testing patterns for database integrations
Demonstrates pytest fixtures, test database setup, and CRUD test patterns
"""

import pytest
from typing import Optional, List
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Field, Session, create_engine

# ============================================================================
# DATABASE MODELS (same as in your app)
# ============================================================================

class Task(SQLModel, table=True):
    """Database model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = None
    status: str = Field(default="todo")
    priority: str = Field(default="medium")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class TaskCreate(SQLModel):
    """Create schema"""
    title: str
    description: Optional[str] = None
    priority: str = "medium"


# ============================================================================
# FIXTURES (Setup for tests)
# ============================================================================

@pytest.fixture(name="test_engine")
def test_engine_fixture():
    """In-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="db_session")
def db_session_fixture(test_engine):
    """Database session for tests"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(db_session):
    """FastAPI test client with overridden database"""
    # Import app after models are defined (in real project, import at top)
    from fastapi import FastAPI, Depends

    app = FastAPI()

    def get_session_override():
        return db_session

    # This would be where you import your actual app and override it
    # app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    # app.dependency_overrides.clear()


# ============================================================================
# BASIC CRUD TESTS
# ============================================================================

class TestCreateTask:
    """Tests for task creation"""

    def test_create_minimal_task(self, db_session):
        """Create task with only required fields"""
        task = Task(title="Test Task")
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status == "todo"
        assert task.priority == "medium"
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_create_task_with_all_fields(self, db_session):
        """Create task with all fields specified"""
        now = datetime.utcnow()
        task = Task(
            title="Complex Task",
            description="Detailed description",
            status="in_progress",
            priority="high"
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.title == "Complex Task"
        assert task.description == "Detailed description"
        assert task.status == "in_progress"
        assert task.priority == "high"

    @pytest.mark.parametrize("invalid_title", [
        "",  # Empty
        "x" * 256,  # Too long
        None,  # Missing
    ])
    def test_invalid_task_creation(self, db_session, invalid_title):
        """Test validation on creation"""
        with pytest.raises(Exception):  # ValidationError or similar
            task = Task(title=invalid_title)
            db_session.add(task)
            db_session.commit()


class TestReadTask:
    """Tests for task retrieval"""

    @pytest.fixture(autouse=True)
    def setup_tasks(self, db_session):
        """Create test tasks for retrieval tests"""
        tasks = [
            Task(title="Task 1", status="todo"),
            Task(title="Task 2", status="in_progress"),
            Task(title="Task 3", status="done"),
        ]
        db_session.add_all(tasks)
        db_session.commit()

    def test_get_single_task(self, db_session):
        """Retrieve single task by ID"""
        task = db_session.query(Task).filter(Task.id == 1).first()
        assert task is not None
        assert task.title == "Task 1"

    def test_get_all_tasks(self, db_session):
        """Retrieve all tasks"""
        tasks = db_session.query(Task).all()
        assert len(tasks) == 3

    def test_filter_by_status(self, db_session):
        """Filter tasks by status"""
        tasks = db_session.query(Task).filter(Task.status == "done").all()
        assert len(tasks) == 1
        assert tasks[0].title == "Task 3"

    def test_pagination(self, db_session):
        """Test pagination with offset and limit"""
        tasks = db_session.query(Task).offset(1).limit(2).all()
        assert len(tasks) == 2


class TestUpdateTask:
    """Tests for task updates"""

    @pytest.fixture(autouse=True)
    def setup_task(self, db_session):
        """Create a task to update"""
        task = Task(title="Original", status="todo")
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    def test_update_title(self, db_session):
        """Update task title"""
        task = db_session.query(Task).first()
        original_created_at = task.created_at
        original_updated_at = task.updated_at

        import time
        time.sleep(0.01)  # Ensure time difference

        task.title = "Updated Title"
        task.updated_at = datetime.utcnow()
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.title == "Updated Title"
        assert task.created_at == original_created_at
        assert task.updated_at > original_updated_at

    def test_update_status_sets_completed_at(self, db_session):
        """Status change to 'done' sets completed_at"""
        task = db_session.query(Task).first()

        task.status = "done"
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.status == "done"
        assert task.completed_at is not None

    def test_partial_update(self, db_session):
        """Update only specific fields"""
        task = db_session.query(Task).first()

        # Only update priority, leave other fields alone
        task.priority = "high"
        task.updated_at = datetime.utcnow()
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.priority == "high"
        assert task.title == "Original"  # Unchanged


class TestDeleteTask:
    """Tests for task deletion"""

    def test_delete_task(self, db_session):
        """Delete a task"""
        task = Task(title="To Delete")
        db_session.add(task)
        db_session.commit()
        task_id = task.id

        db_session.delete(task)
        db_session.commit()

        # Verify it's gone
        deleted = db_session.query(Task).filter(Task.id == task_id).first()
        assert deleted is None

    def test_delete_nonexistent_task(self, db_session):
        """Attempting to delete nonexistent task"""
        # Should not raise error, but return None
        task = db_session.query(Task).filter(Task.id == 9999).first()
        assert task is None


# ============================================================================
# AGGREGATION TESTS
# ============================================================================

class TestAggregations:
    """Tests for statistics and aggregations"""

    @pytest.fixture(autouse=True)
    def setup_tasks(self, db_session):
        """Create tasks for aggregation tests"""
        tasks = [
            Task(title="Task 1", status="todo", priority="high"),
            Task(title="Task 2", status="in_progress", priority="medium"),
            Task(title="Task 3", status="done", priority="low", completed_at=datetime.utcnow()),
            Task(title="Task 4", status="done", priority="high", completed_at=datetime.utcnow()),
        ]
        db_session.add_all(tasks)
        db_session.commit()

    def test_count_total_tasks(self, db_session):
        """Count total tasks"""
        from sqlalchemy import func
        count = db_session.query(func.count(Task.id)).scalar()
        assert count == 4

    def test_count_by_status(self, db_session):
        """Count tasks grouped by status"""
        from sqlalchemy import func
        results = db_session.query(
            Task.status,
            func.count(Task.id).label("count")
        ).group_by(Task.status).all()

        status_counts = {status: count for status, count in results}
        assert status_counts["todo"] == 1
        assert status_counts["in_progress"] == 1
        assert status_counts["done"] == 2

    def test_completion_rate(self, db_session):
        """Calculate completion rate"""
        from sqlalchemy import func
        total = db_session.query(func.count(Task.id)).scalar()
        completed = db_session.query(func.count(Task.id))\
            .filter(Task.completed_at.isnot(None)).scalar()

        rate = (completed / total * 100) if total > 0 else 0
        assert rate == 50.0


# ============================================================================
# TRANSACTION TESTS
# ============================================================================

class TestTransactions:
    """Tests for transaction handling"""

    def test_commit_saves_changes(self, db_session):
        """Commit persists changes"""
        task = Task(title="New Task")
        db_session.add(task)
        db_session.commit()

        # Retrieve in new session to verify persistence
        retrieved = db_session.query(Task).filter(
            Task.title == "New Task"
        ).first()
        assert retrieved is not None

    def test_rollback_discards_changes(self, db_session):
        """Rollback discards uncommitted changes"""
        task = Task(title="Rollback Test")
        db_session.add(task)
        db_session.rollback()

        # Task should not be saved
        retrieved = db_session.query(Task).filter(
            Task.title == "Rollback Test"
        ).first()
        assert retrieved is None


# ============================================================================
# RUNNING TESTS
# ============================================================================
# Run all tests:
#   pytest testing_patterns.py -v
#
# Run specific test class:
#   pytest testing_patterns.py::TestCreateTask -v
#
# Run single test:
#   pytest testing_patterns.py::TestCreateTask::test_create_minimal_task -v
#
# With coverage:
#   pytest testing_patterns.py --cov=your_module
#
# Show print statements:
#   pytest testing_patterns.py -v -s
