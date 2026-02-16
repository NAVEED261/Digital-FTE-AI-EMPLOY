# Detailed Evaluation Criteria for Agents

Complete rubric with 0-3 scoring guidance for every criterion across all 9 categories.

---

## Category 1: Structure & Metadata (Weight: 12%)

### Criterion 1.1: File Structure

**What to evaluate**: Is the agent file properly formatted with valid YAML frontmatter?

| Score | Evidence |
|-------|----------|
| **0** | No frontmatter; agent file is pure markdown with no metadata |
| **1** | Frontmatter present but incomplete or malformed YAML; missing essential fields like `name` or `description` |
| **2** | Valid YAML frontmatter with `name` and `description`, but missing `model` or `color` |
| **3** | Complete, valid YAML frontmatter with all fields (name, description, model, color); optionally includes `skills` field |

**Good example**:
```yaml
---
name: database-skill-tutor
description: "Use this agent when..."
model: sonnet
color: purple
skills: context7-efficient,database-integration-patterns
---
```

**Bad example**:
```
name: database-skill-tutor (not valid YAML)
or
---
name: database-skill-tutor
(missing description and model)
---
```

---

### Criterion 1.2: File Size

**What to evaluate**: Is the agent appropriately sized for agent guidance (not bloated)?

| Score | Evidence |
|-------|----------|
| **0** | Agent file >300 lines (too verbose, wastes context) |
| **1** | Agent file 200-300 lines (larger than ideal, should compress) |
| **2** | Agent file 100-200 lines (acceptable, could trim) |
| **3** | Agent file 70-150 lines (optimal for agent guidance, context-efficient) |

**Rationale**: Agents should guide without overwhelming context. Detailed references go in separate files.

---

### Criterion 1.3: Name Constraints

**What to evaluate**: Does the agent name follow naming standards?

| Score | Evidence |
|-------|----------|
| **0** | Multiple violations: Mixed case, spaces, special chars, >64 chars; doesn't match directory |
| **1** | 1-2 violations: Uppercase letters or single special char outside hyphens/numbers |
| **2** | Mostly valid: Minor issue like 1 space or 1 non-standard char |
| **3** | Perfect compliance: Lowercase, hyphens and numbers only, ≤64 chars, matches directory name |

**Examples**:
- ✅ Valid: `database-skill-tutor`, `frontend-ui-architect`, `prod-microservices-operator`
- ❌ Invalid: `DatabaseSkillTutor`, `database_skill_tutor`, `database-skill-tutor-and-guides` (>64 chars)

---

### Criterion 1.4: Description Format

**What to evaluate**: Is the description complete, well-formatted, and appropriately scoped?

| Score | Evidence |
|-------|----------|
| **0** | Missing or vague ("helpful agent for database things") |
| **1** | Incomplete: Has [What] but missing [When]; or >1024 chars (verbose) |
| **2** | Adequate: [What] + [When] present, ≤1024 chars; may lack examples or detail |
| **3** | Excellent: [What] + [When] + [Examples] format; ≤1024 chars; clear trigger conditions |

**Structure example** (3-point):
```
"Use this agent when you need [WHAT].
This agent is ideal for [SPECIFIC USE CASES].
Trigger this agent when: (1) [Condition], (2) [Condition], (3) [Condition].

Example: [Context], User: [Query], Assistant: [Response]"
```

---

### Criterion 1.5: Metadata Completeness

**What to evaluate**: Are all frontmatter fields present and meaningful?

| Score | Evidence |
|-------|----------|
| **0** | Missing name or description entirely |
| **1** | Name or description absent; file exists but is unusable |
| **2** | Both name and description present but minimal detail; missing model or color |
| **3** | All fields present (name, description, model, color, optional skills); well-populated |

---

## Category 2: Role Definition & Expertise (Weight: 15-23%, dynamic)

### Criterion 2.1: Role Clarity

**What to evaluate**: Is the agent's role crystal clear? Can someone immediately understand what this agent specializes in?

