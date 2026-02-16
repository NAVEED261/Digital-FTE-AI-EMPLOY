---
name: neon-postgres-setup
description: Create LearnFlow database schema on Neon PostgreSQL
version: 1.0.0
cross-agent: claude-code,goose
token-cost: 120
---

# Setup Neon PostgreSQL Database

Creates database schema on Neon PostgreSQL cloud database for LearnFlow application.

## Prerequisites

1. **Neon Account**: Create free account at https://neon.tech/
2. **Neon Project**: Create project named "LearnFlow"
3. **Connection String**: Get `postgresql://...` string from Neon console
4. **Environment Variable**: Set `NEON_CONNECTION_STRING` environment variable

## When to Use

Use this skill when you need to:
- Create LearnFlow database tables on Neon PostgreSQL
- Initialize database schema from scratch
- Reset database to clean state
- Verify database connectivity

## Usage

```bash
export NEON_CONNECTION_STRING="postgresql://user:pass@ep-xxx.neon.tech/learnflow"
claude "Use neon-postgres-setup skill to initialize learnflow database"
```

## Parameters

- **action**: init (default), verify, drop, or reset
- **connection-string**: Neon connection string (optional, uses env var if not provided)

## Output

When successful:
- ✓ Tables created: users, modules, topics, exercises, submissions, conversations, progress_events, struggles, learning_paths
- ✓ Indexes created on key columns
- ✓ 8 Python modules inserted
- ✓ Sample topics and exercises added
- ✓ Verification passed

## Actions

**init** (default) - Create fresh schema
```bash
claude "Use neon-postgres-setup skill"
```

**verify** - Check if tables exist
```bash
claude "Use neon-postgres-setup skill with action=verify"
```

**reset** - Drop and recreate schema
```bash
claude "Use neon-postgres-setup skill with action=reset"
```

## Validation

After running, verify:
- [ ] 9 tables created
- [ ] All indexes present
- [ ] 8 Python modules in database
- [ ] Connection working from application

---

**See [REFERENCE.md](./REFERENCE.md) for advanced options and troubleshooting.**
