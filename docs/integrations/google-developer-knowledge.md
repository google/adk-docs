---
catalog_title: Google Developer Knowledge
catalog_description: Give your agents the ability to search Google's official developer documentation and retrieve code and guidance.
catalog_icon: /adk-docs/integrations/assets/google-developer-knowledge.png
catalog_tags: ["mcp"]
---

# Google Developer Knowledge

The Google Developer Knowledge MCP server provides programmatic access to Google's public developer documentation, enabling you to integrate this knowledge base into your own applications and workflows. By connecting your AI application straight to Google's official library of documentation, it ensures the code and guidance you receive are up-to-date and based on authoritative context.

## Use cases

- **Implementation guidance**: Ask for the best way to implement specific features (e.g., push notifications using Firebase Cloud Messaging).
- **Code generation and explanation**: Search documentation for code examples, such as listing all buckets in a Cloud Storage project in Python.
- **Troubleshooting and debugging**: Query error messages or API key watermarks to quickly resolve issues.
- **Comparative analysis and summarization**: Create comparisons between services like Cloud Run and Cloud Functions.

## Prerequisites

- A [Google Cloud project](https://developers.google.com/workspace/guides/create-project)
- [Developer Knowledge API enabled](https://console.cloud.google.com/start/api?id=developerknowledge.googleapis.com)
- Completed [Authentication Configuration](https://developers.google.com/knowledge/mcp#authentication) (OAuth or API Key)

## Installation

You must enable the Developer Knowledge MCP server in your Google Cloud Project. Please refer to the official [Installation Guide](https://developers.google.com/knowledge/mcp#installation) for the precise `gcloud` command and instructions.

You'll also need to configure your AI tool (e.g., Gemini CLI, Cursor, Windsurf, or Antigravity) with your chosen authentication headers. Detailed instructions for configuring each editor can be found in the [Editor Configuration Guide](https://developers.google.com/knowledge/mcp#configuration).

## Use with agent

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
    
    API_KEY = "YOUR_DEVELOPER_KNOWLEDGE_API_KEY"
    
    root_agent = Agent(
        model="gemini-2.5-pro",
        name="google_knowledge_agent",
        instruction="Search Google developer documentation for implementation guidance.",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://developerknowledge.googleapis.com/mcp",
                    headers={"X-Goog-Api-Key": API_KEY},
                    timeout=30.0,
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const API_KEY = "YOUR_DEVELOPER_KNOWLEDGE_API_KEY";

    const rootAgent = new LlmAgent({
        model: "gemini-2.5-pro",
        name: "google_knowledge_agent",
        instruction: "Search Google developer documentation for implementation guidance.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://developerknowledge.googleapis.com/mcp",
                transportOptions: {
                    requestInit: {
                        headers: {
                            "X-Goog-Api-Key": API_KEY,
                        },
                    },
                },
            }),
        ],
    });

    export { rootAgent };
    ```

## Available tools

| Tool name | Description |
|---|---|
| `search_documents` | Searches Google's developer documentation to find relevant pages and snippets for your query |
| `get_documents` | Retrieves the full page content of multiple documents using the parent reference from search results |

## Resources

- [Developer Knowledge MCP Documentation](https://developers.google.com/knowledge/mcp)
- [Developer Knowledge API Reference](https://developers.google.com/knowledge/api)
- [Corpus Reference](https://developers.google.com/knowledge/reference/corpus-reference)
