# integration-create skill

Usage guide for the `integration-create` skill.

**What it does:** Drafts a new integration page under `docs/integrations/`,
picking the right category template (MCP tool, observability, plugin, etc.) and
following the catalog conventions.

**Audience:** Contributors.

## How to invoke

Ask the agent naturally, for example:

- "Create an integration page for <tool>"
- "Add an integration for <product>"
- "Write an integration page for <service>"

## What you get back

- A drafted `docs/integrations/<name>.md` with frontmatter and the
  category-appropriate sections.
- A hand-off note reminding you to add the icon asset at
  `docs/integrations/assets/<slug>.png` (and any screenshots).

## Follow-up actions

- Provide the inputs it gathers: product name, category, language support,
  package name and install command, the tools or methods it exposes, and links
  (docs, repo, PyPI/npm, API key).
- Iterate on the draft.
- Run the `integration-review` skill before submitting.
- Run `mkdocs serve` to confirm the card renders and the icon loads.
- Open a pull request.
