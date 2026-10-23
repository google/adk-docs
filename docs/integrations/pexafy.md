---
catalog_title: Pexafy
catalog_description: Find free stock photos by description, with license and credit
catalog_icon: /integrations/assets/pexafy.png
catalog_tags: ["mcp", "search"]
---

# Pexafy MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Pexafy MCP Server](https://github.com/Pexafy/pexafy-mcp) connects your ADK
agent to [Pexafy](https://pexafy.com), a semantic search engine for free-to-use
stock photos from Unsplash, Pexels, Pixabay and other libraries. Your agent
describes the photo it needs in plain language and gets back real photographs,
each with its license and the credit line to display.

## Use cases

- **Illustrate content**: Pick a photo for an article, a landing page, a
  newsletter or a slide from a description of what it should show.
- **Find alternatives**: Search for photos that look like a reference image, or
  like a photo found in an earlier search.
- **Credit photographers**: Every result carries its license and a ready-to-use
  credit line.

## Prerequisites

- A Pexafy API key. Create one for free at
  [pexafy.com/dashboard/api-keys/create](https://pexafy.com/dashboard/api-keys/create/).

## Installation

=== "Python"

    ```bash
    pip install "google-adk[mcp]"
    ```

=== "TypeScript"

    ```bash
    npm install @google/adk @modelcontextprotocol/sdk
    ```

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        PEXAFY_API_KEY = "YOUR_PEXAFY_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="pexafy_agent",
            instruction="Find free stock photos for the user and give each photo's credit line",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.pexafy.com/mcp",
                        headers={"Authorization": f"Bearer {PEXAFY_API_KEY}"},
                    ),
                    tool_filter=["search_photos", "search_photos_by_image"],
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const PEXAFY_API_KEY = "YOUR_PEXAFY_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "pexafy_agent",
            instruction: "Find free stock photos for the user and give each photo's credit line",
            tools: [
                new MCPToolset(
                    {
                        type: "StreamableHTTPConnectionParams",
                        url: "https://mcp.pexafy.com/mcp",
                        transportOptions: {
                            requestInit: {
                                headers: { Authorization: `Bearer ${PEXAFY_API_KEY}` },
                            },
                        },
                    },
                    ["search_photos", "search_photos_by_image"],
                ),
            ],
        });

        export { rootAgent };
        ```

The tool filter keeps the two search tools. The other tools are meant for chat
clients where a person views a photo grid or links an account.

## Available tools

Tool | Description
---- | -----------
`search_photos` | Find photos from a one-sentence description of the scene, with an optional orientation filter
`search_photos_by_image` | Find photos that look like a reference: an image URL, base64 image data, or the `photo_id` of an earlier result
`get_photo_file_by_photo_id` | Return one photo from an earlier result as an image file
`get_grid_selected_photos` | Return the photos a person liked in the Pexafy results grid
`connect_account` | Ask the host to offer its flow for connecting a Pexafy account

## Additional resources

- [Pexafy MCP Server Documentation](https://docs.pexafy.com/mcp)
- [Pexafy MCP Server Repository](https://github.com/Pexafy/pexafy-mcp)
- [Pexafy API Documentation](https://docs.pexafy.com)
