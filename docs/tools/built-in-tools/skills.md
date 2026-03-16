# Skills

Skills are specialized packages of instructions and resources that extend an agent's capabilities for specific tasks. A skill is essentially a folder containing a `SKILL.md` file (manifest) and optional resources like scripts, assets, and reference documents.

## Skill Structure

A skill folder typically has the following structure:

```
my-skill/
├── SKILL.md          # Required: Metadata and main instructions
├── scripts/          # Optional: Python or Bash scripts
│   ├── setup.py
│   └── process.sh
├── references/       # Optional: Additional markdown documentation
│   └── details.md
└── assets/           # Optional: Binary or text assets
    └── logo.png
```

### SKILL.md

The `SKILL.md` file contains YAML frontmatter for metadata and Markdown for instructions.

```markdown
---
name: my-skill
description: Performs complex data processing.
metadata:
  adk_additional_tools: ["analyze_data"] # Tools to dynamically enable
---

# My Skill Instructions

Follow these steps to process data:
1. Run the setup script.
2. ...
```

## Using `SkillToolset`

To use skills in your agent, add the `SkillToolset` to your agent's tools.

```python
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.skills import load_skills_from_directory

# Load skills
skills = load_skills_from_directory("./my_skills")

# Create toolset
skill_toolset = SkillToolset(
    skills=skills,
    code_executor=agent_engine_executor, # Required for running scripts
)

# Add to agent
agent = LlmAgent(
    # ...
    tools=[skill_toolset]
)
```

## Features

### Script Execution
Skills can contain scripts in the `scripts/` directory. The `RunSkillScriptTool` allows the agent to execute these scripts using the configured `code_executor`.

### Binary Content
The `LoadSkillResourceTool` supports reading binary files (e.g., images, PDFs) from `assets/` or `references/`. The content is automatically injected into the conversation history for the model to analyze.

### Dynamic Tools
Skills can request additional tools via the `adk_additional_tools` metadata key. When the skill is activated, these tools are dynamically resolved from the `SkillToolset`'s available tools.
