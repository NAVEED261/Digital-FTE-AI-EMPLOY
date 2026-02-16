# Improvement Patterns: Common Issues and Fixes

Actionable solutions for the most common issues found during agent validation.

---

## Quick Reference: Issue → Solution Matrix

| Issue | Category | Priority | Fix Time | Expected Gain |
|-------|----------|----------|----------|-------------|
| No frontmatter | Structure | **Critical** | 5 min | +20 points |
| Vague description | Structure | **Critical** | 10 min | +10 points |
| No role defined | Role Definition | **Critical** | 15 min | +15 points |
| Vague methodology | Methodology | **High** | 20 min | +12 points |
| No verification steps | Quality Standards | **High** | 15 min | +10 points |
| No anti-patterns listed | Quality Standards | **High** | 15 min | +8 points |
| No context strategy | Context Management | **High** | 20 min | +15 points |
| No specialization | Role Definition | **Medium** | 10 min | +8 points |
| Weak examples | Pedagogical (Tutors) | **Medium** | 30 min | +8 points |
| No safeguards | Production Readiness (Operators) | **High** | 25 min | +12 points |

---

## Category 1: Structure & Metadata Issues

### Issue 1.1: Missing or Incomplete Frontmatter

**Problem**:
```
# Agent Name

I'm a helpful agent...
(No YAML frontmatter)
```

**Impact**: Cannot identify agent; missing critical metadata
**Severity**: 🔴 **Critical** - blocks deployment
**Fix time**: 5 minutes

**Solution**:

```yaml
---
name: agent-name
description: |
  [What the agent does] + [When to use it] + [Example use cases]
model: sonnet
color: blue
skills: skill1,skill2
---
```

**Checklist**:
- [ ] Add YAML delimiters (`---`)
- [ ] Include `name` (lowercase, hyphens, ≤64 chars)
- [ ] Include `description` ([What] + [When], ≤1024 chars)
- [ ] Add `model` (haiku/sonnet/opus)
- [ ] Add `color` (matches agent personality)
- [ ] Add `skills` (comma-separated if any)

**Expected improvement**: +20 points (from 0/100 to ~85/100 for structure)

---

### Issue 1.2: Vague or Generic Description

**Problem**:
```yaml
description: "A helpful AI assistant for developers"
```

**Impact**: User doesn't know when/why to use agent; too generic
**Severity**: 🟠 **High**
**Fix time**: 10 minutes

**Solution**:

Use the [What] + [When] + [Examples] formula:

```yaml
description: |
  Use this agent when you need to build production-ready React/Next.js applications
  with modern styling and responsive design. This agent is ideal for:
  (1) creating new apps with shadcn/ui and Tailwind CSS,
  (2) building chat widgets and interactive components,
  (3) enhancing existing frontends with context-efficient patterns.

  Example: User needs a chat widget for a RAG system.
  Assistant: "I'll use the frontend-ui-architect agent to design the widget
  with optimal styling and context efficiency."
```

**Checklist**:
- [ ] Start with "Use this agent when..."
- [ ] Include 2-3 specific use cases in parentheses
- [ ] Add example: User question + Expected response
- [ ] Keep ≤1024 characters total
- [ ] Make it specific, not generic

**Expected improvement**: +8-12 points to description criterion

---

## Category 2: Role Definition Issues

### Issue 2.1: Role Is Too Broad/Unfocused

**Problem**:
```
You are an expert in software development.
I can help with programming, design, architecture, databases,
DevOps, testing, documentation, and more.
```

**Impact**: User confused about scope; agent lacks specialization
**Severity**: 🟠 **High**
**Fix time**: 15-20 minutes

**Solution**:

Narrow focus to 1-3 core domains:

```markdown
You are an elite Frontend UI Architect specializing in building
production-ready React/Next.js applications. Your expertise is:

**Core Expertise Areas:**
- React component architecture and composition patterns
- Next.js full-stack applications with optimized performance
- Tailwind CSS and shadcn/ui integration
- Accessible, responsive design (WCAG 2.1 compliance)
- Context-efficient UI patterns for minimal token usage

**What You Don't Do:**
- Backend architecture (focus is frontend)
- Database design (defer to backend specialists)
- DevOps/infrastructure setup
- Non-React frameworks (not your specialty)
```

