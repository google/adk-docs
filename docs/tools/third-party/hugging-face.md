# Hugging Face

The [Hugging Face MCP Server](https://github.com/huggingface/hf-mcp-server) can be used to connect
your ADK agent to the Hugging Face Hub and thousands of Gradio AI Applications.

## Use cases

- **Discover AI/ML Assets**: Search and filter the Hub for models, datasets, and
  papers based on tasks, libraries, or keywords.
- **Build Multi-Step Workflows**: Chain tools together, such as transcribing
  audio with one tool and then summarizing the resulting text with another.
- **Find AI Applications**: Search for Gradio Spaces that can perform a specific
  task, like background removal or text-to-speech.

## Prerequisites

- Create a [user access token](https://huggingface.co/settings/tokens) in
  Hugging Face. Refer to the
  [documentation](https://huggingface.co/docs/hub/en/security-tokens) for more
  information.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="hugging_face_agent",
        instruction="Help users get information from Hugging Face",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@llmindset/hf-mcp-server",
                        ],
                        env={
                            "HF_TOKEN": "YOUR-HUGGING-FACE-TOKEN",
                        }
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
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

    HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="hugging_face_agent",
        instruction="""Help users get information from Hugging Face""",
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://huggingface.co/mcp",
                    headers={
                        "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
                    },
                ),
            )
        ],
    )
    ```

## Available tools

Tool | Description
---- | -----------
Spaces Semantic Search | Find the best AI Apps via natural language queries
Papers Semantic Search | Find ML Research Papers via natural language queries
Model Search | Search for ML models with filters for task, library, etc…
Dataset Search | Search for datasets with filters for author, tags, etc…
Documentation Semantic Search | Search the Hugging Face documentation library
Hub Repository Details | Get detailed information about Models, Datasets and Spaces

## Configuration

To configure which tools are available in your Hugging Face Hub MCP server,
visit the [MCP Settings Page](https://huggingface.co/settings/mcp) in your
Hugging Face account.


To configure the local MCP server, you can use the following environment
variables:

- `TRANSPORT`: The transport type to use (`stdio`, `sse`, `streamableHttp`, or
  `streamableHttpJson`)
- `DEFAULT_HF_TOKEN`: ⚠️ Requests are serviced with the `HF_TOKEN` received in
  the Authorization: Bearer header. The DEFAULT_HF_TOKEN is used if no header
  was sent. Only set this in Development / Test environments or for local STDIO
  Deployments. ⚠️
- If running with stdio transport, `HF_TOKEN` is used if `DEFAULT_HF_TOKEN` is
  not set.
- `HF_API_TIMEOUT`: Timeout for Hugging Face API requests in milliseconds
  (default: 12500ms / 12.5 seconds)
- `USER_CONFIG_API`: URL to use for User settings (defaults to Local front-end)
- `MCP_STRICT_COMPLIANCE`: set to True for GET 405 rejects in JSON Mode (default
  serves a welcome page).
- `AUTHENTICATE_TOOL`: whether to include an Authenticate tool to issue an OAuth
  challenge when called
- `SEARCH_ENABLES_FETCH`: When set to true, automatically enables the
  hf_doc_fetch tool whenever hf_doc_search is enabled


## Additional resources

- [Hugging Face MCP Server Repository](https://github.com/huggingface/hf-mcp-server)
- [Hugging Face MCP Server Documentation](https://huggingface.co/docs/hub/en/hf-mcp-server)
