# Environment Configuration in FastAPI

> **Official Docs**: [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

## Installation

```bash
pip install pydantic-settings
# or
uv add pydantic-settings
```

## Basic Settings Class

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra env vars
    )

    # Database
    database_url: str

    # Security
    secret_key: str
    access_token_expire_minutes: int = 60

    # App settings
    debug: bool = False
    app_name: str = "My FastAPI App"
    api_prefix: str = "/api/v1"
```

## Environment File (.env)

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=true
APP_NAME="My Production App"
```

## Loading Settings with lru_cache

```python
from functools import lru_cache
from fastapi import Depends

@lru_cache  # Load once, reuse everywhere
def get_settings() -> Settings:
    return Settings()

# Usage in endpoints
@app.get("/info")
def get_info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "debug": settings.debug
    }

# Usage in app creation
settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)
```

## .gitignore for Secrets

```gitignore
# .gitignore

# Environment files with secrets
.env
.env.local
.env.*.local
.env.production

# Keep example file
!.env.example

# Never commit these
*.pem
*.key
credentials.json
secrets.yaml
```

## Example Environment File

Create `.env.example` (committed to git) as documentation:

```bash
# .env.example - Copy to .env and fill in values

# Database (required)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security (required)
SECRET_KEY=generate-with-openssl-rand-hex-32

# Optional settings
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Environment-Specific Configuration

### Multiple Environment Files

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'development')}",
        env_file_encoding="utf-8",
    )

    environment: str = "development"
    database_url: str
    debug: bool = False
```

File structure:
```
.env.development    # Local development
.env.staging        # Staging server
.env.production     # Production server
.env.test           # Test environment
```

### Environment Detection

```python
class Settings(BaseSettings):
    environment: str = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

# Usage
settings = get_settings()
if settings.is_production:
    # Production-only logic
    ...
```

## Nested Settings

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "myapp"
    user: str = "postgres"
    password: str

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"  # Use __ for nested vars
    )

    database: DatabaseSettings

# .env file:
# DATABASE__HOST=localhost
# DATABASE__PORT=5432
# DATABASE__NAME=myapp
# DATABASE__USER=postgres
# DATABASE__PASSWORD=secret
```

## Validation and Computed Fields

```python
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    allowed_origins: str = "http://localhost:3000"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @computed_field
    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
```

## Secrets from Files (Docker/Kubernetes)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets"  # Docker secrets location
    )

    # Will read from /run/secrets/database_password if env var not set
    database_password: str
```

## Complete Production Settings Example

```python
from functools import lru_cache
from typing import Literal
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,  # DATABASE_URL and database_url both work
    )

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    # Database
    database_url: str
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Security
    secret_key: str
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # App
    app_name: str = "FastAPI App"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # External services
    redis_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v, info):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @computed_field
    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## Using Settings in Application

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    openapi_url=f"{settings.api_prefix}/openapi.json" if not settings.is_production else None,
)

# CORS from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database engine from settings
from sqlmodel import create_engine

engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.debug,
)
```

## Testing with Environment Overrides

```python
# conftest.py
import pytest
from unittest.mock import patch

@pytest.fixture
def test_settings():
    with patch.dict("os.environ", {
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key-at-least-32-chars-long",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
    }):
        # Clear the cache to reload with test values
        get_settings.cache_clear()
        yield get_settings()
        get_settings.cache_clear()
```

## Generating Secret Keys

```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Output: a94d8fe5c4a1c3e7b2f6d8e0a1c3e5f7a94d8fe5c4a1c3e7b2f6d8e0a1c3e5f7
```

## Common Settings Patterns

### Feature Flags

```python
class Settings(BaseSettings):
    feature_dark_mode: bool = False
    feature_beta_api: bool = False
    feature_new_checkout: bool = False

# Usage
@app.get("/beta/endpoint")
def beta_endpoint(settings: Settings = Depends(get_settings)):
    if not settings.feature_beta_api:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Welcome to beta!"}
```

### Rate Limiting Config

```python
class Settings(BaseSettings):
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
```

### Logging Config

```python
import logging

class Settings(BaseSettings):
    log_level: str = "INFO"

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level))
```
