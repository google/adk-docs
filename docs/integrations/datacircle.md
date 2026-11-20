---
catalog_title: Datacircle
catalog_description: Find the best GTM APIs: compare the plans, prices and speeds of every GTM API we benchmark
catalog_icon: /integrations/assets/datacircle.png
catalog_tags: ["data", "mcp"]
---

# Datacircle MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Datacircle MCP server](https://datacircle.dev/docs/mcp) connects your ADK
agent to [Datacircle](https://datacircle.dev). Find the best GTM APIs. We
benchmark all the GTM APIs and we put the results on our website. The server is
open to anyone, with no key.

The server is hosted at `https://api.datacircle.dev/mcp` over streamable HTTP,
so there is nothing to install on the server side. It answers from the sheet:
every GTM API we find, one row for each plan of each call, with what it costs
per 1,000, what it charges when it finds nothing, its rate limits, its speed and
the fields it returns.

## Use cases

- **Choose an API**: Ask which API to use for a job, such as finding a person's
  work email or checking a phone number, and get the plans that do it, the best
  first, each with its score out of 100.

- **Compare prices**: Compare what each plan costs per 1,000 calls and what it
  charges when it finds nothing, before you build on one.

- **Check limits and speed**: Read each plan's rate limits, its speed and the
  fields it returns, with the pages each row was read from.

## Prerequisites

- ADK with its MCP extra, without which the MCP classes are not importable:

    ```bash
    pip install "google-adk[mcp]"
    ```

- No account and no API key: the server is open to anyone.

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="datacircle_agent",
            instruction="Help users find the best GTM API for a job, using Datacircle",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.datacircle.dev/mcp",
                    ),
                )
            ],
        )
        ```

Then ask the agent, for example: "Which API finds a person's work email for
the lowest price per 1,000?"

## Available tools

Tool | Description
---- | -----------
`list_apis` | List the APIs on Datacircle's sheet, with the number of plans and providers for each
`search_plans` | Find plans by API, provider or price; each row has its provider, plan, price per 1,000, score out of 100, rate limits, speed and the fields it returns

## Additional resources

- [Datacircle MCP server documentation](https://datacircle.dev/docs/mcp)
- [Datacircle](https://datacircle.dev)
- [The sheet as a file](https://datacircle.dev/datacircle.json)
