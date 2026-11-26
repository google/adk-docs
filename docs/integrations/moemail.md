---
catalog_title: MoeMail
catalog_description: Disposable email inboxes for agents that test sign-up and verification flows
catalog_icon: /integrations/assets/moemail.png
catalog_tags: ["mcp"]
---

# MoeMail MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [MoeMail MCP Server](https://moemail.app/en/mcp) connects your ADK agent to
[MoeMail](https://moemail.app), an open-source temporary email service. Your agent
can create a disposable mailbox, wait for an incoming email, read it and delete the
mailbox when it is done.

## Use cases

- **Test sign-up flows**: Give the agent a fresh address, let it submit your
  registration form and confirm the verification email.

- **Handle one-time codes**: Wait for an OTP or a magic link and continue the flow
  with it.

- **QA for transactional email**: Check that password-reset and notification
  emails arrive and contain the right content.

## Prerequisites

- A [MoeMail](https://moemail.app) account
- An API key from MoeMail → Profile → API Keys (if using API key authentication)

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        MOEMAIL_API_KEY = os.environ["MOEMAIL_API_KEY"]

        root_agent = Agent(
            model="gemini-flash-latest",
            name="moemail_agent",
            instruction=(
                "Help users test sign-up and email verification flows with disposable "
                "MoeMail inboxes. After submitting a form with a new mailbox, call "
                "wait_for_email with since '0' so an email that already arrived is "
                "returned at once."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://moemail.app/mcp",
                        headers={"X-API-Key": MOEMAIL_API_KEY},
                        timeout=120,
                    ),
                )
            ],
        )
        ```

    === "Local MCP Server (OAuth)"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-flash-latest",
            name="moemail_agent",
            instruction=(
                "Help users test sign-up and email verification flows with disposable "
                "MoeMail inboxes. After submitting a form with a new mailbox, call "
                "wait_for_email with since '0' so an email that already arrived is "
                "returned at once."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=["-y", "mcp-remote", "https://moemail.app/mcp"],
                        ),
                        timeout=120,
                    ),
                )
            ],
        )
        ```

        !!! note

            When you run this agent for the first time, a browser window opens to
            sign in to MoeMail. The consent screen lets you choose which tools the
            agent may use (read, create, send, delete).

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const MOEMAIL_API_KEY = process.env.MOEMAIL_API_KEY;

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "moemail_agent",
            instruction:
                "Help users test sign-up and email verification flows with disposable " +
                "MoeMail inboxes. After submitting a form with a new mailbox, call " +
                "wait_for_email with since '0' so an email that already arrived is " +
                "returned at once.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://moemail.app/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                "X-API-Key": MOEMAIL_API_KEY,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Local MCP Server (OAuth)"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "moemail_agent",
            instruction:
                "Help users test sign-up and email verification flows with disposable " +
                "MoeMail inboxes. After submitting a form with a new mailbox, call " +
                "wait_for_email with since '0' so an email that already arrived is " +
                "returned at once.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "mcp-remote", "https://moemail.app/mcp"],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            When you run this agent for the first time, a browser window opens to
            sign in to MoeMail. The consent screen lets you choose which tools the
            agent may use (read, create, send, delete).

!!! tip

    A verification email often lands while the agent is still submitting the form.
    Call `wait_for_email` with `since: "0"` on a new mailbox so that email is
    returned at once, and pass a result's `cursor` as `since` to wait for the next
    one.

## Available tools

Tool | Description
---- | -----------
`create_email` | Create a mailbox (`1h`, `24h`, `3d` or `permanent`)
`list_emails` | List your mailboxes
`list_messages` | List the messages in a mailbox
`read_message` | Read a message (text and HTML)
`wait_for_email` | Wait up to 90 seconds for a message; `since: "0"` includes mail already there, and each result returns a `cursor`
`send_email` | Send an email from a mailbox (needs send permission)
`delete_email` | Delete a mailbox and its messages
`delete_message` | Delete a message

## Additional resources

- [MoeMail MCP Server Documentation](https://moemail.app/en/mcp)
- [MoeMail source code](https://github.com/beilunyang/moemail)
