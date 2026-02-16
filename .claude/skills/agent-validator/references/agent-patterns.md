# Agent Pattern Definitions and Requirements

Comprehensive guide to the three primary agent patterns: Tutor, Architect, and Operator.

---

## Overview: What Are Patterns?

**Agent patterns** are distinct behavioral archetypes that reflect how an agent approaches problem-solving and user interaction. Agents aren't neutral; they have a *teaching style*, *design philosophy*, or *operational discipline* that shapes every decision.

Recognizing these patterns:
1. Helps categorize and evaluate agents fairly
2. Allows pattern-specific validation criteria
3. Ensures agents fulfill their core promise
4. Guides users to the right agent for their needs

---

## Pattern 1: Tutor Pattern

### Core Definition

**Tutors teach concepts progressively**, building learner understanding from fundamentals to advanced patterns. They emphasize *explanation*, *example*, *practice*, and *feedback*.

**Primary goal**: User walks away understanding the "why" and "how" through guided learning.

### Pattern Signature Keywords

Scan for these phrases and concepts:
- "Learn", "teach", "instruct", "guided", "practice", "exercise", "understand"
- "Beginner", "intermediate", "advanced" (explicit levels)
- "Progressive", "build on", "layer", "foundation"
- "Example", "walkthrough", "hands-on"
- "Feedback", "clarify", "ask if", "encourage"
- "Why", not just "what"
- Teaching methodology section

### Pattern Recognition Checklist

Does the agent...

- [ ] Explicitly mention teaching/instructing/guiding as core function?
- [ ] Reference multiple complexity levels (beginner/intermediate/advanced)?
- [ ] Describe how to start simple and build complexity?
- [ ] Include practice exercises or practice prompts?
- [ ] Explain "why" things work, not just "what" to do?
- [ ] Include encouraging or celebratory language?
- [ ] Have a feedback mechanism (asking if user understands)?
- [ ] Provide examples for key concepts?

**Pattern detected if**: 5+ of 8 criteria are true

---

### Tutor Pattern Requirements (Must Have)

#### 1. Learning Progression Section
**What it is**: Explicit statement of how complexity increases

**Must include**:
- Statement about starting with basics
- Progression to intermediate concepts
- Advancement to advanced patterns
- How these levels are distinguished

**Example**:
```markdown
## Learning Progression

I teach PostgreSQL through clear progression:
1. **Fundamentals**: Basic schema design, simple queries, relationships
2. **Intermediate**: Query optimization, indexing, transactions
3. **Advanced**: Window functions, CTEs, performance tuning

Each level builds on previous knowledge.
```

---

#### 2. Practice Exercises (or Clear Practice Protocol)
**What it is**: Hands-on opportunities for learners to apply knowledge

**Must include (choose one)**:
- Explicit practice exercises with difficulty levels
- Clear protocol for creating practice opportunities
- Method for hands-on learning

**Example 1** (explicit exercises):
```markdown
## Practice Exercises

### Beginner
Exercise 1: Create a schema with 3 tables and 1-to-many relationship
Exercise 2: Write SELECT queries with WHERE and JOIN

### Intermediate
Exercise 3: Optimize a slow query using EXPLAIN ANALYZE
Exercise 4: Design an index strategy for a workload
```

**Example 2** (clear protocol):
```markdown
## Instruction Structure

For each teaching session:
4. **Present the Concept**: Use clear analogies and bullet points
5. **Show Working Code**: Provide Python+PostgreSQL examples
6. **Practice Prompts**: Suggest hands-on exercises ("Try modifying this...")
```

---

#### 3. Examples (Runnable or Realistic)
**What it is**: Code samples, diagrams, walkthroughs that illustrate concepts

**Must include**:
- At least 3 significant examples per domain
- Examples marked with difficulty level or use case
- Explanation of what the example demonstrates
- Context for when/why to use the pattern

**Example**:
```markdown
# Example: Connection Pooling - Intermediate
# Use case: Production applications with concurrent requests

async with asyncpg.create_pool(dsn) as pool:
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM users')

Why: Connection pooling reuses connections, avoiding expensive
connection creation for each query. Critical for performance.
```

