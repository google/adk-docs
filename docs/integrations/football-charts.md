---
catalog_title: Football Charts
catalog_description: Query football results, league tables, fixtures, and projections
catalog_icon: /integrations/assets/football-charts.png
catalog_tags: ["mcp", "data"]
---

# Football Charts MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Football Charts MCP server](https://github.com/ddevetak/footballcharts-mcp)
connects your ADK agent to [Football Charts](https://www.football-charts.com/),
a football (soccer) statistics site. It exposes results, league tables,
fixtures, goal timing, and season projections for 93 leagues in 42 countries,
including lower divisions and four women's leagues, as MCP tools. Your agent can
then answer questions such as "Show me the Serie C Group A table" or "When does
Flamengo score most of their goals?".

The server is hosted at `https://mcp.football-charts.com/mcp` over streamable
HTTP. It needs no account or API key, so the agent connects to the remote
endpoint directly.

## Use cases

- **League tables and form**: Get the standings of a league season with points,
  goal difference, last-five form, and expected points.

- **Results and goal timing**: Look up finished matches with full-time and
  half-time scores and first-goal minutes, or compare when teams score across
  15-minute periods.

- **Fixtures and match detail**: List upcoming matches with kick-off times and
  the probabilities a baseline statistical model assigns to each outcome.

- **Season projections**: See title, top-four, and relegation probabilities
  from 10,000 simulations of the rest of the season.

## Prerequisites

- A working [ADK installation](/get-started/installation/) with MCP support.
  For Python, install the `mcp` extra with `pip install "google-adk[mcp]"`. For
  TypeScript, add the MCP SDK with
  `npm install @google/adk @modelcontextprotocol/sdk`.
- No account or API key. An optional free key gives you your own daily quota
  (see [Configuration](#configuration)).

## Use with agent

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    root_agent = Agent(
        model="gemini-flash-latest",
        name="football_charts_agent",
        instruction=(
            "You are a football statistics assistant. Use the Football Charts "
            "tools to look up results, league tables, fixtures, goal timing, "
            "and season projections."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://mcp.football-charts.com/mcp",
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "football_charts_agent",
        instruction:
            "You are a football statistics assistant. Use the Football Charts " +
            "tools to look up results, league tables, fixtures, goal timing, " +
            "and season projections.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://mcp.football-charts.com/mcp",
            }),
        ],
    });

    export { rootAgent };
    ```

## Available tools

Tool | Description
---- | -----------
`about_football_charts` | Describe the leagues and data covered, what is not held, and the free-tier limits
`list_leagues` | List the 93 leagues with their keys and available seasons
`get_league_table` | Get a league season's standings with form and expected points
`get_results` | Get finished matches with full-time and half-time scores and first-goal minutes
`get_fixtures` | Get upcoming matches with kick-off times and model probabilities
`get_match` | Get one match in full: model probabilities, team ratings, and the score once played
`get_season_projection` | Get title, top-four, and relegation probabilities from 10,000 simulations
`get_team` | Get one team's season: table row, match log, and goal timing
`get_goal_timing` | Get goals per 15-minute period for every team in a league season
`get_track_record` | Get the model's public calibration record: hit rate, Brier score, and reliability

## Configuration

Without a key, all keyless users share the hosted server's daily request budget.
To get your own quota of 5,000 requests per day, register a free key at
[football-charts.com/developers](https://www.football-charts.com/developers) and
send it as a bearer token:

=== "Python"

    ```python
    McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://mcp.football-charts.com/mcp",
            headers={"Authorization": "Bearer YOUR_FOOTBALL_CHARTS_KEY"},
        ),
    )
    ```

=== "TypeScript"

    ```typescript
    new MCPToolset({
        type: "StreamableHTTPConnectionParams",
        url: "https://mcp.football-charts.com/mcp",
        transportOptions: {
            requestInit: {
                headers: { Authorization: "Bearer YOUR_FOOTBALL_CHARTS_KEY" },
            },
        },
    });
    ```

The free tier covers the current and previous season of every league.

## Additional resources

- [Football Charts developer documentation](https://www.football-charts.com/developers)
- [Football Charts MCP server repository](https://github.com/ddevetak/footballcharts-mcp)
- [Football Charts homepage](https://www.football-charts.com/)
