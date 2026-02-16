# Scoring Examples and Calibration

Real and hypothetical agent validations to calibrate scoring consistency across evaluators.

---

## Example 1: database-skill-tutor (Real - Tutor Pattern)

### Agent Overview

Located: `/.claude/agents/database-skill-tutor.md` (~80 lines)

**Summary**: Expert database instructor specializing in PostgreSQL, SQL, and Python integration. Progressive teaching methodology with examples, practice opportunities, and feedback mechanisms.

---

### Category-by-Category Scoring

#### Category 1: Structure & Metadata (12%)

| Criterion | Score | Evidence | Justification |
|-----------|-------|----------|-------------|
| File structure | 3/3 | Valid YAML: name, description, model, color, skills | Complete frontmatter with all fields |
| File size | 3/3 | ~80 lines | Optimal for agent, context-efficient |
| Name constraints | 3/3 | `database-skill-tutor` | Lowercase, hyphens, ≤64 chars |
| Description format | 3/3 | [What] + [When] + [Examples] structure | Clear use cases and trigger conditions |
| Metadata completeness | 3/3 | All fields present and meaningful | name, description, model (sonnet), color (purple), skills listed |

**Category Score**: 15/15 = **100/100**

---

#### Category 2: Role Definition & Expertise (15%)

| Criterion | Score | Evidence | Justification |
|-----------|-------|----------|-------------|
| Role clarity | 3/3 | "Expert database instructor specializing in PostgreSQL, SQL, Python integration" | Crystal-clear role with unique value |
| Expertise domains | 3/3 | 3 major domains with multiple sub-topics | PostgreSQL, Neon, Python-DB integration all detailed |
| Specialization | 3/3 | Laser-focused on database education | Not general programming, specifically databases + Python |
| Anti-scope | 2/3 | Implicitly clear (teaches PostgreSQL, not MySQL), but no explicit anti-scope section | Could be more explicit about what it doesn't do |
| Skill integration | 3/3 | Skills in frontmatter, integrated into workflow | "context7-efficient, database-integration-patterns" are referenced |

**Category Score**: 14/15 = **93/100**

---

#### Category 3: Methodology & Workflow (14%)

| Criterion | Score | Evidence | Justification |
|-----------|-------|----------|-------------|
| Workflow structure | 3/3 | 5 clear phases: Assess, Explain, Contextualize, Examples, Emphasize Why | Numbered, detailed approach |
| Context gathering | 3/3 | "Clarify the Goal: ask or confirm skill/concept and why" | Structured protocol for understanding user needs |
| Progressive structure | 3/3 | "Beginner/intermediate/advanced" marked for examples | Clear difficulty levels throughout |
| Decision points | 2/3 | Some decision criteria ("if user asks ambiguous question"), but could be more systematic | Most decisions implicit rather than explicit |
| Adaptation guidance | 3/3 | "Offer multiple explanation styles if concept isn't clicking" | Clear adaptation to learning style |
| Feedback mechanisms | 3/3 | "Does this make sense? What would you like to dive deeper into?" | Explicit feedback loop requested |

**Category Score**: 17/18 = **94/100**

---

#### Category 4: User Interaction Patterns (12%)

| Criterion | Score | Evidence | Justification |
|-----------|-------|----------|-------------|
| Clarification strategy | 3/3 | "If a learner's question is ambiguous, ask 1–2 clarifying questions" | Structured clarification protocol |
| Tone & voice | 3/3 | "Be encouraging and patient", "use 'we' language", "celebrate progress" | Warm, encouraging, supportive tone evident |
| Question quality | 3/3 | Clarification questions are specific ("Are you asking about raw SQL or ORM usage?") | Targeted and necessary |
| Error handling | 3/3 | "Gently correct misconceptions", "offer multiple explanation styles" | Clear error recovery protocol |
| Output communication | 3/3 | "Code examples must be syntactically correct", "use proper formatting" | Clear output specification |

**Category Score**: 15/15 = **100/100**

---

#### Category 5: Quality Standards & Gates (13%)

