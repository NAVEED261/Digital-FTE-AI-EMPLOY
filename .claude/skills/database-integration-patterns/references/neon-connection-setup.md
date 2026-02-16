# Neon Connection Setup

## Connection String Format

```
postgresql://user:password@host:port/database
postgresql://user:password@host/database?sslmode=require
```

### Neon Specific Format

```
postgresql://neon_user:neon_password@ep-xxxxx.us-east-1.aws.neon.tech/dbname?sslmode=require
```

## Environment Configuration

### .env file

```bash
# Development (SQLite)
DATABASE_URL=sqlite:///./tasks.db

# Production (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-1.aws.neon.tech/dbname?sslmode=require
```

### Load with python-dotenv

```python
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")
```

## Sync Connection Setup

```python
from sqlmodel import SQLModel, Session, create_engine

# For development (SQLite)
sqlite_url = "sqlite:///./tasks.db"
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    echo=True  # Log SQL queries
)

# For production (Neon/PostgreSQL)
neon_url = "postgresql://user:pass@host/db?sslmode=require"
engine = create_engine(
    neon_url,
    echo=False,
    future=True
)

# Create tables at startup
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency injection for endpoints
def get_session():
    with Session(engine) as session:
        yield session
```

## Async Connection Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa

# Async Neon connection (production)
async_neon_url = "postgresql+asyncpg://user:pass@host/db?ssl=require"

# Create async engine
async_engine = create_async_engine(
    async_neon_url,
    echo=False,
    future=True,
    pool_size=20,  # Connection pool size
    max_overflow=10,  # Max overflow beyond pool_size
    pool_pre_ping=True,  # Test connections before use
)

# Session factory
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Async dependency injection
async def get_async_session():
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Create tables (async)
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Connection Pooling

### For Production (Neon)

```python
from sqlalchemy.pool import NullPool, QueuePool

# Production configuration
engine = create_engine(
    neon_url,
    poolclass=QueuePool,
    pool_size=20,  # Active connections
    max_overflow=10,  # Additional connections
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600,  # Recycle after 1 hour
    echo=False,
)
```

### Connection Pool Settings

- **pool_size=20**: Base pool size (adjust based on app concurrency)
- **max_overflow=10**: Additional connections beyond base pool
- **pool_pre_ping=True**: Send test query before using connection
- **pool_recycle=3600**: Recycle connections after 1 hour (prevent stale connections)

## SSL/TLS Configuration

```python
import ssl

# For production with self-signed certs
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_engine(
    neon_url,
    connect_args={"ssl": ssl_context},
)

# Or use Neon's SSL support
# Connection string already includes ?sslmode=require
```

## Error Handling & Retries

```python
from sqlalchemy import event
from sqlalchemy.pool import Pool
from sqlalchemy.exc import OperationalError
import time

@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Called when connection is created"""
    dbapi_conn.isolation_level = None  # Autocommit

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Verify connection before use"""
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("SELECT 1")
    except OperationalError:
        raise DisconnectionError()
    finally:
        cursor.close()

# Retry logic for transient failures
def create_with_retry(url, max_retries=3, backoff_factor=1):
    for attempt in range(max_retries):
        try:
            return create_engine(url)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_factor * (2 ** attempt)
            print(f"Connection failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
```

## Development vs Production

### Development (SQLite)

```python
import os

if os.getenv("ENV") == "development":
    database_url = "sqlite:///./tasks.db"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=True  # Log SQL for debugging
    )
else:  # Production (Neon)
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(
        database_url,
        echo=False,
        pool_size=20,
        max_overflow=10,
    )
```

### Alembic Migrations (for schema changes)

```bash
# Install
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migration
alembic upgrade head
```

## Testing Database Setup

```python
import pytest
from sqlmodel import create_engine, Session, SQLModel

@pytest.fixture(name="session")
def session_fixture():
    """In-memory SQLite for tests"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """FastAPI test client with overridden DB"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

## Connection String Security

```python
import os
from dotenv import load_dotenv

# Never hardcode credentials
load_dotenv()

# Good: From environment variable
database_url = os.getenv("DATABASE_URL")

# Bad: Hardcoded
# database_url = "postgresql://user:password@host/db"

# Use Neon's connection pooler for serverless
# https://neon.tech/docs/connect/connection-pooling
pooler_url = os.getenv("DATABASE_POOLER_URL")  # For high-concurrency apps
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection timeout | Increase `pool_recycle`, check network access to Neon |
| "too many connections" | Reduce `pool_size`, enable connection pooling |
| SSL certificate error | Add `?sslmode=require` to connection string |
| Stale connections | Set `pool_pre_ping=True` and `pool_recycle=3600` |
| Connection pool exhaustion | Check for connections not being closed, use context managers |
