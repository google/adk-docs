---
catalog_title: SpecStream
catalog_description: Build lists from the live web, each row with its source
catalog_icon: /integrations/assets/specstream.png
catalog_tags: ["mcp", "data"]
---

# SpecStream MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [SpecStream MCP Server](https://specstream.ai/docs/mcp) connects your ADK
agent to [SpecStream](https://specstream.ai/), a service that builds lists from
the live web. Your agent describes the list in plain words, reviews the price,
and gets back every matching row with the page it was read from. SpecStream
charges per matching row, up to a maximum you approve before anything runs.

## Use cases

- **Build prospect and research lists**: Ask for "roofing companies in
  Columbus, Ohio with their website and phone" or "food banks in Texas with
  their annual revenue" and get all matching rows instead of a handful of
  search results.

- **Cite every fact**: Each row carries the source page and the time it was
  read, so your agent can show where a value came from.

- **Control spending**: Your agent reads the request back, gets a quote, and
  starts the work only after the quoted maximum is approved. A search that
  finds nothing costs nothing.

- **Keep lists current**: Schedule a list to rerun and report which rows
  changed.

- **Send results where people work**: Export a list as CSV, Excel, or JSON, or
  send it to Google Sheets, Notion, Airtable, HubSpot, or Salesforce.

## Prerequisites

- Create a [SpecStream account](https://specstream.ai/workspace). New accounts
  start with $10 of work free for 30 days, no card required.
- Create an API key under **Agents & API** in the workspace. Give it only the
  permissions the task needs (read, prepare, or execute), the projects it may
  use, an expiry, and a spending limit.
- Install the MCP client libraries with your ADK package:
    - Python: `pip install "google-adk[mcp]"`
    - TypeScript: `npm install @google/adk @modelcontextprotocol/sdk`

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        SPECSTREAM_API_KEY = "YOUR_SPECSTREAM_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="specstream_agent",
            instruction=(
                "Help users build lists from the live web with SpecStream. "
                "Read the request back, show the quoted price, and start work "
                "only after the user approves the maximum."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.specstream.ai/mcp",
                        headers={
                            "Authorization": f"Bearer {SPECSTREAM_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const SPECSTREAM_API_KEY = "YOUR_SPECSTREAM_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "specstream_agent",
            instruction:
                "Help users build lists from the live web with SpecStream. " +
                "Read the request back, show the quoted price, and start work " +
                "only after the user approves the maximum.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.specstream.ai/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${SPECSTREAM_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

Then ask your agent for a list, for example: "Find food banks in Texas with
their annual revenue."

## Available tools

The server exposes the full SpecStream workspace. These are the tools a list
request uses:

Tool | Description
---- | -----------
`compile` | Read a plain-English request and show the conditions, the facts to bring back, and the quantity
`edit_spec` | Change a condition or a fact to bring back without rewriting the request
`quote_capacity_work` | Get the price and the maximum for the exact request. Nothing runs
`authorize_capacity_work` | Approve a quote up to a maximum and start the work
`get_find` | Check the progress of a run
`list_find_rows` | Read the matching rows, each with its source
`export_find` | Create a download link for a finished list
`send_to_destination` | Send results to Google Sheets, Notion, Airtable, HubSpot, or Salesforce
`create_capacity_schedule` | Rerun a list on a schedule

## Configuration

The server offers many tools. To give your agent only the list workflow, pass a
tool filter. In Python, set `tool_filter` on `McpToolset`:

```python
McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://api.specstream.ai/mcp",
        headers={"Authorization": f"Bearer {SPECSTREAM_API_KEY}"},
    ),
    tool_filter=[
        "compile",
        "edit_spec",
        "quote_capacity_work",
        "authorize_capacity_work",
        "get_find",
        "list_find_rows",
        "export_find",
    ],
)
```

A key with only the read and prepare permissions can read and quote but cannot
start paid work, which suits an agent that should only prepare lists.

## Additional resources

- [SpecStream MCP documentation](https://specstream.ai/docs/mcp)
- [SpecStream tools on GitHub](https://github.com/specstream/specstream-tools)
- [SpecStream pricing](https://specstream.ai/pricing)
