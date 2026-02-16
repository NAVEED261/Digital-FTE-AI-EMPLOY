# Query Optimization

## N+1 Query Problem

### The Problem

```python
@app.get("/posts")
def get_posts(session: Session = Depends(get_session)):
    posts = session.query(Post).all()

    # For each post, this triggers a separate query for author
    for post in posts:
        print(post.author.name)  # ❌ 1 + N queries (1 for posts, N for authors)

    return posts
```

### Solution 1: Eager Loading with selectinload

```python
from sqlalchemy.orm import selectinload

@app.get("/posts")
def get_posts(session: Session = Depends(get_session)):
    posts = session.query(Post)\
        .options(selectinload(Post.author))\
        .all()  # ✅ 2 queries total (1 for posts, 1 for all authors)

    for post in posts:
        print(post.author.name)  # No extra queries

    return posts
```

### Solution 2: Eager Loading with joinedload

```python
from sqlalchemy.orm import joinedload

@app.get("/posts")
def get_posts(session: Session = Depends(get_session)):
    posts = session.query(Post)\
        .options(joinedload(Post.author))\
        .all()  # ✅ 1 query with JOIN (fastest)

    return posts
```

### Solution 3: Explicit Join

```python
@app.get("/posts")
def get_posts(session: Session = Depends(get_session)):
    posts = session.query(Post, Author)\
        .outerjoin(Author)\
        .all()  # ✅ 1 query (manual join)

    return posts
```

## Index Usage

### Index Frequently-Filtered Columns

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)  # Index for WHERE title = X
    status: str = Field(index=True)  # Index for WHERE status = X
    user_id: int = Field(index=True)  # Index for WHERE user_id = X
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True  # Index for date range queries
    )
```

### Composite Index

```python
from sqlalchemy import Index

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    status: str
    created_at: datetime

    # Composite index for frequently-filtered combo
    __table_args__ = (
        Index("idx_user_status_created", "user_id", "status", "created_at"),
    )

@app.get("/orders")
def get_user_orders(user_id: int, session: Session = Depends(get_session)):
    # This query uses the composite index
    orders = session.query(Order)\
        .filter(Order.user_id == user_id)\
        .filter(Order.status == "completed")\
        .order_by(Order.created_at.desc())\
        .all()
    return orders
```

## Query Efficiency Patterns

### Use .scalars() for Single Column

```python
# ❌ Slow: Gets full objects
ids = session.query(Task.id).all()  # Returns List[Tuple[int]]

# ✅ Fast: Gets single column
ids = session.query(Task.id).scalars().all()  # Returns List[int]
```

### Avoid SELECT *

```python
# ❌ Gets all columns
tasks = session.query(Task).all()

# ✅ Gets only needed columns
from sqlalchemy import select
tasks = session.query(Task.id, Task.title, Task.status).all()
```

### Use COUNT Efficiently

```python
from sqlalchemy import func

# ❌ Slow: Gets all records in memory
count = len(session.query(Task).all())

# ✅ Fast: COUNT at database level
count = session.query(func.count(Task.id)).scalar()
```

### Limit Query Results

```python
# ❌ Gets 10,000 records to return 10
tasks = session.query(Task).all()[:10]

# ✅ Database returns only 10
tasks = session.query(Task).limit(10).all()
```

## Filtering Optimization

### Use .filter() on Indexed Columns First

```python
# ❌ Less efficient: Filters after join
posts = session.query(Post)\
    .join(Author)\
    .filter(Post.status == "published")\
    .filter(Author.is_active == True)\
    .all()

# ✅ More efficient: Filter indexed columns first
posts = session.query(Post)\
    .filter(Post.status == "published")\  # Indexed, filtered first
    .join(Author)\
    .filter(Author.is_active == True)\
    .all()
```

### Batch Filters for IN Clauses

```python
# ❌ Multiple OR filters
tasks = session.query(Task).filter(
    (Task.status == "todo") |
    (Task.status == "in_progress") |
    (Task.status == "done")
).all()

# ✅ Use IN clause (more efficient)
tasks = session.query(Task).filter(
    Task.status.in_(["todo", "in_progress", "done"])
).all()
```

## Pagination Optimization

### Offset-Limit Pattern

```python
@app.get("/tasks")
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session)
):
    # ⚠️ Offset is slow for large skips (must scan through all skipped rows)
    tasks = session.query(Task)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return tasks
