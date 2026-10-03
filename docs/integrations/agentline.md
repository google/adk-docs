---
catalog_title: AgentLine
catalog_description: Make voice calls, read inbound SMS, and provision numbers
catalog_icon: /integrations/assets/agentline.png
catalog_tags: ["mcp"]
---

# AgentLine MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [AgentLine MCP Server](https://github.com/AgentLineHQ/agentline-mcp)
connects your ADK agent to [AgentLine](https://agentline.cloud), an AI-native
telephony platform. This integration gives your agent the ability to provision
US phone numbers, make and receive voice calls, retrieve transcripts, read
inbound SMS, and manage billing using natural language.

## Use cases

- **Autonomous Phone Calls**: Have your agent call a US number, hold an
  AI-powered conversation with a custom greeting and system prompt, then return
  the full transcript.

- **Inbound Voice Agents**: Create a voice agent, attach a phone number, and let
  AgentLine answer inbound calls with the agent's prompt, greeting, and voice.

- **Phone Number Management**: Provision a US local or toll-free number with a
  preferred area code and assign it to an agent.

- **Inbound SMS**: Read SMS that callers send to the agent's number and poll
  for `sms.received` events.

- **Transcripts and Events**: List calls, hang up an in-progress call, and poll
  or peek at the event mailbox for `call.completed` and `call.owner_task`
  results.

- **Voice and Billing**: Choose a TTS voice preset and check account balance
  before placing calls or buying numbers.

## Prerequisites

- Create an [AgentLine account](https://agentline.cloud/signup)
- Generate an API key with the email one-time-code flow. See
  [Authentication](https://docs.agentline.cloud/authentication)

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        AGENTLINE_API_KEY = "YOUR_AGENTLINE_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="agentline_agent",
            instruction="Help users make phone calls, read inbound SMS, and manage phone numbers",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.agentline.cloud/mcp",
                        headers={
                            "Authorization": f"Bearer {AGENTLINE_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const AGENTLINE_API_KEY = "YOUR_AGENTLINE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "agentline_agent",
            instruction: "Help users make phone calls, read inbound SMS, and manage phone numbers",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.agentline.cloud/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${AGENTLINE_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Agents

Tool | Description
---- | -----------
`create_agent` | Create a voice agent with a name, system prompt, greeting, and voice
`list_agents` | List all agents
`get_agent` | Get details for a specific agent
`update_agent` | Update an agent's prompt, greeting, voice, or owner phone
`delete_agent` | Delete an agent

### Phone numbers

Tool | Description
---- | -----------
`buy_phone_number` | Provision a US local or toll-free number and attach it to an agent
`list_phone_numbers` | List phone numbers on the account

### Voice calls

Tool | Description
---- | -----------
`make_outbound_call` | Place an outbound call from an agent's number
`list_calls` | List recent calls
`get_call_details` | Get status and metadata for a call
`get_call_transcript` | Get the full `{role, text, timestamp}` transcript
`hangup_call` | End an active call

### SMS

Outbound SMS is not available. Inbound messages arrive as `sms.received` events.

Tool | Description
---- | -----------
`list_messages` | List inbound SMS for an agent

### Events

The `poll_events` tool consumes pending events. Use `peek_events` to inspect
the queue without deleting it. Common `event_type` values include
`call.received`, `call.completed`, `call.owner_task`, and `sms.received`.

Tool | Description
---- | -----------
`poll_events` | Consume pending call and SMS events from the mailbox
`peek_events` | Preview pending events without consuming them

### Billing

Tool | Description
---- | -----------
`get_account_balance` | Get the current account balance
`get_expenditure_breakdown` | Get spending for the current period

### Voice

Voice presets include `female-1`, `female-2`, `female-3`, `male-1`, `male-2`,
and `male-3`. Per-call and per-agent settings override the account default.

Tool | Description
---- | -----------
`list_available_voices` | List TTS voice presets
`get_account_voice` | Get the account-level default voice
`set_account_voice` | Set the account-level default voice
`reset_account_voice` | Reset the account voice to the platform default

## Configuration

The remote AgentLine MCP server authenticates with a Bearer API key. Keys use
the `al_live_` prefix. Legacy `sk_live_` keys are also accepted.

| Setting | Description | Default |
| ------- | ----------- | ------- |
| `Authorization` header | `Bearer al_live_...` | Required |
| MCP URL | Hosted Streamable HTTP endpoint | `https://api.agentline.cloud/mcp` |

Phone numbers are E.164 (for example, `+12125557890`). Each agent can have one
active number. Numbers are US-only.

## Additional resources

- [AgentLine Documentation](https://docs.agentline.cloud/introduction)
- [AgentLine MCP Server on GitHub](https://github.com/AgentLineHQ/agentline-mcp)
- [AgentLine on GitHub](https://github.com/AgentLineHQ/AgentLine)
- [AgentLine Website](https://agentline.cloud)
- [Discord](https://discord.gg/69SVE2jWNr)
