---
name: adk-bot-review
description: Reviews adk-bot pull requests by validating technical correctness against source code, checking PR states and formatting, and following Google's developer documentation style and ADK docs conventions. Triggers on "review bot PR", "check bot changes", or "verify bot issue".
---

# Review changes proposed by adk-bot (adk-bot-review)

This skill guides a rigorous review of adk-bot changes. It ensures documentation
updates are technically accurate, appropriately sized, and follow ADK docs
conventions, based on Google's developer documentation style.

## Step 1: Verify and research the proposed adk-bot change

- Check that the PR title briefly describes the topic being updated, not only
  the issue.
- Confirm changes are made directly in the `.md` files and no "do not merge"
  status tags were prematurely removed.
- Check the PR's mergeable state and CI status. Note git conflicts and failing
  checks as findings to resolve or to fix in the consolidating PR.
- The input is one adk-bot-authored PR, or occasionally a few. From the PR,
  trace back to the issue and the specific item it addresses. Identify the item
  from the PR title ("Update ADK doc according to issue #<N> - <item>") and
  body. adk-bot often opens more than one PR for the same item. If multiple PRs
  are provided, confirm they all address the same item and review them together
  as one consolidation set. If they address different items, ask the user which
  one to focus on before continuing.
- Search closed issues and merged/rejected PRs across the repository for similar
  topics. Ensure the bot is not re-introducing changes, APIs, or stylistic
  choices that human maintainers have previously debated and rejected.
- Summarize the item's intended change and stated reasoning, and carry that
  intent into the technical validation in the next steps.

## Step 2: Assess update criteria and architecture

- Prioritize smaller, surgical updates over comprehensive overhauls unless the
  existing docs are entirely unclear.
- Verify that the update provides a useful learning experience and is actionable
  for a developer.
- Ensure the content is placed appropriately within the ADK docs information
  architecture.
- Confirm the update length and prioritization are appropriate for the specific
  code change (check if it is already covered by existing docs or API
  references).

## Step 3: Validate the change against source and intent

- **Never assume an AI agent's code snippet is correct.**
- Cross-reference all code examples against the
  `https://github.com/google/adk-python` repository.
- Verify the information against relevant pull requests and actual ADK code in
  the `https://github.com/google/adk-python` repo.
- Confirm the change actually implements what the linked issue and adk-bot PR
  set out to do, and resolves the issue item it references.
- Flag any part of the change that drifts from that stated intent, or any part
  of the intent the change leaves unaddressed.

## Step 4: Check quality and style

### Headings

- Maintain a logical h1, h2, h3 hierarchy without empty headings (stacking
  headers).
- Do not number headings (Use `## This heading`, not `## 1. This heading`).
- Use imperative titles (e.g., "Build agents", not "Building agents").
- Do not use command names in headings; call out the task to be done.

### Language

- Follow Google's developer documentation style
  (https://developers.google.com/style) as the basis for conventions; consult it
  for anything not covered here.
- Use active voice phrasing (e.g., "The system does X", not "X is done").
- Never use the word "this" without a noun object (e.g., "This function is
  used...", not "This is used...").

### Code snippets and formatting

- **Enforce an 80-character line length limit** for general Markdown text
  (excluding long URLs, unbreakable code blocks, or tables).
- Check for rendering errors caused by spaces before backticks (```).
- Use the `!!! warning/tip/note` mkdocs-material admonition format for notes and
  warnings instead of quote formats (`>`).
- Do not use ALL CAPS except for code syntax; use bold or italics for emphasis.

## Step 5: Report findings and decide the recommendation

First, summarize the findings from the verification steps above, ordered
blockers first, then required edits, then nits. Then choose one outcome below,
justified by those findings:

- **Close the bot PR(s).** (sometimes) The change is wrong, outdated, targets a
  deprecated or unreleased API, or is already covered by live docs or a merged
  PR. Record the reason and link the superseding doc or PR.
- **Approve as-is** (rare). The bot PR(s) are correct, well-placed, and need no
  edits.
- **Edit in place, then approve** (sometimes). The existing branch is usable but
  needs conflict resolution, corrections, consolidation, copyedits, or
  relocation.
- **Open a new consolidating PR** (most common). Rework the change across the
  1-3 bot PRs into one PR that fixes code errors and hallucinations, edits for
  quality, and places the content in the correct file. Then close the superseded
  bot PR(s).

Also confirm the change targets the correct file (files may have moved or been
restructured, or the edit may belong on a different page).

## Step 6: Produce an action plan

Output the concrete next actions for the chosen recommendation:

- The specific local edits needed: file paths, what to change, code fixes,
  consolidation of the 1-3 bot PRs, and correct placement.
- A short list of the verification findings that justify them, ordered blockers
  first (unverified/hallucinated code, wrong file, failing CI checks, broken
  rendering), then required edits, then nits.
- Which bot PR(s) to close.
- A PR description following the repo convention:
    - a short bullet summary of what changed
    - `Rendered page:` <preview link>
    - `Agent PR:` <link(s)>
    - `Original issue:` #<N> - <item>

## Style rules to bake in

- Model strings should be `gemini-flash-latest`, `gemini-pro-latest`, or other
  valid `*-latest` aliases in sample code rather than specific versioned model
  strings, which increase the maintenance burden when new model versions are
  released.
- Imports: `from google.adk.agents import Agent`; MCP uses `from
  google.adk.tools.mcp_tool import McpToolset`. Agent variable is `root_agent`
  (Python).
- No em dashes or verbose AI-generated content: Use a colon in `**term**:
  definition` bullets; split prose into sentences otherwise.
- When referring to ADK, use "ADK", never "Google ADK" or "The ADK".
- Do not start a sentence with an inline-code word.
- Internal ADK-docs links are site-relative (e.g. `/sessions/memory/`); external
  links must resolve. Do not invent links.
- Verify all code samples against actual APIs and library code. The canonical
  source repositories are listed in `docs/community/contributing-guide.md`.
