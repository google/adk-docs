# How to contribute

Thank you for your interest in contributing! We appreciate your willingness to
share your patches and improvements with the project.

## Before You Start

We're excited to have you contribute! To help your contribution go smoothly,
please review the following sections before you begin.

### Find Something to Work On

Check the [GitHub Issues](https://github.com/google/adk-docs/issues) for bug
reports or feature requests. Feel free to pick up an existing issue or open a
new one if you have an idea or find a bug.

### Sign the Contributor License Agreement

Contributions to this project must be accompanied by a
[Contributor License Agreement](https://cla.developers.google.com/about) (CLA).
You (or your employer) retain the copyright to your contribution; this simply
gives us permission to use and redistribute your contributions as part of the
project.

If you or your current employer have already signed the Google CLA (even if it
was for a different project), you probably don't need to do it again.

Visit <https://cla.developers.google.com/> to see your current agreements or to
sign a new one.

### Review Community Guidelines

We adhere to [Google's Open Source Community Guidelines](https://opensource.google/conduct/).
Please familiarize yourself with these guidelines to ensure a positive and
collaborative environment for everyone.

### Acceptance Criteria

We review contributions for integrations based on the following criteria:

- **Completeness and testability**: The integration should be functional and
  testable. Include working code examples that developers can run.
- **Value for developers**: The integration should provide clear value for
  developers building agents with ADK.
- **Publishability**: We must be able to publish the documentation in our
  official docs. For example, we cannot accept integrations that circumvent
  technical protection measures, violate terms of service, or access services
  without authorization.

### Tips for Success

- **Test your documentation locally** using `mkdocs serve` before submitting
- **Include complete, working code examples** that users can copy and run
- **Keep descriptions concise** but informative
- **Link to external resources** for detailed platform-specific documentation
- **Use consistent formatting** with existing documentation pages

## AI-Assisted Development

This repo includes built-in skills for AI coding agents to help with ADK
documentation contributions:

- **`integration-create`:** Draft a new integration page under
  `docs/integrations/`: gathers details, picks the right category template (MCP
  tool, observability, plugin, etc.), and follows the catalog conventions.

- **`integration-review`:** Review an integration page or PR for correct
  frontmatter, structure, working code, valid links, and catalog conventions,
  and produce a prioritized report.

These skills are located in `.agents/skills/` and are automatically available
when using compatible AI coding tools in this repo.

## Set Up Your Environment

1. **Clone the repository:**

    ```shell
    git clone git@github.com:google/adk-docs.git
    cd adk-docs
    ```

2. **Create and activate a virtual environment:**

    ```shell
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```shell
    pip install -r requirements.txt
    ```

4. **Run the local development server:**

    ```shell
    mkdocs serve
    ```

    This command starts a local docs server, typically at
    `http://127.0.0.1:8000/`.

## Language-Scoped Documentation

The site is built from one source tree into a separate view per SDK:
`/python/`, `/typescript/`, `/go/`, `/java/` and `/kotlin/`. Each view keeps
only the content for its language. Never create these directories or
per-language files by hand; the build generates them
(`hooks/language_scope.py`, with the logic in `langscope/`).

**Which pages a language gets**

- A page is built for the languages in its *page banner*: the
  `<div class="language-support-tag">` before the page's second heading.
  Attributes such as `title="..."` are fine. A page with no page banner is
  built for all five languages.
- A page written for one SDK that has no banner, such as a quickstart, must
  say so in its frontmatter:

    ```yaml
    ---
    languages: [go]
    ---
    ```

  `languages:` overrides the banner. Unknown names fail the build.

**What each view keeps**

The rules below only ever remove content that is clearly marked as
language-specific. When in doubt the build keeps content, so plain prose or
untabbed code for one language is shown in every view the page is built
for. To scope such content, put it in a tab or mark it as described below.

- Content tabs named after a language (`=== "Python"`) keep only the
  reader's language. A label that starts with a language also counts:
  `"Python - adk CLI"`, `"Python (Telegram)"`, `"JavaScript / TypeScript"`.
  When several tabs remain for a language, they stay tabs, named by the rest
  of the label (`"adk CLI"`). Tabs for anything else (`"Maven"`,
  `"API Testing (curl)"`) are kept, and language tabs inside them are scoped.
- Tab content is indented four spaces past its `=== "..."` marker. The
  first line after a tab group indented less than that, such as a list item
  indented two spaces, ends the group and is shown in every view. Start text
  that follows a tab group at the marker's own indentation, so it's clear
  the text is not part of the last tab.
- If a tab group has no tab for a language the page supports, that view
  leaves the group out. If the sentence before the group ends with a colon
  and every tab in the group is a language tab, a "Not yet available for
  <Language>" note takes its place. Add the missing tab rather than relying
  on the note.
- Tabs for a language the page is not built for (not in its banner, or in a
  section banner that omits it) appear in no view at all. The build reports
  this as a warning, which fails `mkdocs build --strict` and CI (see below):
  add the language to the banner or remove the tab.
- A banner directly under a heading (a *section banner*) scopes that
  heading's section. In other languages the section is removed. A section
  runs from its heading to the next heading of the same or a higher level,
  so everything under the heading goes with it, including closing remarks
  that apply to all SDKs: put those under their own heading. A banner that
  is not directly under a heading scopes nothing. To keep a section banner
  as a version badge only, add the `langscope-all` class:
  `<div class="language-support-tag langscope-all">`.
- A heading below the page title scopes its section when its text is only
  language names (`## Python`, `## Java and Kotlin`) or ends in a
  parenthesis holding only language names (`### Log levels (Python)`).
  Headings that merely mention a language (`## ADK for Java`,
  `### Configure in Python`) are not scoped.
- An admonition titled only languages plus "only" (`"Python only"`,
  `"Go-only"`, `"Only Python and TypeScript"`) appears only in those
  languages. If it comes directly after a heading, it scopes that heading's
  whole section. Other titles that name a language (`"Go: API path
  prefix"`, `"Requires ADK Python 2.4 or higher"`) are not scoped.
- To scope something explicitly, add a `langscope-<language>` class
  (repeat it for several languages):
    - On a heading, with attribute list syntax, it scopes the section:
      `## Kotlin programmatic setup { .langscope-kotlin }`.
    - On an admonition, as an extra type word, it scopes the admonition:
      `!!! note langscope-go "API path prefix"`.
- To stop the heading and admonition rules from scoping something, add
  the `langscope-all` class to it the same way. To turn them off for a whole
  page, set `language_heuristics: false` in its frontmatter. Banners, tabs
  and `langscope-<language>` classes still apply.
- No rule removes content that would then appear in no view: on a
  Kotlin-only page, `## Java` is kept.
- The banner that remains shows only the reader's language and version.
- The build log lists, at INFO level, every tab group, section and
  admonition left out of a view and every rule skipped because it names
  none of the page's languages. Source lines that reach no view are
  WARNINGs, so they fail `--strict`. The log ends with a summary count:

    ```text
    language_scope: tools/limitations.md: line 210: section banner 'Workaround #2: bypass_multi_tools_limit' (marker, for Python, Java, Kotlin) left out of the TypeScript view
    language_scope: generated 572 pages ... 0 source spans reach no view
    ```

**Links**

- Write links as usual, relative (`../agents/index.md`) or root-absolute
  (`/agents/`). The build points them at the reader's language, or at
  another language's view when the target page doesn't exist in it. Links
  to retired URLs in the `redirects` plugin map go straight to the new page.
- An in-page link (`#section`) to a section that this language's view
  removed points at a language view that has the section.
- Old flat URLs (`/agents/llm-agents/`) redirect to the reader's last-used
  SDK if that SDK has the page, else to the first SDK that has it, in the
  order Python, TypeScript, Go, Java, Kotlin (`/runtime/cancel/` has no
  Python page, so it goes to TypeScript). A tab anchor such as `#go` picks
  that SDK.
- Anchor validation is on (`validation: anchors: warn` in `mkdocs.yml`), so
  a link to a heading anchor that doesn't exist fails `mkdocs build
  --strict` and CI. This catches links into sections a view removed.

**Search, Markdown views and llms.txt**

- Search returns results from the SDK of the current page, plus shared
  pages such as the homepage and the API reference. This follows the page,
  not the saved preference: on `/python/live/models/`, reached through a
  link from the Go docs, search covers Python. On shared pages, search
  covers the last SDK the reader chose, or Python.
- Every page has a Markdown version at `<page URL>index.md`.
  `/<lang>/llms.txt` and `/<lang>/llms-full.txt` index each SDK.
  The root `/llms.txt` links to them and lists each page in its default
  language.

**Local preview and testing**

- To build only some languages, which is faster, set
  `MKDOCS_LANGSCOPE_LANGUAGES`, for example
  `MKDOCS_LANGSCOPE_LANGUAGES=python,go mkdocs serve`.
  `MKDOCS_LANGSCOPE_SKIP=1` builds only Python.
- Run the tooling tests (CI runs them on every pull request):

    ```shell
    pip install -r requirements-dev.txt
    python -m pytest tests/langscope -q
    ```

- The supported languages are defined once, in `langscope/config.py`.

## Create Your Contribution

| Type | Description |
|------|-------------|
| [Documentation fixes](#documentation-fixes) | Fix typos, broken links, or minor wording improvements |
| [New documentation](#new-documentation) | Add a new guide, tutorial, or reference page |
| [Major changes](#major-changes) | Large-scale reorganization or refactoring |
| [API and CLI reference](#api-and-cli-reference) | Pre-built reference docs generated from upstream ADK repositories |
| [Integrations](#integrations) | Tools, plugins, observability libraries, user interfaces, or any extensions to ADK agents or agent development |

### Documentation Fixes

For typo fixes, broken links, or small wording improvements:

1. Edit the file directly on GitHub or clone the repo locally
2. Submit a pull request with a clear description of the fix
3. No issue required for small fixes

### New Documentation

For new guides, tutorials, or reference pages:

1. **Open an issue first** to discuss the proposed content
2. Create your Markdown file in the appropriate `docs/` subdirectory
3. Add navigation entry to `mkdocs.yml` if needed
4. Test locally with `mkdocs serve`

### Major Changes

For large-scale reorganization or refactoring:

1. **Open an issue first** to discuss the scope and approach
2. Wait for maintainer feedback before starting work
3. Consider breaking large changes into smaller, reviewable PRs

### API and CLI Reference

For changes to the API and CLI reference pages, **do not edit files in
`docs/api-reference/` directly.** These are pre-built HTML generated from the
upstream ADK source repositories and are overwritten each time the docs are
regenerated.

To contribute to API and CLI reference documentation, make your changes in the
ADK source repository for the relevant language (for example, adding or updating
docstrings, exporting new public symbols, etc.).

The reference docs are regenerated periodically, and your changes will be
included in the next update. See the [ADK Contributing
Guide](https://adk.dev/community/contributing-guide/) for links to each
language-specific repository.

### Integrations

Integrations include third-party tools, plugins, and observability platforms for
ADK agents. All integrations live under `docs/integrations/`. Examples include
[GitHub](https://adk.dev/integrations/github/),
[Daytona](https://adk.dev/integrations/daytona/), and
[AgentOps](https://adk.dev/integrations/agentops/).

> [!TIP]
> If you use an AI coding agent in this repo, the `integration-create` skill can
> scaffold a draft page for you, and `integration-review` can check it before you
> submit. See [AI-Assisted Development](#ai-assisted-development).

**To contribute an integration:**

1. **Create the documentation file:**

    Create a new Markdown file at `docs/integrations/<name>.md`.

2. **Follow the standard structure:**

    Your documentation should include frontmatter and the sections below that
    are relevant to your integration.

    See [existing integration
    pages](https://github.com/google/adk-docs/tree/main/docs/integrations) for
    reference.

    ````markdown
    ---
    catalog_title: Integration Name
    catalog_description: A short description of what your integration does
    catalog_icon: /integrations/assets/<name>.png
    ---

    # Integration Name

    Brief description of the integration and what it provides for ADK agents.

    ## Use cases

    - **Use Case 1**: Description of what users can accomplish
    - **Use Case 2**: Another common use case
    - **Use Case 3**: Additional use case

    ## Prerequisites

    - Required software versions
    - Required accounts or API keys
    - Any setup steps needed

    ## Installation

    ```bash
    pip install your-package-name
    ```

    ## Use with agent

    ```python
    from google.adk.agents import Agent

    # Show a complete, working example
    ```

    ## Available tools

    Tool | Description
    ---- | -----------
    `tool_name_1` | What this tool does
    `tool_name_2` | What this tool does

    ## Resources

    - [Platform Documentation](https://example.com/docs)
    - [GitHub Repository](https://github.com/example/repo)
    - [Community/Support Links](https://example.com/community)
    ````

3. **Add an image asset:**

    Add a logo image to `docs/integrations/assets/` named `<name>.png`.
    Images should be square and appropriately sized for display as a card.

4. **Include screenshots:**

    Screenshots or visuals that illustrate your integration in action are
    strongly encouraged. Add them to `docs/integrations/assets/`.

## Submit Your Contribution

All contributions, including those from project members, undergo a review
process.

1. **Create a Pull Request:** We use GitHub Pull Requests (PRs) for code review.
   Please refer to [GitHub
   Help](https://help.github.com/articles/about-pull-requests/) if you're
   unfamiliar with PRs.

2. **Review Process:** Project maintainers will review your PR, providing
   feedback or requesting changes if necessary.

3. **Merging:** Once the PR is approved and passes any required checks, it will
   be merged into the main branch.

We look forward to your contributions!
