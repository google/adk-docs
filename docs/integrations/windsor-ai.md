---
catalog_title: Windsor.ai
catalog_description: Query and analyze marketing, sales, and customer data from 325+ platforms
catalog_icon: /integrations/assets/windsor-ai.png
catalog_tags: ["mcp", "data"]
---

# Windsor.ai MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Windsor MCP Server](https://github.com/windsor-ai/windsor_mcp) connects
your ADK agent to [Windsor.ai](https://windsor.ai/), a data integration
platform that unifies marketing, sales, and customer data from 325+ sources.
This integration gives your agent the ability to query and analyze cross-channel
business data using natural language, without writing SQL or custom scripts.

## Use cases

- **Marketing Performance Analysis**: Analyze campaign performance across
  channels like Facebook Ads, Google Ads, TikTok Ads, and more. Ask questions
  like "What campaigns had the best ROAS last month?" and get instant insights.

- **Cross-Channel Reporting**: Generate comprehensive reports combining data
  from multiple platforms such as GA4, Shopify, Salesforce, and HubSpot to get
  a unified view of business performance.

- **Budget Optimization**: Identify underperforming campaigns, detect budget
  inefficiencies, and get AI-driven recommendations for spend allocation across
  advertising channels.

## Prerequisites

- A [Windsor.ai](https://windsor.ai/) account with connected data sources
- A Windsor.ai API key (obtain from [onboard.windsor.ai](https://onboard.windsor.ai))

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/windsor-ai/001-use-with-agent.py"
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/windsor-ai/002-use-with-agent.ts"
        ```

## Capabilities

Windsor MCP provides a natural language interface to your integrated business
data. Rather than exposing discrete tools, it interprets your questions and
returns structured insights from your connected data sources.

Capability | Description
---------- | -----------
Data querying | Query normalized data from any of your 325+ connected platforms
Performance analysis | Analyze KPIs, trends, and campaign metrics across channels
Report generation | Create marketing dashboards and cross-channel performance reports
Budget analysis | Identify spend inefficiencies and get optimization recommendations
Anomaly detection | Detect outliers and unusual patterns in performance data

## Supported data sources

Windsor.ai connects to 325+ platforms, including:

- **Advertising**: Facebook Ads, Google Ads, TikTok Ads, LinkedIn Ads, Microsoft Ads
- **Analytics**: Google Analytics 4, Adobe Analytics
- **CRM**: Salesforce, HubSpot
- **E-commerce**: Shopify
- **And more**: See the [full list of connectors](https://windsor.ai/) on the
  Windsor.ai website

## Additional resources

- [Windsor MCP Server Repository](https://github.com/windsor-ai/windsor_mcp)
- [Windsor.ai Documentation](https://windsor.ai/documentation/windsor-mcp/)
- [Windsor MCP Introduction](https://windsor.ai/introducing-windsor-mcp/)
- [Windsor MCP Use Cases & Examples](https://windsor.ai/how-to-use-windsor-mcp-examples-use-cases/)
