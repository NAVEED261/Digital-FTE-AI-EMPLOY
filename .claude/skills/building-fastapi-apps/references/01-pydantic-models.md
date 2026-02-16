# Pydantic Models for FastAPI

> **Official Docs**: [Pydantic v2 Validators](https://docs.pydantic.dev/latest/concepts/validators/), [Model Config](https://docs.pydantic.dev/latest/api/config/)

## Field Validation

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    age: int = Field(ge=13, le=120)
    bio: str | None = Field(default=None, max_length=500)
```

### Common Field Constraints

| Constraint | Type | Description |
|------------|------|-------------|
| `min_length` | str | Minimum string length |
| `max_length` | str | Maximum string length |
| `pattern` | str | Regex pattern |
| `ge` | int/float | Greater than or equal |
| `gt` | int/float | Greater than |
| `le` | int/float | Less than or equal |
| `lt` | int/float | Less than |
| `multiple_of` | int/float | Must be multiple of value |

## Literal vs Enum

### Using Literal (Recommended for Simple Cases)

```python
from typing import Literal
from pydantic import BaseModel

class Meeting(BaseModel):
    title: str
    duration: Literal[15, 30, 45, 60]  # Only these values allowed
    priority: Literal["low", "medium", "high"] = "medium"
    is_recurring: bool = False
```

**OpenAPI Output** (better for JavaScript clients):
```json
{
  "duration": {
    "enum": [15, 30, 45, 60],
    "type": "integer"
  },
  "priority": {
    "enum": ["low", "medium", "high"],
    "default": "medium",
    "type": "string"
  }
}
```

### Using Enum (When You Need the Type Elsewhere)

```python
from enum import Enum
from pydantic import BaseModel

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(BaseModel):
    title: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
```

**When to use Enum:**
- Need to reference the type in multiple places
- Need `.value`, `.name` properties
- Need iteration (`for status in TaskStatus`)
- Need type checking elsewhere in code

### Comparison Table

| Feature | Literal | Enum |
|---------|---------|------|
| Simple definition | `Literal["a", "b"]` | Requires class definition |
| OpenAPI clarity | Cleaner inline enum | References enum class |
| Type reuse | Copy-paste needed | Import and reuse |
| Runtime inspection | Limited | Full `.name`, `.value` |
| Iteration | Not possible | `for x in MyEnum` |

## ConfigDict: Controlling Model Behavior

```python
from pydantic import BaseModel, ConfigDict

class StrictTask(BaseModel):
    model_config = ConfigDict(
        extra="forbid",           # Reject unknown fields (raises 422)
        str_strip_whitespace=True,  # Auto-trim strings
        validate_assignment=True,   # Validate on attribute assignment
        frozen=True,               # Make instances immutable
    )

    title: str
    status: str = "todo"
```

### ConfigDict Options

| Option | Default | Description |
|--------|---------|-------------|
| `extra="forbid"` | `"ignore"` | Reject unknown fields |
| `extra="allow"` | - | Store unknown fields |
| `str_strip_whitespace` | `False` | Auto-trim string whitespace |
| `validate_assignment` | `False` | Validate when assigning attributes |
| `frozen` | `False` | Make model immutable |
| `populate_by_name` | `False` | Allow both alias and field name |
| `use_enum_values` | `False` | Use enum `.value` instead of enum |

## Custom Validators

### Field Validator

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()  # Transform to lowercase

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        return v
```

### Model Validator (Cross-field Validation)

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
```

## Request/Response Schema Pattern

```python
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# Base with shared fields
class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    priority: Literal["low", "medium", "high"] = "medium"

# Request schema (what client sends)
class TaskCreate(TaskBase):
    model_config = ConfigDict(extra="forbid")

# Update schema (all fields optional)
class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    priority: Literal["low", "medium", "high"] | None = None
    status: Literal["todo", "in_progress", "done"] | None = None

# Response schema (what server returns)
class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: datetime
```

## Email Validation

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    name: str

# Requires: pip install "pydantic[email]"
```

## Custom Error Messages

```python
from pydantic import BaseModel, Field, field_validator

class Registration(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=20,
        json_schema_extra={"example": "johndoe"}
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v.lower() in ["admin", "root", "system"]:
            raise ValueError("This username is reserved")
        if not v[0].isalpha():
            raise ValueError("Username must start with a letter")
        return v
```

## Complete Example: Meeting Model

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
from datetime import datetime

class MeetingCreate(BaseModel):
    """Request schema for creating a meeting."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    duration: Literal[15, 30, 45, 60] = 30
    priority: Literal["low", "medium", "high"] = "medium"
    attendees: list[EmailStr] = Field(min_length=1, max_length=50)
    is_recurring: bool = False

    @field_validator("attendees")
    @classmethod
    def unique_attendees(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Duplicate attendees not allowed")
        return v

class MeetingRead(BaseModel):
    """Response schema for meeting data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    duration: int
    priority: str
    attendees: list[str]
    is_recurring: bool
    created_at: datetime
    organizer_id: int
```
