# GitLab

The
[GitLab MCP Server](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/)
connects your ADK agent directly to [GitLab.com](https://gitlab.com/) or your
self-managed GitLab instance. This integration gives your agent the ability to
manage issues and merge requests, inspect CI/CD pipelines, perform semantic code
searches, and automate development workflows using natural language.

## Use cases

- **Semantic Code Exploration**: Navigate your codebase using natural language.
  Unlike standard text search, you can query the logic and intent of your code
  to quickly understand complex implementations.

- **Accelerate Merge Request Reviews**: Get up to speed on code changes
  instantly. Retrieve full merge request contexts, analyze specific diffs, and
  review commit history to provide faster, more meaningful feedback to your
  team.

- **Troubleshoot CI/CD Pipelines**: Diagnose build failures without leaving your
  chat. Inspect pipeline statuses and retrieve detailed job logs to pinpoint
  exactly why a specific merge request or commit failed its checks.

## Prerequisites

- A GitLab account with a Premium or Ultimate subscription and
  [GitLab Duo](https://docs.gitlab.com/user/gitlab_duo/) enabled
- [Beta and experimental features](https://docs.gitlab.com/user/gitlab_duo/turn_on_off/#turn-on-beta-and-experimental-features)
  enabled in your GitLab settings

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    # Replace with your instance URL if self-hosted (e.g., "gitlab.example.com")
    GITLAB_INSTANCE_URL = "gitlab.com"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="gitlab_agent",
        instruction="Help users get information from GitLab",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "mcp-remote",
                            f"https://{GITLAB_INSTANCE_URL}/api/v4/mcp",
                            "--static-oauth-client-metadata",
                            "{\"scope\": \"mcp\"}",
                        ],
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

!!! note

    When you run this agent for the first time, a browser window will open
    automatically (and an authorization URL will be printed) requesting OAuth
    permissions. You must approve this request to allow the agent to access your
    GitLab data.

## Available tools

Tool | Description
---- | -----------
`get_mcp_server_version` | Returns the current version of the GitLab MCP server
`create_issue` | Creates a new issue in a GitLab project
`get_issue` | Retrieves detailed information about a specific GitLab issue
`create_merge_request` | Creates a merge request in a project
`get_merge_request` | Retrieves detailed information about a specific GitLab merge request
`get_merge_request_commits` | Retrieves the list of commits in a specific merge request
`get_merge_request_diffs` | Retrieves the diffs for a specific merge request
`get_merge_request_pipelines` | Retrieves the pipelines for a specific merge request
`get_pipeline_jobs` | Retrieves the jobs for a specific CI/CD pipeline
`gitlab_search` | Searches for a term across the entire GitLab instance with the search API
`semantic_code_search` | Searches for relevant code snippets in a project

## Additional resources

- [GitLab MCP Server Documentation](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/)
