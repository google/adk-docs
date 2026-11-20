---
catalog_title: pipe0
catalog_description: Find people and companies and enrich them with contact data
catalog_icon: /integrations/assets/pipe0.png
catalog_tags: ["mcp", "data"]
---

# pipe0 MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [pipe0 MCP Server](https://www.pipe0.com/docs/sdks/mcp) connects your ADK
agent to [pipe0](https://www.pipe0.com/), a data enrichment platform for
go-to-market teams. Your agent can search for people and companies, then add
work emails, phone numbers, profiles, and firmographics to them. Enrichments
try data providers in order and stop at the first match, so one pipe0 account
covers many providers.

## Use cases

- **Build lead lists**: Search for people by job title, employer, seniority, and
  location, or for companies by industry, size, and location.

- **Enrich records**: Add work emails, mobile numbers, profiles, and
  company firmographics to people and companies your agent already has.

- **Keep lists up to date**: Save results to pipe0 sheets, schedule recurring
  runs, and route new leads to HubSpot, Salesforce, Attio, or Slack.

## Prerequisites

- A [pipe0 account](https://app.pipe0.com). Searches and enrichments spend
  credits. See [pricing](https://www.pipe0.com/pricing).
- ADK with MCP support: `pip install "google-adk[mcp]"` for Python, or
  `npm install @google/adk @modelcontextprotocol/sdk` for TypeScript.
- Node.js, which runs [`mcp-remote`](https://github.com/punkpeye/mcp-remote) to
  connect to the hosted server.

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-flash-latest",
            name="pipe0_agent",
            instruction="Help users find people and companies and enrich them with contact data using pipe0",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://api.pipe0.com/v1/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

        !!! note

            When you run this agent for the first time, a browser window opens
            automatically to request access via OAuth. Alternatively, you can use
            the authorization URL printed in the console. You must approve this
            request to allow the agent to access your pipe0 account.

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "pipe0_agent",
            instruction: "Help users find people and companies and enrich them with contact data using pipe0",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "mcp-remote", "https://api.pipe0.com/v1/mcp"],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            When you run this agent for the first time, a browser window opens
            automatically to request access via OAuth. Alternatively, you can use
            the authorization URL printed in the console. You must approve this
            request to allow the agent to access your pipe0 account.

## Available tools

Tool | Description
---- | -----------
`list_searches` | Find searches that return people or companies matching criteria
`get_search_schema` | Get a search's input schema and example payloads
`run_search_oneshot` | Run a search once and return the matching records
`list_pipes` | Find enrichment pipes, such as work email, phone, or company data
`get_pipe_schema` | Get a pipe's input schema and example payloads
`run_pipes_oneshot` | Run enrichment pipes over up to 100 records and return the results
`check_run_status` | Check the status of a one-off search or enrichment run
`autocomplete_field` | List valid values for a config field, such as locations or industries
`get_provider_context` | Fetch live context from a connected provider for a configured pipe or search
`list_playbooks` | Find recipes that map a goal to a tested chain of searches and pipes
`get_playbook` | Get a playbook's steps, variants, and an example chain
`get_guide` | Read a workflow guide on demand
`list_connections` | List the provider and CRM connections your team has set up
`list_secrets` | List secret names your team has stored (never their values)
`list_sheets` | List your team's sheets
`create_sheet` | Create a sheet whose columns are filled by pipes
`get_sheet_schema` | Get the open sheet's columns, pipes, and row count
`get_sheet_rows` | Read rows from the open sheet
`get_field_values` | Read the full value of specific cells
`list_effects` | Find effects, the operations that change a sheet
`get_effect_schema` | Get an effect's input schema and an example payload
`validate_effects` | Check a chain of effects against the open sheet without changing it
`run_effects` | Run a chain of effects on the open sheet
`wait_for_run` | Wait for an effect run to finish and return its outcome
`cancel_effect_run` | Cancel a running effect run
`get_recent_effects` | List recent effect runs on the open sheet and their status
`verify_outcome` | Measure how well a finished run filled the target fields
`list_buckets` | List stores used for deduplication, counters, and suppression lists
`create_report` | Create a report that lives next to a project's sheets
`read_report` | Read the active report's content and recent versions
`list_schedules` | List your team's recurring workflows
`create_schedule` | Schedule a workflow to run on a recurring cron
`update_schedule` | Change a schedule's cron, timezone, name, or enabled state
`delete_schedule` | Delete a schedule and stop its recurring workflow
`list_folders` | List your team's folders and the projects in them
`organize_folders` | Create, rename, move, and delete folders and projects

## Additional resources

- [pipe0 MCP Server Documentation](https://www.pipe0.com/docs/sdks/mcp)
- [pipe0 Documentation](https://www.pipe0.com/docs)
