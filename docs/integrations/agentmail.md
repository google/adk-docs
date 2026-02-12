---
catalog_title: AgentMail
catalog_description: Create email inboxes for AI agents to send, receive, and manage messages
catalog_icon: /adk-docs/integrations/assets/agentmail.png
catalog_tags: ["mcp"]
---

# AgentMail MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [AgentMail MCP Server](https://github.com/agentmail-to/agentmail-mcp)
connects your ADK agent to [AgentMail](https://agentmail.to/), an email inbox
API built for AI agents. This integration gives your agent its own email
inboxes to send, receive, reply to, and forward messages using natural
language.

## Use cases

- **Give Agents Their Own Inboxes**: Create dedicated email addresses for your
  agents so they can send and receive emails independently, just like a human
  team member.

- **Automate Email Workflows**: Let your agent handle email conversations end
  to end, including sending initial outreach, reading replies, and following up
  on threads.

- **Manage Conversations Across Inboxes**: List and search across threads and
  messages, forward emails, and retrieve attachments to keep your agent informed
  and responsive.

## Prerequisites

- Create an [AgentMail account](https://agentmail.to/)
- Generate an API key from the
  [AgentMail Dashboard](https://agentmail.to/)

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="agentmail_agent",
            instruction="Help users manage email inboxes and send messages",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "agentmail-mcp",
                            ],
                            env={
                                "AGENTMAIL_API_KEY": AGENTMAIL_API_KEY,
                            }
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

        const AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "agentmail_agent",
            instruction: "Help users manage email inboxes and send messages",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "agentmail-mcp"],
                        env: {
                            AGENTMAIL_API_KEY: AGENTMAIL_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Inbox management

Tool | Description
---- | -----------
`list_inboxes` | List all inboxes
`get_inbox` | Get details for a specific inbox
`create_inbox` | Create a new inbox with a username and domain
`delete_inbox` | Delete an inbox

### Thread management

Tool | Description
---- | -----------
`list_threads` | List threads in an inbox
`get_thread` | Get a specific thread with its messages
`get_attachment` | Download an attachment from a message

### Message operations

Tool | Description
---- | -----------
`send_message` | Send a new email from an inbox
`reply_to_message` | Reply to an existing message
`forward_message` | Forward a message to another recipient
`update_message` | Update message properties such as read status

## Additional resources

- [AgentMail MCP Server Repository](https://github.com/agentmail-to/agentmail-mcp)
- [AgentMail Documentation](https://docs.agentmail.to/)
- [AgentMail Toolkit](https://github.com/agentmail-to/agentmail-toolkit)
