# Reusable Skills Quick Reference

## Overview

Four professional, modular, production-ready skills for FastAPI/Python development.

## Available Skills

### 1. Building FastAPI Apps
**File:** `building-fastapi-apps.skill` (16.0 KB)

Use when: Creating FastAPI web applications, REST APIs, or microservices.

**Includes:**
- Project structure templates
- 10 core patterns with examples
- API design patterns (CRUD, filtering, pagination)
- Database integration patterns
- Security & authentication patterns
- Scaffolding tool for rapid project setup

**Key Files:**
- `SKILL.md` - Main documentation (350+ lines)
- `references/api-patterns.md` - API design patterns
- `references/database-patterns.md` - Database techniques
- `references/security-patterns.md` - Auth & security
- `scripts/scaffold_fastapi_app.py` - Project generator

---

### 2. Testing with Pytest
**File:** `testing-with-pytest.skill` (7.2 KB)

Use when: Writing unit tests, integration tests, or implementing testing infrastructure.

**Includes:**
- Basic test structure and assertions
- 10 fixture patterns (function, module, session scopes)
- Parametrization strategies
- Mocking with unittest.mock
- Async/await testing
- Database fixtures with transactions
- Coverage analysis
- Factory patterns
- Performance testing
- Integration testing

**Key Sections:**
- Core patterns (10 patterns)
- Advanced patterns (5 patterns)
- Configuration (pytest.ini, conftest.py)
- Best practices (10 rules)
- Common commands

---

### 3. FastAPI + SQLModel
**File:** `fastapi-sqlmodel.skill` (4.4 KB)

Use when: Building FastAPI apps with SQLModel for database operations.

**Includes:**
- Database setup (sync & async)
- Model definitions with relationships
- Pydantic schema validation
- CRUD operations
- Dependency injection patterns
- API endpoint implementation
- Relationship management
- Async database operations
- Query optimization

**Key Patterns:**
- Models with SQLModel
- Relationships (one-to-many, many-to-one)
- CRUD helper functions
- API endpoints with dependencies
- Async operations
- Transaction handling

---

### 4. ToDo Task Manager
**File:** `todo-task-manager.skill` (4.5 KB)

Use when: Implementing task management features in an application.

**Includes:**
- Task models with status and priority
- Complete CRUD operations
- Filtering by status/priority
- Sorting and searching
- Overdue task detection
- Completion tracking
- Statistics and dashboards
- User isolation
- API endpoints

**Key Features:**
- TaskStatus enum (todo, in_progress, done)
- TaskPriority enum (low, medium, high, urgent)
- Full CRUD endpoints
- Advanced filtering
- Search functionality
- Task statistics

---

## Quick Start Guide

### For Testing
```bash
# Use patterns from testing-with-pytest.skill
# Create tests/conftest.py with fixtures
# Use parametrization for multiple test cases
# Add markers for test organization
```

### For Database Layer
```bash
# Use patterns from fastapi-sqlmodel.skill
# Define models in app/models/
# Create CRUD functions in app/crud/
# Use dependency injection for sessions
```

### For Task Management
```bash
# Use patterns from todo-task-manager.skill
# Define Task model with status/priority
# Implement filtering endpoints
# Add search and statistics
```

### For FastAPI Project
```bash
# Use scaffold tool: python scripts/scaffold_fastapi_app.py myapp
# Or reference patterns from building-fastapi-apps.skill
# Implement security, CORS, error handling
```

---

## File Organization

```
.claude/skills/Reusable skills/
├── building-fastapi-apps/
│   ├── SKILL.md
│   ├── references/
│   │   ├── api-patterns.md
│   │   ├── database-patterns.md
│   │   └── security-patterns.md
│   ├── scripts/
│   │   ├── scaffold_fastapi_app.py
│   │   └── verify.py
│   └── assets/
├── testing-with-pytest/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── verify.py
│   └── references/
├── fastapi-sqlmodel/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── verify.py
│   └── references/
├── todo-task-manager/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── verify.py
│   └── references/
├── building-fastapi-apps.skill
├── testing-with-pytest.skill
├── fastapi-sqlmodel.skill
└── todo-task-manager.skill
```

---

## Common Patterns Quick Lookup

### Database
- Models: See `fastapi-sqlmodel.skill`
- Relationships: `fastapi-sqlmodel/SKILL.md` sections 3
- CRUD: `fastapi-sqlmodel/SKILL.md` sections 4
- Async: `fastapi-sqlmodel/SKILL.md` sections 7

### Testing
- Fixtures: `testing-with-pytest/SKILL.md` sections 2
- Mocking: `testing-with-pytest/SKILL.md` sections 5
- Async: `testing-with-pytest/SKILL.md` advanced section 1
- Integration: `testing-with-pytest/SKILL.md` advanced section 10

### API Endpoints
- CRUD: `building-fastapi-apps.skill` or `fastapi-sqlmodel/SKILL.md`
- Filtering: `todo-task-manager/SKILL.md` sections 2
- Search: `todo-task-manager/SKILL.md` sections 2

### Security
- JWT Auth: `building-fastapi-apps/references/security-patterns.md`
- RBAC: `building-fastapi-apps/references/security-patterns.md`
- CORS: `building-fastapi-apps.skill`

---

## Usage Examples

### Example 1: Create User API with Tests
1. Reference `fastapi-sqlmodel.skill` for User model and CRUD
2. Reference `building-fastapi-apps.skill` for API endpoints
3. Reference `testing-with-pytest.skill` for test fixtures and parametrization
4. Create tests using patterns from both

### Example 2: Build Task Management Feature
1. Reference `todo-task-manager.skill` for Task model
2. Reference `fastapi-sqlmodel.skill` for CRUD patterns
3. Reference `building-fastapi-apps.skill` for API endpoints
4. Reference `testing-with-pytest.skill` for endpoint tests

### Example 3: Setup Complete FastAPI Project
1. Use `building-fastapi-apps/scripts/scaffold_fastapi_app.py`
2. Reference `fastapi-sqlmodel.skill` for database layer
3. Reference `testing-with-pytest.skill` for test structure
4. Reference security patterns for auth

---

## Integration Map

```
building-fastapi-apps
├── API structure & patterns
├── Security patterns
└── Project scaffolding

fastapi-sqlmodel
├── Database models
├── CRUD operations
└── ORM patterns

testing-with-pytest
├── Test fixtures
├── Test patterns
└── Testing strategies

todo-task-manager
├── Domain models
├── Business logic
└── Feature implementation
```

---

## Best Practices Summary

**Code Organization:**
- Keep models separate from schemas
- Use CRUD modules for database operations
- Use dependency injection extensively

**Testing:**
- Use fixtures for reusable test data
- Parametrize test variations
- Mock external dependencies

**Database:**
- Use relationships for data integrity
- Leverage async/await for I/O
- Use transactions for critical operations

**API Design:**
- Use proper HTTP status codes
- Validate input with Pydantic
- Document with OpenAPI/Swagger

---

## Support

For detailed information on any skill:
1. Extract the .skill file (it's a ZIP archive)
2. Read the SKILL.md file
3. Review reference files for detailed patterns
4. Copy examples and adapt to your needs

All skills include:
- Real-world examples
- Best practices
- Error handling patterns
- Type safety
- Production-ready code

---

**Last Updated:** 2026-01-11
**Total Skills:** 4
**Total Size:** 32.1 KB
**Status:** Production Ready