| Score | Evidence |
|-------|----------|
| **0** | Role undefined or contradictory; unclear what agent does |
| **1** | Role stated but vague: "You are an expert in databases" (too broad) |
| **2** | Clear role statement: "You are an expert database instructor specializing in PostgreSQL and Python integration" |
| **3** | Crystal-clear with unique value: "You are an elite Frontend UI Architect specializing in React/Next.js with focus on context-efficient, production-ready components" |

**Good example** (3-point):
```
You are an expert database instructor specializing in PostgreSQL, SQL fundamentals,
and Python database integration. Your role is to teach complex database concepts
through clear explanations, real-world examples, and hands-on practice.
```

---

### Criterion 2.2: Expertise Domains

**What to evaluate**: Are specific expertise areas enumerated and explained?

| Score | Evidence |
|-------|----------|
| **0** | No expertise domains defined |
| **1** | Vague list: "Knows about databases" without specifics |
| **2** | 3-5 clear domains listed: "PostgreSQL, SQL, Python ORM, query optimization" |
| **3** | 5+ domains clearly described: Each domain gets 1-2 lines of context on why it matters |

**Good example** (3-point):
```
## Content Domains

**PostgreSQL/SQL Fundamentals:**
- Schema design, normalization, relationships (1:1, 1:N, N:M)
- Query optimization, indexing strategies
- Transactions, ACID properties, isolation levels

**Python-Database Integration:**
- psycopg2/psycopg3 connection management
- SQLAlchemy ORM: models, sessions, relationships
```

---

### Criterion 2.3: Specialization

**What to evaluate**: Is the agent laser-focused on a specific domain, or is it too general?

| Score | Evidence |
|-------|----------|
| **0** | Generic: "I'm a helpful AI assistant" or "I know about many things" |
| **1** | Broad: "I'm good at software engineering" (covers too much) |
| **2** | Clear specialization: "I'm a database instructor focused on PostgreSQL and Python" |
| **3** | Laser-focused: "I'm an elite Frontend UI Architect specializing in React/Next.js with context-efficient, production-ready components" with clear differentiation |

---

### Criterion 2.4: Anti-Scope (What Agent Doesn't Do)

**What to evaluate**: Are exclusions and boundaries clearly stated?

| Score | Evidence |
|-------|----------|
| **0** | No mention of what agent doesn't do |
| **1** | Vague exclusions: "I'm not good at everything" |
| **2** | Some clear exclusions: "I don't provide hardware recommendations" or "I don't cover MySQL" |
| **3** | Comprehensive anti-scope: Clear section listing 3-5 things agent explicitly doesn't handle and why |

**Good example** (3-point):
```
## What This Agent Does NOT Do
- Provide MySQL/MariaDB guidance (PostgreSQL only)
- Debug application code (SQL/schema focus only)
- Provide deployment/infrastructure setup (unless directly database-related)
- Teach non-relational databases (NoSQL out of scope)
```

---

### Criterion 2.5: Skill Integration

**What to evaluate**: Are skills appropriately integrated and explained?

| Score | Evidence |
|-------|----------|
| **0** | No skills listed or referenced |
| **1** | Skills listed in frontmatter but never mentioned again in agent content |
| **2** | Skills integrated into workflow: "I'll use the [skill] to..." |
| **3** | Skills explicitly tied to use cases: "When the user needs [X], I use [skill] because [reason]" |

---

## Category 3: Methodology & Workflow (Weight: 14-22%, dynamic)

### Criterion 3.1: Workflow Structure

**What to evaluate**: Is there a clear, numbered workflow with distinct phases?

| Score | Evidence |
|-------|----------|
| **0** | No workflow described; agent describes tasks but not a process |
| **1** | Mentions steps but vague: "I explain concepts and provide examples" |
| **2** | Clear numbered process: "1. Assess knowledge, 2. Explain, 3. Show examples, 4. Practice, 5. Feedback" |
| **3** | 4+ clear phases with sub-steps: "### Phase 1: Clarify..." with bullet points under each |

**Good example** (3-point):
```
## Core Teaching Methodology

Your approach:
1. **Assess Prior Knowledge**: Before diving deep...
2. **Explain Concepts Progressively**: Start with fundamentals...
3. **Contextualize with Python**: Always connect...
4. **Provide Runnable Examples**: Every significant concept...
5. **Emphasize Why**: Explain not just HOW but WHY...
```

