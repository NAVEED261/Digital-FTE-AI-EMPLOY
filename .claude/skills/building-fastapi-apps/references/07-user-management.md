# User Management in FastAPI

> **Official Docs**: [FastAPI Security OAuth2 JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

## Password Hashing with pwdlib (Argon2)

FastAPI docs recommend `pwdlib` with Argon2 for modern password hashing.

### Installation

```bash
pip install "pwdlib[argon2]"
```

### Password Hasher Setup

```python
from pwdlib import PasswordHash

# Create hasher instance (Argon2 is default)
password_hash = PasswordHash.recommended()

# Hash a password
hashed = password_hash.hash("user_password")

# Verify a password
is_valid = password_hash.verify("user_password", hashed)
```

## User Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    """User database model."""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """Hash and set the password."""
        self.hashed_password = password_hash.hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against the hash."""
        return password_hash.verify(password, self.hashed_password)
```

## Request/Response Schemas

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    """Schema for user registration."""
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)

class UserRead(BaseModel):
    """Schema for user response (no password)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    is_active: bool
    is_admin: bool
    created_at: datetime

class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
```

## Password Validation

```python
from pydantic import BaseModel, field_validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
```

## Signup Endpoint

```python
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Register a new user."""
    # Check if email already exists
    existing = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user with hashed password
    user = User(
        email=user_data.email,
        name=user_data.name,
    )
    user.set_password(user_data.password)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
```

## Login Endpoint

```python
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """Authenticate user and return tokens."""
    # Find user by email (OAuth2 uses 'username' field)
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    # Verify credentials
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Generate tokens (see JWT reference)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

## Get Current User Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.get(User, int(user_id))
    if user is None:
        raise credentials_exception

    return user

def get_active_user(user: User = Depends(get_current_user)) -> User:
    """Dependency to get current active user."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return user

def get_admin_user(user: User = Depends(get_active_user)) -> User:
    """Dependency to get current admin user."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user
```

## Profile Endpoints

```python
@router.get("/me", response_model=UserRead)
def get_profile(current_user: User = Depends(get_active_user)):
    """Get current user's profile."""
    return current_user

@router.put("/me", response_model=UserRead)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_active_user),
    session: Session = Depends(get_session)
):
    """Update current user's profile."""
    # Check if new email is taken
    if user_update.email and user_update.email != current_user.email:
        existing = session.exec(
            select(User).where(User.email == user_update.email)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Email already taken"
            )

    # Apply updates
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)

    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user
```

## Password Change

```python
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

@router.post("/me/password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_active_user),
    session: Session = Depends(get_session)
):
    """Change current user's password."""
    # Verify current password
    if not current_user.check_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Set new password
    current_user.set_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    session.commit()

    return {"message": "Password changed successfully"}
```

## Admin User Management

```python
@router.get("/users", response_model=list[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session)
):
    """List all users (admin only)."""
    users = session.exec(
        select(User).offset(skip).limit(limit)
    ).all()
    return users

@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session)
):
    """Delete a user (admin only)."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself"
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()

@router.post("/users/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session)
):
    """Deactivate a user account (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(user)

    return user
```

## Complete Auth Service Module

```python
# services/auth.py
from pwdlib import PasswordHash
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

from ..config import get_settings

settings = get_settings()
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None
```

## Testing User Management

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient

def test_signup(client):
    response = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "hashed_password" not in response.json()

def test_signup_duplicate_email(client):
    # First signup
    client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })
    # Second signup with same email
    response = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "AnotherPass123!",
        "name": "Another User"
    })
    assert response.status_code == 409

def test_login(client):
    # Create user first
    client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })
    # Login
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401
```