**Checklist**:
- [ ] Choose 1-3 core specializations
- [ ] List 4-6 expertise areas (specific, not generic)
- [ ] Add "What You Don't Do" section (3-5 items)
- [ ] Each expertise area gets 1 line of context
- [ ] No more than 15 expertise areas total (or split into new agent)

**Expected improvement**: +10-15 points to Role Definition

---

### Issue 2.2: Expertise Domains Not Enumerated

**Problem**:
```
I'm an expert database instructor.
```

**Impact**: User doesn't know specific topics covered
**Severity**: 🟡 **Medium**
**Fix time**: 15 minutes

**Solution**:

Add "Content Domains" or "Expertise Areas" section:

```markdown
## Content Domains

**PostgreSQL/SQL Fundamentals:**
- Schema design, normalization, relationships (1:1, 1:N, N:M)
- Query optimization, indexing strategies
- Transactions, ACID properties, isolation levels
- Window functions, CTEs, subqueries, advanced joins
- JSON/JSONB data types and operations

**Python-Database Integration:**
- psycopg2/psycopg3 connection management
- SQLAlchemy ORM: models, sessions, relationships
- Async patterns with asyncpg and asyncio
- Parameter binding and SQL injection prevention
- Connection pooling strategies
- Error handling and retry logic

**Neon-Specific Topics:**
- Serverless Postgres architecture and cold starts
- Connection limits and branching for development
- Autoscaling and compute separation
```

**Checklist**:
- [ ] Group domains into 2-4 major categories
- [ ] Each category has 5-8 specific topics
- [ ] Use bullet points for clarity
- [ ] Don't list >30 topics total (if more, consider splitting)
- [ ] Each topic is concrete and specific ("schema design", not "databases")

**Expected improvement**: +8-10 points to expertise criterion

---

## Category 3: Methodology Issues

### Issue 3.1: Vague or Implicit Workflow

**Problem**:
```
I explain concepts and provide examples.
I ask questions to understand the problem.
Sometimes I provide multiple approaches.
```

**Impact**: Unclear how agent approaches problems; no decision framework
**Severity**: 🟠 **High**
**Fix time**: 20-25 minutes

**Solution**:

Define explicit phases with clear steps:

```markdown
## Core Methodology

**Your approach:**

### Phase 1: Clarify Requirements
- Ask about component purpose, target users, constraints
- Confirm design intent and brand guidelines
- Identify any performance or accessibility requirements

### Phase 2: Architecture Planning
- Propose component structure and state management
- Discuss styling strategy (Tailwind + custom CSS balance)
- Recommend performance optimizations upfront

### Phase 3: Component Development
- Build reusable components following React best practices
- Implement proper TypeScript typing
- Create semantic HTML structure with accessibility support

### Phase 4: Verification & Documentation
- Verify responsive design across all breakpoints
- Test accessibility compliance (WCAG 2.1 AA)
- Provide clear documentation and usage examples

**Decision points:**
- If user is uncertain about architecture → Phase 2 (redesign)
- If user needs only styling → Skip Phase 2 (go Phase 1 → 3)
- If performance critical → Add performance profiling step
```

**Checklist**:
- [ ] 3-5 clear phases with names
- [ ] Each phase has 3-4 numbered sub-steps
- [ ] Entry/exit criteria for each phase
- [ ] Decision logic ("if X, then Y")
- [ ] Not just a list of actions, but a structured flow

**Expected improvement**: +10-15 points to Methodology

---

### Issue 3.2: No Learning Progression (Tutors)

**Problem**:
```
Here are examples:
1. SELECT * FROM users;
2. SELECT * FROM users WHERE age > 18;
3. SELECT u.*, o.* FROM users u JOIN orders o ON u.id = o.user_id;
```

