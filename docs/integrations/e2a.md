---
catalog_title: e2a
catalog_description: Authenticated email gateway for AI agents with human-in-the-loop approval
catalog_icon: /integrations/assets/e2a.png
catalog_tags: ["mcp"]
---

# e2a MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [e2a MCP Server](https://github.com/tokencanopy/e2a/tree/main/mcp) connects
your ADK agent to [e2a](https://e2a.dev), an authenticated email gateway built
for AI agents. This integration gives your agent its own email inbox to send,
receive, and reply to messages using natural language, with SPF/DKIM/DMARC
verification on inbound mail and an optional human review hold on outbound
messages.

The server is hosted at `https://api.e2a.dev/mcp` and speaks Streamable HTTP —
there is nothing to install or run locally.

## Use cases

- **Give agents their own inboxes**: Provision dedicated email addresses (e.g.
  `support-bot@your-domain.com`) and let agents send and receive mail just like
  a teammate.

- **Authenticated inbound**: Every incoming message carries SPF, DKIM, and
  DMARC evidence, so your agent can tell whether the sender is who they claim
  to be before acting on the content.

- **Human-in-the-loop review**: Turn on a review hold and outbound messages are
  parked as `pending_review` until a human approves them — optionally with
  edits to the subject, body, or recipients before sending.

- **Automate threaded conversations**: Reply with `In-Reply-To` and
  `References` headers preserved, so threads stay intact across multiple turns
  in the recipient's mail client.

## Prerequisites

- A free [e2a account](https://e2a.dev) and an API key from the dashboard

## Use with agent

=== "Python"

    === "Remote MCP Server"

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

=== "TypeScript"

    === "Remote MCP Server"

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

## Key scope determines the tool surface

e2a issues two kinds of API key, and the MCP server exposes a different set of
tools to each:

- **Agent-scoped** (`e2a_agt_…`) — the credential *is* one agent. It sees only
  the runtime inbox tools below. Prefer this for a deployed ADK agent: it can
  act as its own inbox and nothing else.
- **Account-scoped** (`e2a_acct_…`) — sees the runtime tools plus every admin
  tool. Use it for provisioning and setup.

Scope is enforced server-side per handler, so an agent-scoped credential is
rejected on admin operations regardless of which tools were listed. Call
`whoami` to see which scope you are holding.

With an account-scoped key that owns more than one agent, pass `email` (or
`agent_email` on the compatibility aliases) to identify which inbox you mean.

!!! note "Interactive clients can use OAuth instead"

    ADK connects with a Bearer API key, which is the right choice for a
    deployed agent. Interactive MCP clients can instead add
    `https://api.e2a.dev/mcp` as an OAuth 2.1 connector and authorize in the
    browser — no key to paste. The endpoint advertises this via
    `/.well-known/oauth-protected-resource`.

## Available tools

The hosted server exposes roughly 60 tools, grouped below. Call `tools/list`
against the endpoint for the authoritative set your credential can see.

### Runtime — inbox tools (agent- and account-scoped)

Tool | Description
---- | -----------
`whoami` | Return the authenticated identity: user, credential scope, plan and usage limits, plus `agent_email` for an agent-scoped credential
`get_agent` | Fetch one agent's full record
`list_messages` | List inbox or sent mail with `direction`, `read_status`, search filters (`from_`, `subject_contains`, `conversation_id`, `since`, `until`) and cursor pagination
`get_message` | Full body, headers, attachment metadata, and SPF/DKIM/DMARC evidence for one message
`get_message_lifecycle` | Reconstructed delivery history for one message
`get_attachment` | Attachment metadata, or the bytes inline with `inline: true`
`send_message` | Send a new email; returns `accepted`, or `pending_review` when a review hold catches it
`reply_to_message` | Reply in-thread; preserves `In-Reply-To` and `References`
`forward_message` | Forward a message to new recipients
`list_conversations` / `get_conversation` | Browse threads rather than individual messages
`update_message_labels` | Add or remove labels on a message
`delete_message` / `restore_message` | Soft-delete to trash, and restore

### Admin — provisioning and setup (account-scoped only)

Tool | Description
---- | -----------
`list_agents`, `create_agent`, `update_agent`, `delete_agent`, `restore_agent` | Manage agent inboxes. `create_agent` takes a full email address on a verified custom domain or on the deployment's shared domain
`get_protection`, `update_protection` | Per-agent screening and review-hold configuration
`list_domains`, `register_domain`, `get_domain`, `verify_domain`, `delete_domain` | Custom domain registration and DNS verification
`list_reviews`, `get_review`, `approve_review`, `reject_review` | Work the human review queue; approve optionally with edits to subject, body, or recipients
`list_webhooks`, `create_webhook`, `update_webhook`, `delete_webhook`, `rotate_webhook_secret`, `test_webhook`, `list_webhook_deliveries` | Webhook subscriptions and delivery history
`list_events`, `get_event`, `redeliver_event` | Event log and replay
`list_templates`, `create_template`, `update_template`, `delete_template`, `validate_template`, `list_starter_templates` | Server-side email templates (beta)
`list_api_keys`, `create_api_key`, `delete_api_key` | API key management

!!! note "Compatibility aliases"

    `send_email`, `get_attachment_data`, `list_pending_messages`,
    `get_pending_message`, `approve_pending_message`, and
    `reject_pending_message` remain registered as frozen v1 aliases and keep
    working. New agents should prefer `send_message`, `get_attachment`, and the
    `*_review` tools.

## Receiving mail

Inbound is always available — there is no delivery mode to choose when creating
an agent. Pick whichever fits your deployment:

- **Poll** with `list_messages` (default `read_status: unread`). Simplest, and
  all an ADK agent needs to get started.
- **Subscribe** with `create_webhook` to have deliveries pushed to you.

!!! warning "Webhook handlers must verify the HMAC signature"

    Every webhook delivery is signed. Your handler must verify that signature
    before trusting the payload. See the [ADK webhook
    example](https://github.com/tokencanopy/e2a/tree/main/examples/adk-cloud-webhook)
    for a complete setup — signature verification, typed event decoding, and
    mapping e2a's `conversation_id` onto an ADK `session_id` so each thread
    keeps its own session.

## Sending and review holds

`send_message` and `reply_to_message` return one of two successful outcomes:

- `accepted` — durably persisted and queued for submission.
- `pending_review` — a human review hold caught it first; it sends once a
  reviewer approves.

**Neither is a failure, and neither should be retried.** The terminal outcome
arrives later through the `email.sent` / `email.failed` webhook events, or by
polling `get_message`. An agent should never approve or reject its own held
mail — the review tools are account-scoped precisely so a gated agent cannot
self-approve.

## Configuration

The hosted endpoint needs no environment variables beyond your API key, which
ADK passes in the `Authorization` header shown above.

To point at a self-hosted e2a deployment, change the `url` passed to
`StreamableHTTPConnectionParams` to that deployment's `/mcp` endpoint.

## Additional resources

- [e2a MCP Server source](https://github.com/tokencanopy/e2a/tree/main/mcp)
- [Runnable ADK example](https://github.com/tokencanopy/e2a/tree/main/mcp/examples/adk)
- [ADK webhook example](https://github.com/tokencanopy/e2a/tree/main/examples/adk-cloud-webhook)
- [e2a documentation](https://e2a.dev)
- [e2a in the MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=e2a) (`dev.e2a/mcp-server`)