---

#### 4. Feedback Mechanism
**What it is**: How the agent gathers and acts on learner feedback

**Must include**:
- Clear mechanism for learner to indicate confusion
- How agent will respond to signals of misunderstanding
- How agent will adjust based on feedback

**Example**:
```markdown
## Feedback & Adjustment

After each explanation, I ask: "Does this make sense? What's unclear?"

If you signal confusion:
- I rephrase using different mental model (analogy vs. code vs. diagram)
- I provide simpler example
- I slow down and recap prerequisites

If you're ready to advance:
- I move to next level
- I ask challenge questions to deepen understanding
```

---

### Tutor Pattern Anti-Patterns (Must Avoid)

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| **All examples at same level** | Beginners overwhelmed; advanced learners bored | Mark examples with difficulty |
| **No explanation of "why"** | Learners memorize, don't understand; can't adapt | Always include rationale |
| **No practice opportunities** | Passive learning; skills don't stick | Include practice prompts or exercises |
| **Generic encouragement** | Feels hollow; user doesn't trust sincerity | Celebrate specific progress: "Great question—shows you're thinking about optimization!" |
| **No feedback mechanism** | Can't tell if learner understood; might miss confusion | Explicitly ask comprehension questions and adjust |
| **One-size-fits-all pace** | Doesn't adapt to learner needs | Offer options: "Want more detail or keep moving?" |

---

### Tutor Pattern Quality Checklist

Before delivery, verify:

- [ ] Learning progression is explicit (fundamentals → intermediate → advanced)
- [ ] At least one practice exercise per major concept
- [ ] Examples are runnable (code) or realistic (diagrams/descriptions)
- [ ] Examples have context ("Use case: ...", "Why: ...")
- [ ] Encouraging language present ("Great question", "You're thinking like a...")
- [ ] Feedback mechanism described (how to get clarification)
- [ ] Explanations include "why", not just "how" or "what"
- [ ] Mistakes/misconceptions are addressed
- [ ] Connection to learner goals or prior knowledge

---

## Pattern 2: Architect Pattern

### Core Definition

**Architects design systems and enforce quality.** They think in terms of *principles*, *trade-offs*, *verification*, and *standards*.

**Primary goal**: User builds something correct, high-quality, and maintainable, following proven patterns and best practices.

### Pattern Signature Keywords

Scan for these phrases and concepts:
- "Design", "architecture", "pattern", "best practice", "principle"
- "Quality", "standard", "checklist", "verification", "gate"
- "Trade-off", "when to use X vs Y", "decision framework"
- "Anti-pattern", "don't", "must avoid", "pitfall"
- "Verify", "before delivery", "production-ready"
- "Component", "system", "structure", "layer"

### Pattern Recognition Checklist

Does the agent...

- [ ] Focus on design and architecture decisions?
- [ ] Mention quality standards or best practices?
- [ ] Include checklists or verification steps?
- [ ] Discuss trade-offs (time vs. memory, simplicity vs. flexibility)?
- [ ] Warn against anti-patterns or common mistakes?
- [ ] Have a "before delivery" quality gate?
- [ ] Reference design principles (SOLID, DRY, etc.)?
- [ ] Help choose between multiple valid approaches?

**Pattern detected if**: 5+ of 8 criteria are true

---

### Architect Pattern Requirements (Must Have)

#### 1. Design Workflow (Phases/Steps)
**What it is**: Clear process for approaching design challenges

**Must include**:
- Named phases or steps (e.g., Clarify → Design → Verify)
- What happens in each phase
- Decision criteria between phases
- Entry/exit conditions

**Example**:
```markdown
## Design Workflow

### Phase 1: Clarify Requirements
Confirm component purpose, users, performance targets, brand guidelines

### Phase 2: Architecture Planning
Propose component structure, state management, styling strategy

### Phase 3: Component Development
Build reusable components following best practices

### Phase 4: Verification
Check responsive design, accessibility, performance

Decision gates: Clarity (do we understand?) → Feasibility (is it doable?) → Quality (does it pass gates?)
```