All at different levels, no clear progression or explanation.

**Impact**: Overwhelming for beginners; boring for advanced users
**Severity**: 🟠 **High** (for tutors)
**Fix time**: 25-30 minutes

**Solution**:

Organize examples by explicit difficulty level:

```markdown
## Learning Progression

I teach database concepts through clear stages:

### Fundamentals (Start here)
- Basic schema design with simple relationships
- SELECT queries with WHERE clauses
- Basic JOINs (INNER, LEFT)
- Simple indexing concepts

### Intermediate (After fundamentals)
- Complex relationships and normalization
- Query optimization and EXPLAIN ANALYZE
- Transactions and isolation levels
- Window functions basics

### Advanced (For experienced learners)
- Advanced window functions and CTEs
- Performance tuning and index strategies
- Stored procedures and triggers
- Full-text search and custom data types

## Examples with Difficulty Markers

### Beginner Example: Simple SELECT
```sql
-- Use case: Retrieve all users
SELECT id, name, email FROM users;
```

### Intermediate Example: JOIN with Filter
```sql
-- Use case: Find user's recent orders
SELECT u.name, o.order_date, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.order_date > NOW() - INTERVAL '30 days'
ORDER BY o.order_date DESC;
```

### Advanced Example: Window Functions
```sql
-- Use case: Rank users by total spending
SELECT id, name,
  SUM(o.total) as lifetime_value,
  RANK() OVER (ORDER BY SUM(o.total) DESC) as user_rank
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```
```

**Checklist**:
- [ ] 3+ explicit difficulty levels (beginner/intermediate/advanced)
- [ ] Each level has 3-5 topics listed
- [ ] Examples marked with difficulty label
- [ ] Prerequisites mentioned ("Start here" for fundamentals)
- [ ] Progression is cumulative (each level builds on previous)

**Expected improvement**: +10-12 points to pedagogical effectiveness (tutors)

---

## Category 4: Quality Standards Issues

### Issue 4.1: No Verification Steps

**Problem**:
```
I verify outputs are correct.
```

**Impact**: Vague; reader doesn't know what "correct" means
**Severity**: 🟠 **High**
**Fix time**: 15-20 minutes

**Solution**:

Define explicit verification steps:

```markdown
## Output Constraints & Verification

Before delivering code examples, I verify:

### Code Verification
- [ ] Code is syntactically correct for Python 3.10+
- [ ] Code runs without errors (tested mentally against test case)
- [ ] All imports are included and correct
- [ ] No placeholder code (comments like "TODO" only if marked clearly)
- [ ] Example includes all necessary context (schema, setup)

### Explanation Verification
- [ ] Explanation covers "what", "why", and "when to use"
- [ ] Explanation is concise but complete (no vague hand-waving)
- [ ] Key concepts are bolded or highlighted
- [ ] Analogies are helpful and relevant

### Completeness Verification
- [ ] All necessary context provided (schema definitions, imports)
- [ ] Output can be reproduced by reader
- [ ] Error cases mentioned if relevant
- [ ] Performance implications discussed if relevant
```

**Checklist**:
- [ ] 2-3 verification categories (code, explanation, completeness)
- [ ] 3-5 specific checks per category
- [ ] Checks are concrete and testable, not vague
- [ ] Before/after examples helpful (code that passes checks, code that fails)
- [ ] Total 8-15 verification items

**Expected improvement**: +8-10 points to verification criterion

---

### Issue 4.2: No Anti-Patterns Section

**Problem**:
```
I follow best practices and avoid mistakes.
```

**Impact**: Vague; user doesn't know what to avoid
**Severity**: 🟠 **High**
**Fix time**: 15 minutes

**Solution**:

Add explicit "Must Avoid" section:

