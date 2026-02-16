# Agent-Validator Skill: Quick Start Guide

The **agent-validator** skill provides systematic evaluation of AI agents against production-level quality criteria.

---

## What This Skill Does

Validates any agent file (`.md` in `/.claude/agents/`) across **9 categories** with:
- **0-100 scoring** system
- **Actionable recommendations** (High/Medium/Low priority)
- **Pattern detection** (Tutor/Architect/Operator)
- **Production readiness assessment**

---

## When to Use This Skill

Use agent-validator when:
- ✅ Evaluating agent quality before deployment
- ✅ Planning agent improvements to Production level (90+)
- ✅ Auditing existing agents for compliance/standards
- ✅ Comparing multiple agents across consistent criteria
- ✅ Understanding what makes agents "Production-ready"

---

## How to Use It

### Basic Validation
```
Validate the database-skill-tutor agent against production criteria
```

### Pattern-Focused Review
```
Check if frontend-ui-architect meets Architect pattern requirements
```

### Improvement Planning
```
Validate prod-microservices-operator and generate roadmap to 95+ score
```

---

## What You'll Get

**Validation Report includes**:

1. **Overall Score** (0-100)
2. **Rating** (Production/Good/Adequate/Developing/Incomplete)
3. **Category Breakdown** (9 categories with scores and weights)
4. **Pattern Analysis** (Tutor/Architect/Operator compliance)
5. **Critical Issues** (if any blocking deployment)
6. **Improvement Recommendations** (prioritized High/Medium/Low)
7. **Strengths** (what the agent does well)

---

## Evaluation Categories

| # | Category | Weight | Applies To |
|---|----------|--------|-----------|
| 1 | Structure & Metadata | 12% | All |
| 2 | Role Definition & Expertise | 15-23% | All |
| 3 | Methodology & Workflow | 14-22% | All |
| 4 | User Interaction Patterns | 12% | All |
| 5 | Quality Standards & Gates | 13% | All |
| 6 | Context Management | 10-18% | All |
| 7 | Technical Robustness | 8% | All |
| 8 | Pedagogical Effectiveness | 0-8% | Tutors only |
| 9 | Production Readiness | 0-8% | Operators only |

**Weight adjustment**: Unused categories (8-9) are redistributed to applicable categories (all weights sum to 100%)

---

## Scoring Scale

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | 🟢 Production | Expert-level, ready for wide use |
| 75-89 | 🟢 Good | Solid functionality, minor improvements needed |
| 60-74 | 🟡 Adequate | Functional but needs significant work |
| 40-59 | 🟠 Developing | Major gaps, not ready |
| 0-39 | 🔴 Incomplete | Major issues, not deployable |

---

## Agent Patterns

### Tutor Pattern
**Teaching-focused agents** (e.g., database-skill-tutor)
- Progressive learning structure (Fundamentals → Intermediate → Advanced)
- Practice exercises and hands-on opportunities
- Runnable examples with explanations
- Feedback mechanisms and encouragement

### Architect Pattern
**Design-focused agents** (e.g., frontend-ui-architect)
- Design workflow and decision frameworks
- Quality verification checklists
- Design trade-offs discussed
- Best practices enforced

### Operator Pattern
**Operations-focused agents** (e.g., prod-microservices-operator)
- Step-by-step operational procedures
- Production safeguards and verification
- Runbooks for common operations
- Compliance and standards requirements

---

## Quick Validation Checklist

For rapid self-assessment before requesting formal validation:

- [ ] **Frontmatter complete**: name, description, model, color present?
- [ ] **Role clear**: What specialization? What domains?
- [ ] **Workflow defined**: How does agent approach problems (3-5 phases)?
- [ ] **User interaction**: How does agent clarify, ask questions, provide feedback?
- [ ] **Quality gates**: How are outputs verified? What's the checklist?
- [ ] **Context management**: Tool/skill usage strategy? Delegation criteria?
- [ ] **Pattern aligned**: Is Tutor/Architect/Operator pattern clear?
- [ ] **Examples provided**: Code or workflow examples included?

**Scoring estimate**:
- 7-8 ✅ → Likely Production (90+)
- 5-6 ✅ → Likely Good (75-89)
- 3-4 ✅ → Likely Adequate (60-74)
- <3 ✅ → Needs more work

---

## Reference Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill guide with workflow and categories |
| `references/detailed-criteria.md` | Full rubric with 0-3 scoring for every criterion |
| `references/agent-patterns.md` | Pattern definitions and requirements |
| `references/scoring-examples.md` | Real validations for calibration |
| `references/improvement-patterns.md` | Common issues and fixes |

---

## Common Improvements (Fastest to 90+)

| Improvement | Time | Gain |
|-------------|------|------|
| Add frontmatter | 5 min | +35 pts |
| Define role clearly | 10 min | +15 pts |
| Add workflow/methodology | 15 min | +10 pts |
| Add verification steps | 10 min | +7 pts |
| Add context management strategy | 15 min | +6 pts |

**Total time to Production**: ~55 minutes from adequate state

---

## Examples

### Example 1: Production Tutor
**Agent**: database-skill-tutor
**Score**: 83.5/100 (Good)
**Path to Production**: Add quality gates + context strategy (~25 min)

### Example 2: Production Architect
**Agent**: frontend-ui-architect
**Score**: ~91/100 (Production)
**Recommendation**: Minor optimizations for 95+ score

### Example 3: Adequate Agent
**Score**: 50-65/100
**Issues**: No specialization, vague methodology, no verification
**Time to Production**: ~2-3 hours with focused work

---

## Tips for Success

### When Requesting Validation
- Provide agent file path or paste agent content
- Ask for specific focus ("improve to 90+" vs. "full assessment")
- Mention current concerns ("weak context management?" etc.)
- Specify urgency (quick audit vs. detailed improvement plan)

### After Receiving Report
1. **Read "Critical Issues" first** - must fix to deploy
2. **Address "High Priority" recommendations** - unlocks Production level
3. **Consider "Medium/Low Priority"** - nice to have improvements
4. **Use "Strengths" section** - reinforce what's working well

### Common Pitfalls to Avoid
- **Too broad**: Agent tries to do too much → Pick specialization
- **Vague methodology**: No clear workflow → Define 4-5 phases
- **No verification**: Can't tell if output is correct → Add checklist
- **Missing examples**: User can't understand → Add runnable examples
- **No context strategy**: Agent bloats → Define token-saving tactics

---

## Success Metrics

**Agent is Production-ready (90+) when**:
- ✅ Clear specialization and expertise
- ✅ Structured methodology (workflow with phases)
- ✅ Quality gates (before-delivery verification)
- ✅ User interaction clear (how agent asks questions, provides feedback)
- ✅ Context strategy defined (token efficiency)
- ✅ Pattern-specific requirements met (Tutor/Architect/Operator)
- ✅ Examples or runbooks provided
- ✅ No critical blocking issues

---

## Get Help

For specific questions about:
- **0-3 scoring**: See `references/detailed-criteria.md`
- **Pattern requirements**: See `references/agent-patterns.md`
- **Common fixes**: See `references/improvement-patterns.md`
- **Calibration**: See `references/scoring-examples.md`

---

**Ready to validate an agent?** Use the agent-validator skill and get a structured assessment with actionable roadmap to Production level!