---

#### 2. Quality Verification Checklist
**What it is**: Explicit checklist of non-negotiable quality requirements

**Must include**:
- 5+ specific, actionable items
- Clear pass/fail criteria
- When to verify (before delivery)
- Consequences of not verifying

**Example**:
```markdown
## Quality Verification Checklist

Before Delivery:
- [ ] All components are responsive and tested at multiple breakpoints
- [ ] Accessibility standards are met (WCAG 2.1 AA minimum)
- [ ] Performance is optimized (images optimized, bundle size reasonable)
- [ ] TypeScript types are properly defined
- [ ] Components are documented with usage examples
- [ ] Dark mode support is implemented
- [ ] Error states and loading states are handled
- [ ] No console warnings or errors
```

---

#### 3. Design Trade-Offs Explained
**What it is**: Acknowledgment that design decisions involve trade-offs

**Must include**:
- Scenarios where different approaches apply
- Pros/cons of each approach
- When to choose which approach
- Examples of trade-off decisions

**Example**:
```markdown
## Design Trade-Offs

**Virtual scrolling vs. rendering all items:**
- Virtual scrolling: Better performance (only render visible items)
- Render all: Simpler code, worse performance
- Use virtual scrolling when: >100 items, mobile performance critical
- Use render all when: <50 items, WCAG 1.4.4 zoom is critical

**Controlled vs. uncontrolled components:**
- Controlled: More predictable, integrates better with external state
- Uncontrolled: Simpler, less boilerplate
- Use controlled when: Multiple inputs linked, external state needed
- Use uncontrolled when: Isolated, simple form
```

---

#### 4. Best Practices Enforced
**What it is**: Standards and patterns that must be followed

**Must include**:
- List of non-negotiable best practices
- Why each matters
- How to verify compliance
- Consequences of non-compliance

**Example**:
```markdown
## Best Practices You Must Follow

- Always use semantic HTML elements (`<header>`, `<nav>`, `<main>`)
  Why: Accessibility, SEO, maintainability
  Verify: Run accessibility audit, check HTML validation

- Implement proper heading hierarchy
  Why: Screen readers depend on it; crucial for navigation
  Verify: Check h1, h2, h3 nesting is correct

- Ensure all interactive elements are keyboard accessible
  Why: Users with motor disabilities depend on it
  Verify: Navigate entire UI using only Tab/Enter keys
```

---

### Architect Pattern Anti-Patterns (Must Avoid)

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| **No trade-off discussion** | User has no basis for choosing between valid approaches | Explicitly state trade-offs and decision criteria |
| **Vague quality gates** | User can't verify quality; likely delivers subpar work | Use specific checklist: "Responsive at 5 breakpoints", not "responsive design" |
| **No consequences for violations** | User ignores best practices; quality suffers | Explain why each best practice matters |
| **Too prescriptive** | Stifles creativity; user can't adapt to unique constraints | Show decision framework, not rules |
| **No anti-patterns listed** | User doesn't know what to avoid; repeats mistakes | Explicitly list 4-5 anti-patterns and why they're bad |
| **Generic design principles** | User doesn't understand how principles apply here | Provide concrete examples in this domain |

---

### Architect Pattern Quality Checklist

Before delivery, verify:

- [ ] Design workflow has 3-5 clear phases with decision gates
- [ ] Quality checklist has 5+ specific, measurable items
- [ ] Trade-offs are discussed (at least 3 important ones)
- [ ] Each trade-off shows when to use which approach
- [ ] Best practices are enumerated (5+ items) with rationale
- [ ] Anti-patterns are listed (3-5) with consequences
- [ ] "Before delivery" checklist is explicit and complete
- [ ] Architecture principles are stated (SOLID, DRY, etc.)
- [ ] Examples show good and bad design

---

## Pattern 3: Operator Pattern

### Core Definition

**Operators manage production systems and ensure reliability.** They think in terms of *procedures*, *compliance*, *verification*, and *rollback*.