```markdown
## Must Avoid

- **Unfinished code or placeholder logic**
  Why: Reader might copy incomplete code; causes runtime errors
  Instead: Mark pseudocode clearly with "//pseudocode" comments

- **Generic database advice without PostgreSQL specifics**
  Why: Different databases have different best practices
  Instead: Always mention "For PostgreSQL" or note when advice differs for MySQL

- **Examples without schema context**
  Why: Reader can't reproduce the example
  Instead: Always include CREATE TABLE statements

- **Vague explanations of "why"**
  Why: Reader memorizes facts, doesn't understand concepts
  Instead: Always explain "why this approach" and "when to use it"

- **Ignoring edge cases**
  Why: Production code breaks in edge cases
  Instead: Mention edge cases: "This example handles X but not Y. For Y, use..."

- **Complex examples for beginners**
  Why: Overwhelms learners; they stop trying to understand
  Instead: Start simple, add complexity progressively
```

**Checklist**:
- [ ] 4-6 specific anti-patterns listed
- [ ] Each has explanations (Why + Instead)
- [ ] Anti-patterns are concrete, not generic
- [ ] Anti-patterns align with agent's domain/pattern
- [ ] Examples of what NOT to do included

**Expected improvement**: +6-8 points to anti-patterns criterion

---

## Category 5: Context Management Issues

### Issue 5.1: No Tool/Skill Usage Strategy

**Problem**:
```
I can use various tools and skills.
```

**Impact**: User doesn't know when/why to use them
**Severity**: 🟠 **High**
**Fix time**: 20 minutes

**Solution**:

Add explicit tool/skill decision framework:

```markdown
## Tool & Skill Integration

### When to Use Available Skills

**Using context7-efficient Skill:**
- When fetching external library documentation
- Use case: "Get React documentation examples" → Skill extracts relevant code
- Saves ~80% context tokens vs. manual fetching

**Using database-integration-patterns Skill:**
- When building Python-database connection patterns
- Use case: "Show me asyncpg connection pooling patterns"
- Provides tested patterns without context bloat

### When to Use Subagents

**Using Explore Agent:**
- When researching unfamiliar codebase structure
- When analyzing large React project architectures
- Reason: Finds patterns faster than manual reading

**Using Plan Agent:**
- When designing multi-phase implementation
- When making architectural decisions for new systems
- Reason: Structures complex decisions before implementation

**Using General-Purpose Agent:**
- When combining multiple specialized tasks
- When debugging complex issues
- Reason: Broader capabilities for synthesis

### Context Efficiency Strategy

**To minimize token usage, I:**
1. **Ask clarifying questions first**: Understand constraints before generating code
2. **Reference existing patterns**: "Like database-integration-patterns shows..."
3. **Use skills for documentation**: Don't inline entire external docs
4. **Progressive disclosure**: Show basic example, offer advanced details on request
5. **Delegate to subagents**: Don't handle complex exploration in main session
```

**Checklist**:
- [ ] Each skill/tool mentioned with specific use cases
- [ ] Decision criteria clear ("use X when...")
- [ ] Context efficiency strategy explicitly stated
- [ ] Subagent delegation criteria present
- [ ] Rationale for each choice explained

**Expected improvement**: +12-15 points to Context Management

---

### Issue 5.2: No Delegation Strategy

**Problem**:
```
I handle all tasks in this session.
```

**Impact**: Agent tries to do too much; context bloats; performance degrades
**Severity**: 🟠 **High**
**Fix time**: 15 minutes

**Solution**:

Add explicit delegation criteria:

```markdown
## Delegation Strategy

I strategically use subagents to optimize context and speed:

### Use Explore Agent When
- User asks "What files handle X?" or "How is X structured?"
- Searching for patterns across multiple files (>5)
- Analyzing unfamiliar codebases
- Reason: Explore agent is specialized for fast pattern finding
- Example: User: "Where are errors from the client handled?"
  → I launch Explore agent to scan entire codebase quickly

### Use Plan Agent When
- Designing multi-phase implementations (>3 phases)
- Making architectural decisions affecting multiple files
- User needs a detailed implementation strategy
- Reason: Plan agent structures complex decisions
- Example: User: "How should we redesign authentication?"
  → I launch Plan agent to design the approach first

### Keep in Main Session When
- Single-file edits (reading/writing specific files)
- Running tests (quick bash commands)
- Git commits (direct operations)
- Answering clarification questions
- Reason: Faster, less context overhead

### Result
**Expected context savings**: 70-80% on research phases by delegating to Explore
**Expected speed gain**: 2-3x faster for complex tasks via parallel subagents
```

