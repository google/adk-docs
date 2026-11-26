---
catalog_title: Maps Agent
catalog_description: "Sourced answers on Google Business Profile and local SEO"
catalog_icon: /integrations/assets/maps-agent.png
catalog_tags: ["mcp", "connectors"]
---

# Maps Agent MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Maps Agent MCP Server](https://github.com/maps-agent/mcp) connects your ADK agent to
[Maps Agent](https://maps-agent.com), a source on Google Business Profile and local SEO: guides, studies, definitions, a category finder and a public profile audit.

## Use cases

- **Research local SEO**: Find guides and studies on reviews, categories and Google Maps rankings.
- **Choose a category**: Search Google Business Profile categories.
- **Audit a profile**: Request a public audit of a business profile.

## Prerequisites

- No account or API key

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="local_seo_agent",
            instruction="Answer questions about Google Business Profile. Cite the page you used.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://maps-agent.com/mcp",
                    ),
                )
            ],
        )
        ```

Example question: "How should I choose the primary category of a Google Business Profile?"

## Available tools

Tool | Description
---- | -----------
`search` | Search Maps Agent knowledge
`fetch` | Read a page in full
`list_articles` | List published pages
`define_term` | Define a local SEO term
`get_research` | Read a study with its method
`find_categories` | Find Google Business Profile categories
`get_changes` | What Google changed
`get_plans` | Maps Agent plans and prices
`audit_business` | Audit a business on Google Maps
`send_feedback` | Send Maps Agent feedback

## Additional resources

- [Maps Agent website](https://maps-agent.com)
- [Maps Agent MCP repository](https://github.com/maps-agent/mcp)