---

### Criterion 3.2: Context Gathering

**What to evaluate**: Does agent have a protocol for understanding user needs before acting?

| Score | Evidence |
|-------|----------|
| **0** | No mention of context gathering; assumes it knows what user needs |
| **1** | Vague mention: "I ask questions when needed" |
| **2** | Structured approach: "Ask before acting" principle mentioned |
| **3** | Clear protocol: "1. Clarify the Goal [with questions], 2. Assess understanding level, 3. Gather specific requirements" |

---

### Criterion 3.3: Progressive Structure

**What to evaluate**: Does the agent progress from simple to complex? Is there a clear learning curve?

| Score | Evidence |
|-------|----------|
| **0** | All content at same level; no differentiation between beginner/advanced |
| **1** | Mentions progression but not systematic: "I explain things gradually" |
| **2** | Clear progression: "Start with basics, build to intermediate, explore advanced patterns" |
| **3** | Explicit layering: "Beginner level: [what's covered], Intermediate: [what's covered], Advanced: [what's covered]" |

---

### Criterion 3.4: Decision Points

**What to evaluate**: Are there clear decision criteria (if X then do Y)?

| Score | Evidence |
|-------|----------|
| **0** | No decision logic; agent follows same path regardless |
| **1** | Implicit decisions: Agent might adapt but not explicitly stated |
| **2** | Some decision criteria: "If user asks about performance, explain indexes" |
| **3** | Clear decision framework: "If [condition], then [action]; if [condition], then [action]" |

**Good example** (3-point):
```
## When to Escalate
- If user asks about MySQL/MongoDB → Acknowledge, redirect to PostgreSQL
- If user asks about infrastructure → Acknowledge, keep focus on schema/queries
- If user needs debugging help → Offer guidance on debugging approach
```

---

### Criterion 3.5: Adaptation Guidance

**What to evaluate**: Does agent adapt to different user levels and needs?

| Score | Evidence |
|-------|----------|
| **0** | Rigid, one-size-fits-all approach |
| **1** | Mentions flexibility: "I adapt my explanations" |
| **2** | Some adaptation examples: Different explanations for different backgrounds |
| **3** | Clear adaptation protocol: "If [user level], use [approach]; if [user need], use [different approach]" |

---

### Criterion 3.6: Feedback Mechanisms

**What to evaluate**: Does agent have a protocol for receiving and acting on feedback?

| Score | Evidence |
|-------|----------|
| **0** | No mention of feedback |
| **1** | Mentions feedback loop: "Tell me if this isn't clear" |
| **2** | Structured feedback approach: "I'll ask: Does this make sense?" |
| **3** | Clear feedback protocol: "After explanation, I ask [specific question], and adjust approach based on response" |

---

## Category 4: User Interaction Patterns (Weight: 12%)

### Criterion 4.1: Clarification Strategy

**What to evaluate**: When does agent ask questions? Are clarifications structured or haphazard?

| Score | Evidence |
|-------|----------|
| **0** | No clarification strategy; agent plows ahead with assumptions |
| **1** | Asks questions when stuck, but strategy is unclear |
| **2** | Proactive clarification: "I ask questions before diving deep" |
| **3** | Structured protocol: "I clarify [X], [Y], [Z] upfront using structured questions" |

---

### Criterion 4.2: Tone & Voice

**What to evaluate**: Is there a consistent, clear voice/personality?

| Score | Evidence |
|-------|----------|
| **0** | No discernible tone; sounds generic or robotic |
| **1** | Generic tone; could apply to any agent |
| **2** | Consistent persona: "I use 'we' language and celebrate progress" or "I use technical precision" |
| **3** | Clear, distinctive voice: "I use encouraging, patient language with celebration of progress" or "Elite, precision-focused architectural approach" |

**Good examples**:
- (3-point Tutor) "Be encouraging and patient—database concepts require building mental models. Use 'we' language to create partnership. Celebrate progress."
- (3-point Architect) "Elite, precision-focused. Enforce standards. No compromises on quality gates."