| Criterion | Score | Evidence | Justification |
|-----------|-------|----------|-------------|
| Must Follow checklist | 3/3 | Multiple items: syntactically correct code, table definitions, no placeholder code | 5+ specific items listed |
| Must Avoid | 2/3 | "Avoid unfinished code", "avoid unfinished or placeholder code" | Present but could be more systematic |
| Verification steps | 2/3 | "Tested mentally against PostgreSQL 12+", "learners can reproduce" | Some verification implied but not explicit |
| Quality gates | 1/3 | No explicit "before delivery" checklist | Could have formal QA checklist |
| Success criteria | 3/3 | "Code examples must be syntactically correct", clear output expectations | Success is measurable |

**Category Score**: 11/15 = **73/100**

---

#### Category 6: Context Management (10%)

| Criterion | Score | Evidence | Justification |
|-----------|-------|----------|-------------|
| Token efficiency | 2/3 | "Use proper formatting", "keep explanations concise" | Some optimization but not explicit strategy |
| Tool usage | 1/3 | No specific tool guidance provided | Could mention when to use which tools |
| Skill leverage | 2/3 | Skills listed but integration could be clearer | Mentioned in frontmatter |
| Sub-agent delegation | 1/3 | No mention of delegating to other agents | Could guide when to use Explore, Plan, etc. |
| Context preservation | 2/3 | Not explicitly addressed for multi-turn | Implicit understanding but not stated |

**Category Score**: 8/15 = **53/100**

---

#### Category 7: Technical Robustness (8%)

| Criterion | Score | Evidence | Justification |
|-----------|-------|----------|-------------|
| Error recovery | 2/3 | "Offer multiple explanation styles", gentle correction of misconceptions | Some error handling but could be more explicit |
| Edge case awareness | 2/3 | Common database pitfalls mentioned implicitly | Could list specific edge cases explicitly |
| Dependency clarity | 2/3 | PostgreSQL 12+ and Python libraries mentioned | Dependencies clear but versions could be explicit |
| Validation | 2/3 | "Learners can reproduce" implies validation | Could be more explicit |

**Category Score**: 8/12 = **67/100**

---

#### Category 8: Pedagogical Effectiveness (8% - Tutor only)

| Criterion | Score | Evidence | Justification |
|-----------|-------|----------|-------------|
| Learning progression | 3/3 | Fundamentals → Intermediate → Advanced | Clear explicit levels |
| Practice exercises | 3/3 | "Practice Prompts: Suggest exercises or modifications" | Clear practice protocol |
| Example quality | 3/3 | Code examples included, tested, realistic | Excellent examples with context |
| Feedback mechanism | 3/3 | "Tell me if this isn't clear", "What would you like to dive deeper into?" | Strong feedback loop |

**Category Score**: 12/12 = **100/100**

---

#### Category 9: Production Readiness (8% - N/A for Tutor)

**Not applicable to Tutor pattern** → Redistribute 8% to other categories

---

### Weight Adjustment for Tutor Pattern

Base weights:
- Structure: 12%
- Role Definition: 15%
- Methodology: 14%
- Interaction: 12%
- Quality Standards: 13%
- Context Management: 10%
- Technical Robustness: 8%
- Pedagogical: 8%
- Production: 0% (not applicable)
- **Total: 92%**

Remaining 8% redistributed to Context Management (critical for all agents):
- Context Management: 10% + 8% = **18%**

**Adjusted weights**:
- Structure: 12%
- Role Definition: 15%
- Methodology: 14%
- Interaction: 12%
- Quality Standards: 13%
- Context Management: **18%**
- Technical Robustness: 8%
- Pedagogical: 8%

---

### Overall Score Calculation

```
Structure (100 × 0.12) = 12.0
Role Definition (93 × 0.15) = 13.95
Methodology (94 × 0.14) = 13.16
Interaction (100 × 0.12) = 12.0
Quality Standards (73 × 0.13) = 9.49
Context Management (53 × 0.18) = 9.54  ← Lowest category
Technical Robustness (67 × 0.08) = 5.36
Pedagogical (100 × 0.08) = 8.0

Overall Score = 83.5/100
```

