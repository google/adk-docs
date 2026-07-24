---
name: integration-review
description: Reviews an ADK integration documentation page (a Markdown file under docs/integrations/) or an integration pull request for correctness, structure, style, working code, valid links, and catalog conventions. Produces a prioritized review report and only fixes issues when explicitly asked. Triggers on "integration-review", "review integration page", "review integration PR", "review this integration", "check integration docs".
---

# ADK Integration Page Reviewer (integration-review)

This skill guides a rigorous review of integration documentation pages in the
[adk-docs](https://github.com/google/adk-docs) repository. Integration pages
live under `docs/integrations/` and document third-party tools, plugins,
observability platforms, data stores, MCP servers, connectors, and other
extensions to ADK agents.

The authoritative sources of truth for this review are:

1. The repository's `CONTRIBUTING.md` (see the "Integrations" section and its
   acceptance criteria).
2. The **existing shipping integration pages**, which are the real template.
   Always open and compare against peers of the same category:
    - MCP tools: `docs/integrations/github.md`, `docs/integrations/notion.md`
    - Observability: `docs/integrations/phoenix.md`, `docs/integrations/arize-ax.md`
    - Plugins: `docs/integrations/daytona.md`, `docs/integrations/goodmem.md`
3. The catalog rendering logic in `scripts/integrations.py`.

> [!NOTE]
> Read this skill and follow its steps whenever asked to review an integration
> page or an integration PR.

## Review workflow

### Step 1: Gather the change

- If reviewing a PR, use `gh` to pull it and read the **full cumulative diff**,
  not a single commit: `gh pr view <n> --repo google/adk-docs` and `gh pr diff
  <n> --repo google/adk-docs`. A stale `mkdocs.yml` entry or asset can hide in
  files that only show in the full diff.
- Check whether "Allow edits from maintainers" is enabled
  (`maintainerCanModify`) so fixes can be pushed directly if requested later.
- Confirm the CLA is signed (the `google-cla` bot). An unsigned CLA is a hard
  blocker.
- If reviewing a local file, run `git status` and `git diff` to see the change.

### Step 2: Find and read similar pages

Find 5 or more similar pages and read them in full. Identify candidates in one
pass by scanning `catalog_tags` (`grep catalog_tags docs/integrations/*.md`) and
matching the tag under review (e.g. `mcp`, `observability`); widen the set with
other signals such as product domain, structural template, and language support
(they need not all be the exact same category). Reading the full pages, not just
frontmatter, grounds the review in live examples and repo conventions rather
than inferring everything from the templates in this skill.

### Step 3: Run the checklist

Work through every dimension in the review checklist below.

### Step 4: Verify code, packages, and links

Do real verification, not a surface read (see "Deep verification").

### Step 5: Report and stop

Produce the prioritized report (see "Report format"). Do **not** edit files or
offer to fix issues by default. Stop and wait for an explicit instruction to
fix.

### Step 6 (only if asked): Apply fixes

If, and only if, the user explicitly asks you to fix findings: apply precise
edits, keep the contributor's wording where possible, fix only ADK-owned issues
unless told otherwise (leave vendor-SDK bugs for the author), and verify with
`mkdocs serve` where practical.

## Review checklist

### 1. Frontmatter (catalog metadata)

Every page starts with exactly these four YAML fields:

```yaml
---
catalog_title: <Display Name>
catalog_description: <short verb-led phrase>
catalog_icon: /integrations/assets/<slug>.png
catalog_tags: ["<tag>", "<tag>"]
---
```

- **`catalog_title`**: the human-readable product name shown on the card.
- **`catalog_description`**: short, verb-led, roughly 45 to 75 characters (about
  6 to 11 words). Flag anything over ~80 characters as likely to wrap awkwardly
  on a card. It must **not repeat the product name** (the title already shows
  it). No verbose lists of technologies; describe what the integration does. No
  overclaims.
- **`catalog_icon`**: `/integrations/assets/<slug>.png` (or `.svg` or `.jpg`).
  The referenced asset file must actually exist in `docs/integrations/assets/`
  and be a real image.
