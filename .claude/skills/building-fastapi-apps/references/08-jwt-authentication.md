# JWT Authentication in FastAPI

> **Official Docs**: [FastAPI OAuth2 JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

## Installation

```bash
pip install "python-jose[cryptography]"
```

## Token Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str  # Generate with: openssl rand -hex 32
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = {"env_file": ".env"}
```

## Token Creation

```python
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()  # Issued at
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token (longer-lived)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
```

## OAuth2PasswordBearer Setup

```python
from fastapi.security import OAuth2PasswordBearer

# tokenUrl is the path to your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
```

## Token Validation

```python
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

## Get Current User Dependency

```python
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Extract and validate user from JWT token."""
    payload = decode_token(token)

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Extract user ID
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Fetch user from database
    user = session.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

def get_active_user(user: User = Depends(get_current_user)) -> User:
    """Verify user is active."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return user

def get_admin_user(user: User = Depends(get_active_user)) -> User:
    """Verify user is admin."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
```

## Login Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """Authenticate user and return JWT tokens."""
    # Find user by email (OAuth2 uses 'username' field)
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    # Verify credentials
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )
```

## Token Refresh Endpoint

```python
class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
def refresh_token(
    request: RefreshRequest,
    session: Session = Depends(get_session)
):
    """Get new access token using refresh token."""
    payload = decode_token(request.refresh_token)

    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user
    user_id = payload.get("sub")
    user = session.get(User, int(user_id))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )
```

## Protected Route Examples

```python
# Requires authentication
@router.get("/me", response_model=UserRead)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Requires active user
@router.get("/dashboard")
def dashboard(user: User = Depends(get_active_user)):
    return {"message": f"Welcome {user.name}!"}

# Requires admin
@router.get("/admin/users", response_model=list[UserRead])
def list_users(
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session)
):
    return session.exec(select(User)).all()
```

## Token Payload Structure

```python
# Access token payload
{
    "sub": "123",              # User ID (subject)
    "exp": 1699999999,         # Expiration timestamp
    "iat": 1699999000,         # Issued at timestamp
    "type": "access"           # Token type
}

# Refresh token payload
{
    "sub": "123",
    "exp": 1700604799,         # Longer expiration
    "iat": 1699999000,
    "type": "refresh"
}

# Extended payload with roles
{
    "sub": "123",
    "exp": 1699999999,
    "iat": 1699999000,
    "type": "access",
    "role": "admin",           # User role
    "email": "user@example.com"
}
```

## Token Blacklist (Optional)

For logout functionality, maintain a blacklist:

```python
from datetime import datetime
from sqlmodel import SQLModel, Field

class TokenBlacklist(SQLModel, table=True):
    """Revoked tokens."""
    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(index=True)
    revoked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # When token would naturally expire

def is_token_blacklisted(token: str, session: Session) -> bool:
    """Check if token is blacklisted."""
    return session.exec(
        select(TokenBlacklist).where(TokenBlacklist.token == token)
    ).first() is not None

def blacklist_token(token: str, session: Session):
    """Add token to blacklist."""
    payload = decode_token(token)
    expires_at = datetime.fromtimestamp(payload["exp"])

    blacklisted = TokenBlacklist(token=token, expires_at=expires_at)
    session.add(blacklisted)
    session.commit()

# Logout endpoint
@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    blacklist_token(token, session)
    return {"message": "Successfully logged out"}

# Update get_current_user to check blacklist
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    if is_token_blacklisted(token, session):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    # ... rest of validation
```

## Multi-Tenant JWT (Optional)

```python
# Include tenant in token
def create_access_token(data: dict, tenant_id: str) -> str:
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "tenant_id": tenant_id
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

# Validate tenant access
def get_current_tenant_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> tuple[User, str]:
    payload = decode_token(token)
    tenant_id = payload.get("tenant_id")
    user = session.get(User, int(payload["sub"]))
    return user, tenant_id
```

## API Key Authentication (Alternative)

```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key_user(
    api_key: str = Depends(api_key_header),
    session: Session = Depends(get_session)
) -> User:
    """Authenticate via API key."""
    user = session.exec(
        select(User).where(User.api_key == api_key)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return user
```

## Testing Authentication

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def auth_headers(client):
    """Get auth headers for authenticated requests."""
    # Create user
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
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# test_auth.py
def test_protected_route_without_token(client):
    response = client.get("/me")
    assert response.status_code == 401

def test_protected_route_with_token(client, auth_headers):
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_invalid_token(client):
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/me", headers=headers)
    assert response.status_code == 401

def test_refresh_token(client, auth_headers):
    # Get refresh token from login
    login_response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "SecurePass123!"
    })
    refresh_token = login_response.json()["refresh_token"]

    # Use refresh token
    response = client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Security Best Practices

1. **Use HTTPS** in production
2. **Keep tokens short-lived** (15-30 min for access tokens)
3. **Use refresh tokens** for extended sessions
4. **Store secrets securely** (environment variables, not code)
5. **Validate token type** (access vs refresh)
6. **Include only necessary claims** in tokens
7. **Implement token blacklist** for logout
8. **Use strong secrets** (at least 32 characters)