---

### Validation Report

```
# Agent Validation Report: database-skill-tutor

**Pattern Detected**: Tutor (Teaching-focused)
**Rating**: Good (83.5/100)
**Overall Score**: 83.5/100

## Summary
Strong tutor agent with excellent pedagogical structure, clear role definition, and
engaging interaction patterns. Learning progression is well-organized with multiple
examples and feedback mechanisms. Primary area for improvement is context management
and explicit quality gates.

## Category Scores

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Structure & Metadata | 100/100 | 12% | 12.0 |
| Role Definition & Expertise | 93/100 | 15% | 13.95 |
| Methodology & Workflow | 94/100 | 14% | 13.16 |
| User Interaction Patterns | 100/100 | 12% | 12.0 |
| Quality Standards & Gates | 73/100 | 13% | 9.49 |
| Context Management | 53/100 | 18% | 9.54 |
| Technical Robustness | 67/100 | 8% | 5.36 |
| Pedagogical Effectiveness | 100/100 | 8% | 8.0 |
| **Overall** | **83.5**/100 | - | - |

## Critical Issues
None. Agent is fully functional and good quality.

## Improvement Recommendations

### High Priority
1. **Explicit quality gates**: Add "Before Delivery" checklist (currently mentioned informally)
   - Expected improvement: +5-7 points to Quality Standards category
   - Example: "Before providing examples, verify: [X], [Y], [Z]"

2. **Context management strategy**: Define explicit token-saving techniques
   - Expected improvement: +8-12 points to Context Management category
   - Example: "When context is limited, I [compress examples], [use references]"

### Medium Priority
1. **Anti-scope section**: Explicitly list what agent doesn't cover
   - Example: "I don't cover: MySQL/MariaDB, distributed databases, NoSQL"
   - Expected improvement: +2-3 points to Role Definition

2. **Sub-agent delegation guidance**: Guide when to use other agents
   - Example: "If you need to explore a complex codebase pattern, I recommend using Explore agent"
   - Expected improvement: +4-6 points to Context Management

### Low Priority
1. **Decision framework**: More explicit decision criteria for when to adapt
   - Example: "If user asks about [topic], I [approach]; if [different topic], I [different approach]"

## Pattern Compliance Check

**Pattern Detected**: Tutor (Teaching-focused)
**Pattern Requirements Met**: 4/4 ✅

- [✅] Learning progression (Fundamentals → Intermediate → Advanced)
- [✅] Practice exercises (Practice Prompts section)
- [✅] Example quality (Runnable, well-explained)
- [✅] Feedback mechanism (Explicit feedback loop)

All tutor pattern requirements met. Agent is well-aligned with tutor archetype.

## Strengths

- Crystal-clear role and expertise definition
- Excellent learning progression with explicit levels
- Warm, encouraging tone that builds learner confidence
- Strong feedback mechanisms that adapt to learner needs
- High-quality examples with context and explanations
- Comprehensive domain coverage (SQL, PostgreSQL, Python)

## Weight Adjustments

Production Readiness category (8%) was not applicable to Tutor pattern and redistributed
to Context Management (from 10% to 18%), bringing context efficiency into focus as critical
for this tutor agent.

---

**Recommendation**: Address High Priority items (quality gates, context strategy)
to reach Production level (90+). Core teaching quality is already excellent.
```

---

## Example 2: frontend-ui-architect (Real - Architect Pattern)

### Quick Scoring Summary

**Pattern**: Architect (Design-focused)

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Structure | 100/100 | 12% | 12.0 |
| Role Definition | 96/100 | 15%+8% | 21.84 |
| Methodology | 95/100 | 14% | 13.3 |
| Interaction | 95/100 | 12% | 11.4 |
| Quality Standards | 92/100 | 13% | 11.96 |
| Context Management | 88/100 | 10% | 8.8 |
| Technical Robustness | 85/100 | 8% | 6.8 |
| Pedagogical | N/A | 0% | 0 |
| **Production** | N/A | 0% | 0 |
| **Overall** | **91.2**/100 | - | - |

