# Coding with AI

The Agent Development Kit (ADK) documentation supports the [`/llms.txt` standard](https://llmstxt.org/), providing a machine-readable index of the documentation optimized for Large Language Models (LLMs). This allows you to easily use the ADK documentation as context in your AI-powered development environment.

## What is llms.txt?

`llms.txt` is a standardized text file that acts as a map for LLMs, listing the most important documentation pages and their descriptions. This helps AI tools understand the structure of the ADK documentation and retrieve relevant information to answer your questions.

The ADK documentation provides the following files that are automatically generated with every update:

| File                | Best For...                                                   | URL                                                                                                  |
| ------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **`llms.txt`**      | Tools that can fetch links dynamically                        | [`https://google.github.io/adk-docs/llms.txt`](https://google.github.io/adk-docs/llms.txt)           |
| **`llms-full.txt`** | Tools that need a single, static text dump of the entire site | [`https://google.github.io/adk-docs/llms-full.txt`](https://google.github.io/adk-docs/llms-full.txt) |

## Usage in Development Tools

You can use these files to power your AI coding assistants with ADK knowledge. This functionality allows your agents to autonomously search and read the ADK documentation while planning tasks and generating code.

### Gemini CLI

The [Gemini CLI](https://geminicli.com/) can be configured to query the ADK documentation using the [ADK Docs Extension](https://github.com/derailed-dash/adk-docs-ext).

**Installation:**

To install the extension, run the following command:

```bash
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

**Usage:**

Once installed, the extension is automatically enabled. You can ask questions about ADK directly in the Gemini CLI, and it will use the `llms.txt` file and ADK documentation to provide accurate answers and generate code.

For example, you can ask the following question from within Gemini CLI:

> How do I create a function tool using Agent Development Kit?

______________________________________________________________________

### Antigravity

The [Antigravity](https://antigravity.google/) IDE can be configured to access the ADK documentation by running a custom MCP server that points to the `llms.txt` file for ADK.

**Prerequisites:**

Ensure you have the [`uv`](https://docs.astral.sh/uv/) tool installed, as this configuration uses `uvx` to run the documentation server without manual installation.

**Configuration:**

1. Open the MCP store via the **...** (more) menu at the top of the editor's agent panel.

1. Click on **Manage MCP Servers**.

1. Click on **View raw config**.

1. Add the following entry to `mcp_config.json` with your custom MCP server configuration. If this is your first MCP server, you can paste the entire code block:

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

Refer to the [Antigravity MCP documentation](https://antigravity.google/docs/mcp) for more information on managing MCP servers.

**Usage:**

Once configured, you can prompt the coding agent with instructions like:

> Use the ADK docs to build a multi-tool agent that uses Gemini 2.5 Pro and includes a mock weather lookup tool and a custom calculator tool. Verify the agent using `adk run`.

______________________________________________________________________

### Claude Code

[Claude Code](https://code.claude.com/docs/en/overview) can be configured to query the ADK documentation by adding an [MCP server](https://code.claude.com/docs/en/mcp).

**Installation:**

To add an MCP server for the ADK docs to Claude Code, run the following command:

```bash
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt --transport stdio
```

**Usage:**

Once installed, the MCP server is automatically enabled. You can ask questions about ADK directly in Claude Code, and it will use the `llms.txt` file and ADK documentation to provide accurate answers and generate code.

For example, you can ask the following question from within Claude Code:

> How do I create a function tool using Agent Development Kit?

______________________________________________________________________

### Cursor

The [Cursor](https://cursor.com/) IDE can be configured to access the ADK documentation by running a custom MCP server that points to the `llms.txt` file for ADK.

**Prerequisites:**

Ensure you have the [`uv`](https://docs.astral.sh/uv/) tool installed, as this configuration uses `uvx` to run the documentation server without manual installation.

**Configuration:**

1. Open **Cursor Settings** and navigate to the **Tools & MCP** tab.

1. Click on **New MCP Server**, which will open `mcp.json` for editing.

1. Add the following entry to `mcp.json` with your custom MCP server configuration. If this is your first MCP server, you can paste the entire code block:

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

Refer to the [Cursor MCP documentation](https://cursor.com/docs/context/mcp) for more information on managing MCP servers.

**Usage:**

Once configured, you can prompt the coding agent with instructions like:

> Use the ADK docs to build a multi-tool agent that uses Gemini 2.5 Pro and includes a mock weather lookup tool and a custom calculator tool. Verify the agent using `adk run`.

______________________________________________________________________

### Other Tools

Any tool that supports the `llms.txt` standard or can ingest documentation from a URL can benefit from these files. You can provide the URL `https://google.github.io/adk-docs/llms.txt` (or `llms-full.txt`) to your tool's knowledge base configuration or MCP server configuration.
