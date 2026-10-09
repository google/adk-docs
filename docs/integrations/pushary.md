---
catalog_title: Pushary
catalog_description: Collect human answers and send agent updates through push notifications
catalog_icon: /integrations/assets/pushary.png
catalog_tags: ["mcp"]
---

# Pushary MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Pushary MCP server](https://pushary.com/docs/agents/reference/tools)
connects your ADK agent to [Pushary](https://pushary.com/) to ask its operator
questions and send progress updates through push notifications. The hosted
server uses Streamable HTTP; no local MCP server is required.

## Use cases

- **Collect missing information**: Ask the operator to choose an option or
  provide text while an agent prepares a draft.
- **Review a draft from a phone**: Send a confirmation question and use the
  recorded answer to revise or finalize the draft.
- **Report completion**: Send an update when a long-running task finishes.

## Prerequisites

- Set up an agent and model credentials using the
  [Python quickstart](/get-started/python/) or
  [TypeScript quickstart](/get-started/typescript/).
- Create a Pushary account and copy an API key from
  [API key guide](https://pushary.com/docs/agents/api-key).
- [Connect your phone](https://pushary.com/docs/agents/receiving-notifications)
  and select a delivery mode that sends questions to it. Terminal mode keeps
  questions in the client; Updates mode sends awareness-only notifications.
- Set the `PUSHARY_API_KEY` environment variable in the process running ADK.
  Keep the key out of source control.

## Use with agent

This example prepares a draft and asks the operator for missing information.
It exposes only the four tools needed for questions and task updates.

=== "Python"

    === "Remote MCP Server"

        Install the MCP extra in your agent's environment:

        ```bash
        pip install 'google-adk[mcp]'
        ```

        Replace your agent's `agent.py` with:

        ```python
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="pushary_agent",
            instruction=(
                "Help the operator prepare a draft. Use ask_user to collect missing "
                "information or request feedback. Follow handoffAction when present, "
                "otherwise nextAction. Never treat an unanswered question or a no "
                "as approval. Do not publish or perform external actions."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://pushary.com/api/mcp/mcp",
                        headers={"Authorization": f"Bearer {os.environ['PUSHARY_API_KEY']}"},
                    ),
                    tool_filter=[
                        "ask_user", "wait_for_answer", "cancel_question", "send_notification"
                    ],
                )
            ],
        )
        ```

        Run the agent with `adk run <agent-directory>` as in the quickstart.

=== "TypeScript"

    === "Remote MCP Server"

        Install ADK and its optional MCP peer in your agent project:

        ```bash
        npm install @google/adk @modelcontextprotocol/sdk
        ```

        Replace your project's `agent.ts` with:

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const apiKey = process.env.PUSHARY_API_KEY;
        if (!apiKey) {
            throw new Error("Set PUSHARY_API_KEY before starting the agent");
        }

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "pushary_agent",
            instruction:
                "Help the operator prepare a draft. Use ask_user to collect missing " +
                "information or request feedback. Follow handoffAction when present, " +
                "otherwise nextAction. Never treat an unanswered question or a no " +
                "as approval. Do not publish or perform external actions.",
            tools: [
                new MCPToolset(
                    {
                        type: "StreamableHTTPConnectionParams",
                        url: "https://pushary.com/api/mcp/mcp",
                        transportOptions: {
                            requestInit: {
                                headers: { Authorization: `Bearer ${apiKey}` },
                            },
                        },
                    },
                    ["ask_user", "wait_for_answer", "cancel_question", "send_notification"],
                ),
            ],
        });

        export { rootAgent };
        ```

        Run the agent with `npx adk run agent.ts` as in the quickstart.

Try: "Prepare a short release announcement. Ask me through Pushary which
feature to highlight before drafting it."

The question tools return an explicit answer state. Follow `handoffAction`
when present, otherwise `nextAction`. If a live question times out, poll once
with `wait_for_answer`. If it remains pending, cancel it before asking in the
current client. Stop if cancellation returns `handoffAction: "stop"`; otherwise,
if cancellation returns false, poll once for one second and honor any answer
that arrived during cancellation. See the
[question lifecycle](https://pushary.com/docs/agents/human-in-the-loop).

These tools collect feedback; registering them does not enforce approval on
other tools. Enforce any authorization requirements in application code before
performing protected actions.

## Available tools

The example filters the server's tools to this subset:

Tool | Description
---- | -----------
`ask_user` | Ask a confirmation, multiple-choice, or free-text question
`wait_for_answer` | Check or wait for a question's answer using its correlation ID
`cancel_question` | Cancel a pending question before handing off to the current client
`send_notification` | Send a push notification or task update

Available tools depend on the API key and plan. These operator question tools
are separate from the Partner decision tools for a product's end users.
See the [tool reference](https://pushary.com/docs/agents/reference/tools)
for parameters, delivery behavior, and Partner tools.

## Additional resources

- [Pushary documentation](https://pushary.com/docs/agents/quickstart)
- [Pushary human-in-the-loop guide](https://pushary.com/docs/agents/human-in-the-loop)
- [Pushary open-source integrations](https://github.com/Pushary)
