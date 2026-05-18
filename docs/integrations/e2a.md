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

The [e2a MCP Server](https://github.com/Mnexa-AI/e2a/tree/main/mcp) connects
your ADK agent to [e2a](https://e2a.dev), an authenticated email gateway
built for AI agents. Inbound mail is SPF/DKIM-verified before it reaches
your agent. Outbound mail can be held for human approval before it ships.

## Use cases

- **Give agents their own inboxes**: Provision dedicated email addresses
  (e.g. `support-bot@your-domain.com`) and let agents send and receive
  mail just like a teammate.

- **Authenticated inbound**: Every incoming message arrives with SPF and
  DKIM verification results so your agent knows whether the sender is who
  they claim to be.

- **Human-in-the-loop approval**: Configure HITL on any agent and
  outbound messages are held in a pending queue until a reviewer
  approves them — optionally with edits to subject, body, or recipients
  before sending.

- **Automate threaded conversations**: Reply to received emails with
  proper In-Reply-To and References headers preserved, so threads stay
  intact across multiple turns.

## Prerequisites

- A free [e2a account](https://e2a.dev) and an API key from the dashboard.
- Node.js 18+ on the machine running the agent (the MCP server is
  distributed via `npx -y @e2a/mcp-server`).

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        E2A_API_KEY = "YOUR_E2A_API_KEY"
        E2A_AGENT_EMAIL = "your-bot@your-domain.com"  # optional default inbox

        root_agent = Agent(
            model="gemini-flash-latest",
            name="e2a_agent",
            instruction=(
                "You manage email through the e2a tools. Call whoami once "
                "to find your inbox address. Use list_messages and "
                "get_message to read; use reply_to_message (not "
                "send_email) when replying to an existing thread so "
                "threading headers are preserved."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=["-y", "@e2a/mcp-server"],
                            env={
                                "E2A_API_KEY": E2A_API_KEY,
                                "E2A_AGENT_EMAIL": E2A_AGENT_EMAIL,
                            },
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

        const E2A_API_KEY = "YOUR_E2A_API_KEY";
        const E2A_AGENT_EMAIL = "your-bot@your-domain.com"; // optional default inbox

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "e2a_agent",
            instruction:
                "You manage email through the e2a tools. Call whoami once " +
                "to find your inbox address. Use list_messages and " +
                "get_message to read; use reply_to_message (not " +
                "send_email) when replying to an existing thread so " +
                "threading headers are preserved.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@e2a/mcp-server"],
                        env: {
                            E2A_API_KEY: E2A_API_KEY,
                            E2A_AGENT_EMAIL: E2A_AGENT_EMAIL,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Identity

Tool | Description
---- | -----------
`whoami` | Return the default agent's full record (requires `E2A_AGENT_EMAIL`)
`list_agents` | List every agent inbox owned by the authenticated user
`create_agent` | Register a new inbox using a slug on the shared domain; defaults to `local` mode so the agent receives mail by polling — no webhook required

!!! warning "Cloud-mode agents must verify webhook signatures"

    When you create an agent with `agent_mode: "cloud"`, e2a HMAC-signs every
    webhook delivery against your account's webhook signing secret
    (`E2A_WEBHOOK_SECRET`, shown in the [e2a dashboard](https://e2a.dev)).
    Your webhook handler must verify the signature on every request —
    the e2a SDK exposes `parseWebhook(body, secret)` which parses and
    verifies in one call. Local-mode agents (the default) avoid this
    entirely by polling via `list_messages`. A complete runnable
    cloud-mode + ADK example with proper signature verification lives
    at [github.com/Mnexa-AI/e2a/tree/main/examples/adk-cloud-webhook](https://github.com/Mnexa-AI/e2a/tree/main/examples/adk-cloud-webhook).

### Messages

Tool | Description
---- | -----------
`send_email` | Send a new email; returns `status: pending_approval` instead of `sent` when HITL is enabled
`reply_to_message` | Reply to an inbound message; preserves In-Reply-To and References headers
`list_messages` | List inbound mail with `status` filter (unread / read / all) and pagination
`get_message` | Fetch full body, headers, and attachment metadata for one message

### Human-in-the-loop approval

Tool | Description
---- | -----------
`list_pending_messages` | List outbound mail awaiting human approval, soonest-expiring first
`get_pending_message` | Get the full draft (subject, recipients, body) of a pending message
`approve_pending_message` | Send a held message, optionally with reviewer edits (subject / body / recipients)
`reject_pending_message` | Discard a held message; optional `reason` stored for audit

## Configuration

Variable | Required | Default | Description
-------- | -------- | ------- | -----------
`E2A_API_KEY` | Yes | — | Your e2a API key
`E2A_AGENT_EMAIL` | No | — | Default agent inbox; scopes tools so the LLM doesn't repeat the address on every call
`E2A_BASE_URL` | No | `https://e2a.dev` | Self-hosted deployment URL

## Additional resources

- [e2a MCP Server source](https://github.com/Mnexa-AI/e2a/tree/main/mcp)
- [Runnable ADK example](https://github.com/Mnexa-AI/e2a/tree/main/mcp/examples/adk)
- [e2a documentation](https://e2a.dev)
- [npm package](https://www.npmjs.com/package/@e2a/mcp-server)
