---
name: adk-scaffold
description: >
  MUST READ before creating or enhancing any ADK agent project.
  Use when the user wants to build a new agent (e.g. "build me a search agent")
  or enhance an existing project (e.g. "add CI/CD to my project", "add RAG").
metadata:
  license: Apache-2.0
  author: Google
---

# ADK Project Scaffolding Guide

Use the `agent-starter-pack` CLI (via `uvx`) to create new ADK agent projects or enhance existing ones with deployment, CI/CD, and infrastructure scaffolding.

---

## Step 1: Gather Requirements

Start with the use case, then ask follow-ups based on answers.

**Always ask:**

1. **What problem will the agent solve?** — Core purpose and capabilities
2. **External APIs or data sources needed?** — Tools, integrations, auth requirements
3. **Safety constraints?** — What the agent must NOT do, guardrails
4. **Deployment preference?** — Prototype first (recommended) or full deployment? If deploying: Agent Engine, Cloud Run, or GKE?

**Ask based on context:**

- If **retrieval or search over data** mentioned (RAG, semantic search, vector search, embeddings, similarity search, data ingestion) → **Datastore?** Use `--agent agentic_rag --datastore <choice>`:
  - `vertex_ai_vector_search` — for embeddings, similarity search, vector search
  - `vertex_ai_search` — for document search, search engine
- If agent should be **available to other agents** → **A2A protocol?** Use `--agent adk_a2a` to expose the agent as an A2A-compatible service.
- If **full deployment** chosen → **CI/CD runner?** GitHub Actions (default) or Google Cloud Build?
- If **Cloud Run** or **GKE** chosen → **Session storage?** In-memory (default), Cloud SQL (persistent), or Agent Engine (managed).
- If **deployment with CI/CD** chosen → **Git repository?** Does one already exist, or should one be created? If creating, public or private?


---

## Step 2: Write DESIGN_SPEC.md

Compose a **detailed** spec with these sections. Present the full spec for user approval before scaffolding.

```markdown
# DESIGN_SPEC.md

## Overview
2-3 paragraphs describing the agent's purpose and how it works.

## Example Use Cases
3-5 concrete examples with expected inputs and outputs.

## Tools Required
Each tool with its purpose, API details, and authentication needs.

## Constraints & Safety Rules
Specific rules — not just generic statements.

## Success Criteria
Measurable outcomes for evaluation.

## Edge Cases to Handle
At least 3-5 scenarios the agent must handle gracefully.
```

The spec should be thorough enough for another developer to implement the agent without additional context.

---

## Step 3: Create or Enhance the Project

### Create a New Project

```bash
uvx agent-starter-pack create <project-name> \
  --agent <template> \
  --deployment-target <target> \
  --region <region> \
  --prototype \
  -y
```

**Constraints:**
- Project name must be **26 characters or less**, lowercase letters, numbers, and hyphens only.
- Do NOT `mkdir` the project directory before running `create` — the CLI creates it automatically. If you mkdir first, `create` will fail or behave unexpectedly.
- Auto-detect the guidance filename based on the IDE you are running in and pass `--agent-guidance-filename` accordingly.
- When enhancing an existing project, check where the agent code lives. If it's not in `app/`, pass `--agent-directory <dir>` (e.g. `--agent-directory agent`). Getting this wrong causes enhance to miss or misplace files.

#### Create Flags

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--agent` | `-a` | `adk` | Agent template (see template table below) |
| `--deployment-target` | `-d` | `agent_engine` | Deployment target (`agent_engine`, `cloud_run`, `gke`, `none`) |
| `--region` | | `us-central1` | GCP region |
| `--prototype` | `-p` | off | Skip CI/CD and Terraform (recommended for first pass) |
| `--cicd-runner` | | `skip` | `github_actions` or `google_cloud_build` |
| `--datastore` | `-ds` | — | Datastore for data ingestion (`vertex_ai_search`, `vertex_ai_vector_search`) |
| `--session-type` | | `in_memory` | Session storage (`in_memory`, `cloud_sql`, `agent_engine`) |
| `--auto-approve` | `-y` | off | Skip confirmation prompts |
| `--skip-checks` | `-s` | off | Skip GCP/Vertex AI verification checks |
| `--agent-directory` | `-dir` | `app` | Agent code directory name |
| `--agent-guidance-filename` | | `GEMINI.md` | Guidance file name (`CLAUDE.md`, `AGENTS.md`) |
| `--debug` | | off | Enable debug logging for troubleshooting |

By default, the scaffolded project uses Google Cloud credentials (Vertex AI). For API key setup and model configuration, see [Configuring Gemini models](https://adk.dev/agents/models/google-gemini/index.md) and [Supported models](https://adk.dev/agents/models/index.md).

### Enhance an Existing Project

```bash
uvx agent-starter-pack enhance . \
  --deployment-target <target> \
  -y
```

Run this from inside the project directory (or pass the path instead of `.`). Remember that enhance creates new files (`.github/`, `deployment/`, `tests/load_test/`, etc.) that need to be committed.

#### Enhance Flags

All create flags are supported, plus:

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--name` | `-n` | directory name | Project name for templating |
| `--base-template` | `-bt` | — | Override base template (e.g. `agentic_rag` to add RAG) |
| `--dry-run` | | off | Preview changes without applying |
| `--force` | | off | Force overwrite all files (skip smart-merge) |

