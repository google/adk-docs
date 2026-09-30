---
name: integration-create
description: Creates a new ADK integration documentation page (a Markdown file under docs/integrations/) for a third-party tool, plugin, observability platform, data store, MCP server, or connector. Gathers details, picks the right category template, and drafts a page that follows adk-docs conventions. Triggers on "integration-create", "create integration page", "new integration", "add an integration", "write an integration page".
---

# ADK Integration Page Creator (integration-create)

This skill creates a new integration page for the
[adk-docs](https://github.com/google/adk-docs) repository. Integration pages
live under `docs/integrations/` and are auto-discovered into a card catalog. The
output of this skill is a strong starting point, not a finished page: when done,
run the `integration-review` skill on it and test with `mkdocs serve`.

The real template is the set of **existing shipping pages**. Before drafting,
open the exemplar(s) for the chosen category and match their structure and
conventions:

- MCP tools: `docs/integrations/github.md`, `docs/integrations/notion.md`
- Observability: `docs/integrations/phoenix.md`, `docs/integrations/arize-ax.md`
- Plugins: `docs/integrations/daytona.md`, `docs/integrations/goodmem.md`

To find more similar pages, scan `catalog_tags` in one pass (`grep catalog_tags
docs/integrations/*.md`) and read the ones sharing the category's tag (e.g.
`mcp`, `observability`) or product domain in full. Match live pages and repo
conventions rather than inferring everything from the templates below.

See `CONTRIBUTING.md` (the "Integrations" section) for the human-facing
contract. For the full rulebook applied during review, see the
`integration-review` skill.

## Step 1: Gather inputs

Ask the user for whatever is not already provided:

- **Product / integration name** (drives `catalog_title` and the H1).
- **Category**, which selects the template:
    - **MCP tool** (an MCP server the agent connects to)
    - **Observability** (tracing / metrics / evaluation exporter)
    - **Plugin** (an installable package exposing tools or callbacks)
- **Language support**: Python only, or Python + TypeScript.
- **Package name** (PyPI / npm) and install command.
- **Connection style** for MCP: local (stdio) and/or remote (HTTP).
- **Tools or methods** the integration exposes (for the table).
- **Links**: product docs, GitHub repo, PyPI/npm, where to get an API key.
- **Icon**: confirm an asset will be added at
  `docs/integrations/assets/<slug>.png`.

## Step 2: Choose the filename

- Use a short, lowercase, hyphenated slug based on the product or technology
  name.
- Avoid `adk-` or other prefixes that would float the card to the top of the
  alphabetically sorted catalog.
- Create the file at `docs/integrations/<slug>.md`.

## Step 3: Draft the page

Use the frontmatter and the category skeleton below. Fill each section by
reading the exemplar page(s) for the same category and adapting their prose and
code.

Do **not** add a `mkdocs.yml` nav entry; pages are auto-discovered by
`render_catalog('integrations/*.md')`. Add a redirect only if this page replaces
an existing URL, and never chain redirects.

## Step 4: Hand off

Tell the user this is a draft, then:

- Remind them to add the icon asset at `docs/integrations/assets/<slug>.png`
  (square, reasonably sized) and any screenshots.
- Recommend running the `integration-review` skill on the new page.
- Recommend `mkdocs serve` to confirm the card renders and the icon loads.

## Frontmatter (all categories)

```yaml
---
catalog_title: <Display Name>
catalog_description: <short verb-led phrase>
catalog_icon: /integrations/assets/<slug>.png
catalog_tags: ["<tag>", "<tag>"]
---
```

- `catalog_description`: short and verb-led, roughly 45 to 75 characters (about
  6 to 11 words); keep it under ~80 so it does not wrap awkwardly on a card. Do
  not repeat the product name (the title shows it). No verbose lists, no
  overclaims.
- `catalog_tags`: use only tags that already exist in the catalog; never invent
  one. Enumerate the valid tags in one pass with
  `grep catalog_tags docs/integrations/*.md`. Tags combine. Any page that uses
  MCP must include `mcp`.
- `catalog_icon`: `/integrations/assets/<slug>.png` (or `.svg` or `.jpg`). No
  `/adk-docs/` prefix.

## H1 and language support tag (all categories)

```markdown
# <Product> <type> for ADK
```

`<type>` is `MCP tool`, `observability`, or `plugin` per category. Immediately
after the H1, add the language support div (spans must be on a single line; drop
the TypeScript span if Python-only):

```html
<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>
```

## Skeleton: MCP tool

````markdown
## Use cases

- **<Use case>**: <what the user accomplishes>
- **<Use case>**: <...>

## Prerequisites

- <account, API key, or token, with a link to where to get it>

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="<slug>_agent",
            instruction="Help users get information from <Product>",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="<server url>",
                        headers={"Authorization": "Bearer YOUR_TOKEN"},
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "<slug>_agent",
            instruction: "Help users get information from <Product>",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "<server url>",
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

Tool | Description
---- | -----------
`<tool>` | <what it does>

## Additional resources

- [<Product> Documentation](<url>)
- [<Product> Repository](<url>)
````

Include both `Local MCP Server` (stdio) and `Remote MCP Server` sub-tabs when
the server supports both. Add a `## Configuration` section for optional headers
or environment variables.

## Skeleton: Observability

````markdown
<one-paragraph intro of what the platform provides for ADK>

## Overview

- **<Capability>**: <...>
- **<Capability>**: <...>

## Installation

```bash
pip install <package>
```

## Setup

<API keys, environment variables, and instrumentor initialization>

## Observe

<a complete, runnable ADK agent example that is traced end-to-end>

## Support and Resources

- [<Platform> Documentation](<url>)
- [<Platform> Repository](<url>)
````

A single copy-pasteable end-to-end code block is acceptable and often better
than splitting Setup and Observe.

## Skeleton: Plugin

````markdown
## Use cases

- **<Use case>**: <...>

## Prerequisites

- <account / API key with link>

## Installation

```bash
pip install <package>
```

## Use with agent

```python
from <package> import <Plugin>
from google.adk.agents import Agent

root_agent = Agent(
    model="gemini-flash-latest",
    name="<slug>_agent",
    instruction="<what the agent does>",
    tools=<plugin>.get_tools(),
)
```

## Available tools

Tool | Description
---- | -----------
`<tool>` | <what it does>

## Additional resources

- [<Product> Documentation](<url>)
- [<Product> on PyPI](<url>)
- [<Product> on GitHub](<url>)
````

Add a `## Configuration` section for environment variables when relevant.

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
