# AgentQL

The [AgentQL MCP Server](https://github.com/tinyfish-io/agentql-mcp) connects
your ADK agent to [AgentQL](https://www.agentql.com/). AgentQL is a semantic
extraction engine that queries web elements based on their meaning rather than
their CSS or XPath selectors. This functionality allows agents to retrieve
specific data points from web pages, PDFs, and authenticated sessions using
natural language definitions.

## Use cases

- **Resilient Web Extraction**: Extract data from dynamic websites using natural
  language descriptions. This feature allows your agent to reliably gather
  information from sites that frequently update their layout or CSS without
  breaking.

- **Data Normalization**: Convert unstructured web pages into clean, predictable
  JSON formats. This capability enables your agent to instantly normalize data
  from different sources (like multiple job boards or shopping sites) into a
  single schema.

## Prerequisites

- Create an [API Key](https://dev.agentql.com/sign-in) in AgentQL. Refer to the
  [documentation](https://docs.agentql.com/quick-start) for more information.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    AGENTQL_API_KEY = "YOUR_AGENTQL_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="agentql_agent",
        instruction="Help users get information from AgentQL",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "agentql-mcp",
                        ],
                        env={
                            "AGENTQL_API_KEY": AGENTQL_API_KEY,
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

## Available tools

Tool <img width="100px"/> | Description
---- | -----------
`extract-web-data` | Extract structured data from a given 'url', using 'prompt' as a description of actual data and its fields to extract

## Best practices

To ensure accurate extraction, follow these guidelines when prompting the agent:

- **Describe the data, not the element**: Avoid visual descriptions (e.g., "the
  blue button"). Instead, describe the data entity (e.g., "the submit button" or
  "the product price").

- **Define the hierarchy**: If extracting a list, explicitly instruct the agent
  to look for a collection of items and define the fields required for each
  item.

- **Filter semantically**: You can instruct the tool to ignore specific data
  types (e.g., "exclude ads and navigation links") within the prompt itself.

## Additional resources

- [AgentQL MCP Server Documentation](https://docs.exa.ai/reference/exa-mcp)
- [AgentQL MCP Server Repository](https://github.com/tinyfish-io/agentql-mcp)
