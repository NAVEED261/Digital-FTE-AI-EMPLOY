---
name: agent-validator
description: |
  Validate AI agents against production-level quality criteria with 0-100 scoring.
  Use when evaluating agent quality, identifying bugs/gaps, or improving agents to expert level.
  Evaluates agents across 9 categories: structure, role definition, methodology, user interaction,
  quality standards, context management, technical robustness, pedagogical effectiveness (tutors),
  and production readiness (operators). Returns actionable validation report with specific improvements.
---

# Agent Validator

Systematically evaluate AI agents against production-level criteria and generate actionable improvement roadmaps.

## Validation Workflow (4 Phases)

### Phase 1: Gather Context (5 min)

1. **Read agent file** completely
2. **Identify agent pattern** from content analysis:
   - **Tutor Pattern**: Teaching, progressive learning, practice exercises, encouraging tone
   - **Architect Pattern**: Design workflows, quality verification, trade-off analysis
   - **Operator Pattern**: Production procedures, operational readiness, runbooks
3. **Estimate line count** (target: 70-174 lines for agents)
4. **Note frontmatter** (name, description, model, color, skills)
5. **Identify expertise domains** from role description

### Phase 2: Apply Criteria (20 min)

Evaluate against **9 categories** with dynamic weighting based on agent pattern.

Each criterion scores **0-3 scale**:
- **0**: Missing/Absent
- **1**: Present but inadequate
- **2**: Adequate implementation
- **3**: Excellent implementation

### Phase 3: Calculate & Report (5 min)

- Calculate category scores: (Sum of criteria) / (Max possible) × 100
- Apply dynamic weights (redistribute unused weights)
- Calculate overall score: Σ(Category Score × Weight)
- Determine rating (Production/Good/Adequate/Developing/Incomplete)

### Phase 4: Generate Recommendations (10 min)

- Identify critical issues (blocks deployment)
- List high/medium/low priority improvements
- Suggest pattern-specific enhancements
- Provide strengths summary

---

## Evaluation Categories (9 Total)

### Category 1: Structure & Metadata (12%)

**Purpose**: Foundation quality—file organization, naming, frontmatter

| Criterion | 0-3 Scoring |
|-----------|------------|
| **File structure** | 0: No frontmatter; 1: Incomplete YAML; 2: Valid YAML, missing fields; 3: Complete YAML (name, description, model, color) |
| **File size** | 0: >300 lines; 1: 200-300 lines; 2: 100-200 lines; 3: 70-150 lines (optimal for agents) |
| **Name constraints** | 0: Invalid format; 1: Multiple violations; 2: Minor issues; 3: Lowercase, hyphens/numbers only, ≤64 chars |
| **Description format** | 0: Absent/vague; 1: Incomplete; 2: Adequate [What/When]; 3: Excellent [What] + [When] + [Examples], ≤1024 chars |
| **Metadata completeness** | 0: Missing name/description; 1: Name or description absent; 2: Both present, minimal detail; 3: All fields present (name, description, model, color, skills) |

**Critical fail condition**: Missing frontmatter or >300 lines = automatic 0 score

---

### Category 2: Role Definition & Expertise (15-23%, dynamic)

**Purpose**: Clear positioning—what the agent does, expertise areas, specialization

| Criterion | 0-3 Scoring |
|-----------|------------|
| **Role clarity** | 0: Undefined/vague; 1: Stated but unclear; 2: Clear role statement; 3: Crystal-clear with specific expertise domain |
| **Expertise domains** | 0: None defined; 1: Vague list; 2: 3-5 domains listed; 3: 5+ domains clearly described with context |
| **Specialization** | 0: General/unfocused; 1: Broad focus; 2: Clear specialization; 3: Laser-focused expertise with unique value prop |
| **Anti-scope** | 0: Not mentioned; 1: Vague exclusions; 2: Some "must avoid" mentioned; 3: Clear "what we don't do" section |
| **Skill integration** | 0: No skills listed; 1: Skills listed, not explained; 2: Skills integrated into workflow; 3: Skills explicitly tied to use cases |

**Dynamic weight adjustment**: If agent has no pedagogical focus (not a tutor) → +8% to this category

---

### Category 3: Methodology & Workflow (14-22%, dynamic)

**Purpose**: Structured approach—how agent tackles problems, decision points, adaptation