**Primary goal**: User can safely deploy, operate, and maintain systems with confidence and compliance.

### Pattern Signature Keywords

Scan for these phrases and concepts:
- "Production", "deploy", "operational", "procedures", "runbook"
- "Monitor", "alert", "SLO", "reliability", "uptime"
- "Compliance", "audit", "standards", "validation"
- "Rollback", "recovery", "disaster", "failover"
- "Safe", "verify", "gate", "test", "stage"
- "Infrastructure", "provisioning", "scaling"

### Pattern Recognition Checklist

Does the agent...

- [ ] Focus on production operations and deployment?
- [ ] Include clear operational procedures (step-by-step)?
- [ ] Mention compliance, standards, or regulatory requirements?
- [ ] Describe safeguards against production mishaps?
- [ ] Include runbooks or operational guides?
- [ ] Mention monitoring, alerting, or incident response?
- [ ] Have testing and staging protocols?
- [ ] Discuss rollback or recovery procedures?

**Pattern detected if**: 5+ of 8 criteria are true

---

### Operator Pattern Requirements (Must Have)

#### 1. Operational Procedures (Step-by-Step)
**What it is**: Clear, numbered procedures for common operations

**Must include**:
- 3+ distinct procedures (deploy, scale, backup, migrate, etc.)
- Each procedure has numbered steps (1, 2, 3...)
- Verification after each major step
- Rollback procedure for each operation

**Example**:
```markdown
## Operational Procedures

### Deploy to Production

1. Run tests: `pytest test_main.py -v` (must be 100% passing)
2. Run security scan: `bandit -r src/`
3. Verify staging: Navigate to staging environment, verify all features
4. Create database backup: `pg_dump prod_db > backup_$(date).sql`
5. Deploy: `kubectl apply -f deployment.yaml --namespace=prod`
6. Verify health: Check /health endpoint responds 200 OK
7. Monitor: Watch logs for 5 minutes, verify no errors
8. Rollback if needed: `kubectl rollout undo deployment/app --namespace=prod`

### Rollback Procedure (if deployment fails)

1. Immediately verify previous version is running: `kubectl rollout history deployment/app`
2. Rollback: `kubectl rollout undo deployment/app`
3. Verify health: Check /health endpoint
4. Notify on-call: Post to #incident channel
```

---

#### 2. Production Safeguards
**What it is**: Protections against common production mishaps

**Must include**:
- Safeguards for critical operations (deploy, migrate, scale)
- Verification steps before and after each safeguard
- Testing in staging before production
- Monitoring and alerting rules

**Example**:
```markdown
## Production Safeguards

### Before Any Production Change

- [ ] Test thoroughly in staging (mirrors production)
- [ ] Have rollback plan ready
- [ ] Schedule during low-traffic window (2-4 AM if possible)
- [ ] Have on-call engineer on standby
- [ ] Database backup exists and verified

### Deployment Safeguards

- [ ] Database schema migrations tested with actual data volume
- [ ] Feature flags used for gradual rollout (10% → 50% → 100%)
- [ ] Monitoring dashboard active during deployment
- [ ] Error budget allows this change (check SLO status)
- [ ] Rollback procedure documented and practiced

### Verification After Change

- [ ] Health checks pass (endpoint, CPU, memory, disk)
- [ ] Error rate unchanged or improved
- [ ] Response times normal
- [ ] Logs show no errors or warnings
- [ ] Business metrics normal (sign-ups, transactions, etc.)

If any verification fails, rollback immediately.
```

---

#### 3. Runbook or Operational Guide
**What it is**: Complete guide to standard operations and incident response

**Must include**:
- Common operations (deploy, scale, backup, restore)
- Incident response procedures (outage, data corruption, security breach)
- Health checks and monitoring commands
- Common troubleshooting steps

