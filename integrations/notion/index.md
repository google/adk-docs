# Notion MCP tool for ADK

Supported in ADKPythonTypeScript

The [Notion MCP Server](https://github.com/makenotion/notion-mcp-server) connects your ADK agent to Notion, allowing it to search, create, and manage pages, databases, and more within a workspace. This gives your agent the ability to query, create, and organize content in your Notion workspace using natural language.

## Use cases

- **Search your workspace**: Find project pages, meeting notes, or documents based on content.
- **Create new content**: Generate new pages for meeting notes, project plans, or tasks.
- **Manage tasks and databases**: Update the status of a task, add items to a database, or change properties.
- **Organize your workspace**: Move pages, duplicate templates, or add comments to documents.

## Prerequisites

- Obtain a Notion integration token by going to [Notion Integrations](https://www.notion.so/profile/integrations) in your profile. Refer to the [authorization documentation](https://developers.notion.com/docs/authorization) for more details.
- Ensure relevant pages and databases can be accessed by your integration. Visit the Access tab in your [Notion Integration](https://www.notion.so/profile/integrations) settings, then grant access by selecting the pages you'd like to use.

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

NOTION_TOKEN = "YOUR_NOTION_TOKEN"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="notion_agent",
    instruction="Help users get information from Notion",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@notionhq/notion-mcp-server",
                    ],
                    env={
                        "NOTION_TOKEN": NOTION_TOKEN,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const NOTION_TOKEN = "YOUR_NOTION_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "notion_agent",
    instruction: "Help users get information from Notion",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@notionhq/notion-mcp-server"],
                env: {
                    NOTION_TOKEN: NOTION_TOKEN,
                },
            },
        }),
    ],
});

export { rootAgent };
```

## Available tools

| Tool                     | Description                                                                                                                                                       |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `notion-search`          | Search across your Notion workspace and connected tools like Slack, Google Drive, and Jira. Falls back to basic workspace search if AI features aren’t available. |
| `notion-fetch`           | Retrieves content from a Notion page or database by its URL                                                                                                       |
| `notion-create-pages`    | Creates one or more Notion pages with specified properties and content.                                                                                           |
| `notion-update-page`     | Update a Notion page's properties or content.                                                                                                                     |
| `notion-move-pages`      | Move one or more Notion pages or databases to a new parent.                                                                                                       |
| `notion-duplicate-page`  | Duplicate a Notion page within your workspace. This action is completed async.                                                                                    |
| `notion-create-database` | Creates a new Notion database, initial data source, and initial view with the specified properties.                                                               |
| `notion-update-database` | Update a Notion data source's properties, name, description, or other attributes.                                                                                 |
| `notion-create-comment`  | Add a comment to a page                                                                                                                                           |
| `notion-get-comments`    | Lists all comments on a specific page, including threaded discussions.                                                                                            |
| `notion-get-teams`       | Retrieves a list of teams (teamspaces) in the current workspace.                                                                                                  |
| `notion-get-users`       | Lists all users in the workspace with their details.                                                                                                              |
| `notion-get-user`        | Retrieve your user information by ID                                                                                                                              |
| `notion-get-self`        | Retrieves information about your own bot user and the Notion workspace you’re connected to.                                                                       |

## Additional resources

- [Notion MCP Server Documentation](https://developers.notion.com/docs/mcp)
- [Notion MCP Server Repository](https://github.com/makenotion/notion-mcp-server)
