---
catalog_title: Mnemoverse
catalog_description: Add hosted long-term memory that learns from outcomes
catalog_icon: /integrations/assets/mnemoverse.png
catalog_tags: ["data", "mcp"]
---

# Mnemoverse MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Mnemoverse MCP server](https://github.com/mnemoverse/mcp-memory-server)
connects your ADK agent to [Mnemoverse](https://mnemoverse.com), hosted
persistent memory for AI agents. The agent stores memories, recalls them with a
natural-language query, and reports whether a recalled memory helped or misled.
That feedback re-ranks what comes back next. Shared rooms let several people's
assistants, on different accounts, read and write one memory.

The server is the open-source `@mnemoverse/mcp-memory-server` package (MIT). It
runs locally through `npx`, talks to your agent over stdio, and stores memories
in the hosted service, so they persist across sessions, processes and machines
that use the same account.

## Use cases

- **Remember across sessions**: Save user preferences, decisions and project
  facts in one run, and recall them in a later run or a new session.
- **Learn from outcomes**: After a recalled memory is used, the agent rates it
  as helpful or misleading, which re-ranks what comes back next.
- **Share memory across accounts**: Create a room, invite another person or
  another account's agent, and read and write the same memory from both sides.

## Prerequisites

- For Python, ADK installed with the MCP extra: `pip install "google-adk[mcp]"`
- For TypeScript, ADK and the MCP SDK, which ADK lists as an optional peer
  dependency: `npm install @google/adk @modelcontextprotocol/sdk`
- [Node.js](https://nodejs.org/en/download) 18 or newer, because the server is
  started with `npx`
- A Mnemoverse API key (it starts with `mk_live_`). The free tier needs no
  credit card: sign up at
  [console.mnemoverse.com](https://console.mnemoverse.com/sign-up).

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        MNEMOVERSE_API_KEY = "YOUR_MNEMOVERSE_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="mnemoverse_agent",
            instruction=(
                "You have long-term memory. Before answering, search it with "
                "memory_read. Save durable facts, preferences and decisions with "
                "memory_write. After you use a recalled memory, call "
                "memory_feedback to say whether it helped."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@mnemoverse/mcp-memory-server@latest",
                            ],
                            env={
                                "MNEMOVERSE_API_KEY": MNEMOVERSE_API_KEY,
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

        const MNEMOVERSE_API_KEY = "YOUR_MNEMOVERSE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "mnemoverse_agent",
            instruction:
                "You have long-term memory. Before answering, search it with " +
                "memory_read. Save durable facts, preferences and decisions with " +
                "memory_write. After you use a recalled memory, call " +
                "memory_feedback to say whether it helped.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@mnemoverse/mcp-memory-server@latest"],
                        env: {
                            MNEMOVERSE_API_KEY: MNEMOVERSE_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

Run the agent and tell it something worth keeping on the first turn, for
example "Staging deploys go through make deploy-staging". Then start a new
session and ask how to deploy to staging: the agent is instructed to search its
memory before answering.

## Available tools

Tool | Description
---- | -----------
`memory_write` | Store a memory that should persist across sessions: a preference, decision, lesson or project fact
`memory_read` | Search memory with a natural-language query before answering or starting a task
`memory_list_recent` | List the newest memories first, filtered by domain and time window, without a query
`memory_feedback` | Rate a recalled memory as helpful or misleading; the rating re-ranks what comes back next
`memory_stats` | Show how many memories are stored and which domains exist
`memory_create_room` | Create a memory room shared across accounts
`memory_invite_to_room` | Create an invite code for a room you own
`memory_join_room` | Join a shared room with an invite code
`memory_list_rooms` | List the rooms you own or have joined
`vault_list` | List stored secrets by alias and purpose; values are never returned
`memory_graph` | Read the association graph the memory has formed around given concepts

## Configuration

The server needs one environment variable, `MNEMOVERSE_API_KEY`. Pass it in
`env` as shown above. The MCP SDKs start a stdio server with only a short list
of inherited variables such as `PATH`, so a key that is set only in your shell
does not reach the server.

## Additional resources

- [Mnemoverse MCP server documentation](https://mnemoverse.com/docs/api/mcp-server)
- [Mnemoverse MCP server repository](https://github.com/mnemoverse/mcp-memory-server)
- [`@mnemoverse/mcp-memory-server` on npm](https://www.npmjs.com/package/@mnemoverse/mcp-memory-server)
- [Get a Mnemoverse API key](https://console.mnemoverse.com/sign-up)
- [Mnemoverse pricing](https://mnemoverse.com/pricing)
- [Mnemoverse security](https://mnemoverse.com/docs/api/security)
