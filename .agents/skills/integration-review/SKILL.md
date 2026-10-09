---
name: integration-review
description: >-
  Reviews an ADK integration documentation page (a Markdown file under docs/integrations/) or an integration pull request for correctness, structure, style, working code, valid links, and catalog conventions. Produces a scored risk report (Critical, High, Medium, Low), a recommended decision (approve, request changes, or close PR), a top-level review response, and draft line-anchored comments; only fixes issues when explicitly asked. Triggers on "integration-review", "review integration page", "review integration PR", "review this integration", "check integration docs".
tags: [integrations, catalog, mcp, plugins, observability, github, technical-writing, content-review, doc-review]
category: review
version: 0.2.0
---

# ADK Integration Page Reviewer (integration-review)

This skill guides a rigorous review of integration documentation pages in the
[adk-docs](https://github.com/google/adk-docs) repository. Integration pages
live under `docs/integrations/` and document third-party tools, plugins,
observability platforms, data stores, MCP servers, connectors, and other
extensions to ADK agents.

This review is the integration-specific counterpart to the general ADK docs
review levels (risk assessment, information architecture, technical accuracy,
product messaging, style guide). It uses the same risk tiers and the same
scoring model, so an integration page can be compared against any other ADK
docs change. When the primary file under review is in `docs/integrations/`, run
this skill instead of the information architecture review.

The authoritative sources of truth for this review are:

1. The repository's
   [CONTRIBUTING.md](https://github.com/google/adk-docs/blob/main/CONTRIBUTING.md)
   (see the "Integrations" section and its acceptance criteria).
2. The **existing shipping integration pages**, which are the real template.
   Always open and compare against peers of the same category:
    - MCP tools: `docs/integrations/github.md`, `docs/integrations/notion.md`
    - Observability: `docs/integrations/phoenix.md`, `docs/integrations/arize-ax.md`
    - Plugins: `docs/integrations/daytona.md`, `docs/integrations/goodmem.md`
3. The catalog rendering logic in `scripts/integrations.py`.

> [!NOTE]
> Read this skill and follow its steps whenever asked to review an integration
> page or an integration PR.

## Input

A pull request, change list, or local file containing changes to an ADK
integration page under `docs/integrations/`.

-   Pull requests should be specified as a URL link, for example:
    https://github.com/google/adk-docs/pull/1000
-   Change lists should be specified as a URL link, for example:
    https://critique.corp.google.com/cl/2000000000 or cl/2000000000
-   Local files should be specified as a repository path, for example:
    `docs/integrations/bigquery.md`

## Review workflow

### Step 1: Gather the change

- If reviewing a PR, use `gh` to pull it and read the **full cumulative diff**,
  not a single commit: `gh pr view <n> --repo google/adk-docs` and `gh pr diff
  <n> --repo google/adk-docs`. A stale `mkdocs.yml` entry or asset can hide in
  files that only show in the full diff.
- Record the change size for the report header: `gh pr view <n> --repo
  google/adk-docs --json additions,deletions,changedFiles`. Lines changed is
  additions plus deletions. For a local change, use `git diff --shortstat`.
- Check whether "Allow edits from maintainers" is enabled
  (`maintainerCanModify`) so fixes can be pushed directly if requested later.
- Confirm the CLA is signed (the `google-cla` bot). An unsigned CLA is an
  ❌ Critical Risk finding and blocks merge until signed.
- If reviewing a local file, run `git status` and `git diff` to see the change.

### Step 2: Find and read similar pages

Find 5 or more similar pages and read them in full. Identify candidates in one
pass by scanning `catalog_tags` (`grep catalog_tags docs/integrations/*.md`) and
matching the tag under review (for example `mcp`, `observability`); widen the
set with other signals such as product domain, structural template, and language
support (they need not all be the exact same category). Reading the full pages,
not just frontmatter, grounds the review in live examples and repo conventions
rather than inferring everything from the templates in this skill.

### Step 3: Run the checklist

Work through every dimension in the review checklist below.

### Step 4: Verify code, packages, and links

Do real verification, not a surface read (see "Deep verification").

### Step 5: Research developer value and maturity

Gather objective evidence about the project's maturity, adoption, and whether it
genuinely integrates with ADK (see "Developer value and maturity"). Base the
assessment on verifiable facts, not impressions or the PR's own marketing.

### Step 6: Classify, score, report, and stop

Assign a risk tier to every finding (see "Risk classification"), compute the
review score, and produce the report (see "Output"). Do **not** edit files, post
to GitHub, or offer to fix issues by default. Stop and wait for an explicit
instruction to fix or to post.

### Step 7 (only if asked): Apply fixes

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
  already exist in the catalog; never invent a new one.** Tags combine (for
  example `["data", "mcp"]`). Any page that uses MCP in its body must carry the
  `mcp` tag. Enumerate the valid tags in one pass with `grep catalog_tags
  docs/integrations/*.md`.

### 2. Structure and required elements

- **H1** follows `# <Product> <type> for ADK`, where `<type>` matches the
  category (for example `# GitHub MCP tool for ADK`, `# AgentOps observability
  for ADK`, `# Daytona plugin for ADK`).
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
  In a `**term**` definition bullet, replace the em dash with a colon; in prose
  split into two sentences or use commas or parentheses. On third-party-owned
  content, flag but leave to the author; on anything you edit, remove them.
- Agent Development Kit should be referred to as "ADK", never "Google ADK" or
  "The ADK", in prose and code comments.
- **Do not start a sentence with an inline-code word.** Rephrase (for example
  "The `package-name` library adds..." rather than "`package-name` adds...").
- **No marketing bias.** These are the ADK docs: remove copy that reads like
  marketing and makes sweeping claims.

### 5. Links and assets

- Internal ADK-docs links should be **site-relative** (for example
  `/sessions/memory/`), not absolute `https://adk.dev/...` or legacy
  `https://google.github.io/...`. Relative links resolve in PR previews, survive
  domain changes, and are caught by the link checker. This is 🟢 Low Risk on a
  vendor-owned page but generally fix it.
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
  and **drop package-name prefixes** (for example `mongodb.md`, not
  `mongodb-mcp-server.md`; avoid `adk-`-prefixed names that float to the top).
- Add a **redirect** in `mkdocs.yml` only when a page is renamed or moved from
  an existing URL. Point redirects directly at the final destination; **never
  chain** them.
- Adding a new integration requires only the `.md` file with correct frontmatter
  plus the icon asset in `assets/`.

## Deep verification

Verify all code samples against actual APIs and library code, using the
currently released version (a GitHub `vX.X.X` release) of the relevant ADK
repository:

-   ADK Python: https://github.com/google/adk-python
-   ADK TypeScript: https://github.com/google/adk-js
-   ADK Go: https://github.com/google/adk-go
-   ADK Java: https://github.com/google/adk-java
-   ADK Kotlin: https://github.com/google/adk-kotlin

- **Package reality**: confirm the PyPI (or npm) package exists and that any
  stated version and Python requirement match the prose.
- **ADK API**: verify every ADK symbol and pattern used in the code samples
  against the repository for the relevant language SDK (for example `Runner`,
  `run_async`, `create_session`, `append_event`, `save_artifact`,
  session/artifact service URIs, `adk web` / `adk run` CLI flags, genai types).
  Do not assume a local checkout: fetch the source with `gh` or `git` (or use a
  local clone if one exists), and check the **released version** the docs target
  rather than a main branch that may be ahead of or behind the release. Note the
  version you verified against, and flag mismatches.
- **Unreleased code**: documentation that depends on code merged to a main
  branch but not yet in an official release is ❌ Critical Risk.
- **Vendor SDK**: verify the vendor's classes, methods, and arguments against
  the vendor SDK source or docs.
- **Ownership of bugs**: distinguish ADK-owned issues from vendor-SDK-owned
  issues (flag and leave for the author).
- **Test by hand** when practical: run the example with a real ADK agent, or at
  minimum `mkdocs serve` to confirm the card renders and the icon loads.

## Developer value and maturity

Integration pages are official ADK documentation, so an integration must earn
its place by offering real, demonstrated value to developers. The goal here is
to research and determine if the integration is for an established platform with
genuine utility, a track record, and real adoption vs. for a brand-new or
low-adoption project with little substance behind it. Do the research and report
the evidence; do not infer value from the PR's own description or marketing.

Gather objective, verifiable signals and cite each with a source:

- **Package reality and age**: confirm a real published package exists. Query
  the PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`) or the npm registry
  (`https://registry.npmjs.org/<pkg>`) for the first-release date, number of
  releases, and latest version, and check download counts (pypistats or the npm
  downloads API). A missing package, or one published the same day as the PR, is
  a strong negative signal.
- **Source repository signals**: use `gh api repos/<owner>/<repo>` to read
  `created_at`, stars, forks, contributor count, commit count, releases,
  license, and last-commit date. A repository created within the last few weeks,
  with a handful of commits, a single author, or no license is a negative
  signal.
- **Adoption and track record**: gauge real usage from verifiable signals:
  package download counts (see above), repository stars, forks, and dependent
  projects, plus any documented production users, case studies, or independent
  third-party coverage found via web search, and how long the product has
  operated. Broad, verifiable usage is a positive signal; its absence across
  every source is a negative one.
- **Genuine ADK integration**: confirm the project actually uses ADK extension
  points (callbacks, plugins, toolsets, MCP) rather than patching a dependency
  such as `google-genai`, or wrapping a REST API with plain functions and
  presenting that as an ADK integration (cross-check against "Deep verification"
  and the scope trigger below).
- **Website liveness**: confirm the linked site is a real, live product site,
  not a parked domain or placeholder.

**Weighing the evidence.** A new project is not automatically low-value: an
established vendor shipping a brand-new package, or a project with clear utility
plus a real source repository, tests, and a license, is credible and should not
be treated as a value concern. Genuine concern is the accumulation of negative
signals: brand-new and unpublished, no adoption or track record, no source or
license, no real ADK extension use, and claims the page makes that your
verification could not confirm. When the evidence is mixed, give the contributor
the benefit of the doubt, lay out the facts, and recommend closing as a judgment
call for the maintainer rather than asserting a verdict. Keep the write-up
neutral and factual.

## Acceptance and rejection

**Rejection triggers (close the PR):**

- Documents unreleased, unmerged, or fabricated APIs. We cannot document
  functionality that does not exist yet.
- Duplicates a page that already exists (vendor-specific features belong in the
  vendor's own docs, with at most a one-line link from the existing ADK page).
- Code that does not match the real ADK or vendor API.
- Broken or hallucinated links.
- Unsigned CLA.
- Insufficient developer value or maturity: a brand-new repository, an
  unpublished or same-day package, no adoption or track record, or no source
  repository or license. Support this with the evidence from "Developer value
  and maturity" and treat it as a maintainer judgment call, not an automatic
  verdict.
- Misrepresented integration: manual code that ignores ADK's extension points
  while claiming to integrate with ADK.
- Out of scope: a generic "wrap a REST API as a function tool" page with no
  ADK-specific artifact. The ADK docs are not an API directory.
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

## Risk classification

Assign exactly one tier to every finding. Reserve ❌ Critical Risk and 🔴 High
Risk for items that block merge. A finding that is genuinely take-or-leave
belongs in 🟢 Low Risk.

### ❌ Critical Risk

Blocks merge, and usually maps to a rejection trigger.

- Fabricated, unreleased, or unmerged ADK or vendor APIs.
- Code that does not run, or does not match the real ADK or vendor API.
- Broken or hallucinated links.
- Unsigned CLA.
- Page in the wrong directory, or a duplicate of an existing page.
- Misrepresented integration: claims ADK integration but ignores ADK extension
  points.
- Out of scope: a generic REST wrapper with no ADK-specific artifact.
- Spam signals.
- Insufficient developer value or maturity. Tag this one "judgment call" and
  back it with the "Developer value and maturity" narrative.

### 🔴 High Risk

Must be fixed before merge. The page itself is salvageable.

- Missing or incomplete frontmatter fields.
- A `catalog_icon` that points at an asset missing from
  `docs/integrations/assets/`, or at a file that is not a real image.
- An invented `catalog_tags` value, or a page that uses MCP without the `mcp`
  tag.
- Wrong H1 pattern, or a missing or malformed language-support div.
- Section order or category template mismatch; missing or misnamed required
  sections.
- Overclaims, or an incorrect ADK or vendor API detail that leaves the sample
  runnable but wrong.
- A `mkdocs.yml` nav entry added for an integration page.
- A rename or move with no redirect, or a chained redirect.
- A filename that carries a package-name prefix or otherwise sorts badly in the
  catalog.

### 🟡 Medium Risk

Should be fixed before merge.

- Em dashes and other verbose AI-generated phrasing.
- "Google ADK" or "The ADK" instead of "ADK".
- A sentence that starts with an inline-code word.
- A pinned model string instead of a `*-latest` alias.
- Non-canonical imports, a wrong agent variable name, or a missing
  `export { rootAgent };`.
- An MCP sample with no Python and TypeScript tabs.
- A `catalog_description` over ~80 characters, or one that repeats the product
  name.
- Marketing tone.
- Absolute `https://adk.dev/...` or `https://google.github.io/...` internal
  links on an ADK-owned page.
- An image path of `../assets/...` where `assets/...` is correct.
- Thin or over-fragmented sections.

### 🟢 Low Risk

Optional. Note it and move on.

- Comma spacing inside `catalog_tags`.
- Absolute rather than relative internal links on a vendor-owned page.
- Image size.
- Heading capitalization variants.
- Word-choice preferences that are genuinely take-or-leave.

## Output

-   **REQUIRED: Code citations with URL links**: Any output that includes code
    or doc source citations must provide URL links that point to github.com,
    cs.corp.google.com, or critique.corp.google.com, including specific line
    numbers. Do NOT point to local files for code citations. For a PR, link the
    head commit blob, for example
    `https://github.com/google/adk-docs/blob/<sha>/docs/integrations/<page>.md#L76`.
    Keep the `file:line` locator alongside the link so a maintainer can anchor
    an inline comment.

-   **Line numbers must be exact.** Derive them from the file under review (the
    local page, or the PR via `gh pr diff` or a fetched copy) using a
    line-numbered read, `grep -n`, or the diff's hunk headers. Never approximate
    (no `~`).

-   **Review Score:** Create a review score starting with a base score of 100,
    and then subtract points based on the following criteria:
    - ❌ Critical Risk: -20 points
    - 🔴 High Risk: -10 points
    - 🟡 Medium Risk: -2 points
    - 🟢 Low Risk: -1 point

    Subtract once per finding, not once per tier, and floor the score at 0.
    Include the final Review Score in the assessment report as defined below.

-   **Overall assessment:** the highest tier that has at least one finding. When
    every tier is empty, the overall assessment is 🟢 Low Risk.

-   Default output is a report with the structure below. Unlike the shared ADK
    review output template, **print all four risk sections in order and write
    `None` under any section with no findings**, so the absence of Critical and
    High risk items is stated rather than implied.

```
# Integration review report

- **Review Score**: [Score out of 100]
- **Overall assessment**: [🟢 Low Risk | 🟡 Medium Risk | 🔴 High Risk | ❌ Critical Risk]
- **Summary reasoning**: [A brief summary of why the overall risk was chosen]
- **Recommended action**: [One of "Approve", "Request changes", or "Close PR";
  include a brief, 2-3 sentence explanation and the top 1 or 2 risk factors
  leading to this recommendation.]
- **Number of lines changed**: [T-Shirt Size: "XS" =< 9 lines changed | "S" =< 49 | "M" =< 249; L =< 999 | "XL" =< 1999 | "XXL" > 1999] [number]
- **Number of files changed**: [number]
- **Verified against**: [ADK release tag, for example google/adk-python v1.20.0]

## ❌ Critical risk items

  - `<file>:<line>` ([link](https://github.com/google/adk-docs/blob/<sha>/<file>#L<line>)):
    [description of the item and the suggested change]

  - ...

## 🔴 High risk items

  - ...

## 🟡 Medium risk items

  - ...

## 🟢 Low risk items

  - ...

## Developer value and maturity

[A short narrative paragraph summarizing the evidence gathered in Step 5:
package age, adoption and track record, repository signals, and genuine ADK
extension use. Cite each signal with a source link. End with a provisional
lean.]

## Review decision

[Approve | Request changes | Close PR, justified by citing the findings above.]

## Top-level review response

[A few sentences, suitable to paste as the GitHub PR review summary.]

## Review comments

[One copy-pasteable inline comment per finding location, grouped by tier.]
```

### Review decision

Choose exactly one, justified by citing the specific findings from the report
above it. Cross-reference the "Acceptance and rejection" criteria so the
decision stays consistent with them, and repeat the choice verbatim in the
**Recommended action** header field.

- **Approve**: the report shows no ❌ Critical, 🔴 High, or 🟡 Medium findings
  (all three are `None`); at most 🟢 Low Risk items remain, and the page meets
  the "A good page" bar.
- **Request changes** (the common case): a salvageable page with any ❌/🔴/🟡
  finding that must be fixed before it can merge. List the must-fix items.
- **Close PR**: hits a rejection trigger from "Acceptance and rejection"
  (fabricated/unreleased APIs, duplicate page, code that does not match the real
  ADK or vendor API, broken or hallucinated links, unsigned CLA, misrepresented
  integration, out of scope, insufficient value/maturity, spam signals).
  Recommend the PR be closed and record the reason (link the superseding doc or
  PR where relevant). When insufficient developer value/maturity is the *only*
  concern (the code otherwise works), present it as a recommendation explicitly
  flagged as a maintainer judgment call, backed by the "Developer value and
  maturity" narrative, rather than an automatic hard blocker.

Do not use a plain "comment" (no-decision) outcome unless there is a strong,
stated reason the review genuinely cannot land on one of the three above.

### Top-level review response

A short review body (a few sentences), suitable to paste as the GitHub PR review
summary. State what the integration is, the overall assessment and score, the
headline reasons, and what needs to happen next. Use the "Feedback tone" below:
short, direct, diplomatic, and actionable. For a Close PR outcome, adapt the
matching snippet from "Decline response templates" and fill in the specific
evidence.

### Review comments

A copy-pasteable list of inline PR comments a maintainer can drop onto the diff.
Cover **every finding in the report, across all four tiers (❌ 🔴 🟡 🟢)**. Do
not filter by severity or decide that some categories are not worth commenting:
every flagged item, down to the last low-risk note, gets a comment so the
maintainer can relay all of it and nothing is silently dropped.

- Prefix each comment with
  `INTEGRATION REVIEW (Critical | High | Medium | Low):`, keeping only the tier
  that applies.
- Keep the text of the comment brief and to the point. Suggest a specific
  content change, using the "```suggestion" comment syntax to fix the noted
  problem if at all possible.
- **Format each comment to be pasted as-is** into a GitHub inline comment: a
  `file:line` (or `file:start-end`) locator on its own line, then the one- to
  two-sentence suggestion as a blockquote so it copies cleanly. For example:

    `docs/integrations/weave.md:76`

    > INTEGRATION REVIEW (Medium): Use `model="gemini-flash-latest"` instead of
    > the pinned `model="gemini-2.5-flash"` to match repo convention and avoid
    > model-version churn.
    >
    > ```suggestion
    >     model="gemini-flash-latest",
    > ```

- Use the exact `file:line` for the finding, taken from the file under review
  (the local page or the PR diff), never approximated (no `~`). Only when a
  finding genuinely maps to no line (for example, a missing section, or the
  value and maturity judgment call) fall back to a page-level or
  frontmatter-level comment, and say so explicitly.
- Give the contributor an out where appropriate (for example "remove this link
  and the page serves as the sample").
- Group the comments by tier in the same order as the report.
- One finding can produce more than one comment: a finding that spans multiple
  locations (for example the same issue in the Python and TypeScript samples)
  gets one comment per location.
- Reconcile before finishing: every finding in the report has at least one
  comment (so comments equal or outnumber findings). If any finding lacks one,
  add it rather than shipping a partial list.

Everything in the report is a **draft**: do not post to GitHub, do not run `gh`
to comment, and do not edit files unless the user explicitly asks. After the
report, **stop**.

## Feedback tone (for PR comments you draft)

- Short and direct. A couple of sentences per point.
- Diplomatic and actionable; give the contributor an out (for example "Do you
  have a sample agent in a repo? Otherwise you can remove this link and this
  page will serve as the sample.").
- Use precise, actionable terminology (for example "rename the catalog title"
  for the frontmatter field, not "rename the page"). Reference the contributing
  guide for mechanics instead of over-explaining.

## Decline response templates

When the decision is Close PR, adapt the matching template below for the
top-level review response. These mirror the maintainer's established voice; keep
them short and **replace every `[bracket]` with the specific, verified
evidence** for this PR. Link the acceptance criteria
(`https://github.com/google/adk-docs/blob/main/CONTRIBUTING.md#acceptance-criteria`).
More than one may apply; combine the relevant paragraphs.

- **Value for developers**: "Thank you for the PR! After reviewing it against
  our [acceptance criteria], we're not able to accept this integration at this
  time. **Value for developers:** We look for integrations that provide clear,
  demonstrated value to developers building agents with ADK, and we evaluate
  factors such as project maturity, active user base, and track record.
  [evidence: for example the supporting repository was created within the last
  few weeks, there is no published package to integrate against, and the project
  does not yet have the community adoption or track record we look for.]"
- **Completeness and testability**: "Thank you for the PR. After reviewing it
  against our [acceptance criteria], we're not able to accept this integration
  at this time. **Completeness and testability:** Code examples in our docs must
  be functional and runnable by developers. [evidence: for example the ADK
  imports and classes referenced do not exist / the `<pkg>` package is not
  published / the example imports from an unmerged PR.]"
- **Publishability**: "Thanks for the PR. However, we're unable to accept this
  integration. Per our [acceptance criteria], we can't publish integrations for
  services that may circumvent technical protection measures, violate terms of
  service, or access services without authorization. [evidence]"
- **Out of scope**: "Thanks for the PR! However, this integration page is out of
  scope for the ADK docs. Integration pages are for third-party functionality
  that extends or tightly integrates with ADK (tools, plugins, toolsets, MCP
  servers, or observability platforms). [evidence: for example this defines
  plain functions that call a REST API, the generic 'wrap a REST API as a
  function tool' pattern, which is already documented and applies to any API.
  The ADK docs are not an API directory.]"
- **Duplicate / superseded**: "Thanks for the PR. This is superseded by #`<N>` /
  duplicates the existing [`<page>`]. [Optional: vendor-specific features belong
  in the vendor's own docs, with at most a one-line link from the existing ADK
  page.]"