**Example**:
```markdown
## Runbook: Production Operations

### Common Operations

#### Scale Application (Horizontal)
1. Check current replicas: `kubectl get deployment app -o yaml`
2. Update replicas: `kubectl scale deployment app --replicas=5`
3. Verify scaling: `kubectl get pods -l app=app`
4. Monitor CPU/memory: `kubectl top pods`

#### Database Backup
1. Trigger backup: `pg_dump prod_db > backup_$(date +%Y%m%d).sql`
2. Verify backup: `psql prod_db < backup_XXX.sql --echo-errors` (on test DB)
3. Store backup: `aws s3 cp backup_XXX.sql s3://backups/prod/`
4. Verify storage: `aws s3 ls s3://backups/prod/` (confirm file present)

#### Incident Response: Database Connection Failures

1. Check database health: `pg_isready -h prod-db.internal`
2. Check connection pool: `SELECT count(*) FROM pg_stat_activity`
3. If pool exhausted, kill idle: `SELECT pg_terminate_backend(pid) WHERE state = 'idle'`
4. Verify app recovery: Monitor error rate for 5 minutes
5. If not recovering, scale down app: `kubectl scale deployment app --replicas=1`
6. Investigate root cause: Check logs, query performance, recent changes
```

---

#### 4. Compliance and Standards
**What it is**: Reference to compliance requirements and verification

**Must include**:
- Standards that must be met (security, reliability, audit)
- How to verify compliance
- Audit procedures
- Consequences of non-compliance

**Example**:
```markdown
## Compliance & Standards

### Security Standards
- Encryption in transit (TLS 1.3) ✓ Verify: `openssl s_client -connect api.example.com:443`
- Encryption at rest (AES-256) ✓ Verify: Check database settings
- No secrets in code ✓ Verify: `git log -p | grep -i 'password\|token\|secret'` (should return nothing)

### Reliability Standards
- Uptime target: 99.9% (SLO) ✓ Monitor: Check dashboard weekly
- Automated failover: <5 minutes ✓ Test: Simulate failure monthly
- Backup frequency: Daily ✓ Verify: Check S3 bucket for daily backups

### Audit Requirements
- All deployments logged ✓ Verify: `kubectl logs -n prod deployment/audit`
- Configuration changes tracked ✓ Verify: Git history of infrastructure
- Access logs maintained ✓ Verify: S3 logs for API access
```

---

### Operator Pattern Anti-Patterns (Must Avoid)

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| **Vague procedures** | Operator doesn't know exact steps; risks mistakes | Use numbered steps with exact commands |
| **No verification** | Operator can't tell if operation succeeded | Add verification after each step |
| **No rollback plan** | If something goes wrong, operator panics | Always include rollback procedure |
| **No safeguards** | Production mistakes break everything | List safeguards and verification gates |
| **No runbooks** | Operator must remember everything; errors likely | Provide step-by-step guides for common ops |
| **No compliance checklist** | Operator doesn't know standards; audit fails | List requirements and verification methods |
| **No incident response** | When things break, operator has no playbook | Include incident response procedures |
| **No monitoring guidance** | Operator doesn't know what to watch for | Define health checks and alert conditions |

---

### Operator Pattern Quality Checklist

Before delivery, verify:

- [ ] 3+ operational procedures with numbered steps
- [ ] Each procedure has verification steps
- [ ] Rollback procedure included for critical operations
- [ ] Production safeguards listed (5+ specific checks)
- [ ] Safeguards include pre-change and post-change verification
- [ ] Runbook covers common operations (deploy, scale, backup, restore)
- [ ] Runbook includes incident response procedures
- [ ] Compliance/standards clearly stated with verification methods
- [ ] Monitoring/alerting rules defined
- [ ] Commands are exact and tested (copy-paste ready)

---

## Mixed or Unclear Patterns

### When an Agent Doesn't Fit

Some agents combine patterns or are too specialized to classify clearly. That's okay.

**Mixed Pattern Example**:
- Architect-Operator hybrid: Designs production systems (architect) + deploys them (operator)
- Tutor-Architect hybrid: Teaches design patterns (tutor) + enforces quality gates (architect)

**Handling Mixed Patterns**:
1. Identify the dominant pattern (which one describes 60%+ of content?)
2. Apply criteria for dominant pattern
3. Apply criteria for secondary pattern
4. Note weights adjusted for mixed pattern
5. In report, list both patterns and note the mix

**Handling Unclear Patterns**:
1. If pattern can't be identified, note as "Unclear" in report
2. Still evaluate all 9 categories (don't skip)
3. Don't penalize for unclear pattern (note context)
4. Recommend clarifying agent's primary role

---

## Pattern Detection Decision Tree

```
Does agent focus on TEACHING/LEARNING?
├─ YES → Check for progressive levels, practice, examples → TUTOR
└─ NO ─→ Does agent focus on DESIGN/ARCHITECTURE/QUALITY?
        ├─ YES → Check for checklists, trade-offs, best practices → ARCHITECT
        └─ NO ─→ Does agent focus on PRODUCTION/OPERATIONS?
                ├─ YES → Check for procedures, runbooks, safeguards → OPERATOR
                └─ NO ─→ UNCLEAR or SPECIALIZED (note in report)
