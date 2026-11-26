---
catalog_title: APIVerve
catalog_description: Validate contacts, look up IPs and DNS, and fetch live rates
catalog_icon: /integrations/assets/apiverve.png
catalog_tags: ["data", "mcp"]
---

# APIVerve MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [APIVerve MCP Server](https://docs.apiverve.com/vervekit/mcp) gives your
ADK agent one connection to the APIVerve catalog of about 380 REST APIs. Each
API is exposed as its own MCP tool, so the agent can validate an email address,
look up an IP address or a domain's DNS records, check an SSL certificate,
fetch exchange or VAT rates, or decode a VIN, and get structured JSON back
instead of guessing.

## Use cases

- **Signup and contact validation**: Check that an email address is well
  formed and can receive mail, that a phone number is valid, or that an IBAN is
  correctly structured before the data reaches your systems.
- **Network and security lookups**: Resolve DNS records, geolocate an IP
  address, check an SSL certificate's expiry, or read WHOIS data while
  investigating a domain.
- **Live reference data**: Ground answers in current exchange rates, VAT rates
  by country, or vehicle details decoded from a VIN.

## Prerequisites

- Create a free [APIVerve account](https://dashboard.apiverve.com) and copy
  your API key. No card is required for the free plan.
- Install ADK with MCP support:

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

        APIVERVE_API_KEY = "YOUR_APIVERVE_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="apiverve_agent",
            instruction=(
                "Use the APIVerve tools to validate data and look up facts."
                " Report what the tool returned rather than guessing."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.apiverve.com/v1/mcp",
                        headers={"x-api-key": APIVERVE_API_KEY},
                    ),
                    tool_filter=["EmailValidator", "IPLookup", "DNSLookup"],
                )
            ],
        )
        ```

The server also accepts the key as an `Authorization: Bearer` header.

!!! tip "Load only the tools you need"

    Without `tool_filter`, the server returns a tool for every API in the
    catalog, about 380 of them. Every tool definition is sent to the model on
    each turn, which costs tokens and makes it harder for the model to pick the
    right tool. List the handful of tools your agent needs in `tool_filter`.

## Available tools

Tool names match the API names in the
[APIVerve catalog](https://apiverve.com/marketplace). A few commonly used ones:

Tool | Description
---- | -----------
`EmailValidator` | Checks whether an email address is well formed, whether its domain can receive mail, and whether it is disposable
`PhoneNumberValidator` | Validates a phone number and returns its line type, country, and standard formats
`IPLookup` | Returns the country, region, and time zone of an IP address
`DNSLookup` | Returns the DNS records for a domain
`SSLCertificateChecker` | Returns a domain's SSL certificate details, including issuer and expiry
`WHOISLookup` | Returns the registration details of a domain
`ExchangeRate` | Returns the current exchange rate between two currencies
`VATRates` | Returns the VAT rates for a country
`IBANValidator` | Checks an IBAN's checksum, length, and format for its country
`VINDecoder` | Decodes a vehicle identification number into make, model, and year

## Configuration

Each tool call uses credits from your APIVerve plan. Connecting to the server
and listing tools is free. See [APIVerve pricing](https://apiverve.com/pricing)
for plan limits.

## Additional resources

- [APIVerve MCP Server documentation](https://docs.apiverve.com/vervekit/mcp)
- [APIVerve API catalog](https://apiverve.com/marketplace)
- [APIVerve MCP Server repository](https://github.com/apiverve/mcp-server)