**Rating**: **Production (91.2/100)** ✅

---

### Key Findings

**Strengths**:
- Comprehensive design workflow with clear phases
- Quality assurance checklist with 10+ items
- Best practices enforced (semantic HTML, accessibility, etc.)
- Design trade-offs discussed (virtual scrolling vs. render all, etc.)
- Context-efficient UI patterns explicitly mentioned
- Chat widget and RAG system specializations

**High Priority Improvements** (to reach 95+):
1. **Expand anti-patterns section**: Currently mentions some, could be more systematic (4-5 anti-patterns with consequences)
2. **Add decision framework**: When to use which tool/approach (currently good, could be explicit)

**Result**: Already Production-level. Minor tweaks for excellence.

---

## Example 3: Hypothetical Adequate Agent

### Agent Content (Excerpt)

```
---
name: example-adequate-agent
description: "A helpful agent for software development"
---

## Role

I'm a software development assistant that helps with coding problems.

## What I Do

I can help with:
- Writing code
- Fixing bugs
- Explaining concepts
- Best practices

## Methodology

I ask questions to understand the problem, then provide solutions.
I give examples and explain my reasoning.
I help verify the solution works.

## Standards

I follow best practices and avoid common mistakes.
```

---

### Scoring Analysis

| Category | Score | Issue |
|----------|-------|-------|
| Structure | 60/100 | Description vague ("helpful agent for software development") |
| Role Definition | 55/100 | Too broad, no specialization, no anti-scope |
| Methodology | 50/100 | Vague workflow, no decision criteria, no adaptation |
| Interaction | 65/100 | Generic interaction, no clarification protocol |
| Quality Standards | 40/100 | No specific standards, no verification, no gates |
| Context Management | 35/100 | No tool/skill guidance, no delegation |
| Technical Robustness | 45/100 | No error handling, no edge cases |
| Pedagogical/Production | N/A | Pattern unclear |

**Overall**: ~50/100 → **Adequate**

---

### Key Issues

1. **Pattern unclear**: Reads like general developer assistant, not specialized tutor/architect/operator
2. **No specialization**: Expertise too broad ("coding problems")
3. **Vague methodology**: No clear workflow, no decision points
4. **Weak standards**: Generic best practices, no verification
5. **No context strategy**: Doesn't mention tools, skills, or delegation

---

### Path to Good (75+)

1. **Narrow focus**: Pick one specialization (e.g., "React component development" instead of "software development")
2. **Explicit workflow**: Define phases with decision criteria
3. **Pattern clarity**: Lean into Tutor or Architect patterns
4. **Quality gates**: Add specific checklist (5+ items) with verification
5. **Context management**: Explain tool usage and skill leverage

---

## Example 4: Incomplete Agent (Hypothetical)

### Agent Content (Minimal)

```
---
name: incomplete-agent
---

I'm an AI agent that helps with stuff.
I answer questions and provide guidance.
I try to be helpful.
```

---

### Scoring Analysis

| Category | Score | Issue |
|----------|-------|-------|
| Structure | 10/100 | Missing required fields (description, model, color) |
| Role Definition | 0/100 | No role defined, expertise undefined |
| Methodology | 5/100 | No methodology described |
| Interaction | 10/100 | No clarification strategy, no output spec |
| Quality Standards | 0/100 | No standards, no verification, no gates |
| Context Management | 0/100 | No mention of context, tools, skills |
| Technical Robustness | 5/100 | No error handling, no dependencies |
| Pedagogical/Production | 0/100 | Pattern completely unclear |

**Overall**: ~3/100 → **Incomplete** ❌

---

### Critical Failures

1. **Frontmatter incomplete**: Missing description, model, color
2. **Role undefined**: "I'm an AI that helps with stuff" is not a role
3. **No methodology**: Just says "try to be helpful"
4. **No quality gates**: No verification possible
5. **Not deployable**: Doesn't meet minimum production standards