---

### Criterion 4.3: Question Quality

**What to evaluate**: Are questions necessary, targeted, and not obvious?

| Score | Evidence |
|-------|----------|
| **0** | Asks obvious questions: "Do you know what a database is?" or doesn't ask meaningful questions |
| **1** | Some unnecessary questions; some useful ones |
| **2** | Generally good questions; occasional unnecessary one |
| **3** | Targeted, necessary clarifications: Only asks when truly needed; clarifications enable specific adaptations |

---

### Criterion 4.4: Error Handling

**What to evaluate**: What happens when things go wrong? Is there a protocol?

| Score | Evidence |
|-------|----------|
| **0** | No error handling described |
| **1** | Mentions errors but vague: "I handle errors gracefully" |
| **2** | Some error scenarios: "If user is confused, I rephrase" or "If question is about non-domain, I redirect" |
| **3** | Clear protocol: "When [error scenario], do [action]; when [error scenario], do [different action]" |

---

### Criterion 4.5: Output Communication

**What to evaluate**: Is output format, style, and expectations clear?

| Score | Evidence |
|-------|----------|
| **0** | Undefined outputs; reader doesn't know what to expect |
| **1** | Vague output style: "I provide clear explanations" |
| **2** | General output style: "I provide code examples and explanations; use formatted text" |
| **3** | Clear output format: "Output includes: [1] explanation, [2] code example, [3] common mistakes, [4] practice prompt" |

---

## Category 5: Quality Standards & Gates (Weight: 13%)

### Criterion 5.1: Must Follow Checklist

**What to evaluate**: Does agent have a checklist of non-negotiable requirements?

| Score | Evidence |
|-------|----------|
| **0** | No checklist |
| **1** | Mentioned: "I follow best practices" but not enumerated |
| **2** | Partial checklist: 3-4 items listed |
| **3** | Complete checklist: 5+ specific, actionable items; covers critical aspects |

**Good example** (3-point):
```
## Must Follow
- [ ] All code examples are syntactically correct and runnable
- [ ] Always include table/schema definitions for reproducibility
- [ ] No unfinished or placeholder code
- [ ] Keep explanations concise but complete
- [ ] Use proper formatting: code fences, bold for key terms, bullet lists
- [ ] Verify output against quality gates before delivery
```

---

### Criterion 5.2: Must Avoid

**What to evaluate**: Are anti-patterns clearly enumerated?

| Score | Evidence |
|-------|----------|
| **0** | No anti-pattern guidance |
| **1** | Vague: "Avoid bad practices" |
| **2** | 2-3 specific anti-patterns listed |
| **3** | 4+ specific, well-explained anti-patterns with consequences |

**Good example** (3-point):
```
## Must Avoid
- Unfinished code (pseudocode must be clearly marked)
- Vague hand-waving explanations
- Overlooking edge cases
- Generic database advice (must be PostgreSQL-specific)
- Complex examples for beginners (always start simple)
```

---

### Criterion 5.3: Verification Steps

**What to evaluate**: Does agent have a protocol for verifying work before delivery?

| Score | Evidence |
|-------|----------|
| **0** | No verification steps |
| **1** | Mentioned: "I verify my work" but not detailed |
| **2** | 2-3 verification steps described |
| **3** | Complete verification protocol: 4+ steps, each with success criteria |

---

### Criterion 5.4: Quality Gates

**What to evaluate**: Is there an explicit "before delivery" checklist?

| Score | Evidence |
|-------|----------|
| **0** | No quality gates |
| **1** | Informal checks implied |
| **2** | Structured quality check mentioned |
| **3** | Explicit checklist: "Before delivering, verify: [ ] X, [ ] Y, [ ] Z" |

---

### Criterion 5.5: Success Criteria

**What to evaluate**: How does agent know when output is successful/acceptable?

| Score | Evidence |
|-------|----------|
| **0** | Undefined; agent doesn't have clear success criteria |
| **1** | Vague: "I provide good outputs" |
| **2** | Stated: "Success means user understands the concept" |
| **3** | Measurable: "Success criteria: User can reproduce the example, answer a related question, and identify potential pitfalls" |

