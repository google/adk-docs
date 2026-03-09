---
name: adk-cheatsheet
description: >
  MUST READ before writing or modifying ADK agent code.
  ADK API quick reference for Python — agent types, tool definitions,
  orchestration patterns, callbacks, and state management.
  Includes an index of all ADK documentation pages.
  Do NOT use for creating new projects (use adk-scaffold).
metadata:
  license: Apache-2.0
  author: Google
---

# ADK Cheatsheet

> **Python only for now.** This cheatsheet currently covers the Python ADK SDK.
> Support for other languages is coming soon.

## Reference Files

| File | Contents |
|------|----------|
| `references/python.md` | Python ADK API quick reference — agents, tools, auth, orchestration, callbacks, plugins, state, artifacts, context caching/compaction, session rewind |
| `references/docs-index.md` | ADK docs index (synced from llms.txt) — titles and URLs for fetching ADK documentation pages. If missing, fetch `https://google.github.io/adk-docs/llms.txt` using your agent's web fetch tool or `curl`. |

Read `references/python.md` for the full API quick reference.

> **Creating a new agent project?** Use `/adk-scaffold` instead — this skill is for writing code in existing projects.
