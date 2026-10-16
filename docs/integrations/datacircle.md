---
catalog_title: Datacircle
catalog_description: Fetch live LinkedIn profiles from B2B data APIs, with no markup
catalog_icon: /integrations/assets/datacircle.png
catalog_tags: ["data", "mcp"]
---

# Datacircle MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Datacircle MCP server](https://docs.datacircle.dev/mcp-server) connects
your ADK agent to [Datacircle](https://datacircle.dev). Datacircle is a data
co-op. Query your favorite B2B data APIs through us. Same request, same price,
no markup. Right now we have 3 live LinkedIn profile APIs that we trust:
Up2Data, HarvestAPI and Fetchin.

The server is hosted at `https://api.datacircle.dev/mcp` over streamable HTTP,
so there is nothing to install on the server side. Your agent calls it with a
Datacircle API key, and each call is paid from that account's balance.

## Use cases

- **Look up a profile**: Give the agent a LinkedIn profile URL and get the
  person's name, headline, location, current company and title, positions,
  education, and skills. Each request goes to the provider and gets the
  profile as it is today.

- **Pick the provider**: Up2Data answers by default, and a profile it can't
  find is free. Use HarvestAPI or Fetchin when Up2Data answers `429`,
  HarvestAPI when the user needs the member's interests, which only it
  returns. The agent chooses with the tool's `provider` argument.

- **Watch the spend**: Read the account's balance before or after a batch of
  lookups, so the agent can stop when the balance runs low.

- **Get the flat file**: Every morning, you get the flat file of your data
  plus everyone else's. Add $50 to your account: you get $50 of API PLUS the
  flat file. List the files and get a download link for one.

## Prerequisites

- A Datacircle account. Sign up at [datacircle.dev](https://datacircle.dev)
  with your work email: a $5 credit, that's 2,105 LinkedIn profiles at $2.375
  per 1,000.
- Your API key, from your dashboard at datacircle.dev (see the
  [quickstart](https://docs.datacircle.dev/quickstart)).
- ADK with its MCP extra, without which the MCP classes are not importable:

    ```bash
    pip install "google-adk[mcp]"
    ```

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        DATACIRCLE_API_KEY = "YOUR_DATACIRCLE_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="datacircle_agent",
            instruction="Help users look up LinkedIn profiles with Datacircle",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.datacircle.dev/mcp",
                        headers={
                            "Authorization": f"Bearer {DATACIRCLE_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

Then ask the agent, for example: "Get the LinkedIn profile at
https://www.linkedin.com/in/williamhgates and tell me where he works now."

## Available tools

Tool | Description
---- | -----------
`get_linkedin_profile` | Fetch one person's LinkedIn profile by its URL, through `up2data` (the default), `harvestapi` or `fetchin`
`get_balance` | Read the account's balance in USD (free)
`list_files` | List the data files the account can download, and whether each is unlocked (free)
`get_download_link` | Get a download link for one file from `list_files`, by its id (free)
`add_funds` | Start a Stripe Checkout that adds $5 to $10,000 to the balance; it returns a link for the user to open and pay, and nothing is charged until they do

## Additional resources

- [Datacircle MCP Server Documentation](https://docs.datacircle.dev/mcp-server)
- [Datacircle API Reference](https://docs.datacircle.dev/api-reference/up2data/enrich-one-linkedin-profile)
- [Datacircle Pricing](https://docs.datacircle.dev/pricing)