---

## Category 6: Context Management (Weight: 10-18%, dynamic)

### Criterion 6.1: Token Efficiency Awareness

**What to evaluate**: Does agent show awareness of context window constraints?

| Score | Evidence |
|-------|----------|
| **0** | Ignores context; could be verbose |
| **1** | Mentioned: "I keep responses concise" |
| **2** | Some optimization guidance: "I avoid unnecessary detail" |
| **3** | Explicit strategy: "I use [specific techniques] to minimize token usage, such as progressive disclosure and reference files" |

---

### Criterion 6.2: Tool Usage Strategy

**What to evaluate**: Does agent have clear guidance on which tools to use and when?

| Score | Evidence |
|-------|----------|
| **0** | No guidance on tool selection |
| **1** | Generic tool advice: "I use tools when helpful" |
| **2** | Tool selection criteria: "I use [Tool X] for [Purpose], [Tool Y] for [Purpose]" |
| **3** | Clear decision logic: "When user needs [X], I use [Tool] because [efficiency/accuracy reason]. When user needs [Y], I use [different Tool] for [reason]" |

---

### Criterion 6.3: Skill Leverage

**What to evaluate**: Are relevant skills integrated into the workflow with clear delegation?

| Score | Evidence |
|-------|----------|
| **0** | No skills mentioned or integrated |
| **1** | Skills listed but not integrated: "I can use [skills]" without when/why |
| **2** | Skills integrated: "I'll use [skill] to..." mentioned in workflow |
| **3** | Clear skill delegation: "When user needs [X], I leverage [skill] for [specific reason]" |

---

### Criterion 6.4: Sub-Agent Delegation

**What to evaluate**: Does agent have clear criteria for using other agents?

| Score | Evidence |
|-------|----------|
| **0** | No mention of agent delegation |
| **1** | Mentions: "I can use other agents" but no criteria |
| **2** | Some criteria: "I use Explore agent for [purpose]" |
| **3** | Clear delegation matrix: "I use [Explore] when [condition]; [Plan] when [condition]; [general-purpose] when [condition]" |

---

### Criterion 6.5: Context Preservation

**What to evaluate**: In multi-turn interactions, does agent maintain context effectively?

| Score | Evidence |
|-------|----------|
| **0** | No mention of context preservation across turns |
| **1** | Mentioned: "I keep context across turns" |
| **2** | Some strategies: "I reference previous decisions" |
| **3** | Clear strategy: "I maintain [what] and update [what] across turns; I use [techniques like summaries] for long conversations" |

---

## Category 7: Technical Robustness (Weight: 8%)

### Criterion 7.1: Error Recovery

**What to evaluate**: When things fail, can the agent recover and guide user through it?

| Score | Evidence |
|-------|----------|
| **0** | No error recovery mentioned |
| **1** | Vague: "I handle errors" |
| **2** | Some recovery paths: "If code fails, I suggest debugging steps" |
| **3** | Clear recovery strategies: "When [error], I [diagnose], then [recover]. When [different error], I [different approach]" |

---

### Criterion 7.2: Edge Case Awareness

**What to evaluate**: Are common edge cases acknowledged and handled?

| Score | Evidence |
|-------|----------|
| **0** | No mention of edge cases |
| **1** | Acknowledges complexity: "Some cases are tricky" |
| **2** | 2-3 specific edge cases addressed |
| **3** | Common edge cases documented: "Edge cases handled: [1] empty result sets, [2] null values, [3] timezone handling" |

---

### Criterion 7.3: Dependency Clarity

**What to evaluate**: Are external dependencies, APIs, tools documented?

| Score | Evidence |
|-------|----------|
| **0** | No dependencies noted |
| **1** | Some mentioned: "I use PostgreSQL and Python" |
| **2** | Most dependencies clear: Tools, libraries, versions mentioned |
| **3** | All dependencies documented: Versions, alternatives, constraints listed |

---

### Criterion 7.4: Validation Guidance

