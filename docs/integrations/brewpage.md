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
publication gets a shareable HTTPS link. The remote server needs no account or
API key, so an agent can publish the reports, pages and data it produces and
return a link to the user.

## Use cases

- **Share agent output**: Publish a generated report, summary or HTML page and
  give the user a link instead of a long chat message.
- **Host small sites**: Publish a multi-file HTML site and update it in place
  later with the owner token returned at creation.
- **Store structured results**: Save JSON documents or key-value entries that
  other agents or scripts can read by namespace and ID.

## Prerequisites

- A [Gemini API key](https://aistudio.google.com/apikey) for the agent's model.
- No BrewPage account or API key is needed. Publications are private (unlisted)
  unless the agent sends `namespace="public"`.

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
                "page link. Keep pages private unless the user asks for a public page."
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
                "page link. Keep pages private unless the user asks for a public page.",
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

Tool | Description
---- | -----------
`publish_html` | Publish HTML, Markdown, code or JSON as a page
`update_html` | Update an existing page with its owner token
`get_page` | Fetch the stored content of a page
`publish_site` | Publish a multi-file HTML site
`republish_site` | Replace the files of an existing site at the same link
`publish_file` | Upload a file from a URL
`publish_json` | Publish a JSON document
`get_json` | Fetch a JSON document
`update_json` | Update a JSON document with its owner token
`publish_kv` | Create a key-value store with its first entry
`set_kv` | Set or update a key in a key-value store
`get_kv` | Fetch a value from a key-value store
`delete_resource` | Delete a page, site, file, JSON document or key-value store
`set_title` | Rename a page or site
`set_visibility` | Hide or show a public publication in the gallery
`update_hosting` | Change the delivery mode of a publication
`search_gallery` | Search the public gallery
`get_limits` | Read the current size, count and expiry limits
`get_stats` | Read platform-wide usage statistics

The server also exposes profile and custom-domain tools (`bind_token`,
`mint_token`, `set_domain`, `list_domains`, `check_domain`, `remove_domain`)
for users with a BrewPage profile.

## Additional resources

- [BrewPage](https://brewpage.app)
- [BrewPage API and MCP documentation](https://kochetkov-ma.github.io/brewpage-openapi/)
- [BrewPage MCP server repository](https://github.com/kochetkov-ma/brewpage-openapi)
- [brewpage-mcp on npm](https://www.npmjs.com/package/brewpage-mcp)
