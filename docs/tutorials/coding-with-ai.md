# Coding with AI

The Agent Development Kit (ADK) documentation supports the
[`/llms.txt`](https://llmstxt.org/) standard, providing a machine-readable index
of the documentation optimized for Large Language Models (LLMs). This allows you
to easily use the ADK documentation as context in your AI-powered development
environment.

## What is llms.txt?

`llms.txt` is a standardized text file that acts as a map for LLMs, listing the
most important documentation pages and their descriptions. This helps AI tools
understand the structure of the ADK documentation and retrieve relevant
information to answer your questions.

The ADK documentation provides two files:

File | Best For... | URL
---- | ----------- | ---
**`llms.txt`** | Tools that can fetch links dynamically | `https://google.github.io/adk-docs/llms.txt`
**`llms-full.txt`** | Tools that need a single, static text dump of the entire site | `https://google.github.io/adk-docs/llms-full.txt`

## Usage in Development Tools

You can use these files to power your AI coding assistants with ADK knowledge.
This functionality allows your agents to autonomously search and read the ADK
documentation while planning tasks and generating code.

### Gemini CLI

The [Gemini CLI](https://geminicli.com/) can be configured to query the ADK
documentation using the
[ADK Docs Extension](https://github.com/derailed-dash/adk-docs-ext).

**Installation:**

To install the extension, run the following command:

```bash
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

**Usage:**

Once installed, the extension is automatically enabled. You can ask questions
about ADK directly in the Gemini CLI, and it will use the `llms.txt` file and
ADK documentation to provide accurate answers and generate code.

For example, you can ask the following question from within Gemini CLI:

```
How do I create a function tool using Agent Development Kit?
```

### Antigravity

The [Antigravity](https://antigravity.google/) IDE can be configured to access
the ADK documentation by running a custom MCP server that points to the
`llms.txt` file for ADK.

**Prerequisites:**

Ensure you have the [`uv`](https://docs.astral.sh/uv/) tool installed, as this
configuration uses `uvx` to run the documentation server without manual
installation.

**Configuration:**

1. Open the MCP store via the **...** (more) menu at the top of the editor's
   agent panel.
2. Click on **Manage MCP Servers**
3. Click on **View raw config**
4. Add the following entry to `mcp_config.json` with your custom MCP server
   configuration. If this is your first MCP server, you can paste the entire
   code block:

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

Refer to the [Antigravity MCP](https://antigravity.google/docs/mcp)
documentation for more information on managing MCP servers.

**Usage:**

Once configured, you can prompt the coding agent with instructions like:

```
Use the ADK docs to build a multi-tool agent that uses Gemini 2.5 Pro and
includes a mock weather lookup tool and a custom calculator tool. Verify the
agent using `adk run`.
```

### Other Tools

Any tool that supports the `llms.txt` standard or can ingest documentation from
a URL can benefit from these files. You can provide the URL
`https://google.github.io/adk-docs/llms.txt` (or `llms-full.txt`) to your tool's
knowledge base configuration or MCP server configuration.