| Criterion | 0-3 Scoring |
|-----------|------------|
| **Workflow structure** | 0: No workflow; 1: Mentions steps but vague; 2: 3-5 clear phases; 3: 4+ phases with numbered steps |
| **Context gathering** | 0: None mentioned; 1: Vague gathering; 2: Structured approach ("ask before acting"); 3: Clear protocols (what/when/how to gather) |
| **Progressive structure** | 0: All-at-once approach; 1: Some progression; 2: Clear progression; 3: Explicit layering (fundamentals → advanced) |
| **Decision points** | 0: No decisions shown; 1: Implicit decisions; 2: Some decision criteria; 3: Clear "when to do X" guidance |
| **Adaptation guidance** | 0: Rigid, no adaptation; 1: Mentions flexibility; 2: Some adaptation patterns; 3: Clear "if user needs X, then do Y" |
| **Feedback mechanisms** | 0: None; 1: Mentioned; 2: Structured feedback; 3: Clear feedback loops with verification steps |

---

### Category 4: User Interaction Patterns (12%)

**Purpose**: Quality of user engagement—how well agent communicates, clarifies, handles questions

| Criterion | 0-3 Scoring |
|-----------|------------|
| **Clarification strategy** | 0: No clarification; 1: Asks when stuck; 2: Proactive clarification; 3: Structured clarification protocol |
| **Tone & voice** | 0: Absent/robotic; 1: Generic; 2: Consistent persona; 3: Clear, encouraging, personable voice throughout |
| **Question quality** | 0: Asks obvious/vague questions; 1: Some unnecessary questions; 2: Generally good questions; 3: Targeted, necessary clarifications |
| **Error handling** | 0: No error protocol; 1: Vague handling; 2: Some error scenarios covered; 3: Clear "when this happens, do that" guidance |
| **Output communication** | 0: Undefined outputs; 1: Vague outputs; 2: General output style; 3: Clear output format with examples |

---

### Category 5: Quality Standards & Gates (13%)

**Purpose**: Verification—how agent ensures output quality, validates completeness, prevents bad outputs

| Criterion | 0-3 Scoring |
|-----------|------------|
| **Must Follow checklist** | 0: None; 1: Mentioned; 2: Partial checklist (3-4 items); 3: Complete checklist (5+ items) covering all critical aspects |
| **Must Avoid section** | 0: None; 1: Vague anti-patterns; 2: 2-3 specific anti-patterns; 3: 4+ specific, well-explained anti-patterns |
| **Verification steps** | 0: None; 1: Mentioned; 2: 2-3 verification steps; 3: Complete verification protocol with success criteria |
| **Quality gates** | 0: No gates; 1: Informal checks; 2: Structured quality check; 3: Explicit "before delivery" checklist |
| **Success criteria** | 0: Undefined; 1: Vague; 2: Stated; 3: Measurable, clear success definition |

---

### Category 6: Context Management (10-18%, dynamic)

**Purpose**: Efficiency—token optimization, tool usage, skill leverage, delegation decisions

| Criterion | 0-3 Scoring |
|-----------|------------|
| **Token efficiency awareness** | 0: Ignores context; 1: Mentioned; 2: Some optimization guidance; 3: Explicit token-saving strategies |
| **Tool usage strategy** | 0: No guidance; 1: Generic tool advice; 2: Tool selection criteria; 3: Clear "use tool X when Y" with rationale |
| **Skill leverage** | 0: No skills mentioned; 1: Skills listed; 2: Skills integrated into workflow; 3: Clear skill delegation strategy |
| **Sub-agent delegation** | 0: No delegation guidance; 1: Mentions delegation; 2: Some delegation criteria; 3: Clear "use Explore agent when X" patterns |
| **Context preservation** | 0: No mention; 1: Mentioned; 2: Some guidance; 3: Clear strategies for multi-turn context maintenance |

**Dynamic weight adjustment**: Central to all agents - increases to 18% if other categories need redistribution

---

### Category 7: Technical Robustness (8%)

**Purpose**: Reliability—error recovery, edge cases, dependencies, validation

| Criterion | 0-3 Scoring |
|-----------|------------|
| **Error recovery** | 0: No error handling; 1: Vague handling; 2: Some error scenarios; 3: Clear recovery strategies |
| **Edge case awareness** | 0: No mention; 1: Acknowledges complexity; 2: 2-3 edge cases addressed; 3: Common edge cases documented |
| **Dependency clarity** | 0: No dependencies noted; 1: Some mentioned; 2: Most dependencies clear; 3: All external dependencies documented |
| **Validation guidance** | 0: None; 1: Informal; 2: Structured validation; 3: Clear validation criteria for outputs |

