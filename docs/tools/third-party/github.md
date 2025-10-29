# GitHub

The [GitHub MCP Server](https://github.com/github/github-mcp-server) connects AI
tools directly to GitHub's platform. This gives your ADK agent the ability to
read repositories and code files, manage issues and PRs, analyze code, and
automate workflows using natural language.

## Use cases

- **Repository Management**: Browse and query code, search files, analyze
  commits, and understand project structure across any repository you have
  access to.
- **Issue & PR Automation**: Create, update, and manage issues and pull
  requests. Let AI help triage bugs, review code changes, and maintain project
  boards.
- **Code Analysis**: Examine security findings, review Dependabot alerts,
  understand code patterns, and get comprehensive insights into your codebase.

## Prerequisites

- Create a
  [Personal Access Token](https://github.com/settings/personal-access-tokens/new) in GitHub. Refer to the [documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for more information.

## Use with agent

=== "Remote MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

    GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="github_agent",
        instruction="Help users get information from GitHub",
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://api.githubcopilot.com/mcp/",
                    headers={
                        "Authorization": f"Bearer {GITHUB_TOKEN}",
                        "X-MCP-Toolsets": "all",
                        "X-MCP-Readonly": "true"
                    },
                ),
            )
        ],
    )
    ```

## Available tools

Tool | Description
---- | -----------
`context` | Tools that provide context about the current user and GitHub context you are operating in
`copilot` | Copilot related tools (e.g. Copilot Coding Agent)
`copilot_spaces` | Copilot Spaces related tools
`actions` | GitHub Actions workflows and CI/CD operations
`code_security` | Code security related tools, such as GitHub Code Scanning
`dependabot` | Dependabot tools
`discussions` | GitHub Discussions related tools
`experiments` | Experimental features that are not considered stable yet
`gists` | GitHub Gist related tools
`github_support_docs_search` | Search docs to answer GitHub product and support questions
`issues` | GitHub Issues related tools
`labels` | GitHub Labels related tools
`notifications` | GitHub Notifications related tools
`orgs` | GitHub Organization related tools
`projects` | GitHub Projects related tools
`pull_requests` | GitHub Pull Request related tools
`repos` | GitHub Repository related tools
`secret_protection` | Secret protection related tools, such as GitHub Secret Scanning
`security_advisories` | Security advisories related tools
`stargazers` | GitHub Stargazers related tools
`users` | GitHub User related tools

## Configuration

The Remote GitHub MCP server has optional headers that can be used to configure
available toolsets and read-only mode:

- `X-MCP-Toolsets`: Comma-separated list of toolsets to enable. (e.g., "repos,issues")
    - If the list is empty, default toolsets will be used. If a bad toolset is
      provided, the server will fail to start and emit a 400 bad request status.
      Whitespace is ignored.

- `X-MCP-Readonly`: Enables only "read" tools.
    - If this header is empty, "false", "f", "no", "n", "0", or "off" (ignoring
      whitespace and case), it will be interpreted as false. All other values
      are interpreted as true.


## Additional resources

- [GitHub MCP Server Repository](https://github.com/github/github-mcp-server)
- [Remote GitHub MCP Server Documentation](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [Policies and Governance for the GitHub MCP Server](https://github.com/github/github-mcp-server/blob/main/docs/policies-and-governance.md)