**What to evaluate**: Does agent give user clear ways to validate outputs?

| Score | Evidence |
|-------|----------|
| **0** | No validation guidance |
| **1** | Mentioned: "Verify the output" |
| **2** | Some validation: "Test the code" or "Check the schema" |
| **3** | Clear validation protocol: "Validate by: [1] [method], [2] [method], [3] [method]" |

---

## Category 8: Pedagogical Effectiveness (Weight: 8%, Tutors Only)

### Criterion 8.1: Learning Progression

**What to evaluate** (TUTORS ONLY): Is learning structured from basic to advanced?

| Score | Evidence |
|-------|----------|
| **0** | All content at same level; no progression |
| **1** | Vague progression: "I teach basics first" |
| **2** | Clear progression: "Basics → intermediate → advanced" |
| **3** | Explicit layered approach: Each phase clearly scoped; prerequisites stated; difficulty levels marked |

---

### Criterion 8.2: Practice Exercises

**What to evaluate** (TUTORS ONLY): Are there opportunities for hands-on practice?

| Score | Evidence |
|-------|----------|
| **0** | No practice exercises |
| **1** | Mentioned: "I provide practice prompts" |
| **2** | 2-3 exercises included or clear method for practice |
| **3** | Regular practice with difficulty levels: "Beginner exercise: [X], Intermediate: [Y], Advanced: [Z]" |

---

### Criterion 8.3: Example Quality

**What to evaluate** (TUTORS ONLY): Are examples runnable, realistic, and well-explained?

| Score | Evidence |
|-------|----------|
| **0** | No examples provided |
| **1** | Generic examples: "SELECT * FROM users;" |
| **2** | Domain-specific examples: Real-world patterns but simple |
| **3** | Excellent examples: Runnable, well-explained, with context for when/why to use |

**Good example** (3-point):
```python
# Example: Connection Pooling - Intermediate
# Use case: Production applications with many concurrent requests
async with asyncpg.create_pool(dsn) as pool:
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM users')
```

---

### Criterion 8.4: Feedback Mechanism

**What to evaluate** (TUTORS ONLY): How does tutor provide feedback and adapt?

| Score | Evidence |
|-------|----------|
| **0** | No feedback mechanism |
| **1** | Mentioned: "Tell me if confused" |
| **2** | Some feedback: "I ask if explanations are clear" |
| **3** | Clear protocol: "After teaching, I ask [specific question]; based on answer, I [adjust approach/reteach/advance]" |

---

## Category 9: Production Readiness (Weight: 8%, Operators Only)

### Criterion 9.1: Operational Procedures

**What to evaluate** (OPERATORS ONLY): Are step-by-step operational procedures clear?

| Score | Evidence |
|-------|----------|
| **0** | No procedures |
| **1** | Vague: "I help with production" |
| **2** | Some procedures: "Deploy to [environment], verify [status]" |
| **3** | Complete procedures: Step-by-step with checkpoints, verification, rollback |

---

### Criterion 9.2: Compliance Standards

**What to evaluate** (OPERATORS ONLY): Are compliance/standards requirements stated?

| Score | Evidence |
|-------|----------|
| **0** | No standards mentioned |
| **1** | Mentioned: "I follow best practices" |
| **2** | Some standards: "OWASP security standards, SLA compliance" |
| **3** | Clear compliance: Specific standards listed with verification methods |

---

### Criterion 9.3: Runbook Completeness

**What to evaluate** (OPERATORS ONLY): Are runbooks provided for common operations?

| Score | Evidence |
|-------|----------|
| **0** | No runbooks |
| **1** | Mentioned: "I provide operational guidance" |
| **2** | Partial runbooks: 1-2 procedures documented |
| **3** | Complete runbooks: 3+ operations with steps, verification, and rollback |

---

### Criterion 9.4: Production Safeguards

**What to evaluate** (OPERATORS ONLY): Are there safeguards against production mishaps?

| Score | Evidence |
|-------|----------|
| **0** | No safeguards |
| **1** | Mentioned: "I'm careful with production" |
| **2** | Some safeguards: "Always test in staging first" |
| **3** | Clear safeguards: "Before production: [1] [verification], [2] [verification]; Rollback procedure: [steps]" |

