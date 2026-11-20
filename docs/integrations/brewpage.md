---
catalog_title: BrewPage
catalog_description: Publish HTML, Markdown, JSON and files as shareable links
catalog_icon: /integrations/assets/brewpage.png
catalog_tags: ["mcp"]
---

# BrewPage MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [BrewPage MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
connects your ADK agent to [BrewPage](https://brewpage.app), a hosting service
for HTML pages, Markdown, JSON documents, key-value data and files. Each
publication gets a shareable HTTPS link. Connect ADK to `https://brewpage.app/mcp`
over Streamable HTTP. The hosted server supports anonymous publication and
optional OAuth for a BrewPage profile.

## Use cases

- **Share agent output**: Publish a generated report, summary or HTML page and
  give the user a link instead of a long chat message.
- **Host small sites**: Publish a multi-file HTML site and update it in place
  later with the owner token returned at creation.
- **Store structured results**: Save JSON documents or key-value entries that
  other agents or scripts can read by namespace and ID.

## Prerequisites

- A [Gemini API key](https://aistudio.google.com/apikey) for the agent's model.
- Anonymous publishing requires no BrewPage account or API key. An ordinary
  publication is unlisted and anyone with its link can open it. Set `public: true`
  when the user asks to list the publication publicly.

## Installation

Install ADK with the `mcp` extra, which provides the MCP classes:

```bash
pip install "google-adk[mcp]"
```

For TypeScript, install the MCP SDK next to ADK:

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

        root_agent = Agent(
            model="gemini-flash-latest",
            name="brewpage_agent",
            instruction=(
                "Publish the content the user asks for to BrewPage and reply with the "
                "page link. Keep pages unlisted unless the user asks for public listing."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://brewpage.app/mcp",
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "brewpage_agent",
            instruction:
                "Publish the content the user asks for to BrewPage and reply with the " +
                "page link. Keep pages unlisted unless the user asks for public listing.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://brewpage.app/mcp",
                }),
            ],
        });

        export { rootAgent };
        ```

Each publish call returns the page link, a private management link and an
owner token. The agent needs the owner token to update or delete that
publication later.

## Available tools

BrewPage MCP 3.0.0 advertises 13 tools over the hosted connection.

Tools | Purpose
----- | -------
`publish`, `list_publications`, `read_publication` | Publish content, list publications and read content or statistics
`update_publication`, `publication_settings`, `delete_publication` | Revise content, change settings or delete a publication
`read_page_data`, `write_page_data`, `delete_page_data` | Work with saved Page data, including visitor responses
`domains`, `account`, `notifications` | Manage custom domains, account access and publication notifications
`get_guide` | Read instructions and examples for a specific operation

## Additional resources

- [BrewPage](https://brewpage.app)
- [BrewPage API and MCP documentation](https://kochetkov-ma.github.io/brewpage-openapi/)
- [BrewPage MCP server repository](https://github.com/kochetkov-ma/brewpage-openapi)
- [brewpage-mcp on npm](https://www.npmjs.com/package/brewpage-mcp)
