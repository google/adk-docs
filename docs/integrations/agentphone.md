---
catalog_title: AgentPhone
catalog_description: Make phone calls, send SMS, manage numbers, and build AI voice agents
catalog_icon: /integrations/assets/agentphone.png
catalog_tags: ["mcp"]
---

# AgentPhone MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [AgentPhone MCP Server](https://github.com/AgentPhone-AI/agentphone-mcp)
connects your ADK agent to [AgentPhone](https://agentphone.to/), a telephony
platform built for AI agents. This integration gives your agent the ability to
make and receive phone calls, send and receive SMS, manage phone numbers, and
create autonomous AI voice agents using natural language.

## Use cases

- **Autonomous Phone Calls**: Have your agent call a phone number and hold a
  full AI-powered conversation about a specified topic, returning the complete
  transcript when done.

- **SMS Messaging**: Send and receive text messages, manage conversation threads
  across multiple phone numbers, and retrieve message history.

- **Phone Number Management**: Provision phone numbers with specific area codes,
  assign them to agents, and release them when no longer needed.

- **AI Voice Agents**: Create agents with configurable voices, system prompts,
  and model tiers (turbo, balanced, max) that autonomously handle inbound and
  outbound calls without requiring webhooks.

- **Call Transfer & Voicemail**: Configure agents to transfer calls to a human
  and set up voicemail greetings for unanswered calls.

- **Webhook Integration**: Set up project-level or per-agent webhooks to receive
  real-time notifications for inbound messages and call events.

## Prerequisites

- Create an [AgentPhone account](https://agentphone.to/)
- Generate an API key from the [AgentPhone Settings](https://agentphone.to/)

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="agentphone_agent",
            instruction="Help users make phone calls, send SMS, and manage phone numbers",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "agentphone-mcp",
                            ],
                            env={
                                "AGENTPHONE_API_KEY": AGENTPHONE_API_KEY,
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="agentphone_agent",
            instruction="Help users make phone calls, send SMS, and manage phone numbers",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.agentphone.to/mcp",
                        headers={
                            "Authorization": f"Bearer {AGENTPHONE_API_KEY}",
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

        const AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "agentphone_agent",
            instruction: "Help users make phone calls, send SMS, and manage phone numbers",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "agentphone-mcp"],
                        env: {
                            AGENTPHONE_API_KEY: AGENTPHONE_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "agentphone_agent",
            instruction: "Help users make phone calls, send SMS, and manage phone numbers",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.agentphone.to/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${AGENTPHONE_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Account

Tool | Description
---- | -----------
`account_overview` | Full snapshot of account: agents, numbers, webhook status, usage limits
`get_usage` | Detailed usage stats: plan limits, number quotas, message/call volume

### Phone numbers

Tool | Description
---- | -----------
`list_numbers` | List all phone numbers in account
`buy_number` | Purchase a new phone number with optional country and area code

### SMS / Messages

Tool | Description
---- | -----------
`send_message` | Send an SMS or iMessage from an agent's phone number
`get_messages` | Get SMS messages for a specific phone number
`list_conversations` | List SMS conversation threads, optionally filtered by agent
`get_conversation` | Get a specific conversation with full message history
`update_conversation` | Set or clear metadata on a conversation

### Voice calls

Tool | Description
---- | -----------
`list_calls` | List recent calls with optional agent, number, status, or direction filters
`get_call` | Get call details and transcript with optional long-polling
`make_call` | Place an outbound call with optional voice override, using webhook for conversation handling
`make_conversation_call` | Place an autonomous AI call with optional voice override that returns the full transcript

### Agents

Tool | Description
---- | -----------
`list_agents` | List all agents with phone numbers and voice config
`create_agent` | Create a new agent with voice, system prompt, model tier, call transfer, and voicemail
`update_agent` | Update agent configuration including voice, model tier, transfer, and voicemail
`delete_agent` | Delete an agent
`get_agent` | Get agent details including numbers and voice config
`attach_number` | Assign a phone number to an agent
`detach_number` | Detach a phone number from an agent
`list_voices` | List available voice options

### Webhooks

All webhook tools accept an optional `agent_id` parameter. When provided, the
operation targets that agent's webhook. When omitted, it targets the
project-level default. Agent-level webhooks take priority over project-level.

Tool | Description
---- | -----------
`get_webhook` | Get webhook configuration
`set_webhook` | Set webhook URL for inbound messages and call events
`delete_webhook` | Remove a webhook
`test_webhook` | Send a test event to verify a webhook is working
`list_webhook_deliveries` | View recent webhook delivery history

## Configuration

The AgentPhone MCP server can be configured using environment variables:

Variable | Description | Default
-------- | ----------- | -------
`AGENTPHONE_API_KEY` | Your AgentPhone API key | Required (stdio mode)
`AGENTPHONE_BASE_URL` | Override API base URL | `https://api.agentphone.to`

For remote HTTP mode, pass the API key via the `Authorization: Bearer` header
instead of an environment variable.

## Additional resources

- [AgentPhone MCP Server on GitHub](https://github.com/AgentPhone-AI/agentphone-mcp)
- [agentphone-mcp on npm](https://www.npmjs.com/package/agentphone-mcp)
- [AgentPhone Website](https://agentphone.to/)
