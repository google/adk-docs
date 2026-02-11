---
catalog_title: Linear
catalog_description: Manage issues, track projects, and streamline development
catalog_icon: /adk-docs/integrations/assets/linear.png
catalog_tags: ["mcp"]
---

# Linear MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Linear MCP Server](https://linear.app/docs/mcp) connects your ADK agent to
[Linear](https://linear.app/), a purpose-built tool for planning and building
products. This integration gives your agent the ability to manage issues, track
project cycles, and automate development workflows using natural language.

## Use cases

- **Streamline Issue Management**: Create, update, and organize issues using
  natural language. Let your agent handle logging bugs, assigning tasks, and
  updating statuses.

- **Track Projects and Cycles**: Get instant visibility into your team's
  momentum. Query the status of active cycles, check project milestones, and
  retrieve deadlines.

- **Contextual Search & Summarization**: Quickly catch up on long discussion
  threads or find specific project specifications. Your agent can search
  documentation and summarize complex issues.

## Prerequisites

- [Sign up](https://linear.app/signup) for a Linear account
- Generate an API key in
  [Linear Settings > Security & access](https://linear.app/docs/security-and-access)
  (if using API authentication)

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="linear_agent",
            instruction="Help users manage issues, projects, and cycles in Linear",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.linear.app/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

        !!! note

            When you run this agent for the first time, a browser window will open
            automatically to request access via OAuth. Alternatively, you can use
            the authorization URL printed in the console. You must approve this
            request to allow the agent to access your Linear data.

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        LINEAR_API_KEY = "YOUR_LINEAR_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="linear_agent",
            instruction="Help users manage issues, projects, and cycles in Linear",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://mcp.linear.app/mcp",
                        headers={
                            "Authorization": f"Bearer {LINEAR_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

        !!! note

            This code example uses an API key for authentication. To use a
            browser-based OAuth authentication flow instead, remove the `headers`
            parameter and run the agent.

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "linear_agent",
            instruction: "Help users manage issues, projects, and cycles in Linear",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "mcp-remote", "https://mcp.linear.app/mcp"],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            When you run this agent for the first time, a browser window will open
            automatically to request access via OAuth. Alternatively, you can use
            the authorization URL printed in the console. You must approve this
            request to allow the agent to access your Linear data.

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const LINEAR_API_KEY = "YOUR_LINEAR_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "linear_agent",
            instruction: "Help users manage issues, projects, and cycles in Linear",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.linear.app/mcp",
                    header: {
                        Authorization: `Bearer ${LINEAR_API_KEY}`,
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            This code example uses an API key for authentication. To use a
            browser-based OAuth authentication flow instead, remove the `header`
            property and run the agent.

## Available tools

Tool | Description
---- | -----------
`list_comments` | List comments on an issue
`create_comment` | Create a comment on an issue
`list_cycles` | List cycles in a project
`get_document` | Get a document
`list_documents` | List documents
`get_issue` | Get an issue
`list_issues` | List issues
`create_issue` | Create an issue
`update_issue` | Update an issue
`list_issue_statuses` | List issue statuses
`get_issue_status` | Get an issue status
`list_issue_labels` | List issue labels
`create_issue_label` | Create an issue label
`list_projects` | List projects
`get_project` | Get a project
`create_project` | Create a project
`update_project` | Update a project
`list_project_labels` | List project labels
`list_teams` | List teams
`get_team` | Get a team
`list_users` | List users
`get_user` | Get a user
`search_documentation` | Search documentation

## Additional resources

- [Linear MCP Server Documentation](https://linear.app/docs/mcp)
- [Linear Getting Started Guide](https://linear.app/docs/start-guide)