---

### Path to Developing (40-59)

1. **Complete frontmatter**: Add description, model, color fields
2. **Define role and expertise**: Pick specialization, list domains
3. **Add basic methodology**: 3-4 phases with clear steps
4. **Add quality checklist**: At least 3-4 items
5. **Identify pattern**: Is it Tutor, Architect, or Operator?

---

## Scoring Consistency Guidelines

### Key Calibration Points

1. **Score 3/3 only when**:
   - Criterion is comprehensive and excellent
   - Clear examples or evidence in agent content
   - Goes beyond minimum requirement
   - Example: Role clarity scored 3 = "Elite Frontend UI Architect specializing in React/Next.js" (not just "I'm a frontend developer")

2. **Score 2/3 when**:
   - Criterion is present and adequate
   - Meets minimum requirement but not exceptional
   - Example: Role clarity scored 2 = "I'm a database instructor for PostgreSQL" (clear but generic phrasing)

3. **Score 1/3 when**:
   - Criterion is present but inadequate
   - Partially addressed or vague
   - Example: Role clarity scored 1 = "I help with databases" (too vague, could mean many things)

4. **Score 0/3 when**:
   - Criterion is missing entirely
   - Example: Role clarity scored 0 = No role statement at all

### Category Score Interpretation

- **90-100**: Excellent (all criteria 2.5-3)
- **75-89**: Good (mostly 2-3, some 1-2)
- **60-74**: Adequate (mix of 1-2, few 0s)
- **40-59**: Developing (mix of 0-2, many gaps)
- **0-39**: Incomplete (many 0s, missing critical items)

### Variance Management

When evaluating the same agent across multiple reviewers:
- Expected variance: ±3-5 points due to subjective judgment
- If variance >10 points: Review scoring with focus on ambiguous criteria
- If variance >15 points: Criteria definition may be unclear; consider updating rubric

---

## Quick Reference: Score Calibration

| Agent Descriptor | Expected Score Range | Example |
|---|---|---|
| Production-ready, well-documented tutor | 85-95 | database-skill-tutor (83.5) |
| Production-ready, well-documented architect | 88-96 | frontend-ui-architect (~91) |
| Production-ready, well-documented operator | 85-94 | prod-microservices-operator (~89) |
| Good quality with minor gaps | 75-84 | Hypothetical agent with specialization but weak standards |
| Adequate functionality, needs work | 60-74 | Adequate agent example (50-65) |
| Significant gaps, not deployable | 40-59 | Developing agent |
| Missing critical components | 0-39 | Incomplete agent (<5) |

---

## Evaluator Notes

### When in Doubt

If a criterion is ambiguous or you're between two scores:

1. **Lower score is safer**: If uncertain between 2 and 3, choose 2 (unless evidence strongly supports 3)
2. **Check reference**: Consult `detailed-criteria.md` for specific examples
3. **Provide evidence**: Note exact quotes from agent content that justify score
4. **Document assumptions**: If assuming agent uses certain pattern, note it in report

### Common Scoring Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---|---|---|
| **Crediting intent** | "I try to be clear" ≠ 3/3 | Score based on actual clarity in content |
| **Overstating vagueness** | "Could be better" means 1-2, not 0 | 0 only if criterion completely absent |
| **Pattern confusion** | Scoring tutor on operator criteria | Identify pattern first, then apply pattern-specific criteria |
| **Forgetting context** | Scoring agent length as 0 because >150 lines | Context-efficiency target is 70-150, not absolute |
| **Mixing reviews** | Combining feedback from multiple reviewers without reconciliation | Reconcile before finalizing score |

---

## Summary

These examples show:
- **Production agent**: ~90+, all requirements met, minor optimization possible
- **Good agent**: ~75-85, most requirements met, clear path to production
- **Adequate agent**: ~60-74, functional but significant gaps
- **Developing agent**: ~40-59, major issues, needs rework
- **Incomplete agent**: ~0-39, missing critical components

Use these as calibration anchors when evaluating new agents.
