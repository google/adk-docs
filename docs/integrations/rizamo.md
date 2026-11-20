---
catalog_title: Rizamo
catalog_description: Publish, schedule and measure social posts, and answer comments
catalog_icon: /integrations/assets/rizamo.png
catalog_tags: ["mcp", "connectors"]
---

# Rizamo MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Rizamo MCP Server](https://docs.rizamo.com/connect-an-agent) connects your
ADK agent to [Rizamo](https://rizamo.com), a social media API for AI agents. It
gives your agent the ability to publish and schedule posts on Instagram,
Facebook, TikTok, Threads, LinkedIn and YouTube, read their analytics and
audience, and answer comments and messages, using natural language. The server
is hosted by Rizamo, so there is nothing to install or run.

## Use cases

- **Publishing**: draft, schedule or queue one post for several networks at
  once, with each network's own rules checked before anything goes out.
- **Reporting**: ask how the accounts did over a period, which posts did best,
  and who the followers are.
- **Inbox**: find open comments and messages, read the thread, and reply or
  hand it to a teammate.
- **Client review**: share a preview link of a post that anyone can open
  before it goes out.

## Prerequisites

- A [Rizamo](https://rizamo.com) account. The first 2 social accounts are free,
  with no card.
- An API key, created in the Rizamo web app under **Developers**. Its scopes
  decide which tools the agent sees. See
  [Authentication](https://docs.rizamo.com/authentication#api-keys).

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        RIZAMO_API_KEY = "YOUR_RIZAMO_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="social_media_agent",
            instruction=(
                "You publish and measure the team's social posts with Rizamo. "
                "Save drafts unless the user asks to schedule or publish."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.rizamo.com/mcp",
                        headers={
                            "Authorization": f"Bearer {RIZAMO_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

        !!! note

            MCP support needs `pip install "google-adk[mcp]"` since ADK 2.

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const RIZAMO_API_KEY = "YOUR_RIZAMO_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "social_media_agent",
            instruction:
                "You publish and measure the team's social posts with Rizamo. " +
                "Save drafts unless the user asks to schedule or publish.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.rizamo.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${RIZAMO_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            MCP needs the optional peer dependency
            `npm install @modelcontextprotocol/sdk`.

## Available tools

Tool | Description
---- | -----------
`list_profiles` | The brands or clients the team posts for, each with its accounts, queue and time zone
`list_accounts` | Connected social accounts, with what each can publish
`create_media` | Add an image or video for a post
`validate_post` | Check a post against every network it targets, without creating it
`create_post` | Draft, schedule or queue a post on one or more accounts
`publish_post` | Publish a post now
`get_post` | Follow a post's status on each network
`share_post` | A preview link anyone can open before the post goes out
`get_analytics` | Views, reach, engagements and followers over a period, against the one before
`list_post_performance` | Rank a period's posts by views, reach and engagements
`get_audience` | Who follows each account and who engaged, by age, gender and place
`list_threads` | Comments and messages to answer, newest first
`reply_to_thread` | Reply to a comment or message

The server has more tools (queues, short links, comment automations, account
connection). The ones an agent sees follow its key's scopes.

## Additional resources

- [Rizamo with Google ADK](https://docs.rizamo.com/frameworks/google-adk)
- [Connect an agent](https://docs.rizamo.com/connect-an-agent)
- [Rizamo MCP Server on GitHub](https://github.com/rizamohq/rizamo-mcp)
- [API reference](https://docs.rizamo.com/api)
