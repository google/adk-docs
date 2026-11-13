---
catalog_title: Taskade
catalog_description: Manage projects, tasks, AI agents, and automations in a workspace
catalog_icon: /integrations/assets/taskade.png
catalog_tags: ["mcp"]
---

# Taskade MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Taskade MCP Server](https://www.taskade.com/docs/mcp) connects your ADK
agent to [Taskade](https://www.taskade.com/), an AI-native workspace for
projects, AI agents, and automations. This integration gives your agent the
ability to read and update projects and tasks, prompt Taskade AI agents, and run
automations using natural language.

## Use cases

- **Plan Work**: Create projects and tasks, set due dates, assign tasks, and
  mark them complete from a single prompt.

- **Report on Projects**: Read projects, tasks, and custom fields across
  workspaces, then summarize the status of the work.

- **Work with AI Agents**: Create Taskade AI agents, add projects or media as
  knowledge, and send prompts to an agent.

- **Run Automations**: List automations, start a run, and read the recent runs
  of an automation with their status.

## Prerequisites

- A [Taskade](https://www.taskade.com/) account. The hosted MCP server needs a
  [paid Taskade plan](https://www.taskade.com/pricing).
- A personal access token from
  [Taskade Settings > API](https://www.taskade.com/settings/api)

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        TASKADE_API_KEY = "YOUR_TASKADE_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="taskade_agent",
            instruction="Help users manage projects, tasks, and AI agents in Taskade",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=["-y", "@taskade/mcp-server"],
                            env={
                                "TASKADE_API_KEY": TASKADE_API_KEY,
                            },
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

        TASKADE_API_KEY = "YOUR_TASKADE_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="taskade_agent",
            instruction="Help users manage projects, tasks, AI agents, and automations in Taskade",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://www.taskade.com/mcp",
                        headers={
                            "Authorization": f"Bearer {TASKADE_API_KEY}",
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

        const TASKADE_API_KEY = "YOUR_TASKADE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "taskade_agent",
            instruction: "Help users manage projects, tasks, and AI agents in Taskade",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@taskade/mcp-server"],
                        env: {
                            TASKADE_API_KEY: TASKADE_API_KEY,
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

        const TASKADE_API_KEY = "YOUR_TASKADE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "taskade_agent",
            instruction: "Help users manage projects, tasks, AI agents, and automations in Taskade",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://www.taskade.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${TASKADE_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    The local MCP server runs the
    [`@taskade/mcp-server`](https://www.npmjs.com/package/@taskade/mcp-server)
    package with `npx` and calls the Taskade public API. The remote MCP server
    is hosted by Taskade and also supports a browser-based OAuth 2.1 flow for
    clients that support it. Both examples use a personal access token.

## Available tools

The hosted Taskade MCP server includes tools organized by area. Tools are
automatically discovered when your agent connects. Use the
[ADK Web UI](/runtime/web-interface/) to view available tools in the trace graph
after running your agent.

Area | Description
---- | -----------
Workspaces | List workspaces, folders, media, and templates
Projects | Create, copy, read, complete, and share projects
Tasks | Create, update, move, assign, complete, and delete tasks, notes, dates, and field values
AI agents | Create and update AI agents, manage agent knowledge, and prompt an agent
Automations | List automations, run an automation, and read its recent runs

The local package exposes tools generated from the Taskade public API, which
include the webhook tools.

## Additional resources

- [Taskade MCP Server Documentation](https://www.taskade.com/docs/mcp)
- [Taskade MCP Repository](https://github.com/taskade/mcp)
- [Taskade API Documentation](https://www.taskade.com/api/documentation/v2)
