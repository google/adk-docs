# Mailgun MCP tool for ADK

Supported in ADKPythonTypeScript

The [Mailgun MCP Server](https://github.com/mailgun/mailgun-mcp-server) connects your ADK agent to [Mailgun](https://www.mailgun.com/), a transactional email service. This integration gives your agent the ability to send emails, track delivery metrics, manage domains and templates, and handle mailing lists using natural language.

## Use cases

- **Send and Manage Emails**: Compose and send transactional or marketing emails, retrieve stored messages, and resend messages through conversational commands.
- **Monitor Delivery Performance**: Fetch delivery statistics, analyze bounce classifications, and review suppression lists to maintain sender reputation.
- **Manage Email Infrastructure**: Verify domain DNS configuration, configure tracking settings, create email templates, and set up inbound routing rules.

## Prerequisites

- Create a [Mailgun account](https://www.mailgun.com/)
- Generate an API key from the [Mailgun Dashboard](https://app.mailgun.com/settings/api_security)

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="mailgun_agent",
    instruction="Help users send emails and manage their Mailgun account",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@mailgun/mcp-server",
                    ],
                    env={
                        "MAILGUN_API_KEY": MAILGUN_API_KEY,
                        # "MAILGUN_API_REGION": "eu",  # Optional: defaults to "us"
                    }
                ),
                timeout=30,
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "mailgun_agent",
    instruction: "Help users send emails and manage their Mailgun account",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@mailgun/mcp-server"],
                env: {
                    MAILGUN_API_KEY: MAILGUN_API_KEY,
                    // MAILGUN_API_REGION: "eu",  // Optional: defaults to "us"
                },
            },
        }),
    ],
});

export { rootAgent };
```

## Available tools

### Messaging

| Tool                 | Description                                                 |
| -------------------- | ----------------------------------------------------------- |
| `send_email`         | Send an email with support for HTML content and attachments |
| `get_stored_message` | Retrieve a stored email message                             |
| `resend_message`     | Resend a previously sent message                            |

### Domains

| Tool                       | Description                                       |
| -------------------------- | ------------------------------------------------- |
| `get_domain`               | View details for a specific domain                |
| `verify_domain`            | Verify DNS configuration for a domain             |
| `get_tracking_settings`    | View tracking settings (click, open, unsubscribe) |
| `update_tracking_settings` | Update tracking settings for a domain             |

### Webhooks

| Tool             | Description                          |
| ---------------- | ------------------------------------ |
| `list_webhooks`  | List all event webhooks for a domain |
| `create_webhook` | Create a new event webhook           |
| `update_webhook` | Update an existing webhook           |
| `delete_webhook` | Delete a webhook                     |

### Routes

| Tool           | Description                      |
| -------------- | -------------------------------- |
| `list_routes`  | View inbound email routing rules |
| `update_route` | Update an inbound routing rule   |

### Mailing lists

| Tool                  | Description                                 |
| --------------------- | ------------------------------------------- |
| `create_mailing_list` | Create a new mailing list                   |
| `manage_list_members` | Add, remove, or update mailing list members |

### Templates

| Tool                       | Description                         |
| -------------------------- | ----------------------------------- |
| `create_template`          | Create a new email template         |
| `manage_template_versions` | Create and manage template versions |

### Analytics and stats

| Tool            | Description                                                            |
| --------------- | ---------------------------------------------------------------------- |
| `query_metrics` | Query sending and usage metrics for a date range                       |
| `get_logs`      | Retrieve email event logs                                              |
| `get_stats`     | View aggregate statistics by domain, tag, provider, device, or country |

### Suppressions

| Tool               | Description                       |
| ------------------ | --------------------------------- |
| `get_bounces`      | View bounced email addresses      |
| `get_unsubscribes` | View unsubscribed email addresses |
| `get_complaints`   | View complaint records            |
| `get_allowlist`    | View allowlist entries            |

### IPs

| Tool           | Description                          |
| -------------- | ------------------------------------ |
| `list_ips`     | View IP assignments                  |
| `get_ip_pools` | View dedicated IP pool configuration |

### Bounce classification

| Tool                        | Description                              |
| --------------------------- | ---------------------------------------- |
| `get_bounce_classification` | Analyze bounce types and delivery issues |

## Configuration

| Variable             | Required | Default | Description              |
| -------------------- | -------- | ------- | ------------------------ |
| `MAILGUN_API_KEY`    | Yes      | —       | Your Mailgun API key     |
| `MAILGUN_API_REGION` | No       | `us`    | API region: `us` or `eu` |

## Additional resources

- [Mailgun MCP Server Repository](https://github.com/mailgun/mailgun-mcp-server)
- [Mailgun MCP Integration Guide](https://www.mailgun.com/resources/integrations/mcp-server/)
- [Mailgun Documentation](https://documentation.mailgun.com/)
