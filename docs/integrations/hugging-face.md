---
catalog_title: Hugging Face
catalog_description: Access models, datasets, research papers, and AI tools
catalog_icon: /integrations/assets/hugging-face.png
catalog_tags: ["mcp"]
---

# Hugging Face MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Hugging Face MCP Server](https://github.com/huggingface/hf-mcp-server) can be used to connect
your ADK agent to the Hugging Face Hub and thousands of Gradio AI Applications.

## Use cases

- **Discover AI/ML Assets**: Search and filter the Hub for models, datasets, and
  papers based on tasks, libraries, or keywords.
- **Build Multi-Step Workflows**: Chain tools together, such as transcribing
  audio with one tool and then summarizing the resulting text with another.
- **Find AI Applications**: Search for Gradio Spaces that can perform a specific
  task, like background removal or text-to-speech.

## Prerequisites

- Create a [user access token](https://huggingface.co/settings/tokens) in
  Hugging Face. Refer to the
  [documentation](https://huggingface.co/docs/hub/en/security-tokens) for more
  information.

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/hugging-face/001-use-with-agent.py"
        ```

    === "Remote MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/hugging-face/002-use-with-agent.py"
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/hugging-face/003-use-with-agent.ts"
        ```

    === "Remote MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/hugging-face/004-use-with-agent.ts"
        ```

## Available tools

Tool | Description
---- | -----------
Spaces Semantic Search | Find the best AI Apps via natural language queries
Papers Semantic Search | Find ML Research Papers via natural language queries
Model Search | Search for ML models with filters for task, library, etc…
Dataset Search | Search for datasets with filters for author, tags, etc…
Documentation Semantic Search | Search the Hugging Face documentation library
Hub Repository Details | Get detailed information about Models, Datasets and Spaces

## Configuration

To configure which tools are available in your Hugging Face Hub MCP server,
visit the [MCP Settings Page](https://huggingface.co/settings/mcp) in your
Hugging Face account.


To configure the local MCP server, you can use the following environment
variables:

- `TRANSPORT`: The transport type to use (`stdio`, `sse`, `streamableHttp`, or
  `streamableHttpJson`)
- `DEFAULT_HF_TOKEN`: ⚠️ Requests are serviced with the `HF_TOKEN` received in
  the Authorization: Bearer header. The DEFAULT_HF_TOKEN is used if no header
  was sent. Only set this in Development / Test environments or for local STDIO
  Deployments. ⚠️
- If running with stdio transport, `HF_TOKEN` is used if `DEFAULT_HF_TOKEN` is
  not set.
- `HF_API_TIMEOUT`: Timeout for Hugging Face API requests in milliseconds
  (default: 12500ms / 12.5 seconds)
- `USER_CONFIG_API`: URL to use for User settings (defaults to Local front-end)
- `MCP_STRICT_COMPLIANCE`: set to True for GET 405 rejects in JSON Mode (default
  serves a welcome page).
- `AUTHENTICATE_TOOL`: whether to include an Authenticate tool to issue an OAuth
  challenge when called
- `SEARCH_ENABLES_FETCH`: When set to true, automatically enables the
  hf_doc_fetch tool whenever hf_doc_search is enabled


## Additional resources

- [Hugging Face MCP Server Repository](https://github.com/huggingface/hf-mcp-server)
- [Hugging Face MCP Server Documentation](https://huggingface.co/docs/hub/en/hf-mcp-server)
