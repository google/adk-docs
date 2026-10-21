# Coding with AI

You can use AI coding assistants to build agents with Agent Development Kit
(ADK). Give your coding agent ADK expertise by installing development skills
into your project, or by connecting it to ADK documentation through an MCP
server.

- [**Agents CLI in Agent Platform**](#agents-cli): Command-line tool and coding skills for ADK development.
- [**ADK Docs MCP Server**](#adk-docs-mcp-server): Connect your coding tool to
  ADK documentation through an MCP server.
- [**Google Developer Knowledge MCP Server**](#developer-knowledge-mcp-server):
  Search ADK documentation alongside other official Google developer docs
  through a remote MCP server and agent skill.
- [**ADK Docs Index**](#adk-docs-index): Machine-readable documentation files
  following the `llms.txt` standard.

## Agents CLI {#agents-cli}

The [Agents CLI](https://google.github.io/agents-cli/) tool set lets you plug
ADK agent expertise into your favorite AI-coding environments including
Antigravity, Claude Code, Cursor, and other AI coding tools. Install Agents CLI
into your current AI-powered development environment to scaffold, build, test,
evaluate, and deploy ADK agents. Enable your development environment with these
Agents CLI Skills:

*   Development lifecycle and coding guidelines
*   Project scaffolding
*   Evaluation methodology and scoring
*   Agent Runtime, Cloud Run, and GKE deployment
*   Gemini Enterprise agent publishing
*   Trace, logging, and integrations
*   Python API quick reference and docs index

To install Agents CLI and set up ADK development skills:

```bash
uvx google-agents-cli setup
```

For more information on installing Agents CLI and using it in your development
environment, see the
[Agents CLI documentation](https://google.github.io/agents-cli/).

## ADK Docs MCP Server

You can configure your coding tool to search and read ADK documentation using an
MCP server. Below are setup instructions for popular tools.

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
            "--with",
            "mcp<2",
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

To add the ADK docs MCP server to
[Claude Code](https://code.claude.com/docs/en/overview):

```bash
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc --with "mcp<2" mcpdoc --urls AgentDevelopmentKit:https://adk.dev/llms.txt --transport stdio
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
            "--with",
            "mcp<2",
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

!!! note "MCP version setting" 
    The `mcp<2` constraint setting keeps `mcpdoc` compatible with the MCP 1.x 
    FastMCP API it currently uses.

### Other Tools

Any coding tool that supports MCP servers can use the same server configuration
shown above. Adapt the JSON example from the Antigravity or Cursor sections for
your tool's MCP settings.

## Google Developer Knowledge MCP Server {#developer-knowledge-mcp-server}

The
[Developer Knowledge MCP server](https://developers.google.com/knowledge/mcp)
is a remote MCP server that searches the live, official documentation for
Google developer products, including ADK (`adk.dev`), Gemini API, Google Cloud,
and Firebase. Because ADK agents often combine these products, connecting your
coding tool to this server helps it answer questions and generate code from
current docs instead of stale training data or hallucinated APIs. The server
exposes the `search_documents`, `get_documents`, and `answer_query` tools.

Most tools, including Claude Code and Cursor, connect with an API key in the
`X-Goog-Api-Key` header. Add the following to your tool's MCP configuration:

```json
{
  "mcpServers": {
    "google-developer-knowledge": {
      "url": "https://developerknowledge.googleapis.com/mcp",
      "headers": { "X-Goog-Api-Key": "YOUR_API_KEY" }
    }
  }
}
```

Antigravity can instead install the server with Google credentials from its MCP
store. For API key setup and per-tool instructions, refer to
[Connect to the Developer Knowledge MCP server](https://developers.google.com/knowledge/mcp).

To teach your coding assistant when and how to use these tools, install the
[`retrieving-developer-knowledge`](https://github.com/google/skills/tree/main/skills/developers/retrieving-developer-knowledge)
agent skill, which works alongside the ADK skills from Agents CLI:

```bash
npx skills add google/skills --skill retrieving-developer-knowledge
```

With the server and skill in place, you can ask your coding assistant to ground
ADK tasks in the docs, for example:

```text
Look up how to add an MCP toolset to an ADK agent, then add a toolset for a
remote MCP server to my root agent.
```

## ADK Docs Index

The ADK documentation is available as machine-readable files following the
[`llms.txt` standard](https://llmstxt.org/). These files are generated with
every documentation update and are always up to date.

| File | Description | URL |
|------|-------------|-----|
| `llms.txt` | Documentation index with links | [`adk.dev/llms.txt`](https://adk.dev/llms.txt) |
| `llms-full.txt` | Full documentation in a single file | [`adk.dev/llms-full.txt`](https://adk.dev/llms-full.txt) |