---

## Scoring Examples

### Example 1: Strong Structure & Metadata

**Agent**: database-skill-tutor

| Criterion | Score | Justification |
|-----------|-------|-------------|
| File structure | 3/3 | Valid YAML with name, description, model, color, skills |
| File size | 3/3 | ~80 lines, optimal |
| Name constraints | 3/3 | Lowercase, hyphens, ≤64 chars |
| Description format | 3/3 | [What] + [When] + [Examples] format, clear triggers |
| Metadata completeness | 3/3 | All fields present and meaningful |
| **Category Score** | **15/15** | **100/100** | All criteria at 3/3 |

---

### Example 2: Adequate Workflow (but missing progression)

**Agent**: Hypothetical agent with clear workflow but no explicit levels

| Criterion | Score | Justification |
|-----------|-------|-------------|
| Workflow structure | 3/3 | Clear 5-phase numbered approach |
| Context gathering | 2/3 | "Ask questions" mentioned but not protocol |
| Progressive structure | 1/3 | No beginner/intermediate/advanced distinction |
| Decision points | 2/3 | Some "if X, then Y" but not comprehensive |
| Adaptation guidance | 1/3 | Flexibility mentioned but not explicit |
| Feedback mechanisms | 2/3 | Asks if confused, not systematic |
| **Category Score** | **11/18** | **61/100** | Adequate workflow, missing progressive structure |

---

### Example 3: Context Management Red Flag

**Agent**: Agent with skills but no leverage strategy

| Criterion | Score | Justification |
|-----------|-------|-------------|
| Token efficiency | 1/3 | "I'm concise" mentioned, no specific strategy |
| Tool usage strategy | 0/3 | No guidance on which tools to use |
| Skill leverage | 1/3 | Skills listed but never integrated into workflow |
| Sub-agent delegation | 0/3 | No mention of delegating to other agents |
| Context preservation | 1/3 | Mentioned but no specific strategy |
| **Category Score** | **3/15** | **20/100** | Weak context management - critical issue |

---

## Anti-Patterns to Watch For

### Red Flag 1: "I can do everything"
- **Sign**: Agent claims expertise in 10+ domains
- **Impact**: Dilutes specialization, confuses users about scope
- **Fix**: Narrow focus to 3-5 core domains; define clear anti-scope

### Red Flag 2: No verification steps
- **Sign**: Agent doesn't mention how to validate outputs
- **Impact**: Outputs could be wrong; user has no way to verify
- **Fix**: Add "Before delivery" checklist with 4+ verification items

### Red Flag 3: Passive tone
- **Sign**: "Sometimes questions are asked" or "Errors might occur"
- **Impact**: Uncertainty; unclear what agent actually does
- **Fix**: Use active voice: "I ask [specific questions]"; "When [error], I [action]"

### Red Flag 4: No skill integration
- **Sign**: Skills listed but never mentioned in agent guidance
- **Impact**: User won't know when/how to use available skills
- **Fix**: Map each skill to specific use case: "When user needs X, I use [skill]"

### Red Flag 5: Vague methodology
- **Sign**: "I explain concepts and provide examples" (could apply to anyone)
- **Impact**: No differentiation; unclear how this agent approaches problems
- **Fix**: Define specific methodology steps: "1. [Specific action], 2. [Specific action], 3..."

---

## Calibration Notes

### Scoring Consistency
- **Ambiguous cases**: If a criterion is between two scores, prefer the lower score unless evidence strongly supports higher
- **Pattern matching**: If pattern (Tutor/Architect/Operator) is unclear, note as "Mixed" and don't penalize
- **Variance allowance**: Same agent scored by different evaluators should be within ±5 points

### Common Scoring Errors
1. **Overstating clarity**: "I teach well" ≠ 3-point. Need specifics: "I use [method]"
2. **Crediting intent**: "I try to be concise" ≠ 3-point. Need evidence: "I limit to X lines"
3. **Confusing quantity with quality**: Many examples ≠ 3-point. Need: Good examples + clear explanation
