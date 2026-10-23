---
catalog_title: TableJourney
catalog_description: Find places to eat, food festivals with dates, and bookable food tours in 224 cities
catalog_icon: /integrations/assets/tablejourney.png
catalog_tags: ["mcp"]
---

# TableJourney MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [TableJourney MCP server](https://tablejourney.com/agents/) connects your
ADK agent to [TableJourney](https://tablejourney.com/), a food travel guide to
224 cities. It exposes checked restaurants, cafés, markets and street food (each
with the source it was checked against, the date checked, and opening hours),
food festivals with the dates of their next edition, signature dishes, and
bookable food tours, cooking classes, tickets and hotels, as MCP tools your
agent can call with natural language such as "Plan a food day in Lisbon on
Saturday" or "Which food festivals are on in Italy in November?".

The server is hosted at `https://tablejourney.com/mcp` over streamable HTTP and
needs no API key, so no local install or sign-up is required.

## Use cases

- **Find places to eat**: Search verified venues in a city by dish, cuisine,
  diet, price or opening time, and answer "is it open now" from stored hours.

- **Find food festivals**: List food festivals and Christmas markets by
  country, city or month, with the dates of their next edition.

- **Plan a food day or trip**: Compose a breakfast-to-dinner day in a city, pull
  editorial itineraries, and add food tours, cooking classes or hotels.

## Prerequisites

- A working [ADK installation](/get-started/installation/) with MCP support:
  `pip install "google-adk[mcp]"` for Python, or `@google/adk` with
  `@modelcontextprotocol/sdk` for TypeScript

## Use with agent

The agent connects to the hosted TableJourney MCP server over streamable HTTP.
No authentication is needed. The `tool_filter` below keeps the read-only travel
tools.

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    root_agent = Agent(
        model="gemini-flash-latest",
        name="tablejourney_agent",
        instruction=(
            "You are a food travel assistant. Use the TableJourney tools to find "
            "places to eat, food festivals and food tours. Only recommend places "
            "and dates the tools return, and give the page link for each."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://tablejourney.com/mcp",
                ),
                tool_filter=[
                    "cities",
                    "search_places",
                    "place",
                    "plan_day",
                    "festivals",
                    "dishes",
                    "itineraries",
                    "things_to_do",
                    "experiences",
                    "stays",
                    "tickets",
                    "car_hire",
                ],
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "tablejourney_agent",
        instruction:
            "You are a food travel assistant. Use the TableJourney tools to find " +
            "places to eat, food festivals and food tours. Only recommend places " +
            "and dates the tools return, and give the page link for each.",
        tools: [
            new MCPToolset(
                {
                    type: "StreamableHTTPConnectionParams",
                    url: "https://tablejourney.com/mcp",
                },
                [
                    "cities",
                    "search_places",
                    "place",
                    "plan_day",
                    "festivals",
                    "dishes",
                    "itineraries",
                    "things_to_do",
                    "experiences",
                    "stays",
                    "tickets",
                    "car_hire",
                ],
            ),
        ],
    });

    export { rootAgent };
    ```

## Available tools

Tool | Description
---- | -----------
`cities` | List every covered city with the country and city slugs the other tools accept
`search_places` | Search verified venues by text, city, kind, cuisine, diet, price tier, opening time or location
`place` | Get one venue in full by id: provenance, hours, open now, booking link and nearby venues
`plan_day` | Compose a food day for a city: one open venue per slot from morning to evening
`festivals` | Find food festivals and Christmas markets by country, city or month, with next dates
`dishes` | Signature dishes of a city and where to eat them
`itineraries` | Editorial day-by-day food itineraries for a city
`things_to_do` | One call for a trip: the best food tours, classes and places in a city
`experiences` | Bookable food tours, cooking classes and tastings for a city
`stays` | Hotels and stay partners for a city
`tickets` | Attraction tickets and city passes for a city
`car_hire` | Car hire partners that cover a city

All of the tools above are read-only. Booking links are affiliate links. The
server also has optional `partner_*` tools for TableJourney's referral program,
which the filter above leaves out.

## Additional resources

- [TableJourney MCP server documentation](https://tablejourney.com/agents/)
- [TableJourney MCP docs repository](https://github.com/lewismvaughan/tablejourney-mcp)
- [TableJourney REST API reference](https://tablejourney.com/api/v1/docs)
- [TableJourney homepage](https://tablejourney.com/)