---

### Category 8: Pedagogical Effectiveness (8%, tutors only)

**Purpose**: Teaching quality (TUTOR AGENTS ONLY)—progressive learning, practice exercises, feedback

| Criterion | 0-3 Scoring |
|-----------|------------|
| **Learning progression** | 0: All-at-once; 1: Vague progression; 2: Clear progression (basics → advanced); 3: Explicit layered approach with prerequisites |
| **Practice exercises** | 0: None; 1: Mentioned; 2: 2-3 exercises included; 3: Regular practice with difficulty levels |
| **Example quality** | 0: No examples; 1: Generic examples; 2: Domain-specific examples; 3: Runnable, well-explained examples |
| **Feedback mechanism** | 0: None; 1: Mentioned; 2: Some feedback guidance; 3: Clear "how to provide feedback" and "how to receive feedback" |

**Application**: Score if tutor pattern detected; redistribute 8% if not applicable

---

### Category 9: Production Readiness (8%, operators only)

**Purpose**: Operations quality (OPERATOR AGENTS ONLY)—procedures, compliance, artifact completeness

| Criterion | 0-3 Scoring |
|-----------|------------|
| **Operational procedures** | 0: None; 1: Vague; 2: Some procedures; 3: Clear step-by-step operational procedures |
| **Compliance standards** | 0: None; 1: Mentioned; 2: Some standards; 3: Clear compliance requirements and verification |
| **Runbook completeness** | 0: No runbooks; 1: Mentioned; 2: Partial runbooks; 3: Complete runbooks with examples |
| **Production safeguards** | 0: None; 1: Mentioned; 2: Some safeguards; 3: Clear safeguards, validation, rollback procedures |

**Application**: Score if operator pattern detected; redistribute 8% if not applicable

---

## Agent Pattern Detection

### Tutor Pattern (Teaching-Focused)

**Keywords to detect**:
- "Learn", "teach", "instruct", "practice", "exercise", "beginner/intermediate/advanced", "explain", "understand"
- Progressive complexity mentioned
- Examples and code samples provided
- Encouragement and feedback mechanisms

**Required sections**:
- Learning progression
- Practice exercises (or clear method for practice)
- Examples (runnable or realistic)
- Feedback mechanisms

**Category 8 applies**: Pedagogical Effectiveness (8%)
**Category 9 redistributes**: +4% to Methodology, +4% to Role Definition

---

### Architect Pattern (Design-Focused)

**Keywords to detect**:
- "Design", "architecture", "quality", "best practices", "verification", "checklist", "trade-off", "pattern"
- Quality gates and verification steps
- Design workflows and decision frameworks
- Anti-patterns and must-avoid guidance

**Required sections**:
- Design workflow (phases/steps)
- Quality verification checklist
- Design trade-offs explained
- Best practices enforced

**Category 8 redistributes**: +8% to Role Definition
**Category 9 redistributes**: +8% to Context Management

---

### Operator Pattern (Operations-Focused)

**Keywords to detect**:
- "Production", "operational", "deploy", "monitor", "procedures", "runbook", "production-ready", "compliance"
- Clear operational steps
- Production safeguards and validation
- Deployment and rollback procedures

**Required sections**:
- Operational procedures (clear steps)
- Production safeguards
- Runbook(s) or deployment guide
- Compliance requirements

**Category 8 redistributes**: +8% to Role Definition
**Category 9 applies**: Production Readiness (8%)

---

## Scoring Methodology

### Category Score Calculation

```
Category Score = (Sum of criterion scores / Max possible points) × 100

Example:
- Criterion 1: 2/3
- Criterion 2: 3/3
- Criterion 3: 1/3
- Total: 6/9 = 0.667 × 100 = 66.7/100
```

### Overall Score Calculation

```
Overall Score = Σ(Category Score × Adjusted Weight)

With dynamic weight redistribution:
- Base weights = 100% total
- If category N/A → redistribute its weight to applicable categories
- Sum all weighted contributions
```

### Rating Thresholds

| Score Range | Rating | Meaning | Action |
|------------|--------|---------|--------|
| 90-100 | **Production** | Expert-level, ready for wide use | Deploy |
| 75-89 | **Good** | Solid functionality, minor improvements needed | Address High priority items |
| 60-74 | **Adequate** | Functional but needs work | Plan significant improvements |
| 40-59 | **Developing** | Significant gaps, not ready | Major rework required |
| 0-39 | **Incomplete** | Major issues, not deployable | Rebuild or retire |

