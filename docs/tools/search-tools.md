# Choosing the Right Search Tool

The ADK provides several tools for grounding your agents with information from the web. Choosing the right tool is important for getting the best results. This guide explains the differences between the available search tools and helps you decide which one to use.

## Google Search (`google_search`)

The `google_search` tool is a built-in tool that uses Google Search to ground your agent's responses. It is a general-purpose search tool that is suitable for a wide range of applications.

Use the `google_search` tool when:

*   You need to ground your agent with up-to-date information from the web.
*   You are building a general-purpose agent that needs to answer questions about a variety of topics.
*   You are using a Gemini model.

## Enterprise Web Search (`EnterpriseWebSearchTool`)

The `EnterpriseWebSearchTool` is a specialized tool for grounding your agent with information from the web while ensuring enterprise compliance. This tool is designed for use cases where you need to control the source of information and ensure that the grounding data comes from trusted sources.

**Note:** The `EnterpriseWebSearchTool` is not the same as Vertex AI Search.

Use the `EnterpriseWebSearchTool` when:

*   You are building an enterprise-grade agent that requires grounding with vetted web content.
*   You need to ensure that the grounding data is compliant with your organization's policies.
*   You are using a Gemini 2+ model.

## Comparison

| Feature                      | `google_search`                               | `EnterpriseWebSearchTool`                       |
| ---------------------------- | --------------------------------------------- | ----------------------------------------------- |
| **Use Case**                 | General web search                            | Enterprise-compliant web search                 |
| **Compatibility**            | Gemini models                                 | Gemini 2+ models                                |
| **Configuration**            | `types.Tool(google_search=types.GoogleSearch())` | `types.Tool(enterprise_web_search=types.EnterpriseWebSearch())` |

## How to choose

*   For most general-purpose applications, the `google_search` tool is the recommended choice.
*   If you are building an enterprise application and need to ensure compliance and control over the grounding sources, use the `EnterpriseWebSearchTool`.