**Checklist**:
- [ ] 2-3 delegation criteria (when to use each subagent)
- [ ] "Keep in main session" criteria clear
- [ ] Context savings or speed benefit mentioned
- [ ] Examples of when to delegate provided
- [ ] Clear decision rules ("if X, use Y agent")

**Expected improvement**: +10-12 points to Context Management

---

## Category 6: Production Readiness Issues (Operators)

### Issue 6.1: No Safeguards Defined

**Problem**:
```
Deployment Procedure:
1. Update code
2. Deploy to production
3. Verify it works
```

**Impact**: Vague; no protection against mistakes
**Severity**: 🔴 **Critical** (for operators)
**Fix time**: 25-30 minutes

**Solution**:

Add explicit safeguards with verification:

```markdown
## Production Safeguards

### Before ANY Production Change

**Safeguards checklist**:
- [ ] Code changes reviewed and tested (no pushes to main without PR)
- [ ] All tests passing: `pytest test_main.py -v` (100% success required)
- [ ] Staging environment tested: Deploy to staging, verify all features work
- [ ] Database backup exists: `pg_dump prod_db > backup_$(date).sql`
- [ ] Rollback plan documented and practiced
- [ ] On-call engineer available (not deployed during low-coverage periods)
- [ ] Monitoring dashboard active (watch for errors during deployment)
- [ ] Low-traffic window selected (avoid peak hours)

### During Deployment

**Monitoring requirements**:
- [ ] Health check endpoint: `curl https://api.example.com/health` (must return 200)
- [ ] Error rate: Should remain <1% (vs. typical baseline)
- [ ] Response time: Should remain <200ms p95 (vs. baseline)
- [ ] Database connections: Should not exceed 80 of max pool
- [ ] Logs: No errors or warnings appearing
- [ ] Business metrics: Sign-ups, transactions normal

**Abort deployment if**:
- Health check fails
- Error rate exceeds 5%
- Logs show database connection errors
- Business metric drops >10%
- Any safeguard check fails

### Rollback Procedure (If Deployment Fails)

1. Immediately notify team: `#incident` Slack channel
2. Trigger rollback: `kubectl rollout undo deployment/app`
3. Verify rollback: `curl https://api.example.com/health` (should return 200)
4. Verify recovery: Monitor error rate for 5 minutes (should return to baseline)
5. Post-incident: Document what went wrong, how we fixed it, lessons learned
```

**Checklist**:
- [ ] Pre-deployment safeguards checklist (5-8 items)
- [ ] During-deployment monitoring (3-5 specific metrics)
- [ ] Abort criteria (3-5 conditions that trigger rollback)
- [ ] Rollback steps (numbered, exact commands)
- [ ] Post-incident process
- [ ] Each step is specific and measurable

**Expected improvement**: +10-12 points to Production Readiness

---

### Issue 6.2: No Runbooks

**Problem**:
```
To deploy: Run deployment scripts and monitor.
To scale: Increase replicas.
To backup: Use backup procedure.
```

**Impact**: Vague; operator must invent procedures; error-prone
**Severity**: 🟠 **High** (for operators)
**Fix time**: 30-40 minutes

**Solution**:

Create detailed runbooks for 3-5 operations:

```markdown
## Operational Runbooks

### Runbook 1: Deploy Application

**Prerequisites**: Code merged to main, tests passing, staging verified

**Steps**:

1. **Create database backup**
   ```bash
   pg_dump prod_db > backup_$(date +%Y%m%d_%H%M%S).sql
   aws s3 cp backup_*.sql s3://backups/prod/
   ```
   Verification: `aws s3 ls s3://backups/prod/ | tail -1` (should show file from <5 min ago)

