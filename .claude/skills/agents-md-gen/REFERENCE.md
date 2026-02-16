# agents-md-gen Reference Guide

## Overview

The `agents-md-gen` skill analyzes a project structure and generates comprehensive AGENTS.md documentation for all AI agents found in the codebase. This is essential for AAIF (AI Agent Interface Framework) compliance and provides a single source of truth for agent documentation.

## How It Works

The skill:
1. Scans project for agent definitions (Python files with agent patterns)
2. Extracts agent metadata (name, description, capabilities, model)
3. Analyzes API endpoints and integration points
4. Generates AGENTS.md with structured documentation

## Advanced Options

### Output Formats

**Markdown (Default)**
```bash
claude "Use agents-md-gen skill with output-format=markdown"
```

**JSON**
```bash
claude "Use agents-md-gen skill with output-format=json"
```

### Include Flags

Include detailed agent capabilities:
```bash
claude "Use agents-md-gen skill with include-capabilities"
```

Include API documentation:
```bash
claude "Use agents-md-gen skill with include-apis"
```

Include all information:
```bash
claude "Use agents-md-gen skill with include-all"
```

### Custom Template

Specify custom template file:
```bash
claude "Use agents-md-gen skill with template=custom-template.md"
```

## AGENTS.md Structure

Generated file includes:

```markdown
---
version: 1.0.0
generated: 2026-01-23T10:00:00Z
project: learnflow-app
---

# AI Agents

## Triage Agent
- **Purpose**: Route student queries to specialist agents
- **Model**: GPT-4 Turbo
- **Endpoints**: POST /api/query
- **Capabilities**: Query classification, routing logic

## Concepts Agent
- **Purpose**: Explain Python concepts with examples
- **Model**: GPT-4 Turbo
- **Endpoints**: POST /api/explain
- **Capabilities**: Concept explanation, example generation

...
```

## Customization

### Custom YAML Frontmatter

Edit `.claude/skills/agents-md-gen/templates/frontmatter.yaml`:

```yaml
version: "1.0.0"
author: "LearnFlow Team"
license: "MIT"
compliance: ["AAIF", "OpenAI"]
```

### Agent Detection Patterns

The skill looks for agents matching these patterns:

- Class names ending in `Agent` or `agent`
- Python files in `services/` or `agents/` directories
- Functions decorated with `@agent` or `@ai_service`
- Files containing `OpenAI` or `anthropic` imports

### Filter by Type

Include only specific agent types:
```bash
claude "Use agents-md-gen skill with agent-type=FastAPI"
claude "Use agents-md-gen skill with agent-type=OpenAI"
```

## Examples

### Example 1: Basic Generation

```bash
cd learnflow-app
claude "Use agents-md-gen skill to generate AGENTS.md for ."
```

Output: `learnflow-app/AGENTS.md` with all agents documented

### Example 2: Include Capabilities

```bash
claude "Use agents-md-gen skill to generate AGENTS.md for learnflow-app with include-capabilities"
```

Output: Detailed AGENTS.md with:
- Full capability lists
- Parameter descriptions
- Return value documentation
- Example API calls

### Example 3: Skills Library Documentation

```bash
cd skills-library
claude "Use agents-md-gen skill to generate AGENTS.md for ."
```

Output: `skills-library/AGENTS.md` documenting:
- agents-md-gen skill
- neon-postgres-setup skill
- fastapi-service-template skill
- nextjs-k8s-deploy skill

## Troubleshooting

### Issue: No agents found

- Check that agent files are in `services/` or `agents/` directories
- Verify files have agent class/function definitions
- Use `include-apis` flag to expand detection

### Issue: Incomplete agent documentation

- Run with `include-capabilities` flag
- Check that agent files have docstrings
- Verify OpenAI/anthropic imports present

### Issue: Markdown formatting issues

- Verify output file is readable: `cat AGENTS.md`
- Check for special characters in agent names
- Run skill again with `regenerate` flag

## Integration with Other Skills

- Use output from `agents-md-gen` to inform `fastapi-service-template` generation
- Include AGENTS.md in documentation site (with `docusaurus-deploy` skill)
- Reference AGENTS.md in README files

## AAIF Compliance

The generated AGENTS.md complies with AAIF standard v1.0:

- ✅ Mandatory fields: name, description, model, endpoints
- ✅ Optional fields: capabilities, parameters, authentication
- ✅ Valid YAML frontmatter
- ✅ Markdown formatting
- ✅ Version tracking

See: https://github.com/openai/openai-python/blob/main/AGENTS.md