```

---

## Pattern Compliance Matrix

Quick reference: Which requirements apply to each pattern?

| Requirement | Tutor | Architect | Operator |
|---|---|---|---|
| Learning progression | ✅ Required | ⊗ N/A | ⊗ N/A |
| Practice exercises | ✅ Required | ⊗ N/A | ⊗ N/A |
| Examples | ✅ Required | ⚠️ Recommended | ⚠️ Recommended |
| Feedback mechanism | ✅ Required | ⊗ N/A | ⊗ N/A |
| Design workflow | ⊗ N/A | ✅ Required | ⊗ N/A |
| Quality checklist | ⚠️ Recommended | ✅ Required | ✅ Required |
| Trade-offs discussed | ⊗ N/A | ✅ Required | ⊗ N/A |
| Best practices enforced | ⚠️ Recommended | ✅ Required | ✅ Required |
| Operational procedures | ⊗ N/A | ⊗ N/A | ✅ Required |
| Production safeguards | ⊗ N/A | ⊗ N/A | ✅ Required |
| Runbooks | ⊗ N/A | ⊗ N/A | ✅ Required |
| Compliance standards | ⊗ N/A | ⊗ N/A | ✅ Required |

**Legend**: ✅ Required | ⚠️ Recommended | ⊗ N/A (not applicable)

---

## Real-World Pattern Examples

### Example 1: database-skill-tutor (Pure Tutor)
**Key indicators**:
- "Learn PostgreSQL through clear progression"
- "3 complexity levels: Fundamentals, Intermediate, Advanced"
- Multiple practice prompts: "Try modifying this..."
- Encouraging tone: "Great question—shows you're thinking about optimization"
- Feedback mechanism: "Tell me if this isn't clear"

**Classification**: Pure Tutor

---

### Example 2: frontend-ui-architect (Pure Architect)
**Key indicators**:
- "Build stunning, production-ready user interfaces"
- Quality assurance checklist with 10 items
- Design trade-offs discussed: "When to use virtual scrolling vs. render all"
- Best practices enforced: "Always use semantic HTML"
- Anti-patterns: "Avoid unfinished code", "Don't skip accessibility"

**Classification**: Pure Architect

---

### Example 3: prod-microservices-operator (Pure Operator)
**Key indicators**:
- "Production-level microservices operations"
- Operational procedures: Deploy, scale, failover
- Runbooks for incident response
- Production safeguards: Testing in staging, gradual rollout, monitoring
- Compliance standards referenced

**Classification**: Pure Operator

---

## Using Pattern Information in Evaluation

Once pattern is identified:

1. **Weight adjustment**: Redistribute unused category weights to applicable categories
2. **Criterion focus**: Apply pattern-specific criteria from categories 8-9
3. **Expectation setting**: Judge agent against pattern-specific standards
4. **Recommendation focus**: Suggest improvements aligned with pattern
5. **Scoring baseline**: Pattern-aligned agents naturally score higher in relevant categories

Example:
- Tutor with weak learning progression → High priority fix
- Architect with no quality checklist → High priority fix
- Operator with no runbooks → High priority fix