- **`catalog_tags`**: a JSON array of lowercase tags. **Use only tags that
  already exist in the catalog; never invent a new one.** Tags combine (e.g.
  `["data", "mcp"]`). Any page that uses MCP in its body must carry the `mcp`
  tag. Enumerate the valid tags in one pass with `grep catalog_tags
  docs/integrations/*.md`.

### 2. Structure and required elements

- **H1** follows `# <Product> <type> for ADK`, where `<type>` matches the
  category (e.g. `# GitHub MCP tool for ADK`, `# AgentOps observability for
  ADK`, `# Daytona plugin for ADK`).
- **Language support tag** immediately after the H1, as HTML (not bold
  markdown):

    ```html
    <div class="language-support-tag">
      <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
    </div>
    ```

    - Drop the TypeScript span for Python-only integrations.
    - **Spans must be on a single line.** No multi-line span splitting.
    - Using plain bold markdown instead of this div is a defect.
- **Section order** should match one of the three category templates:
    - **MCP tool**: `## Use cases` -> `## Prerequisites` -> `## Use with agent`
      (tabbed Python / TypeScript) -> `## Available tools` -> `## Configuration`
      (optional) -> `## Additional resources`
    - **Observability**: intro -> `## Overview` -> `## Installation` ->
      `## Setup` -> `## Observe` -> `## Support and Resources`
    - **Plugin**: `## Use cases` -> `## Prerequisites` -> `## Installation` ->
      `## Use with agent` -> `## Available tools` -> `## Configuration`
      (optional) -> `## Additional resources`
- **Section names**: prefer `## Use with agent` over `## Usage` or verbose
  `## Example: ...` headings. Prefer `## Installation` for the install step.
  Prefer specific names (`Available tools`, `Available methods`) over a bare
  `## API`.
- Flag **thin or over-fragmented sections** (many H2s that are each a single
  code block); recommend consolidating into a `## Setup` with numbered steps. A
  single copy-pasteable end-to-end code block is acceptable and often better for
  the user than a split Setup/Observe.

### 3. Code correctness

- Model strings should be `gemini-flash-latest`, `gemini-pro-latest`, or other
  valid `*-latest` aliases in sample code rather than specific versioned model
  strings, which increase the maintenance burden when new model versions are
  released.
- Canonical imports: `from google.adk.agents import Agent` (short form), and for
  MCP `from google.adk.tools.mcp_tool import McpToolset`.
- Agent variable is `root_agent` (Python) / `rootAgent` (TypeScript); TypeScript
  files end with `export { rootAgent };`.
- MCP examples should use MkDocs Material tabs (`=== "Python"` / `===
  "TypeScript"`, with nested sub-tabs like `=== "Local MCP Server"` where
  relevant). Admonitions inside tabs use 8-space indentation.
- Code must be complete and runnable, and must match the real ADK and vendor API
  (see "Deep verification").

### 4. Style and typography

- **Little to no use of em dashes or other overly used AI-generated content.**
  In `**term** — definition` bullets replace the em dash with a colon; in prose
  split into two sentences or use commas / parentheses. On third-party-owned
  content, flag but leave to the author; on anything you edit, remove them.
- Agent Development Kit should be referred to as "ADK", never "Google ADK" or
  "The ADK", in prose and code comments.
