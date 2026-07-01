# Coding with AI

You can use AI coding assistants to build agents with Agent Development Kit (ADK). Give your coding agent ADK expertise by installing development skills into your project, or by connecting it to ADK documentation through an MCP server.

- [**Agents CLI in Agent Platform**](#agents-cli): Command-line tool and coding skills for ADK development.
- [**ADK Docs MCP Server**](#adk-docs-mcp-server): Connect your coding tool to ADK documentation through an MCP server.
- [**ADK Docs Index**](#adk-docs-index): Machine-readable documentation files following the `llms.txt` standard.

## Agents CLI

The [Agents CLI](https://google.github.io/agents-cli/) tool set lets you plug ADK agent expertise into your favorite AI-coding environments including Antigravity, Claude Code, Cursor, and other AI coding tools. Install Agents CLI into your current AI-powered development environment to scaffold, build, test, evaluate, and deploy ADK agents. Enable your development environment with these Agents CLI Skills:

- Development lifecycle and coding guidelines
- Project scaffolding
- Evaluation methodology and scoring
- Agent Runtime, Cloud Run, and GKE deployment
- Gemini Enterprise agent publishing
- Trace, logging, and integrations
- Python API quick reference and docs index

To install Agents CLI and set up ADK development skills:

```bash
uvx google-agents-cli setup
```

For more information on installing Agents CLI and using it in your development environment, see the [Agents CLI documentation](https://google.github.io/agents-cli/).

## ADK Docs MCP Server

You can configure your coding tool to search and read ADK documentation using an MCP server. Below are setup instructions for popular tools.

### Antigravity

To add the ADK docs MCP server to [Antigravity](https://antigravity.google/) (requires [`uv`](https://docs.astral.sh/uv/)):

1. Open the MCP store via the **...** (more) menu at the top of the editor's agent panel.

1. Click on **Manage MCP Servers** then **View raw config**.

1. Add the following to `mcp_config.json`:

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
           "AgentDevelopmentKit:https://adk.dev/llms.txt",
           "--transport",
           "stdio"
         ]
       }
     }
   }
   ```

### Claude Code

To add the ADK docs MCP server to [Claude Code](https://code.claude.com/docs/en/overview):

```bash
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://adk.dev/llms.txt --transport stdio
```

### Cursor

To add the ADK docs MCP server to [Cursor](https://cursor.com/) (requires [`uv`](https://docs.astral.sh/uv/)):

1. Open **Cursor Settings** and navigate to the **Tools & MCP** tab.

1. Click on **New MCP Server**, which will open `mcp.json` for editing.

1. Add the following to `mcp.json`:

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
           "AgentDevelopmentKit:https://adk.dev/llms.txt",
           "--transport",
           "stdio"
         ]
       }
     }
   }
   ```

### Other Tools

Any coding tool that supports MCP servers can use the same server configuration shown above. Adapt the JSON example from the Antigravity or Cursor sections for your tool's MCP settings.

## ADK Docs Index

The ADK documentation is available as machine-readable files following the [`llms.txt` standard](https://llmstxt.org/). These files are generated with every documentation update and are always up to date.

| File            | Description                         | URL                                                      |
| --------------- | ----------------------------------- | -------------------------------------------------------- |
| `llms.txt`      | Documentation index with links      | [`adk.dev/llms.txt`](https://adk.dev/llms.txt)           |
| `llms-full.txt` | Full documentation in a single file | [`adk.dev/llms-full.txt`](https://adk.dev/llms-full.txt) |