```

### Cursor-Based Pagination (Better for Large Datasets)

```python
@app.get("/tasks")
def list_tasks(
    cursor: Optional[int] = Query(None),  # ID of last item from previous page
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Efficient pagination using cursor"""
    query = session.query(Task).order_by(Task.id)

    if cursor:
        query = query.filter(Task.id > cursor)

    tasks = query.limit(limit).all()
    return tasks
```

### Keyset-Based Pagination (For Sorted Results)

```python
@app.get("/tasks")
def list_tasks(
    cursor_date: Optional[str] = Query(None),  # ISO format datetime
    cursor_id: Optional[int] = Query(None),  # Tiebreaker
    limit: int = Query(50),
    session: Session = Depends(get_session)
):
    """Efficient pagination for sorted results"""
    query = session.query(Task).order_by(Task.created_at.desc(), Task.id.desc())

    if cursor_date and cursor_id:
        from datetime import datetime
        cursor_dt = datetime.fromisoformat(cursor_date)
        query = query.filter(
            (Task.created_at < cursor_dt) |
            ((Task.created_at == cursor_dt) & (Task.id < cursor_id))
        )

    tasks = query.limit(limit).all()
    return tasks
```

## Query Caching

### Function-Level Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

last_cache_time = None
cached_stats = None

@app.get("/tasks/stats")
def get_task_stats(session: Session = Depends(get_session)):
    """Cache expensive aggregation queries"""
    global last_cache_time, cached_stats

    now = datetime.utcnow()
    if cached_stats and last_cache_time and (now - last_cache_time) < timedelta(minutes=5):
        return cached_stats

    from sqlalchemy import func

    cached_stats = {
        "total": session.query(func.count(Task.id)).scalar(),
        "by_status": dict(
            session.query(Task.status, func.count())\
                .group_by(Task.status)\
                .all()
        )
    }
    last_cache_time = now
    return cached_stats
```

### Redis-Based Caching (Production)

```python
import redis
import json
from datetime import timedelta

cache = redis.Redis(host="localhost", port=6379, decode_responses=True)
CACHE_TTL = 300  # 5 minutes

@app.get("/tasks/stats")
def get_task_stats(session: Session = Depends(get_session)):
    """Cache with Redis"""
    cache_key = "task_stats"
    cached = cache.get(cache_key)

    if cached:
        return json.loads(cached)

    stats = session.query(func.count(Task.id)).scalar()

    cache.setex(cache_key, CACHE_TTL, json.dumps(stats))
    return stats
```

## Connection Pooling

### Configure Pool Size

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=20,  # Base connections
    max_overflow=10,  # Extra connections
    pool_pre_ping=True,  # Verify before use
    pool_recycle=3600,  # Recycle after 1 hour
)
```

### Pool Parameters Explained

- **pool_size=20**: Number of connections to keep in pool (increase for high concurrency)
- **max_overflow=10**: Additional connections beyond pool_size (for temporary spikes)
- **pool_pre_ping=True**: Send test query to verify connection (prevents stale connections)
- **pool_recycle=3600**: Recycle connections after N seconds (prevents timeout)

## Async Queries (FastAPI async endpoints)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@host/db"
)

async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session

@app.get("/tasks")
async def get_tasks(session: AsyncSession = Depends(get_async_session)):
    """Async query (non-blocking)"""
    result = await session.execute(
        select(Task).options(selectinload(Task.author))
    )
    tasks = result.scalars().all()
    return tasks
```

## Query Analysis Tools

### Enable SQL Logging

```python
import logging

# Log all SQL queries
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

engine = create_engine("...", echo=True)  # Also logs in create_engine
```

### Use EXPLAIN PLAN

```python
@app.get("/tasks/explain")
def explain_query(session: Session = Depends(get_session)):
    """See how database executes query"""
    from sqlalchemy import text

    result = session.execute(
        text("EXPLAIN SELECT * FROM task WHERE status = :status"),
        {"status": "todo"}
    )

    for row in result:
        print(row)  # Shows query plan

    return {"plan": [row[0] for row in result]}
```

## Best Practices Summary

1. **Index frequently-filtered columns** → 10-100x faster queries
2. **Eager load relationships** → Prevent N+1 queries
3. **Use pagination** → Limit results at DB level, not in Python
4. **Use COUNT for aggregations** → Not len(session.query())
5. **Filter indexed columns first** → More efficient join plans
6. **Use cursor-based pagination** → For large offset values
7. **Configure connection pooling** → For high-concurrency apps
8. **Cache expensive queries** → Stats, aggregations, read-only data
9. **Monitor with EXPLAIN PLAN** → Understand query performance
10. **Use async queries** → For FastAPI async endpoints
