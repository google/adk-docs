# Exa

The [Exa MCP Server](https://github.com/github/github-mcp-server) connects your
ADK agent to [Exa's search engine](https://exa.ai), a platform built
specifically for AI. This gives your agent the ability to search for relevant
webpages, find similar content based on a link, retrieve clean, parsed content
from URLs, get direct answers to questions, and automate in-depth research
reports using natural language.

## Use cases

- **Find Code & Technical Examples**: Search across GitHub, documentation, and
  technical forums to find up-to-date code snippets, API usage patterns, and
  implementation examples.

- **Perform In-Depth Research**: Launch comprehensive research reports on
  complex topics, gather detailed information on companies, or find professional
  profiles on LinkedIn.

- **Access Real-Time Web Content**: Perform general web searches to get
  up-to-date information or extract the full content from specific articles,
  blog posts, or web pages.

## Prerequisites

- Create an [API Key](https://dashboard.exa.ai/api-keys) in Exa. Refer to the
  [documentation](https://docs.exa.ai/reference/quickstart) for more
  information.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    EXA_API_KEY = "YOUR_EXA_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="exa_agent",
        instruction="Help users get information from Exa",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "exa-mcp-server",
                            # (Optional) Specify which tools to enable
                            # If you don't specify any tools, all tools enabled by default will be used.
                            # "--tools=get_code_context_exa,web_search_exa",
                        ],
                        env={
                            "EXA_API_KEY": EXA_API_KEY,
                        }
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

=== "Remote MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

    EXA_API_KEY = "YOUR_EXA_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="exa_agent",
        instruction="""Help users get information from Exa""",
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://mcp.exa.ai/mcp?exaApiKey=" + EXA_API_KEY,
                    # (Optional) Specify which tools to enable
                    # If you don't specify any tools, all tools enabled by default will be used.
                    # url="https://mcp.exa.ai/mcp?exaApiKey=" + EXA_API_KEY + "&enabledTools=%5B%22crawling_exa%22%5D",
                ),
            )
        ],
    )
    ```

## Available tools

Tool <img width="400px"/> | Description
---- | -----------
`get_code_context_exa` | Search and get relevant code snippets, examples, and documentation from open source libraries, GitHub repositories, and programming frameworks. Perfect for finding up-to-date code documentation, implementation examples, API usage patterns, and best practices from real codebases.
`web_search_exa` | Performs real-time web searches with optimized results and content extraction.
`company_research` | Comprehensive company research tool that crawls company websites to gather detailed information about businesses.
`crawling` | Extracts content from specific URLs, useful for reading articles, PDFs, or any web page when you have the exact URL.
`linkedin_search` | Search LinkedIn for companies and people using Exa AI. Simply include company names, person names, or specific LinkedIn URLs in your query.
`deep_researcher_start` | Start a smart AI researcher for complex questions. The AI will search the web, read many sources, and think deeply about your question to create a detailed research report.
`deep_researcher_check` | Check if your research is ready and get the results. Use this after starting a research task to see if it's done and get your comprehensive report.

## Configuration

To specify which tools to use in the Local Exa MCP server, you can use the
`--tools` parameter:

```
--tools=get_code_context_exa,web_search_exa,company_research,crawling,linkedin_search,deep_researcher_start,deep_researcher_check
```

To specify which tools to use in the Remote Exa MCP server, you can use the
`enabledTools` URL parameter:

```
https://mcp.exa.ai/mcp?exaApiKey=YOUREXAKEY&enabledTools=%5B%22crawling_exa%22%5D
```

## Additional resources

- [Exa MCP Server Documentation](https://docs.exa.ai/reference/exa-mcp)
- [Exa MCP Server Repository](https://github.com/exa-labs/exa-mcp-server)
