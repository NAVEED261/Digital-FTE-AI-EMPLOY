---
name: agents-md-gen
description: Generate AGENTS.md documentation from project structure analysis
version: 1.0.0
cross-agent: claude-code,goose
token-cost: 120
---

# Generate AGENTS.md Documentation

Creates AGENTS.md file documenting all AI agents in your project with AAIF compliance.

## When to Use

Use this skill when you need to:
- Document AI agents in a codebase
- Create AGENTS.md for AAIF compliance
- Update agent manifest when adding new agents

## Usage

```bash
claude "Use agents-md-gen skill to generate AGENTS.md for <project-path>"
```

Or with options:

```bash
claude "Use agents-md-gen skill to generate AGENTS.md for . with include-capabilities"
```

## Parameters

- **project-path**: Root directory of project (required)
- **include-capabilities**: Include detailed agent capabilities (optional)
- **output-format**: markdown (default) or json

## Output

Creates/updates `AGENTS.md` in project root with:
- Agent metadata (name, description, role)
- Capabilities list
- API endpoints
- Model configuration
- Use cases

## Validation

Generates file should contain:
- [ ] AGENTS.md created in project root
- [ ] All agents documented with descriptions
- [ ] YAML frontmatter is valid
- [ ] Markdown formatting is correct

## Examples

Generate basic AGENTS.md:
```bash
claude "Use agents-md-gen skill to generate AGENTS.md for ."
```

Generate with detailed capabilities:
```bash
claude "Use agents-md-gen skill to generate AGENTS.md for skills-library with include-capabilities"
```

---

**See [REFERENCE.md](./REFERENCE.md) for advanced customization options.**
