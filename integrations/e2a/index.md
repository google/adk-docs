# e2a MCP tool for ADK

Supported in ADKPythonTypeScript

The [e2a MCP Server](https://github.com/tokencanopy/e2a/tree/main/mcp) connects your ADK agent to [e2a](https://e2a.dev), an authenticated email gateway built for AI agents. This integration gives your agent its own email inbox to send, receive, and reply to messages using natural language, with SPF/DKIM/DMARC verification on inbound mail and an optional human review hold on outbound messages.

The server is hosted at `https://api.e2a.dev/mcp` and speaks Streamable HTTP — there is nothing to install or run locally.

## Use cases

- **Give agents their own inboxes**: Provision dedicated email addresses (e.g. `support-bot@your-domain.com`) and let agents send and receive mail just like a teammate.
- **Authenticated inbound**: Every incoming message carries SPF, DKIM, and DMARC evidence, so your agent can tell whether the sender is who they claim to be before acting on the content.
- **Human-in-the-loop review**: Turn on a review hold and outbound messages are parked as `pending_review` until a human approves them — optionally with edits to the subject, body, or recipients before sending.
- **Automate threaded conversations**: Reply with `In-Reply-To` and `References` headers preserved, so threads stay intact across multiple turns in the recipient's mail client.

## Prerequisites

- A free [e2a account](https://e2a.dev) and an API key from the dashboard

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)

E2A_API_KEY = "YOUR_E2A_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="e2a_agent",
    instruction=(
        "You manage email through the e2a tools. Call whoami once to "
        "learn your identity and inbox address. Use list_messages and "
        "get_message to read; use reply_to_message when replying to an "
        "existing thread (it preserves In-Reply-To and References), and "
        "send_message only to start a new thread. Both 'accepted' and "
        "'pending_review' are successful outcomes — never re-send after "
        "either one."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.e2a.dev/mcp",
                headers={"Authorization": f"Bearer {E2A_API_KEY}"},
                timeout=30,
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const E2A_API_KEY = "YOUR_E2A_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "e2a_agent",
    instruction:
        "You manage email through the e2a tools. Call whoami once to " +
        "learn your identity and inbox address. Use list_messages and " +
        "get_message to read; use reply_to_message when replying to an " +
        "existing thread (it preserves In-Reply-To and References), and " +
        "send_message only to start a new thread. Both 'accepted' and " +
        "'pending_review' are successful outcomes — never re-send after " +
        "either one.",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://api.e2a.dev/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${E2A_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```

For production, pair the toolset with the e2a SDK

The MCP toolset hands the inbox to the model. Keep the deterministic parts — verifying webhook signatures, handling at-least-once delivery, sending idempotently — in application code with the [Python](https://pypi.org/project/e2a/) or [TypeScript](https://www.npmjs.com/package/@e2a/sdk) SDK. The ADK webhook example below is a complete working version of that shape.

## Available tools

The hosted server exposes 60+ tools; call `tools/list` against the endpoint for the authoritative set. Which ones you see depends on your key: an **agent-scoped** key (`e2a_agt_…`) — recommended for a deployed agent — sees only the runtime tools, while an **account-scoped** key (`e2a_acct_…`) also sees the admin tools below.

### Runtime — inbox tools

| Tool                                      | Description                                                                                                                           |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `whoami`                                  | Return the authenticated identity: user, credential scope, plan and usage limits, plus `agent_email` for an agent-scoped credential   |
| `get_agent`                               | Fetch one agent's full record                                                                                                         |
| `list_messages`                           | List inbox or sent mail with `direction`, `read_status`, search filters, and cursor pagination                                        |
| `get_message`                             | Full body, headers, attachment metadata, and SPF/DKIM/DMARC evidence for one message                                                  |
| `get_message_lifecycle`                   | Reconstructed delivery history for one message                                                                                        |
| `get_attachment`                          | Attachment metadata, or the bytes inline with `inline: true`                                                                          |
| `send_message`                            | Send a new email; returns `accepted`, or `pending_review` when a review hold catches it — both are success, neither should be retried |
| `reply_to_message`                        | Reply in-thread; preserves `In-Reply-To` and `References`                                                                             |
| `forward_message`                         | Forward a message to new recipients                                                                                                   |
| `list_conversations` / `get_conversation` | Browse threads rather than individual messages                                                                                        |
| `update_message_labels`                   | Add or remove labels on a message                                                                                                     |
| `delete_message` / `restore_message`      | Soft-delete to trash, and restore                                                                                                     |

### Admin — provisioning and setup

| Tool                                                                                                                                      | Description                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `list_agents`, `create_agent`, `update_agent`, `delete_agent`, `restore_agent`                                                            | Manage agent inboxes                              |
| `get_protection`, `update_protection`                                                                                                     | Per-agent screening and review-hold configuration |
| `list_domains`, `register_domain`, `get_domain`, `verify_domain`, `delete_domain`                                                         | Custom domain registration and DNS verification   |
| `list_reviews`, `get_review`, `approve_review`, `reject_review`                                                                           | Work the human review queue                       |
| `list_webhooks`, `create_webhook`, `update_webhook`, `delete_webhook`, `rotate_webhook_secret`, `test_webhook`, `list_webhook_deliveries` | Webhook subscriptions and delivery history        |
| `list_events`, `get_event`, `redeliver_event`                                                                                             | Event log and replay                              |
| `list_templates`, `create_template`, `update_template`, `delete_template`, `validate_template`                                            | Server-side email templates (beta)                |
| `list_api_keys`, `create_api_key`, `delete_api_key`                                                                                       | API key management                                |

## Configuration

The hosted endpoint needs no environment variables beyond your API key, which ADK passes in the `Authorization` header shown above. To use a self-hosted e2a deployment, change the `url` to that deployment's `/mcp` endpoint.

Interactive MCP clients can add `https://api.e2a.dev/mcp` as an OAuth 2.1 connector instead of pasting a key. To receive mail, poll `list_messages`, open a WebSocket with the SDK's `listen()` (no public URL required), or subscribe an HTTPS endpoint with `create_webhook`.

## Additional resources

- [e2a MCP Server source](https://github.com/tokencanopy/e2a/tree/main/mcp)
- [Runnable ADK example](https://github.com/tokencanopy/e2a/tree/main/mcp/examples/adk)
- [ADK webhook example](https://github.com/tokencanopy/e2a/tree/main/examples/adk-cloud-webhook)
- [e2a documentation](https://e2a.dev)
