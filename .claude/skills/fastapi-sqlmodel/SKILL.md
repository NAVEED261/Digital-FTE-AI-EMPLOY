---
name: fastapi-sqlmodel
description: |
  Use when building FastAPI applications with SQLModel for database models, CRUD operations, and full-stack data management.
  Also use for implementing relationships, migrations, async queries, and type-safe database interactions with Pydantic integration.
  NOT when using other ORMs (SQLAlchemy directly, Tortoise ORM) or building non-FastAPI applications.
---

# FastAPI + SQLModel Integration

SQLModel combines SQLAlchemy and Pydantic, enabling you to define database models that are simultaneously valid Pydantic models for validation. This skill covers full-stack FastAPI + SQLModel development.

## Quick Start: Project Structure

```
app/
├── models/
│   ├── __init__.py
│   ├── user.py          # User model + schema
│   ├── item.py          # Item model + schema
│   └── base.py          # Base model with common fields
├── crud/
│   ├── __init__.py
│   ├── users.py         # User CRUD operations
│   └── items.py         # Item CRUD operations
├── schemas/
│   ├── __init__.py
│   ├── user.py          # User request/response schemas
│   └── item.py          # Item schemas
├── api/
│   ├── __init__.py
│   ├── deps.py          # Database dependencies
│   └── endpoints/
│       ├── users.py
│       └── items.py
├── core/
│   ├── __init__.py
│   └── database.py      # Database connection
└── main.py
```

## Core Patterns

### 1. Database Setup

```python
# app/core/database.py
from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Sync database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session

# Async database
ASYNC_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async_session = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
```

### 2. Models with SQLModel

```python
# app/models/user.py
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class User(SQLModel, table=True):
    """User model for database."""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    items: list["Item"] = Relationship(back_populates="owner")

class UserCreate(SQLModel):
    """Schema for creating user."""
    email: str
    username: str
    password: str

class UserUpdate(SQLModel):
    """Schema for updating user."""
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserRead(SQLModel):
    """Schema for reading user."""
    id: int
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

### 3. Relationships

```python
# app/models/item.py
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Item(SQLModel, table=True):
    """Item model with relationship to User."""
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    price: float
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    owner: User = Relationship(back_populates="items")

class ItemCreate(SQLModel):
    """Schema for creating item."""
    title: str
    description: Optional[str] = None
    price: float

class ItemRead(SQLModel):
    """Schema for reading item."""
    id: int
    title: str
    description: Optional[str] = None
    price: float
    user_id: int
    created_at: datetime

class ItemReadWithOwner(ItemRead):
    """Item with owner information."""
    owner: UserRead
```

### 4. CRUD Operations

```python
# app/crud/users.py
from sqlmodel import Session, select
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password

def get_user(session: Session, user_id: int) -> User:
    """Get user by ID."""
    return session.get(User, user_id)

def get_user_by_email(session: Session, email: str) -> User:
    """Get user by email."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_users(session: Session, skip: int = 0, limit: int = 10) -> list[User]:
    """Get all users with pagination."""
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_user(session: Session, user_create: UserCreate) -> User:
    """Create new user."""
    user = User(
        email=user_create.email,
        username=user_create.username,
        hashed_password=hash_password(user_create.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_user(
    session: Session,
    db_user: User,
    user_update: UserUpdate
) -> User:
    """Update user."""
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def delete_user(session: Session, user_id: int) -> bool:
    """Delete user."""
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True

def authenticate_user(session: Session, email: str, password: str) -> User:
    """Authenticate user."""
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
```

### 5. API Endpoints with Dependency Injection

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.security import verify_token
from app.crud import users as crud_users
from app.models import User

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user."""
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    user = crud_users.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

### 6. Endpoint Implementation

```python
# app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate
from app.api.deps import get_current_user, get_current_admin_user, get_session
from app.crud import users as crud_users

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    session: Session = Depends(get_session)
):
    """Create new user."""
    db_user = crud_users.get_user_by_email(session, user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud_users.create_user(session, user_in)

@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Get user by ID."""
    user = crud_users.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/", response_model=list[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """List all users."""
    return crud_users.get_users(session, skip, limit)

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update user."""
    db_user = crud_users.get_user(session, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if db_user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return crud_users.update_user(session, db_user, user_in)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Delete user (admin only)."""
    success = crud_users.delete_user(session, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
```

### 7. Async Operations

```python
# Async CRUD operations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_user_async(session: AsyncSession, user_id: int) -> User:
    """Get user asynchronously."""
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalars().first()

async def create_user_async(
    session: AsyncSession,
    user_create: UserCreate
) -> User:
    """Create user asynchronously."""
    user = User(
        email=user_create.email,
        username=user_create.username,
        hashed_password=hash_password(user_create.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Async endpoint
@router.post("/async/", response_model=UserRead)
async def create_user_async(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create user asynchronously."""
    return await create_user_async(session, user_in)
```

## Best Practices

1. **Separate models from schemas** - Use models only for database
2. **Use CRUD modules** - Centralize database operations
3. **Type safety** - Leverage SQLModel's type hints
4. **Async/await** - Use async for I/O-bound operations
5. **Relationships** - Use back_populates for bidirectional
6. **Lazy loading** - Load relationships only when needed
7. **Indexes** - Add to frequently queried fields
8. **Migrations** - Use Alembic for schema changes
9. **Transactions** - Use explicit transactions for critical operations
10. **Testing** - Use in-memory SQLite for tests

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [FastAPI + SQLModel](https://fastapi.tiangolo.com/)
- [Pydantic Integration](https://docs.pydantic.dev/)
