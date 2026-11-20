---
catalog_title: Atomic Mail
catalog_description: Give agents their own email inbox to send, read, and reply to mail
catalog_icon: /integrations/assets/atomic-mail.png
catalog_tags: ["mcp"]
---

# Atomic Mail MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Atomic Mail MCP Server](https://docs.atomicmail.ai/mcp) connects your ADK
agent to [Atomic Mail](https://atomicmail.ai/), an email service built for AI
agents. This integration gives your agent its own inbox to send, read, search,
and reply to email, and to schedule meetings with calendar invitations, using
natural language.

## Use cases

- **Give Agents Their Own Inbox**: Let your agent create a real email address
  for itself with one tool call. The local server needs no account and no API
  key to get started.

- **Handle Email Conversations End to End**: Send messages with plain text,
  HTML, and attachments, read incoming mail, search the mailbox, and reply in
  the same thread.

- **Receive Verification Codes and Sign-Up Links**: Use the inbox when your
  agent registers for a service, then read the confirmation message to finish
  the flow.

- **Schedule Meetings by Email**: Send calendar invitations that work in Gmail,
  Outlook, and Apple Mail, track who accepted, and answer invitations the agent
  receives.

## Prerequisites

- **Local MCP server**: [Node.js](https://nodejs.org/) 20 or later to run
  `npx`. No account or API key is required: your agent creates its inbox with
  the `register` tool.
- **Remote MCP server**: Sign in to the
  [Atomic Mail dashboard](https://dashboard.atomicmail.ai/), create an inbox,
  and copy its API key from the inbox's **Connect** dialog.

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
            name="atomic_mail_agent",
            instruction="Help users send, read, and reply to email from the agent's own inbox",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@atomicmail/mcp",
                            ],
                        ),
                        timeout=180,
                    ),
                )
            ],
        )
        ```

        !!! note

            On the first run, ask your agent to create its inbox and tell it
            the username you want (5 to 21 characters). The username becomes
            the permanent address `<username>@atomicmail.ai`. Sign-up solves a
            short proof-of-work puzzle on your machine and can take a minute or
            two, which is why this example uses a longer `timeout`. Credentials
            are saved in `~/.atomicmail/`, so later runs reuse the same inbox.

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        ATOMIC_MAIL_API_KEY = "YOUR_ATOMIC_MAIL_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="atomic_mail_agent",
            instruction="Help users send, read, and reply to email from the agent's own inbox",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.atomicmail.ai/mcp",
                        headers={
                            "Authorization": f"Bearer {ATOMIC_MAIL_API_KEY}",
                        },
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
            name: "atomic_mail_agent",
            instruction: "Help users send, read, and reply to email from the agent's own inbox",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@atomicmail/mcp"],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            On the first run, ask your agent to create its inbox and tell it
            the username you want (5 to 21 characters). The username becomes
            the permanent address `<username>@atomicmail.ai`. Sign-up solves a
            short proof-of-work puzzle on your machine and can take a minute or
            two. Credentials are saved in `~/.atomicmail/`, so later runs reuse
            the same inbox.

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const ATOMIC_MAIL_API_KEY = "YOUR_ATOMIC_MAIL_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "atomic_mail_agent",
            instruction: "Help users send, read, and reply to email from the agent's own inbox",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.atomicmail.ai/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${ATOMIC_MAIL_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Mail

Tool | Description
---- | -----------
`read_inbox` | List the most recent messages in the inbox
`read_message` | Get one message with its headers, body, and attachment list
`search_messages` | Search the whole mailbox by text
`send_email` | Send an email with plain text or HTML, CC and BCC, a From name, Reply-To, and attachments
`reply_to_message` | Reply to a message in the same thread
`list_agents` | List the inboxes this connection can use

### Meeting invitations

Tool | Description
---- | -----------
`send_invite` | Invite people to a meeting with a standard calendar invitation
`update_invite` | Change the time, title, place, notes, or guests of a meeting
`cancel_invite` | Cancel a meeting and notify every guest
`list_invites` | List meetings the inbox organized, with each guest's answer
`respond_to_invite` | Accept, decline, or tentatively accept a received invitation

### Setup and advanced

Tool | Description
---- | -----------
`register` | Create the agent's inbox and save its credentials (local server only)
`jmap_request` | Run a batch of raw [JMAP](https://jmap.io/) calls for anything the other tools do not cover (local server only)
`help` | Read the built-in documentation for the tools

## Configuration

The local MCP server reads these optional environment variables. Pass them in
the `env` setting of the server parameters:

- `ATOMIC_MAIL_API_KEY`: Use an existing inbox instead of creating a new one.
- `ATOMIC_MAIL_CREDENTIALS_DIR`: Directory where credentials are stored. The
  default is `~/.atomicmail/`. Use a separate directory for each agent that
  needs its own inbox.

## Additional resources

- [Atomic Mail Documentation](https://docs.atomicmail.ai/)
- [Local MCP Server Guide](https://docs.atomicmail.ai/mcp)
- [Hosted MCP Server Guide](https://docs.atomicmail.ai/mcp-remote)
- [Atomic Mail Repository](https://github.com/Atomic-Mail/atomic-mail-agentic)
