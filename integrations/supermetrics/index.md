# Supermetrics MCP tool for ADK

Supported in ADKPythonTypeScript

The [Supermetrics MCP Server](https://mcp.supermetrics.com) connects your ADK agent to the [Supermetrics](https://supermetrics.com/) platform, giving it access to marketing data across 100+ sources including Google Ads, Meta Ads, LinkedIn Ads, and Google Analytics 4. Your agent can discover data sources, explore available metrics, and run queries against your connected accounts using natural language.

## Use cases

- **Marketing Performance Reporting**: Query impressions, clicks, spend, and conversions across campaigns and time periods. Build automated reports that aggregate data from multiple platforms in a single response.
- **Cross-Platform Analysis**: Compare performance across Google Ads, Meta Ads, LinkedIn Ads, and other channels side by side, using a consistent query interface regardless of the underlying platform.
- **Campaign Monitoring**: Retrieve up-to-date metrics for active campaigns and ad accounts, enabling agents to surface anomalies, track pacing, or summarize daily performance.
- **Data Exploration**: Discover which data sources, accounts, and fields are available to a given user before building a query, so agents can adapt dynamically to each user's connected integrations.

## Prerequisites

- Create a [Supermetrics account](https://supermetrics.com/) (a 14-day free trial is created automatically on first login)
- Generate an API key from the [Supermetrics Hub](https://hub.supermetrics.com/)

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="supermetrics_agent",
    instruction="Help users query and analyze their marketing data from Supermetrics",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.supermetrics.com/mcp",
                headers={
                    "Authorization": f"Bearer {SUPERMETRICS_API_KEY}",
                },
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "supermetrics_agent",
    instruction: "Help users query and analyze their marketing data from Supermetrics",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.supermetrics.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${SUPERMETRICS_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```

Query workflow

Data retrieval follows a multi-step workflow: on a user request, first fetch the current date with `get_today`. Next discover a data source with `data_source_discovery`, find connected accounts with `accounts_discovery`, inspect available fields with `field_discovery`, submit a query with `data_query`, then poll `get_async_query_results` with the returned `schedule_id` until results are ready.

## Available tools

| Tool                      | Description                                                                      |
| ------------------------- | -------------------------------------------------------------------------------- |
| `data_source_discovery`   | List available marketing data sources (Google Ads, Meta Ads, etc.) and their IDs |
| `accounts_discovery`      | Discover connected accounts for a specific data source                           |
| `field_discovery`         | Explore available metrics and dimensions for a data source                       |
| `data_query`              | Submit a data query; returns a `schedule_id` for async result retrieval          |
| `get_async_query_results` | Poll for and retrieve the results of a submitted query by `schedule_id`          |
| `user_info`               | Retrieve the authenticated user's profile, team information, and license status  |
| `get_today`               | Get the current date in formats suitable for query date range parameters         |

## Additional resources

- [Supermetrics Hub](https://hub.supermetrics.com/)
- [Supermetrics Knowledge Base](https://docs.supermetrics.com/)
- [Data Source Documentation](https://docs.supermetrics.com/docs/connect)
- [OpenAPI Specification](https://mcp.supermetrics.com/openapi.json)
