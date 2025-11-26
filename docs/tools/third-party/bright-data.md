# Bright Data

The [Bright Data MCP Server](https://github.com/brightdata/brightdata-mcp)
connects your ADK agent to Bright Data's web data platform. This
tool gives your agent the ability to perform real-time web searches, scrape
webpages, extract structured data, control browsers remotely, and access
pre-built data feeds from popular platforms.

## Use cases

- **Real-Time Web Search**: Perform optimized web searches to get up-to-date
  information in AI-friendly formats (JSON/Markdown).

- **Structured Data Extraction**: Use AI-powered extraction to convert any
  webpage into clean, structured JSON data with optional custom prompts.

- **Browser Automation**: Control real browsers remotely for complex
  interactions, JavaScript rendering, and dynamic content extraction.

- **Pre-Built Data APIs**: Access 60+ structured datasets from popular platforms
  including Amazon, LinkedIn, Instagram, TikTok, Google Maps, and more.

- **Advertisement Analysis**: Extract and analyze advertisements from webpages
  using industry-standard ad blocking filter lists.

## Prerequisites

- Sign up for a [Bright Data account](https://brightdata.com/) to obtain an API
  token.
- Refer to the
  [documentation](https://docs.brightdata.com/mcp-server/overview) for more
  information.
- The server offers a **free tier with 5,000 requests/month**, which is useful for
  prototyping and everyday workflows.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    BRIGHTDATA_API_TOKEN = "YOUR_BRIGHTDATA_API_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="brightdata_agent",
        instruction="Help users access web data using Bright Data",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "@brightdata/mcp",
                        ],
                        env={
                            "API_TOKEN": BRIGHTDATA_API_TOKEN,
                            "PRO_MODE": "true",  # Optional: Enable all 60+ tools
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

=== "Remote MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

    BRIGHTDATA_API_TOKEN = "YOUR_BRIGHTDATA_API_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="brightdata_agent",
        instruction="""Help users access web data using Bright Data""",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url=f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_API_TOKEN}",
                ),
            )
        ],
    )
    ```

## Example usage

Once your agent is set up and running, you can interact with it through the
command-line interface or web interface. Here are some examples:

**Sample agent prompts:**

> Get me the current price and details of the iPhone 15 Pro on Amazon

> Search for "climate change news 2025" on Google and summarize the top 5
> results

> Scrape the homepage of techcrunch.com and extract all article headlines and
> links

The agent automatically calls the appropriate Bright Data tools to provide
comprehensive answers, making it easy to access real-time web data without
manual navigation or worrying about getting blocked.

## Available tools

The Bright Data MCP server operates in two modes:

### Rapid Mode (Free Tier - Default)

Tool <img width="100px"/> | Description
---- | -----------
`search_engine` | Scrape Google, Bing, or Yandex SERPs as JSON or Markdown.
`scrape_as_markdown` | Convert webpages into clean Markdown with built-in unblocking.
`scrape_as_html` | Return raw HTML from webpages while bypassing blockers.
`extract` | Transform Markdown output into structured JSON with custom prompts.
`session_stats` | View session usage statistics and tool call counts.

### Pro Mode (60+ Additional Tools)

Enable Pro Mode by setting `PRO_MODE=true` in environment variables to access:

**Batch Operations:**
- `search_engine_batch`: Run up to 10 search queries simultaneously.
- `scrape_batch`: Scrape up to 10 URLs simultaneously.

**Browser Automation:**
- `scraping_browser.*`: Full browser control for complex interactions.
- Navigate, click, type, scroll, take screenshots, and more.

**Web Data APIs (60+ Structured Datasets):**

- **E-commerce**: `web_data_amazon_product`, `web_data_walmart_product`,
  `web_data_ebay_product`, `web_data_etsy_products`, `web_data_bestbuy_products`,
  `web_data_zara_products`
- **Social Media**: `web_data_linkedin_person_profile`,
  `web_data_instagram_profiles`, `web_data_facebook_posts`,
  `web_data_tiktok_profiles`, `web_data_x_posts`, `web_data_reddit_posts`
- **Business Intelligence**: `web_data_linkedin_company_profile`,
  `web_data_crunchbase_company`, `web_data_zoominfo_company_profile`
- **Search & Reviews**: `web_data_amazon_product_search`,
  `web_data_amazon_product_reviews`, `web_data_google_maps_reviews`,
  `web_data_facebook_company_reviews`
- **Maps & Local**: `web_data_google_maps_reviews`,
  `web_data_zillow_properties_listing`, `web_data_booking_hotel_listings`
- **App Stores**: `web_data_google_play_store`, `web_data_apple_app_store`
- **Media & News**: `web_data_youtube_videos`, `web_data_youtube_comments`,
  `web_data_reuter_news`
- **Developer Tools**: `web_data_github_repository_file`
- **Finance**: `web_data_yahoo_finance_business`

All Web Data API tools return cached or fresh structured data in JSON format,
often more reliable than real-time scraping.

## Configuration options

The Bright Data MCP server supports several environment variables for
customization:

Variable | Description | Default
---- | ---- | ----
`API_TOKEN` | Your Bright Data API token (required) | -
`PRO_MODE` | Enable all 60+ advanced tools | `false`
`RATE_LIMIT` | Custom rate limiting (e.g., "100/1h", "50/30m") | No limit
`WEB_UNLOCKER_ZONE` | Custom Web Unlocker zone name | `mcp_unlocker`
`BROWSER_ZONE` | Custom Browser API zone name | `mcp_browser`

## Additional resources

- [Bright Data MCP Server Documentation](https://docs.brightdata.com/mcp-server/overview)
- [Bright Data MCP Server Repository](https://github.com/brightdata/brightdata-mcp)
- [Complete Tool Documentation](https://github.com/brightdata-com/brightdata-mcp/blob/main/assets/Tools.md)
- [Example Use Cases](https://github.com/brightdata-com/brightdata-mcp/blob/main/examples)
- [Interactive Playground](https://brightdata.com/ai/playground-chat)
