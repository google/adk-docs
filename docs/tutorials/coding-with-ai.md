# Coding with AI

You can use AI coding assistants to build agents with Agent Development Kit
(ADK). Give your coding agent ADK expertise by installing development skills
into your project, or by connecting it to ADK documentation through an MCP
server.

- [**ADK Dev Skills**](#adk-dev-skills): Install ADK development skills directly into
  your project.
- [**ADK Docs MCP Server**](#adk-docs-mcp-server): Connect your coding tool to
  ADK documentation through an MCP server.
- [**ADK Docs Index**](#adk-docs-index): Machine-readable documentation files
  following the `llms.txt` standard.

## ADK Dev Skills

ADK provides a set of development [skills](https://agentskills.io/) that cover
APIs, coding patterns, deployment, and evaluation. The skills work with any
compatible tool, including Gemini CLI, Antigravity, Claude Code, and Cursor.

To install the ADK development skills, run the following in your project
directory:

```bash
npx skills add google/adk-docs/skills -y -g
```

Browse the [ADK Dev Skills on
GitHub](https://github.com/google/adk-docs/tree/main/skills), which include:

| Skill | Description |
|-------|-------------|
| `adk-cheatsheet` | Python API quick reference and docs index |
| `adk-deploy-guide` | Agent Engine and Cloud Run deployment |
| `adk-dev-guide` | Development lifecycle and coding guidelines |
| `adk-eval-guide` | Evaluation methodology and scoring |
| `adk-observability-guide` | Tracing, logging, and integrations |
| `adk-scaffold` | Project scaffolding |

## ADK Docs MCP Server

You can configure your coding tool to search and read ADK documentation using an
MCP server. Below are setup instructions for popular tools.

### Gemini CLI

To add the ADK docs MCP server to [Gemini CLI](https://geminicli.com/), install
the [ADK Docs Extension](https://github.com/derailed-dash/adk-docs-ext):

```bash
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

### Antigravity

To add the ADK docs MCP server to [Antigravity](https://antigravity.google/)
(requires [`uv`](https://docs.astral.sh/uv/)):

1. Open the MCP store via the **...** (more) menu at the top of the editor's
   agent panel.
2. Click on **Manage MCP Servers** then **View raw config**.
3. Add the following to `mcp_config.json`:

    ```json
    {
      "mcpServers": {
        "adk-docs-mcp": {
          "command": "uvx",
          "args": [
            "--from",
            "mcpdoc",
            "mcpdoc",
            "--urls",
            "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
            "--transport",
            "stdio"
          ]
        }
      }
    }
    ```

### Claude Code

To add the ADK docs MCP server to
[Claude Code](https://code.claude.com/docs/en/overview):

```bash
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt --transport stdio
```

### Cursor

To add the ADK docs MCP server to [Cursor](https://cursor.com/) (requires
[`uv`](https://docs.astral.sh/uv/)):

1. Open **Cursor Settings** and navigate to the **Tools & MCP** tab.
2. Click on **New MCP Server**, which will open `mcp.json` for editing.
3. Add the following to `mcp.json`:

    ```json
    {
      "mcpServers": {
        "adk-docs-mcp": {
          "command": "uvx",
          "args": [
            "--from",
            "mcpdoc",
            "mcpdoc",
            "--urls",
            "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
            "--transport",
            "stdio"
          ]
        }
      }
    }
    ```

### Other Tools

Any coding tool that supports MCP servers can use the same server configuration
shown above. Adapt the JSON example from the Antigravity or Cursor sections for
your tool's MCP settings.

## ADK Docs Index

The ADK documentation is available as machine-readable files following the
[`llms.txt` standard](https://llmstxt.org/). These files are generated with
every documentation update and are always up to date.

| File | Description | URL |
|------|-------------|-----|
| `llms.txt` | Documentation index with links | [`google.github.io/adk-docs/llms.txt`](https://google.github.io/adk-docs/llms.txt) |
| `llms-full.txt` | Full documentation in a single file | [`google.github.io/adk-docs/llms-full.txt`](https://google.github.io/adk-docs/llms-full.txt) |