---

## Output Format

Generate validation report using this structure:

```markdown
# Agent Validation Report: [agent-name]

**Pattern Detected**: [Tutor/Architect/Operator/Mixed/Unclear]
**Rating**: [Production/Good/Adequate/Developing/Incomplete]
**Overall Score**: [X]/100

## Summary
[2-3 sentence assessment of agent quality, pattern clarity, and main findings]

## Category Scores

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Structure & Metadata | X/100 | 12% | X |
| Role Definition & Expertise | X/100 | 15-23% | X |
| Methodology & Workflow | X/100 | 14-22% | X |
| User Interaction Patterns | X/100 | 12% | X |
| Quality Standards & Gates | X/100 | 13% | X |
| Context Management | X/100 | 10-18% | X |
| Technical Robustness | X/100 | 8% | X |
| Pedagogical Effectiveness | X/100 | 0-8% | X |
| Production Readiness | X/100 | 0-8% | X |
| **Overall** | **X**/100 | - | - |

## Critical Issues (if any)

[If score < 60, list issues preventing deployment]
- [Issue 1 with impact]
- [Issue 2 with impact]

## Improvement Recommendations

### High Priority (Address first)
1. [Specific action with impact]
2. [Specific action with impact]

### Medium Priority (Address next)
1. [Specific action with impact]
2. [Specific action with impact]

### Low Priority (Nice to have)
1. [Specific action with benefit]

## Pattern Compliance Check

**Pattern Detected**: [Tutor/Architect/Operator]
**Pattern Requirements Met**: [X/Y]

- [ ] [Required section 1]
- [ ] [Required section 2]
- [ ] [Required section 3]

[List any missing pattern-specific requirements]

## Strengths

- [What the agent does well]
- [Key differentiator or strong point]
- [Technical or pedagogical strength]

## Weight Adjustments

[Document any dynamic weight redistribution applied]
- Category X weight adjusted: +Y% (reason)
- Category Z weight adjusted: -W% (reason)

---

**Recommendation**: [Next steps to reach Production level if not already there]
```

---

## Quick Validation Checklist

For rapid assessment, verify these critical items:

### Structure & Metadata (Must have)
- [ ] Frontmatter present (name, description)
- [ ] Agent length 70-200 lines (context-efficient)
- [ ] Name format valid (lowercase, hyphens, ≤64 chars)

### Pattern Clarity (Must have)
- [ ] Pattern identifiable (Tutor/Architect/Operator)
- [ ] Pattern requirements present
- [ ] Role clearly defined

### Core Content (Must have)
- [ ] Expertise domains listed
- [ ] Methodology/workflow described
- [ ] User interaction strategy present

### Quality Gates (Must have)
- [ ] Must Follow checklist present
- [ ] Must Avoid section present
- [ ] Verification steps defined

### Context Management (Must have)
- [ ] Tool/skill usage strategy mentioned
- [ ] Context efficiency addressed
- [ ] Delegation patterns present

**Scoring Quick Estimate**:
- All 5 must-haves present → Likely Good/Production (75+)
- 3-4 must-haves → Likely Adequate (60-74)
- <3 must-haves → Likely Developing (40-59)

---

## Reference Files

| File | Purpose | When to Read |
|------|---------|--------------|
| `references/detailed-criteria.md` | Full rubric with examples | Deep evaluation or uncertain scores |
| `references/agent-patterns.md` | Pattern definitions & requirements | Pattern identification or compliance check |
| `references/scoring-examples.md` | Calibration with real agents | Scoring consistency or calibration |
| `references/improvement-patterns.md` | Common issues & fixes | Generating actionable recommendations |

---

## Usage Examples

### Basic validation
```
Validate the database-skill-tutor agent against production criteria
```

### Pattern-focused review
```
Check if the prod-microservices-operator agent meets Operator pattern requirements
```

### Improvement planning
```
Validate frontend-ui-architect and generate a roadmap to reach 95+ score
```

---

## Agent Pattern Classification Summary

| Pattern | Use When | Key Characteristics |
|---------|----------|-------------------|
| **Tutor** | Teaching concepts, progressive learning | Progressive structure, practice exercises, encouragement |
| **Architect** | Design guidance, quality verification | Design workflows, checklists, best practices, trade-offs |
| **Operator** | Production operations, deployment | Procedures, runbooks, compliance, production safeguards |

See `references/agent-patterns.md` for detailed pattern requirements and detection guidelines.