2. **Deploy to production**
   ```bash
   kubectl apply -f deployment.yaml --namespace=prod
   ```
   Verification: `kubectl rollout status deployment/app --namespace=prod`

3. **Verify health checks**
   ```bash
   curl -s https://api.example.com/health | jq '.status'  # Should be "ok"
   ```

4. **Monitor error rate**
   ```bash
   # Check logs for errors
   kubectl logs deployment/app --namespace=prod --since=1m | grep ERROR
   # Should be empty (or very few errors)
   ```

5. **Verify business metrics**
   - Sign-up rate: Normal? (check dashboard)
   - Transaction rate: Normal? (check dashboard)
   - API latency: <200ms p95? (check monitoring)

**Rollback if** any verification fails:
```bash
kubectl rollout undo deployment/app --namespace=prod
sleep 30
curl https://api.example.com/health  # Should succeed within 30s
```

### Runbook 2: Scale Application Horizontally

**When**: Traffic increase detected or performance degradation

**Steps**:

1. **Check current state**
   ```bash
   kubectl get deployment app -o yaml | grep replicas
   kubectl top pods -l app=app  # Check CPU/memory usage
   ```

2. **Update replicas**
   ```bash
   kubectl scale deployment app --replicas=5  # Increase from 3 to 5
   ```

3. **Verify scaling**
   ```bash
   kubectl get pods -l app=app  # Should show 5 running pods
   sleep 30  # Wait for pods to stabilize
   kubectl top pods -l app=app  # Verify CPU distributed
   ```

4. **Monitor metrics** (5-10 minutes):
   - CPU per pod: Should decrease
   - Request latency: Should improve
   - Error rate: Should remain normal

### Runbook 3: Emergency Rollback

**When**: Production is broken, need to revert immediately

**Steps**:

1. **Declare incident**: Post to `#incident` channel
   ```
   @here Production incident: [brief description]
   Rolling back to previous version
   ```

2. **Trigger rollback**
   ```bash
   kubectl rollout undo deployment/app
   sleep 20  # Wait for old pods to start
   ```

3. **Verify rollback success**
   ```bash
   curl -s https://api.example.com/health | jq '.status'  # Should be "ok"
   curl -s https://api.example.com/health | jq '.version'  # Should be old version
   ```

4. **Monitor recovery** (5-10 minutes):
   - Health checks: All passing?
   - Error rate: Returned to normal?
   - Business metrics: Normal?

5. **Root cause investigation** (after incident):
   ```bash
   # Check what changed
   git log -1 --stat
   # Check logs for errors
   kubectl logs deployment/app --namespace=prod --since=1h | grep ERROR
   ```

6. **Document incident**:
   - What went wrong?
   - When did we notice?
   - How did we fix it?
   - What did we learn?
   - How do we prevent it?
```

**Checklist**:
- [ ] 3-5 runbooks (deploy, scale, backup, restore, incident response)
- [ ] Each runbook has numbered steps
- [ ] Each step includes exact commands (copy-paste ready)
- [ ] Verification step after major action
- [ ] Prerequisites and abort criteria clear
- [ ] Examples of success vs. failure output
- [ ] Rollback procedure for each operation

**Expected improvement**: +10-15 points to Production Readiness

---

## Category 7: Tutor-Specific Issues

### Issue 7.1: Weak or Missing Examples

**Problem**:
```
Connection pooling is important for performance.
Use asyncpg.create_pool() to create a pool.
```

**Impact**: Reader doesn't understand how to use it
**Severity**: 🟠 **High** (for tutors)
**Fix time**: 30 minutes

**Solution**:

Create runnable examples with context:

```markdown
## Example: Connection Pooling - Intermediate

**Use case**: Production applications with many concurrent requests. Without pooling,
creating a connection for each request is expensive (~100-500ms). With pooling,
connections are reused (~1-5ms per request).

**Before** (without pooling - slow):
```python
# ❌ Bad: Creates new connection for each query (slow)
async def get_user(user_id):
    conn = await asyncpg.connect(dsn)
    user = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
    await conn.close()
    return user

# Time per request: ~100ms (connection creation) + ~5ms (query) = ~105ms
```

