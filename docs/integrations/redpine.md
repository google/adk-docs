---
catalog_title: Redpine
catalog_description: Answers grounded in licensed publisher content, cited to the source
catalog_icon: /integrations/assets/redpine.png
catalog_tags: ["mcp", "search"]
---

# Redpine MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Redpine MCP Server](https://docs.redpine.ai/docs/mcp) connects your ADK
agent to licensed publisher content. Your agent searches it, reads the passages
that answer a question, and cites each result back to its source. Publishers
are paid when their content is used.

## Use cases

- **Ground answers in the source**: Retrieve the passages behind a claim and
  return them with citation metadata, so every statement can be traced.

- **Check a claim**: Search for evidence for and against a statement, and
  report where the available literature does not cover it.

- **Preview before paying**: See matching results and their price before
  unlocking full passages, and unlock only the ones that answer the question.

## Prerequisites

- ADK installed with the `mcp` extra: `pip install "google-adk[mcp]"`. Without
  the extra, ADK's MCP classes are not importable.
- A [Redpine](https://app.redpine.ai) account
- An API key, created in the Redpine dashboard under **API Keys**

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        REDPINE_API_KEY = os.environ["REDPINE_API_KEY"]

        root_agent = Agent(
            model="gemini-flash-latest",
            name="redpine_agent",
            instruction=(
                "Answer questions using Redpine. Preview results before unlocking "
                "anything, ask the user before spending credits, and cite every "
                "source you use."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.redpine.ai/mcp",
                        headers={"Authorization": f"Bearer {REDPINE_API_KEY}"},
                    ),
                )
            ],
        )
        ```

!!! note

    Previewing results is free and shows the price first. Unlocking results
    spends credits from your Redpine balance, so have your agent ask before
    it spends.

## Available tools

Tool | Description
---- | -----------
`search-redpine-science` | Search the Redpine Science collection of open-access research
`preview` | Run a search and return a teaser plus the cost to unlock the full results, free of charge
`confirm` | Unlock the full results of a previous preview, charging the approved amount
`get_balance` | Check the current credit balance and trial status
`find-tools` | Discover the other tools this account can reach
`inspect-tool` | Return the full argument schema for one of those tools
`call-tool` | Execute a tool found through `find-tools` by name
`request_journal` | Record a request for a journal or publisher that Redpine does not yet cover

The search tools an agent sees depend on the collections its account can
access, so an account with access to more collections is offered more of them.
Use the [ADK Web UI](/runtime/web-interface/) to view the tools in the trace
graph.

## Additional resources

- [Redpine MCP documentation](https://docs.redpine.ai/docs/mcp)
- [Redpine authentication](https://docs.redpine.ai/docs/authentication)
- [Redpine dashboard](https://app.redpine.ai)
