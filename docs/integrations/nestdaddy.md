---
catalog_title: NestDaddy
catalog_description: Live web search, real-time news and full page text from an independent search index
catalog_icon: /integrations/assets/nestdaddy.png
catalog_tags: ["search", "mcp"]
---

# NestDaddy MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [NestDaddy MCP Server](https://nestdaddy.com/mcp) connects your ADK agent
to [NestDaddy](https://nestdaddy.com), a web search and news API that runs its
own crawler and search index. This integration gives your agent current
information from the web: search results, real-time news from around the
world, the full text of any page, and research papers, through one remote MCP
endpoint.

## Use cases

- **Answer with Current Information**: Let your agent search the web and the
  news before it answers, so replies about recent events, releases or prices
  are based on today's sources instead of the model's training cutoff.

- **Research with Sources**: Search, then read the full text of the most
  relevant pages and cite their URLs, for research assistants, briefings and
  fact checks.

- **Monitor News by Topic or Country**: Track news about a company, a product
  or a market, filtered by country, to power alerts, digests and summaries.

## Prerequisites

- Create a [NestDaddy account](https://nestdaddy.com/register)
- Copy your API key from the
  [NestDaddy Dashboard](https://nestdaddy.com/dashboard). The free plan
  includes 1,000 credits a month.

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        NESTDADDY_API_KEY = "YOUR_NESTDADDY_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="nestdaddy_agent",
            instruction=(
                "Use NestDaddy to search the web and the news before answering "
                "questions about recent events. Cite the URLs you used."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.nestdaddy.com/mcp",
                        headers={
                            "Authorization": f"Bearer {NESTDADDY_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

    !!! tip "Limit the tools"

        The server exposes nine tools. To keep the model's context small, pass
        only the ones you need, for example
        `tool_filter=["web_search", "news_search", "read_page"]` to `McpToolset`.

## Available tools

Tool | Description
---- | -----------
`web_search` | Search the web with NestDaddy's own index: title, URL, snippet and domain of each result
`news_search` | Find news articles by key words, newest and best match first
`news` | Latest news headlines with links and summaries, refreshed every few minutes
`country_news` | Latest local news from one country, by two-letter country code
`read_page` | Read the full text of a web page or news article, without menus or ads
`research_papers` | Search scientific papers from arXiv, PubMed, OpenAlex, CrossRef and more
`ai_tools` | New AI models, apps and open-source projects, updated daily
`software` | Software and developer tools with their current version, updated daily
`games` | Top-selling, new and upcoming games, updated daily

## Resources

- [NestDaddy MCP Server](https://nestdaddy.com/mcp)
- [NestDaddy API Documentation](https://nestdaddy.com/apis)
- [Get an API key](https://nestdaddy.com/dashboard)