**After** (with pooling - fast):
```python
# ✅ Good: Reuses connections from pool
pool = None

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(dsn, min_size=10, max_size=20)

async def get_user(user_id):
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
        return user

# Time per request: ~1ms (acquire from pool) + ~5ms (query) = ~6ms (100x faster!)
```

**Why this works**:
1. Pool maintains 10-20 open connections at all times
2. When query needed, acquire a connection (usually instant if available)
3. After query, connection returned to pool (not closed)
4. Later queries reuse same connection
5. Result: Orders of magnitude faster

**When to use this**:
- Production applications with 10+ concurrent users ✅
- Server-side applications handling many requests ✅
- Microservices with high request volume ✅
- NOT needed for: Simple scripts, single-threaded apps

**Common mistake**:
```python
# ❌ Wrong: Pool created in function (recreated each time)
async def get_user(user_id):
    pool = await asyncpg.create_pool(dsn)  # EXPENSIVE! Do this once!
    ...

# ✅ Correct: Pool created once at startup
async def main():
    global pool
    pool = await asyncpg.create_pool(dsn)  # Create once
    # ... now all functions use the same pool
```

**Try this yourself**:
- Modify pool size: Change `min_size=10, max_size=20` to `min_size=1, max_size=5`
- What happens to performance with fewer connections?
- What happens if max_size is too small for concurrent queries?
```

**Checklist**:
- [ ] Example is runnable (correct syntax for target language)
- [ ] Example has clear use case ("when to use")
- [ ] Bad example shown (what NOT to do)
- [ ] Good example shown (what TO do)
- [ ] Explanation of WHY it's better
- [ ] Performance or benefit mentioned ("100x faster", "saves memory", etc.)
- [ ] Common mistake shown with explanation
- [ ] "Try this" prompt for hands-on practice
- [ ] Difficulty level marked (Beginner/Intermediate/Advanced)

**Expected improvement**: +8-12 points to example quality criterion

---

## Quick Improvement Checklist by Priority

### 🔴 Critical (Do First - Blocks Production)
- [ ] Add frontmatter (name, description, model, color)
- [ ] Define role (what agent specializes in)
- [ ] Add verification steps (how to know output is correct)
- [ ] Define production safeguards (if Operator pattern)

### 🟠 High Priority (Do Next - Major Impact)
- [ ] Add methodology/workflow (how agent approaches problems)
- [ ] Add anti-patterns (what to avoid)
- [ ] Add context management strategy (token efficiency)
- [ ] Add examples with difficulty levels (if Tutor)

### 🟡 Medium Priority (Do After)
- [ ] Narrow specialization (less is more)
- [ ] Add learning progression (if Tutor)
- [ ] Add quality checklist (before delivery)
- [ ] Add runbooks (if Operator)

### 🟢 Low Priority (Nice to Have)
- [ ] Add decision framework (if/then logic)
- [ ] Expand explanation of why (rationale)
- [ ] Add more examples (beyond minimum)
- [ ] Add edge case handling

---

## Expected Score Improvements

| Change | Current | After | Gain |
|--------|---------|-------|------|
| Add frontmatter | 15 | 50 | +35 |
| Define role | 50 | 65 | +15 |
| Add workflow | 65 | 75 | +10 |
| Add verification | 75 | 82 | +7 |
| Add context strategy | 82 | 88 | +6 |
| Add runbooks (Operators) | 88 | 95 | +7 |

**Note**: Gains depend on current state. These are typical improvements.

---

## Implementation Order

**For Maximum Impact (Fastest Path to 90+)**:

1. **Hour 1**: Add frontmatter + define role → ~50 points
2. **Hour 2**: Add workflow + verification → ~75 points
3. **Hour 3**: Add context strategy + examples → ~85 points
4. **Hour 4**: Add runbooks/safeguards (if needed) → ~90+ points

**Total time for Production-ready agent**: ~4 hours from adequate state

