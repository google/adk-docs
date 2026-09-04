# Grafana Cloud MCP tool for ADK

Supported in ADKPythonTypeScript

The [Grafana Cloud MCP server](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/) connects ADK agents directly to your Grafana Cloud observability stack. Your agent can query Prometheus metrics, search logs in Loki, trace requests with Tempo, browse dashboards, manage alerts and incidents, and more, with over 60 tools available.

The server is fully hosted and requires no local installation, Docker containers, or service account tokens. Authentication uses OAuth 2.1 with user-scoped permissions through Grafana RBAC.

## Use cases

- **Investigate incidents**: Query metrics, logs, and traces to diagnose production issues. Correlate Prometheus alerts with Loki log patterns and Tempo traces in a single conversation.
- **Manage dashboards**: Search, inspect, and update Grafana dashboards programmatically. Extract panel queries, generate deep links, and render panels as images.
- **Monitor infrastructure**: List data sources, discover available metrics, explore label values, and build PromQL or LogQL queries interactively.
- **Respond to alerts**: View firing alert rules, check on-call schedules, create or update incidents, and add activity notes to incident timelines.

## Prerequisites

- Access to a [Grafana Cloud](https://grafana.com/products/cloud/) instance
- An administrator must accept the Grafana Assistant terms and conditions
- The **Assistant Cloud MCP User** role or `grafana-assistant-app.cloud-mcp:access` permission (users with **Editor** role or higher have this by default)

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

GRAFANA_URL = "https://<your-stack>.grafana.net"

root_agent = Agent(
    model="gemini-flash-latest",
    name="observability_agent",
    instruction="Help users investigate issues using Grafana Cloud observability data",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.grafana.com/mcp",
                headers={
                    "X-Grafana-URL": GRAFANA_URL,
                },
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const GRAFANA_URL = "https://<your-stack>.grafana.net";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "observability_agent",
    instruction: "Help users investigate issues using Grafana Cloud observability data",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.grafana.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        "X-Grafana-URL": GRAFANA_URL,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```

Replace `<your-stack>` with your Grafana Cloud stack name. The `X-Grafana-URL` header is optional but recommended because it skips the URL entry step during OAuth authorization and redirects directly to the consent page.

Note

When the agent first connects, you'll be prompted to authorize the connection in your browser. Your OAuth token is valid for 1 hour and refreshes automatically for 30 days.

## Configuration

The Grafana Cloud MCP server supports read and write access scopes:

- **Read access**: View dashboards, alerts, incidents, and query data sources. Always available.
- **Write access**: Create and modify dashboards, alerts, and incidents. You can grant or withhold write access during the OAuth consent step.

If your agent only needs to query data, deny write access during authorization for a least-privilege setup.

## Available tools

### Search and navigation

| Tool                | Description                                                         |
| ------------------- | ------------------------------------------------------------------- |
| `search_dashboards` | Search for dashboards by query string                               |
| `search_folders`    | Search for folders by query string                                  |
| `generate_deeplink` | Generate deep link URLs for dashboards, panels, and Explore queries |

### Dashboards

| Tool                          | Description                                                | Access |
| ----------------------------- | ---------------------------------------------------------- | ------ |
| `get_dashboard_by_uid`        | Retrieve the complete dashboard JSON by UID                | Read   |
| `get_dashboard_summary`       | Get a compact summary of a dashboard                       | Read   |
| `get_dashboard_property`      | Extract specific parts of a dashboard using JSONPath       | Read   |
| `get_dashboard_panel_queries` | Retrieve panel queries with template variable substitution | Read   |
| `update_dashboard`            | Create or update a dashboard                               | Write  |
| `create_folder`               | Create a Grafana folder                                    | Write  |

### Data sources

| Tool               | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| `list_datasources` | List all configured data sources with optional type filtering |
| `get_datasource`   | Get detailed information about a data source by UID or name   |

### Prometheus

| Tool                              | Description                                                    |
| --------------------------------- | -------------------------------------------------------------- |
| `list_prometheus_metric_names`    | Discover available metrics with regex filtering and pagination |
| `list_prometheus_metric_metadata` | List metadata about currently scraped metrics                  |
| `list_prometheus_label_names`     | List label names with optional series selector and time range  |
| `list_prometheus_label_values`    | Get values for a specific label                                |
| `query_prometheus`                | Execute PromQL instant or range queries                        |
| `query_prometheus_histogram`      | Query histogram percentiles                                    |

### Loki

| Tool                     | Description                                            |
| ------------------------ | ------------------------------------------------------ |
| `list_loki_label_names`  | List available label names in logs                     |
| `list_loki_label_values` | Get unique values for a specific label                 |
| `query_loki_logs`        | Execute LogQL queries for log entries or metric values |
| `query_loki_stats`       | Get statistics about log streams                       |
| `query_loki_patterns`    | Detect and analyze common log patterns                 |

### Tempo

| Tool                            | Description                         |
| ------------------------------- | ----------------------------------- |
| `tempo_traceql-search`          | Search for traces using TraceQL     |
| `tempo_get-trace`               | Retrieve a trace by ID              |
| `tempo_get-attribute-names`     | Discover available trace attributes |
| `tempo_get-attribute-values`    | Get values for a trace attribute    |
| `tempo_traceql-metrics-instant` | Run instant TraceQL metrics queries |
| `tempo_traceql-metrics-range`   | Run range TraceQL metrics queries   |

### Pyroscope

| Tool                           | Description                              |
| ------------------------------ | ---------------------------------------- |
| `list_pyroscope_label_names`   | List available label names in profiles   |
| `list_pyroscope_label_values`  | List values for a specific label         |
| `list_pyroscope_profile_types` | List available profile types             |
| `query_pyroscope`              | Query profiles or metrics from Pyroscope |

### Alerting

| Tool                      | Description                                                    | Access       |
| ------------------------- | -------------------------------------------------------------- | ------------ |
| `alerting_manage_rules`   | List, filter, create, and update alert rules                   | Read / Write |
| `alerting_manage_routing` | View notification policies, contact points, and time intervals | Read         |

### Incidents

| Tool                       | Description                                   | Access |
| -------------------------- | --------------------------------------------- | ------ |
| `list_incidents`           | List incidents with optional status filtering | Read   |
| `get_incident`             | Get full incident details by ID               | Read   |
| `create_incident`          | Create a new incident                         | Write  |
| `add_activity_to_incident` | Add a note to an incident timeline            | Write  |

### OnCall

| Tool                       | Description                                                             |
| -------------------------- | ----------------------------------------------------------------------- |
| `list_oncall_schedules`    | List on-call schedules with optional team filtering                     |
| `get_oncall_shift`         | Get detailed shift information                                          |
| `get_current_oncall_users` | Get users currently on-call for a schedule                              |
| `list_oncall_teams`        | List OnCall teams                                                       |
| `list_oncall_users`        | List OnCall users with optional filtering                               |
| `list_alert_groups`        | List alert groups with filtering by state, team, time range, and labels |

### Additional tools

| Tool                      | Description                                                              | Access |
| ------------------------- | ------------------------------------------------------------------------ | ------ |
| `get_panel_image`         | Render a dashboard panel as a PNG image                                  | Read   |
| `describe_infrastructure` | Retrieve summaries of service groups including topology and dependencies | Read   |
| `get_annotations`         | Fetch annotations filtered by dashboard, time range, or tags             | Read   |
| `create_annotation`       | Create a new annotation on a dashboard or panel                          | Write  |
| `query_clickhouse`        | Execute SQL queries against ClickHouse data sources                      | Read   |
| `query_cloudwatch`        | Query AWS CloudWatch metrics                                             | Read   |
| `query_elasticsearch`     | Execute searches against Elasticsearch data sources                      | Read   |

## Self-hosted Grafana

For self-hosted Grafana instances, use the open source [Grafana MCP server](https://github.com/grafana/mcp-grafana) instead. It runs locally and connects to any Grafana instance using a service account token.

## Additional resources

- [Grafana Cloud MCP Server Documentation](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/)
- [Grafana Cloud](https://grafana.com/products/cloud/)
