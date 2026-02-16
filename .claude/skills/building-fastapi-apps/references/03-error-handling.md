# Error Handling in FastAPI

> **Official Docs**: [FastAPI Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)

## HTTPException Basics

```python
from fastapi import HTTPException, status

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task
```

## Status Module Constants

Always use `status` module for clarity:

```python
from fastapi import status

# Client Errors (4xx)
status.HTTP_400_BAD_REQUEST        # 400 - Malformed request
status.HTTP_401_UNAUTHORIZED       # 401 - Authentication required
status.HTTP_403_FORBIDDEN          # 403 - Authenticated but not authorized
status.HTTP_404_NOT_FOUND          # 404 - Resource doesn't exist
status.HTTP_409_CONFLICT           # 409 - Resource already exists
status.HTTP_422_UNPROCESSABLE_ENTITY  # 422 - Validation failed

# Server Errors (5xx)
status.HTTP_500_INTERNAL_SERVER_ERROR  # 500 - Unexpected error
status.HTTP_502_BAD_GATEWAY           # 502 - Upstream server error
status.HTTP_503_SERVICE_UNAVAILABLE   # 503 - Service temporarily unavailable
```

## Common Error Patterns

### Resource Not Found (404)

```python
@router.get("/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task
```

### Duplicate Resource (409)

```python
@router.post("/users")
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(User).where(User.email == user.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    return db_user
```

### Authentication Failed (401)

```python
@router.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return payload
```

### Permission Denied (403)

```python
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this task"
        )

    session.delete(task)
    session.commit()
```

### Validation Error (422)

FastAPI automatically returns 422 for Pydantic validation errors. For custom validation:

```python
@router.post("/tasks")
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    if task.due_date and task.due_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Due date cannot be in the past"
        )
    ...
```

## Custom Exception Classes

```python
from fastapi import HTTPException

class TaskNotFoundError(HTTPException):
    def __init__(self, task_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

class DuplicateEmailError(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {email} already exists"
        )

class InsufficientPermissionError(HTTPException):
    def __init__(self, action: str = "perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to {action}"
        )

# Usage
@router.get("/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise TaskNotFoundError(task_id)
    return task
```

## Custom Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Custom domain exception
class ItemOutOfStockError(Exception):
    def __init__(self, item_id: int, available: int, requested: int):
        self.item_id = item_id
        self.available = available
        self.requested = requested

# Register handler
@app.exception_handler(ItemOutOfStockError)
async def item_out_of_stock_handler(request: Request, exc: ItemOutOfStockError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "out_of_stock",
            "detail": f"Item {exc.item_id} has only {exc.available} units available",
            "available": exc.available,
            "requested": exc.requested
        }
    )

# Usage in endpoint
@router.post("/orders")
def create_order(order: OrderCreate):
    if item.stock < order.quantity:
        raise ItemOutOfStockError(
            item_id=order.item_id,
            available=item.stock,
            requested=order.quantity
        )
```

## Validation Error Handler Override

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip "body"
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "detail": "Request validation failed",
            "errors": errors
        }
    )
```

## Error Response Schema

Document error responses in OpenAPI:

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str

class ValidationErrorResponse(BaseModel):
    detail: str
    errors: list[dict]

@router.get(
    "/{task_id}",
    response_model=TaskRead,
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    }
)
def get_task(task_id: int):
    ...

@router.post(
    "/",
    response_model=TaskRead,
    status_code=201,
    responses={
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Task already exists"},
    }
)
def create_task(task: TaskCreate):
    ...
```

## Database Error Handling

```python
from sqlalchemy.exc import IntegrityError, OperationalError

@router.post("/tasks")
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    try:
        db_task = Task.model_validate(task)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A task with this identifier already exists"
        )
    except OperationalError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable"
        )
```

## Global Error Handler for Unhandled Exceptions

```python
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the actual error
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )

    # Return generic error to client (don't leak internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "detail": "An unexpected error occurred"
        }
    )
```

## Error Handling Best Practices

### 1. Be Specific with Status Codes

```python
# Bad: Generic 400 for everything
raise HTTPException(status_code=400, detail="Error")

# Good: Specific codes
raise HTTPException(status_code=404, detail="Task not found")  # Not found
raise HTTPException(status_code=409, detail="Email exists")    # Conflict
raise HTTPException(status_code=422, detail="Invalid date")    # Validation
```

### 2. Include Helpful Details

```python
# Bad: Vague message
raise HTTPException(status_code=404, detail="Not found")

# Good: Specific context
raise HTTPException(
    status_code=404,
    detail=f"Task with id {task_id} not found in project {project_id}"
)
```

### 3. Don't Leak Internal Details

```python
# Bad: Exposes internal structure
raise HTTPException(
    status_code=500,
    detail=f"Database error: {str(e)}"  # Might contain SQL, table names
)

# Good: Generic message, log details
logger.error(f"Database error: {e}", exc_info=True)
raise HTTPException(
    status_code=500,
    detail="An internal error occurred"
)
```

### 4. Use Headers When Appropriate

```python
# For 401 errors, include WWW-Authenticate header
raise HTTPException(
    status_code=401,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"}
)

# For rate limiting, include Retry-After
raise HTTPException(
    status_code=429,
    detail="Too many requests",
    headers={"Retry-After": "60"}
)
```

## Client Errors (4xx) vs Server Errors (5xx)

| Scenario | Code | Category |
|----------|------|----------|
| Resource not found | 404 | Client (wrong ID) |
| Invalid input data | 422 | Client (bad request) |
| Missing authentication | 401 | Client (forgot token) |
| No permission | 403 | Client (wrong user) |
| Duplicate resource | 409 | Client (already exists) |
| Database connection failed | 503 | Server (infrastructure) |
| Unexpected null pointer | 500 | Server (bug) |
| Third-party API down | 502 | Server (dependency) |

**Rule**: If the client can fix it by changing their request, it's 4xx. If only the server can fix it, it's 5xx.
