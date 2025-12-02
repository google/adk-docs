# Atlassian

The [Atlassian MCP Server](https://github.com/atlassian/atlassian-mcp-server) ...

## Use cases

...

## Prerequisites

- ...

## Use with agent

=== "Local MCP Server"

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
                            "https://mcp.atlassian.com/v1/sse",
                        ]
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

## Available tools

Tool | Description
---- | -----------
`atlassianUserInfo` | Get information about the user
`getAccessibleAtlassianResources` | Get information about accessible Atlassian resources
`getConfluenceSpaces` | Get information about Confluence spaces
`getConfluencePage` | Get information about a Confluence page
`getPagesInConfluenceSpace` | Get information about pages in a Confluence space
`getConfluencePageFooterComments` | Get information about footer comments in a Confluence page
`getConfluencePageInlineComments` | Get information about inline comments in a Confluence page
`getConfluencePageDescendants` | Get information about descendants of a Confluence page
`createConfluencePage` | Create a new Confluence page
`updateConfluencePage` | Update an existing Confluence page
`createConfluenceFooterComment` | Create a footer comment in a Confluence page
`createConfluenceInlineComment` | Create an inline comment in a Confluence page
`searchConfluenceUsingCql` | Search Confluence using CQL
`getJiraIssue` | Get information about a Jira issue
`editJiraIssue` | Edit a Jira issue
`createJiraIssue` | Create a new Jira issue
`getTransitionsForJiraIssue` | Get transitions for a Jira issue
`transitionJiraIssue` | Transition a Jira issue
`lookupJiraAccountId` | Lookup a Jira account ID
`searchJiraIssuesUsingJql` | Search Jira issues using JQL
`addCommentToJiraIssue` | Add a comment to a Jira issue
`getJiraIssueRemoteIssueLinks` | Get remote issue links for a Jira issue
`getVisibleJiraProjects` | Get visible Jira projects
`getJiraProjectIssueTypesMetadata` | Get issue types metadata for a Jira project
`getJiraIssueTypeMetaWithFields` | Get issue type metadata with fields for a Jira issue
`search` | Search for information
`fetch` | Fetch information

## Configuration

...

## Additional resources

- [Atlassian MCP Server Documentation](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)
- [Atlassian MCP Server Repository](https://github.com/atlassian/atlassian-mcp-server)
