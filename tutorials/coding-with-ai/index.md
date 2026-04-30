# Coding with AI

You can use AI coding assistants to build agents with Agent Development Kit (ADK). Give your coding agent ADK expertise by installing development skills into your project, or by connecting it to ADK documentation through an MCP server.

- [**Agents CLI in Agent Platform**](#agents-cli): Command-line tool and coding skills for ADK development.
- [**ADK Docs MCP Server**](#adk-docs-mcp-server): Connect your coding tool to ADK documentation through an MCP server.
- [**ADK Docs Index**](#adk-docs-index): Machine-readable documentation files following the `llms.txt` standard.

## agents-cli

[Agents CLI in Agent Platform](https://google.github.io/agents-cli/) is the command-line tool for ADK development. It provides scaffolding commands, deployment tools, and development skills that work with any compatible coding assistant, including Gemini CLI, Antigravity, Claude Code, and Cursor.

To install Agents CLI and set up ADK development skills:

```bash
uvx google-agents-cli setup
```

This installs both the CLI and coding skills. Browse the [Agents CLI documentation](https://google.github.io/agents-cli/) for more details.

### CLI Commands

| Command                       | Description                                |
| ----------------------------- | ------------------------------------------ |
| `agents-cli scaffold create`  | Create a new ADK agent project             |
| `agents-cli scaffold enhance` | Add deployment to existing project         |
| `agents-cli eval`             | Run agent evaluations                      |
| `agents-cli deploy`           | Deploy to Agent Runtime, Cloud Run, or GKE |
| `agents-cli publish`          | Publish to Gemini Enterprise               |

### Development Skills

After setup, the following skills are available in your coding tool:

| Skill                             | Description                                  |
| --------------------------------- | -------------------------------------------- |
| `google-agents-cli-workflow`      | Development lifecycle and coding guidelines  |
| `google-agents-cli-adk-code`      | Python API quick reference and docs index    |
| `google-agents-cli-scaffold`      | Project scaffolding                          |
| `google-agents-cli-eval`          | Evaluation methodology and scoring           |
| `google-agents-cli-deploy`        | Agent Runtime, Cloud Run, and GKE deployment |
| `google-agents-cli-publish`       | Gemini Enterprise registration               |
| `google-agents-cli-observability` | Tracing, logging, and integrations           |

## ADK Docs MCP Server

You can configure your coding tool to search and read ADK documentation using an MCP server. Below are setup instructions for popular tools.

### Gemini CLI

To add the ADK docs MCP server to [Gemini CLI](https://geminicli.com/), install the [ADK Docs Extension](https://github.com/derailed-dash/adk-docs-ext):

```bash
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

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
