---
catalog_title: Odile Labs
catalog_description: Reach a business by its phone number and guard the API calls an agent makes
catalog_icon: /integrations/assets/odile.png
catalog_tags: ["mcp"]
---

# Odile Labs MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Odile Labs](https://odilelabs.com/developers) gives an ADK agent two things a
business API cannot: a way to reach a business that has no API, and a guard
around the APIs the agent is allowed to call.

- **Odile Direct** (`https://odilelabs.com/mcp/direct`): `find_business_agent`
  looks a business up by its phone number and returns its card;
  `send_to_business` leaves a message, checks open times or books a time.
  Lookups are free, and each agent identity gets 50 free tasks a month.
- **Odile Gate** (`https://gate.odilelabs.com/mcp`): each app gets its own key,
  an allowed-call list, a loop breaker, holds for risky writes and an audit log.
  Free for 3 apps and 10,000 calls a month.

## Use cases

- **Reach a business the user names**: look it up by phone number, read its open
  times, leave a message with a callback number, or book a slot it offers.
- **Act on a meeting or a conversation**: when a business and a number come up,
  hand the follow-up to the business's own agent instead of a human to-do.
- **Keep an agent inside its API allowance**: route the agent's calls to a
  third-party API through Gate, so repeated calls are stopped and risky writes
  wait for a person.

## Prerequisites

- None for lookups: `https://odilelabs.com/mcp/direct` answers `tools/list` and
  `find_business_agent` without a key.
- For paid tasks beyond the free allowance, an Odile API key from
  [odilelabs.com/developers](https://odilelabs.com/developers), sent as a Bearer
  token, or let the agent pay per task over x402 (USDC on Base).
- For Gate, create an app at [gate.odilelabs.com](https://gate.odilelabs.com) and
  use the app key it gives you.

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="business_reach_agent",
            instruction=(
                "When the user names a business by phone number, look it up with "
                "find_business_agent and act with send_to_business. Never book a "
                "time without the user's explicit yes."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://odilelabs.com/mcp/direct",
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "business_reach_agent",
            instruction:
                "When the user names a business by phone number, look it up with " +
                "find_business_agent and act with send_to_business. Never book a " +
                "time without the user's explicit yes.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://odilelabs.com/mcp/direct",
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

| Tool | What it does |
| --- | --- |
| `find_business_agent` | Looks a business up by its E.164 phone number and returns its Direct card and the skills it accepts. |
| `send_to_business` | One request to that business with a skill its card lists: `take_message`, `check_availability`, `book` or `book_first_available`; idempotent by `message_id`. |
| `get_replies` and `reply_to_business` | Reads the business's replies to a request and continues the thread. |
| `call_business`, `get_call_result`, `answer_call_question` | The opt-in voice pilot: a call placed to the business on the agent's behalf, its result, and answers to questions the business asks during the call. |
| `get_direct_usage` and `get_direct_payment` | The agent identity's free allowance and credits, and how to pay. |
| `get_m2m_network` | What the network offers and how it is priced. |

The full tool list, prices and the A2A agent card are at
[odilelabs.com/a2a](https://odilelabs.com/a2a).

## Additional resources

- [Odile Labs developer docs](https://odilelabs.com/developers)
- [Odile Gate](https://odilelabs.com/gate)
- [Pricing](https://odilelabs.com/pricing)
