---
catalog_title: Fuse
catalog_description: Find and enrich B2B prospects, track buying signals, run outreach
catalog_icon: /integrations/assets/fuse.png
catalog_tags: ["mcp", "connectors"]
---

# Fuse MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Fuse MCP Server](https://github.com/fuse-ai-mcp/fuse) connects your ADK
agent to [Fuse](https://fuseai.com), a B2B sales platform for prospecting,
contact enrichment, buying signals, and outreach. This integration gives your
agent the ability to find people and companies, enrich contacts with work emails
and phone numbers, build lists, monitor buying signals, and draft email and
LinkedIn campaigns using natural language.

## How it works

Fuse hosts the MCP server at `https://mcp.fuseai.com`, so there is nothing to
install or run yourself. The server uses Streamable HTTP and OAuth 2.1 with
dynamic client registration and PKCE. You don't need an API key: you sign in
with your Fuse account, and every tool call runs in your own Fuse workspace.

1. **Connect**: Your agent starts the `mcp-remote` proxy, which connects to the
   Fuse MCP server. On first run, a browser window opens for you to sign in to
   Fuse and approve access.
2. **Discover**: The agent loads the Fuse tools, which cover prospect search,
   lists, enrichment, signals, research, campaigns, inbox, and CRM sync.
3. **Act**: The agent chains tools to complete a request, such as searching for
   people, saving them to a list, and enriching their contact details.

## Use cases

- **Prospect search**: Describe the people or companies you want to reach and
  let your agent turn that into search filters, run the search, and save the
  results to a list.

- **Contact enrichment**: Add verified work emails and phone numbers to the
  people on a list.

- **Buying signals**: Create signal agents that watch for funding
  announcements, job changes, hiring, and website visits, and turn new matches
  into leads.

- **Account research**: Research a company or contact before a call, or run a
  Deep Research job that produces a report and a prospect list.

- **Outreach**: Draft multi-step email and LinkedIn campaigns for a list.
  Campaigns are created as drafts and nothing is sent until you launch them.

## Prerequisites

- A [Fuse](https://fuseai.com) account. A free plan is available.
- For Python, ADK installed with MCP support: `pip install "google-adk[mcp]"`.
- [Node.js](https://nodejs.org/) installed, so that `npx` can run the
  [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) proxy, which handles
  the OAuth sign-in.
- Searches, enrichment, and research use your Fuse credits. See
  [Tools & limits](https://docs.fuseai.com/mcp/tools) for costs and rate limits.

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
            name="fuse_agent",
            instruction=(
                "You are a sales prospecting assistant. Help users find people "
                "and companies, enrich contacts, track buying signals, and draft "
                "outreach campaigns in Fuse. Confirm with the user before "
                "launching a campaign or sending a message."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.fuseai.com",
                            ],
                        ),
                        timeout=60,
                    ),
                )
            ],
        )
        ```

        !!! note

            When you run this agent for the first time, a browser window opens
            automatically to request access via OAuth. Alternatively, you can
            use the authorization URL printed in the console. Sign in with your
            Fuse account and approve the request to allow the agent to access
            your Fuse workspace.

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "fuse_agent",
            instruction:
                "You are a sales prospecting assistant. Help users find people " +
                "and companies, enrich contacts, track buying signals, and draft " +
                "outreach campaigns in Fuse. Confirm with the user before " +
                "launching a campaign or sending a message.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.fuseai.com",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            When you run this agent for the first time, a browser window opens
            automatically to request access via OAuth. Alternatively, you can
            use the authorization URL printed in the console. Sign in with your
            Fuse account and approve the request to allow the agent to access
            your Fuse workspace.

## Available tools

The Fuse MCP server exposes several hundred tools, grouped by area. The table
below lists a selection. See the
[Tool reference](https://docs.fuseai.com/mcp/tool-reference) for the full list.

Tool | Description
---- | -----------
`search_people` | Search the Fuse people database with structured filters
`search_companies` | Search the Fuse company database
`create_prospect_search_filters_tool` | Turn a natural-language description into prospect search filters
`save_people_to_list` | Save people found by a search, or named in the chat, to a list
`list_prospect_lists_tool` | List your prospect lists, including system lists such as website visitors
`get_prospect_list_rows_tool` | Read the rows of a list
`bulk_enrichment_tool` | Enrich the contacts on a list with work emails and phone numbers
`create_funding_announcement_monitor` | Create a signal agent that watches for funding announcements
`create_person_starting_new_job_monitor` | Create a signal agent that watches for people starting a new job
`lead_researcher_tool` | Research contacts and companies on the web and save them to a list
`deep_research_start` | Start a Deep Research run and return its run ID
`deep_research_status` | Check a Deep Research run and return the report when it completes
`initialize_campaign_tool` | Create a draft outreach campaign
`update_sequence_tool` | Edit the steps of a campaign sequence
`push_crm_contacts` | Push contacts to your connected CRM
`get_credits_balance` | Check your remaining Fuse credits

## Additional resources

- [Connect to the Fuse MCP server](https://docs.fuseai.com/mcp/connect)
- [Fuse MCP tools and limits](https://docs.fuseai.com/mcp/tools)
- [Fuse MCP Server on GitHub](https://github.com/fuse-ai-mcp/fuse)
- [Fuse API documentation](https://docs.fuseai.com)