### Common Workflows

**Always ask the user before running these commands.** Present the options (CI/CD runner, deployment target, etc.) and confirm before executing.

```bash
# Add deployment to an existing prototype
uvx agent-starter-pack enhance . --deployment-target agent_engine -y

# Add CI/CD pipeline (ask: GitHub Actions or Cloud Build?)
uvx agent-starter-pack enhance . --cicd-runner github_actions -y

# Add RAG with data ingestion
uvx agent-starter-pack enhance . --base-template agentic_rag --datastore vertex_ai_search -y

# Preview what would change (dry run)
uvx agent-starter-pack enhance . --deployment-target cloud_run --dry-run -y
```

---

## Template Options

| Template | Deployment | Description |
|----------|------------|-------------|
| `adk` | Agent Engine, Cloud Run, GKE | Standard ADK agent (default) |
| `adk_a2a` | Agent Engine, Cloud Run, GKE | Agent-to-agent coordination (A2A protocol) |
| `agentic_rag` | Agent Engine, Cloud Run, GKE | RAG with data ingestion pipeline |

---

## Deployment Options

| Target | Description |
|--------|-------------|
| `agent_engine` | Managed by Google (Vertex AI Agent Engine). Sessions handled automatically. |
| `cloud_run` | Container-based deployment. More control, requires Dockerfile. |
| `gke` | Container-based on GKE Autopilot. Full Kubernetes control. |
| `none` | No deployment scaffolding. Code only. |

### "Prototype First" Pattern (Recommended)

Start with `--prototype` to skip CI/CD and Terraform. Focus on getting the agent working first, then add deployment later with `enhance`:

```bash
# Step 1: Create a prototype
uvx agent-starter-pack create my-agent --agent adk --prototype -y

# Step 2: Iterate on the agent code...

# Step 3: Add deployment when ready
uvx agent-starter-pack enhance . --deployment-target agent_engine -y
```

### Agent Engine and session_type

When using `agent_engine` as the deployment target, Agent Engine manages sessions internally. If your code sets a `session_type`, clear it — Agent Engine overrides it.

---

## Step 4: Save DESIGN_SPEC.md and Load Dev Workflow

After scaffolding, save the approved spec from Step 2 to the project root as `DESIGN_SPEC.md`.

**Then immediately load `/adk-dev-guide`** — it contains the development workflow, coding guidelines, and operational rules you must follow when implementing the agent.

---

## Scaffold as Reference

When you need specific files (Terraform, CI/CD workflows, Dockerfile) but don't want to scaffold the current project directly, create a temporary reference project in `/tmp/`:

```bash
uvx agent-starter-pack create /tmp/ref-project \
  --agent adk \
  --deployment-target cloud_run \
  --cicd-runner github_actions \
  -y
```

Inspect the generated files, adapt what you need, and copy into the actual project. Delete the reference project when done.

This is useful for:
- Non-standard project structures that `enhance` can't handle
- Cherry-picking specific infrastructure files
- Understanding what ASP generates before committing to it

---

## Critical Rules

- **NEVER change the model** in existing code unless explicitly asked
- **NEVER `mkdir` before `create`** — the CLI creates the directory; pre-creating it causes enhance mode instead of create mode
- **NEVER create a Git repo or push to remote without asking** — confirm repo name, public vs private, and whether the user wants it created at all
- **Always ask before choosing CI/CD runner** — present GitHub Actions and Cloud Build as options, don't default silently
- **Agent Engine clears session_type** — if deploying to `agent_engine`, remove any `session_type` setting from your code
- **Start with `--prototype`** for quick iteration — add deployment later with `enhance`
- **Project names** must be ≤26 characters, lowercase, letters/numbers/hyphens only
- **NEVER write A2A code from scratch** — the A2A Python API surface (import paths, `AgentCard` schema, `to_a2a()` signature) is non-trivial and changes across versions. Always use `--agent adk_a2a` to scaffold A2A projects.

---

# Examples

Using scaffold as reference:
User says: "I need a Dockerfile for my non-standard project"
Actions:
1. Create temp project: `uvx agent-starter-pack create /tmp/ref --agent adk --deployment-target cloud_run -y`
2. Copy relevant files (Dockerfile, etc.) from /tmp/ref
3. Delete temp project
Result: Infrastructure files adapted to the actual project

---

A2A project:
User says: "Build me a Python agent that exposes A2A and deploys to Cloud Run"
Actions:
1. Follow the standard flow (gather requirements, DESIGN_SPEC, scaffold)
2. `uvx agent-starter-pack create my-a2a-agent --agent adk_a2a --deployment-target cloud_run --prototype -y`
Result: Valid A2A imports and Dockerfile — no manual A2A code written.

---

## Troubleshooting

### `uvx` command not found

Install `uv` following the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/index.md).

If `uv` is not an option, use pip instead:

```bash
# macOS/Linux
python -m venv .venv && source .venv/bin/activate
# Windows
python -m venv .venv && .venv\Scripts\activate

pip install agent-starter-pack
agent-starter-pack create <project-name> ...
```

For all available options, run `uvx agent-starter-pack create --help`.
