# Contributing to Digital FTE

## Code of Conduct

- **Respect Constitution**: All work must comply with `.specify/memory/constitution.md`
- **100% Test Coverage**: No exceptions
- **Security First**: Never commit credentials
- **Quality Over Speed**: Small, testable changes preferred

## Development Setup

```bash
# Clone repository
git clone https://github.com/[YOUR_USERNAME]/DEGITAL-FTE-EMPLOY.git
cd DEGITAL-FTE-EMPLOY

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r Tier_1_Bronze/src/watchers/requirements.txt
pip install pytest pytest-cov

# Verify setup
./scripts/run_validation_gates.sh bronze
```

## Branch Naming Conventions

- `feature/[feature-name]` – New features
- `bugfix/[bug-name]` – Bug fixes
- `refactor/[component]` – Refactoring work
- `docs/[topic]` – Documentation updates
- `test/[feature]` – Test additions

**Example**: `feature/gmail-fte-agent`

## Commit Message Format

```
[PHASE]: [ACTION] ([TIER])

Brief description (1-2 sentences)

Detailed explanation of changes (if needed)

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

**Example**:
```
Phase 2: Create Gmail FTE watcher (Silver)

Implemented Gmail API watcher that:
- Monitors important emails every 5 minutes
- Classifies as important/spam/follow-up
- Creates action files in /Needs_Action
- Logs all decisions with reasoning

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

## Testing Requirements

**100% Rule**: All code must have 100% test coverage.

```bash
# Run tests
pytest Tier_1_Bronze/tests/ -v

# Check coverage
pytest --cov=Tier_1_Bronze/src Tier_1_Bronze/tests/

# Must show: 100% coverage
```

**Test Structure**:
- Happy path test
- Error handling test
- Edge cases
- Integration test
- Validation gate test

## Creating an Agent Skill

1. **Create skill directory**:
   ```
   Tier_X_Silver/src/skills/[skill-name]/
   ├── SKILL.md
   ├── __init__.py
   ├── requirements.txt
   └── tests/
       ├── test_skill.py
       └── verify.py
   ```

2. **Write SKILL.md**:
   ```markdown
   # Skill: [NAME]
   
   ## Purpose
   One sentence description
   
   ## Usage
   Example code
   
   ## Inputs/Outputs
   Parameter descriptions
   
   ## Tests
   List of test cases
   ```

3. **Implement skill** (with type hints + docstrings)

4. **Write tests** (100% coverage)

5. **Create verify.py**:
   ```python
   #!/usr/bin/env python
   import subprocess
   result = subprocess.run(["pytest", "-v", "--cov=."], cwd=".")
   exit(result.returncode)
   ```

6. **Run `./verify.py`** until 100% pass

7. **Commit with proper message**

## Code Quality Standards

- **Type Hints**: Required on all functions
- **Docstrings**: Required on all public methods
- **PEP 8**: Use `black` for formatting
- **Line Length**: Max 100 characters
- **Complexity**: Max 10 cyclomatic complexity per function
- **Secrets**: Never hardcode (use .env)

## Pull Request Process

1. **Create branch** from `main`
2. **Make changes** with Constitution compliance
3. **Run tests**: `./scripts/run_validation_gates.sh [tier]`
4. **Commit changes** with proper format
5. **Push branch** and create PR
6. **Add description** (what changed, why, testing)
7. **Wait for review** (Constitution compliance check)
8. **Address feedback** (iterate)
9. **Merge** after approval

## Pull Request Checklist

- [ ] Tests pass (100% coverage)
- [ ] Code follows Constitution requirements
- [ ] SKILL.md documentation (if new skill)
- [ ] verify.py validation succeeds
- [ ] Commit message follows format
- [ ] No secrets committed
- [ ] CHANGELOG.md updated (if applicable)

## Constitutional Compliance Review

Every PR must pass:
1. **HITL Threshold Check**: Does code respect Constitution Section II?
2. **Test Coverage**: 100% required (verify.py confirms)
3. **Security**: No hardcoded secrets, .env used correctly
4. **Audit Logging**: All actions logged in JSON format
5. **Skill Quality**: SKILL.md complete, docstrings present
6. **Performance**: Adheres to tier SLOs

## Issue Reporting

**Bug Report Template**:
```markdown
## Description
Brief description of issue

## Steps to Reproduce
1. Step 1
2. Step 2

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Constitution Violation?
Does this violate Constitution rules?
```

**Feature Request Template**:
```markdown
## Description
What feature is needed

## Use Case
Why is this needed

## Constitution Impact
Which principles does this affect?

## Proposed Implementation
High-level approach
```

## Questions?

- **General Questions**: Create issue with `question` label
- **Security Issues**: Contact Constitution Champion immediately
- **Architecture Questions**: See ARCHITECTURE.md first

---

**Last Updated**: 2026-02-26 | **Maintainer**: Digital FTE Team
