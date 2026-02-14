# Atlassian MCP tool for ADK

Supported in ADKPythonTypeScript

The [Atlassian MCP Server](https://github.com/atlassian/atlassian-mcp-server) connects your ADK agent to the [Atlassian](https://www.atlassian.com/) ecosystem, bridging the gap between project tracking in Jira and knowledge management in Confluence. This integration gives your agent the ability to manage issues, search and update documentation pages, and streamline collaboration workflows using natural language.

## Use cases

- **Unified Knowledge Search**: Search across both Jira issues and Confluence pages simultaneously to find project specs, decisions, or historical context.
- **Automate Issue Management**: Create, edit, and transition Jira issues, or add comments to existing tickets.
- **Documentation Assistant**: Retrieve page content, generate drafts, or add inline comments to Confluence documents directly from your agent.

## Prerequisites

- Sign up for an [Atlassian account](https://id.atlassian.com/signup)
- An Atlassian Cloud site with Jira and/or Confluence

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


root_agent = Agent(
    model="gemini-2.5-pro",
    name="atlassian_agent",
    instruction="Help users work with data in Atlassian products",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.atlassian.com/v1/mcp",
                    ]
                ),
                timeout=30,
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "atlassian_agent",
    instruction: "Help users work with data in Atlassian products",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    "https://mcp.atlassian.com/v1/mcp",
                ],
            },
        }),
    ],
});

export { rootAgent };
```

Note

When you run this agent for the first time, a browser window opens automatically to request access via OAuth. Alternatively, you can use the authorization URL printed in the console. You must approve this request to allow the agent to access your Atlassian data.

## Available tools

| Tool                               | Description                                                |
| ---------------------------------- | ---------------------------------------------------------- |
| `atlassianUserInfo`                | Get information about the user                             |
| `getAccessibleAtlassianResources`  | Get information about accessible Atlassian resources       |
| `getJiraIssue`                     | Get information about a Jira issue                         |
| `editJiraIssue`                    | Edit a Jira issue                                          |
| `createJiraIssue`                  | Create a new Jira issue                                    |
| `getTransitionsForJiraIssue`       | Get transitions for a Jira issue                           |
| `transitionJiraIssue`              | Transition a Jira issue                                    |
| `lookupJiraAccountId`              | Lookup a Jira account ID                                   |
| `searchJiraIssuesUsingJql`         | Search Jira issues using JQL                               |
| `addCommentToJiraIssue`            | Add a comment to a Jira issue                              |
| `getJiraIssueRemoteIssueLinks`     | Get remote issue links for a Jira issue                    |
| `getVisibleJiraProjects`           | Get visible Jira projects                                  |
| `getJiraProjectIssueTypesMetadata` | Get issue types metadata for a Jira project                |
| `getJiraIssueTypeMetaWithFields`   | Get issue type metadata with fields for a Jira issue       |
| `getConfluenceSpaces`              | Get information about Confluence spaces                    |
| `getConfluencePage`                | Get information about a Confluence page                    |
| `getPagesInConfluenceSpace`        | Get information about pages in a Confluence space          |
| `getConfluencePageFooterComments`  | Get information about footer comments in a Confluence page |
| `getConfluencePageInlineComments`  | Get information about inline comments in a Confluence page |
| `getConfluencePageDescendants`     | Get information about descendants of a Confluence page     |
| `createConfluencePage`             | Create a new Confluence page                               |
| `updateConfluencePage`             | Update an existing Confluence page                         |
| `createConfluenceFooterComment`    | Create a footer comment in a Confluence page               |
| `createConfluenceInlineComment`    | Create an inline comment in a Confluence page              |
| `searchConfluenceUsingCql`         | Search Confluence using CQL                                |
| `search`                           | Search for information                                     |
| `fetch`                            | Fetch information                                          |

## Additional resources

- [Atlassian MCP Server Repository](https://github.com/atlassian/atlassian-mcp-server)
- [Atlassian MCP Server Documentation](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)