- **Do not start a sentence with an inline-code word.** Rephrase (e.g. "The
  `package-name` library adds..." rather than "`package-name` adds...").
- **No marketing bias.** These are the ADK docs: remove copy that reads like
  marketing and makes sweeping claims.

### 5. Links and assets

- Internal ADK-docs links should be **site-relative** (e.g.
  `/sessions/memory/`), not absolute `https://adk.dev/...` or legacy
  `https://google.github.io/...`. Relative links resolve in PR previews, survive
  domain changes, and are caught by the link checker. This is a nit on
  vendor-owned pages but generally fix it.
- Image references from a page in `docs/integrations/` should use
  `assets/<img>.png`, not `../assets/...` unless the image genuinely lives in
  `docs/assets/`. Trace the path against what peer pages actually do; do not
  theorize.
- External links must resolve (HTTP 200). Hunt for **hallucinated links** to
  nonexistent repos, samples, or docs. When you find one, suggest removing it or
  ask the author for the real target rather than assuming.

### 6. Catalog mechanics

- Integration pages are **auto-discovered** by
  `render_catalog('integrations/*.md')` in `docs/integrations/index.md`. **No
  `mkdocs.yml` nav entry is needed**; adding one is an error.
- Cards sort **alphabetically by filename**. Choose filenames that sort sensibly
  and **drop package-name prefixes** (e.g. `mongodb.md`, not
  `mongodb-mcp-server.md`; avoid `adk-`-prefixed names that float to the top).
- Add a **redirect** in `mkdocs.yml` only when a page is renamed or moved from
  an existing URL. Point redirects directly at the final destination; **never
  chain** them.
- Adding a new integration requires only the `.md` file with correct frontmatter
  plus the icon asset in `assets/`.

## Deep verification

Verify all code samples against actual APIs and library code. The canonical
source repositories are listed in `docs/community/contributing-guide.md`.

- **Package reality**: confirm the PyPI (or npm) package exists and that any
  stated version and Python requirement match the prose.
- **ADK API**: verify every ADK symbol and pattern used in the code samples
  against `~/Repos/adk-python` or the relevant language SDK (e.g. `Runner`,
  `run_async`, `create_session`, `append_event`, `save_artifact`,
  session/artifact service URIs, `adk web` / `adk run` CLI flags, genai types).
  Flag mismatches.
- **Vendor SDK**: verify the vendor's classes, methods, and arguments against
  the vendor SDK source or docs.
- **Ownership of bugs**: distinguish ADK-owned issues from vendor-SDK-owned
  issues (flag and leave for the author).
- **Test by hand** when practical: run the example with a real ADK agent, or at
  minimum `mkdocs serve` to confirm the card renders and the icon loads.

## Acceptance and rejection

**Hard blockers / rejection triggers:**

- Documents unreleased, unmerged, or fabricated APIs. We cannot document
  functionality that does not exist yet.
- Duplicates a page that already exists (vendor-specific features belong in the
  vendor's own docs, with at most a one-line link from the existing ADK page).
- Code that does not match the real ADK or vendor API.
- Broken or hallucinated links.
- Unsigned CLA.
- Spam signals (no connection to either project, no ADK-specific functionality,
  contribution-graph padding, very new integrations with low usage).

**A good page:** complete four-field frontmatter with a short verb-led
description and a valid existing tag; correct H1 and single-line
language-support div; the right category template with specific, non-fragmented
sections; complete, runnable, hand-tested code using `gemini-flash-latest` (or a
valid `*-latest` alias) and canonical imports (plus Python and TypeScript tabs
for MCP); relative internal links, working external links, valid icon asset; no
verbose AI-generated language, correct use when referring to "ADK", no
overclaims or marketing bias; auto-discovered with no nav edits.

## Report format

Produce a Markdown report categorized by priority, each finding with `file:line`
and context:

- 🔴 **Blockers**: fabricated/unreleased APIs, non-working code, broken or
  hallucinated links, unsigned CLA, wrong destination directory, duplicate page.
- 🟠 **Quality**: structure or template mismatch, missing/misnamed sections,
  overclaims, incorrect vendor/ADK API details.
- 🟡 **Style**: verbose AI-generated language, improper usage of "ADK",
  inline-code sentence starts, word-choice, model string, imports, description
  length, marketing tone.
- 🔵 **Nits**: tag comma spacing, absolute-vs-relative ADK links on vendor-owned
  pages, image size, heading-capitalization variants.

After the report, **stop**. Do not modify files unless the user explicitly asks.

## Feedback tone (for PR comments you draft)

- Short and direct. A couple of sentences per point.
- Diplomatic and actionable; give the contributor an out (e.g. "Do you have a
  sample agent in a repo? Otherwise you can remove this link and this page will
  serve as the sample.").
- Use precise, actionable terminology (e.g. "rename the catalog title" for the
  frontmatter field, not "rename the page"). Reference the contributing guide for
  mechanics instead of over-explaining.
