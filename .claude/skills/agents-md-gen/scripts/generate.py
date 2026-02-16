#!/usr/bin/env python3
"""
agents-md-gen: Generate AGENTS.md documentation from project analysis
MCP Code Execution Pattern - Script executes externally (0 tokens in context)
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def find_agent_files(project_path: str) -> List[Path]:
    """Find all potential agent files in project."""
    project = Path(project_path).resolve()
    agent_files = []

    # Look in services, agents, and src directories
    for pattern in ["**/services/**/*.py", "**/agents/**/*.py", "**/src/**/*agent*.py"]:
        agent_files.extend(project.glob(pattern))

    return agent_files

def extract_agent_info(file_path: Path) -> Optional[Dict]:
    """Extract agent information from Python file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Look for class definitions
        class_pattern = r'class\s+(\w*Agent\w*)\s*[\(:]'
        matches = re.findall(class_pattern, content)

        if not matches:
            return None

        agent_name = matches[0]

        # Extract docstring
        docstring_pattern = r'class\s+\w+.*?:\s*"""(.*?)"""'
        docstring_match = re.search(docstring_pattern, content, re.DOTALL)
        description = docstring_match.group(1).strip() if docstring_match else ""

        # Detect model
        model = "GPT-4 Turbo"
        if "claude" in content.lower():
            model = "Claude 3"
        elif "gpt-3.5" in content.lower():
            model = "GPT-3.5 Turbo"

        # Find endpoints
        endpoints = []
        endpoint_pattern = r'@app\.(?:post|get|put|delete)\(["\']([^"\']+)'
        endpoints = re.findall(endpoint_pattern, content)

        return {
            "name": agent_name,
            "description": description or f"AI agent for {agent_name}",
            "file": str(file_path.relative_to(file_path.parent.parent.parent.parent.parent)),
            "model": model,
            "endpoints": endpoints
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return None

def generate_agents_md(project_path: str, agents: List[Dict]) -> str:
    """Generate AGENTS.md content."""
    timestamp = datetime.now().isoformat() + "Z"

    markdown = f"""---
version: 1.0.0
generated: {timestamp}
project: {Path(project_path).name}
compliance:
  - AAIF
  - OpenAI Standard
---

# AI Agents

This document describes all AI agents in the {Path(project_path).name} project.

"""

    if not agents:
        markdown += "No AI agents found in project.\n"
        return markdown

    for agent in agents:
        markdown += f"## {agent['name']}\n\n"
        markdown += f"- **Description**: {agent['description']}\n"
        markdown += f"- **Model**: {agent['model']}\n"
        markdown += f"- **Location**: `{agent['file']}`\n"

        if agent['endpoints']:
            markdown += f"- **Endpoints**: \n"
            for endpoint in agent['endpoints']:
                markdown += f"  - `{endpoint}`\n"

        markdown += "\n"

    markdown += f"---\n\nGenerated: {timestamp}\nAgent Count: {len(agents)}\n"
    return markdown

def main():
    """Main entry point."""
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    # Validate project path
    if not Path(project_path).is_dir():
        print(f"✗ Project path not found: {project_path}", file=sys.stderr)
        sys.exit(1)

    # Find and analyze agent files
    agent_files = find_agent_files(project_path)
    agents = []

    for file_path in agent_files:
        agent_info = extract_agent_info(file_path)
        if agent_info:
            agents.append(agent_info)

    # Generate AGENTS.md
    content = generate_agents_md(project_path, agents)

    # Write to file
    output_path = Path(project_path) / "AGENTS.md"
    with open(output_path, 'w') as f:
        f.write(content)

    # Output summary
    print(f"✓ Generated AGENTS.md with {len(agents)} agents")
    if agents:
        print(f"  Agents: {', '.join([a['name'] for a in agents])}")
    sys.exit(0)

if __name__ == "__main__":
    main()
