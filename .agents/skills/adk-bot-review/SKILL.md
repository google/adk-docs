---
name: bot-pr-review 
description: Reviews ADK bot pull requests by validating technical correctness against source code, checking PR states and formatting, and ensuring adherence to the Google Developer Style Guide and repository standards. Triggers on "review bot PR", "check bot changes", or "verify bot issue".
---

# ADK Bot Change Reviewer (bot-pr-review)

This skill guides a rigorous review of ADK bot changes and AI-generated PR drafts. It ensures documentation updates are technically accurate, appropriately sized, and adhere strictly to ADK docs formatting and the Google Developer Style Guide.

## Step 1: Verification & Workflow Checks
* Check that the PR title briefly describes the topic being updated not only the issue.
* Confirm changes are made directly in the `.md` files and no "do not merge" status tags were prematurely removed.

---

## Step 2: Assess Update Criteria & Architecture
* Prioritize smaller, surgical updates over comprehensive overhauls unless the existing docs are entirely unclear.
* Verify that the update provides a useful learning experience and is actionable for a developer.
* Ensure the content is placed appropriately within the ADK docs information architecture.
* Confirm the update length and prioritization are appropriate for the specific code change (check if it is already covered by existing docs or API references).

---

## Step 3: Deep Technical Validation
* **Never assume an AI agent's code snippet is correct.**
* Cross-reference all code examples against the `google/adk-python/contributing` repository.
* Verify the information against relevant pull requests and actual ADK code in the `google/adk-python` repo.

---

## Step 4: Run the Quality & Style Checklist

### Headings
* Maintain a logical h1, h2, h3 hierarchy without empty headings (stacking headers).
* Do not number headings (Use `## This heading`, not `## 1. This heading`).
* Use imperative titles (e.g., "Build agents", not "Building agents").
* Do not use command names in headings; call out the task to be done.

### Language
* Adhere to the Google Developer Style Guide.
* Use active voice phrasing (e.g., "The system does X", not "X is done").
* Never use the word "this" without a noun object (e.g., "This function is used...", not "This is used...").

### Code Snippets & Formatting
* **Enforce an 80-character line length limit** for general Markdown text (excluding long URLs, unbreakable code blocks, or tables).
* Check for rendering errors caused by spaces before backticks (```).
* Use the `!!! warning/tip/note` mkdocs-material admonition format for notes and warnings instead of quote formats (`>`).
* Do not use ALL CAPS except for code syntax; use bold or italics for emphasis.

---

## Step 5: Report Findings
Produce a prioritized Markdown report categorized by:
* 🔴 **Blockers**: Unverified/hallucinated AI code snippets, missing PR description links, broken Netlify rendering.
* 🟠 **Criteria & Architecture**: Updates that are too broad, non-actionable, or placed incorrectly in the information architecture.
* 🟡 **Style & Mechanics**: Lines exceeding the 80-character limit, empty/numbered headings, passive voice, missing noun objects after "this", or missing `mkdocs.yaml` updates.
* 🔵 **Nits**: Admonition formatting errors, casing issues, or spaces before backticks.

---

## Style rules to bake in

- Model strings should be `gemini-flash-latest`, `gemini-pro-latest`, or other
  valid `*-latest` aliases in sample code rather than specific versioned model
  strings, which increase the maintenance burden when new model versions are
  released.
- Imports: `from google.adk.agents import Agent`; MCP uses
  `from google.adk.tools.mcp_tool import McpToolset`. Agent variable is
  `root_agent` (Python) / `rootAgent` (TypeScript, with `export { rootAgent };`).
- No em dashes or verbose AI-generated content: Use a colon in `**term**:
  definition` bullets; split prose into sentences otherwise.
- When referring to ADK, use "ADK", never "Google ADK" or "The ADK".
- Do not start a sentence with an inline-code word.
- Internal ADK-docs links are site-relative (e.g. `/sessions/memory/`); external
  links must resolve. Do not invent links.
- Verify all code samples against actual APIs and library code. The canonical
  source repositories are listed in `docs/community/contributing-guide.md`.
- Confirm that the package exists on PyPI/npm, before presenting the draft.
