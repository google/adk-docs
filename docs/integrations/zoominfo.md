---
catalog_title: ZoomInfo
catalog_description: Find companies, enrich contacts, and surface go-to-market intelligence
catalog_icon: /integrations/assets/zoominfo.png
catalog_tags: ["mcp", "connectors"]
---

# ZoomInfo MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [ZoomInfo MCP Server](https://docs.zoominfo.com/docs/zi-api-mcp-overview)
connects your ADK agent to the [ZoomInfo](https://www.zoominfo.com/) B2B
intelligence platform, giving it access to 100M+ company profiles, 300M+
professional contacts, and go-to-market signals. This integration gives your
agent the ability to find prospects, enrich records, surface intent signals, and
research accounts using natural language.

## Use cases

- **Prospect Discovery**: Find companies and contacts matching your ICP using
  filters like industry, location, company size, job title, seniority, and tech
  stack.

- **Account & Contact Enrichment**: Append verified firmographic and demographic
  data — revenue, headcount, emails, direct dials, and funding — to existing
  records inside agent workflows.

- **Go-to-Market Signal Detection**: Surface intent signals, leadership changes,
  and strategic scoops to reach buyers at the right moment.

## Prerequisites

- Sign up for a [ZoomInfo
  account](https://www.zoominfo.com/free-trial-contact-sales)
- A ZoomInfo SalesOS or Copilot subscription

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
            name="zoominfo_agent",
            instruction="Help users find companies, enrich contacts, and surface go-to-market insights using ZoomInfo",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.zoominfo.com/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "zoominfo_agent",
            instruction: "Help users find companies, enrich contacts, and surface go-to-market insights using ZoomInfo",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.zoominfo.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    When you run this agent for the first time, a browser window opens
    automatically to request access via OAuth. Alternatively, you can use the
    authorization URL printed in the console. You must approve this request to
    allow the agent to access your ZoomInfo data.

## Available tools

Tool | Description
---- | -----------
`search_companies` | Search ZoomInfo's company database by name, industry, location, employee count, revenue, tech stack, growth metrics, and funding information
`search_contacts` | Search ZoomInfo's contact database by name, job title, management level, department, company, location, and accuracy score
`enrich_companies` | Get complete company profiles — revenue, headcount, funding, tech stack, corporate structure, and more — for up to 10 companies per call
`enrich_contacts` | Get verified business contact details — email, phone, job title, employment history, and accuracy scores — for up to 10 contacts per call
`find_similar_companies` | Find companies similar to a reference company using ML-based firmographic matching, useful for lookalike prospecting and territory expansion
`find_similar_contacts` | Find contacts similar to a reference person, optionally constrained to a target company, using ML-based persona matching
`get_recommended_contacts` | Get AI-ranked contact recommendations at a target company based on your sales motion — PROSPECTING, DEAL_ACCELERATION, or RENEWAL_AND_GROWTH
`search_intent` | Search for companies actively researching specific topics across ZoomInfo's database, with signal score and audience strength filters
`enrich_intent` | Get buyer intent signals for a specific company — topics researched, signal scores, audience strength, and duration
`search_scoops` | Search for real-time business intelligence signals — leadership changes, funding events, product launches, partnerships, and more — across all companies
`enrich_scoops` | Get the latest scoops for a specific company — the full context behind the signal, not just the headline
`enrich_news` | Get recent news coverage for a specific company, filterable by category such as funding, M&A, executive moves, and product launches
`account_research` | Get AI-generated strategic intelligence on a company — overview, financials, competitors, buying committee, deal health, and engagement activity
`contact_research` | Get AI-generated professional background on a specific person — career history, expertise, CRM records, and outreach context
`lookup` | Retrieve standardized reference data for use in search filters — industries, management levels, metro regions, tech products, intent topics, and more
`submit_feedback` | Submit feedback on ZoomInfo MCP tools covering data quality, feature requests, access issues, or other topics

## Additional resources

- [ZoomInfo MCP Overview](https://docs.zoominfo.com/docs/zi-api-mcp-overview)
- [ZoomInfo Developer Documentation](https://docs.zoominfo.com/)
