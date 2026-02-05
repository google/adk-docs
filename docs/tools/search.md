# Search Tools in ADK

ADK offers different tools for performing searches, each tailored for specific use cases. Understanding the differences between them will help you choose the right tool for your agent.

## Google Search

The `google_search` tool is a built-in tool that allows your agent to perform searches using Google Search. This tool is ideal for agents that need to access up-to-date information from the web to answer questions or perform tasks.

- **Use case:** General web search for grounding Gemini models.
- **Tool name:** `google_search`
- **Compatibility:** Gemini models

For more details, see [Google Search](gemini-api/google-search.md).

## Enterprise Web Search

The `EnterpriseWebSearchTool` is a built-in tool that uses web grounding for Enterprise compliance. It is part of Vertex AI and is designed for enterprise-grade applications that require grounding with web content while adhering to enterprise policies.

- **Use case:** Web grounding for Enterprise compliance with Gemini 2+ models.
- **Tool name:** `EnterpriseWebSearchTool`
- **Compatibility:** Gemini 2+ models

**Note:** `EnterpriseWebSearchTool` is not the same as Vertex AI Search.

For more details, see the [`EnterpriseWebSearchTool` documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/web-grounding-enterprise).

## Choosing the Right Tool

| Tool | Use Case | Compatibility |
|---|---|---|
| `google_search` | General web search for grounding Gemini models. | Gemini models |
| `EnterpriseWebSearchTool` | Web grounding for Enterprise compliance. | Gemini 2+ models |

- Use the `google_search` tool when your agent needs to perform general web searches to answer questions or stay up-to-date with the latest information.
- Use the `EnterpriseWebSearchTool` when you are building enterprise applications that require web grounding with compliance and control.
