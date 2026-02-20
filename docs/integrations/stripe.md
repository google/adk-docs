---
catalog_title: Stripe
catalog_description: Manage payments, customers, subscriptions, and invoices
catalog_icon: /adk-docs/integrations/assets/stripe.png
catalog_tags: ["mcp"]
---

# Stripe MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Stripe MCP Server](https://docs.stripe.com/mcp) connects your ADK agent to
the [Stripe](https://stripe.com/) ecosystem. This integration gives your agent
the ability to manage payments, customers, subscriptions, and invoices using
natural language, enabling automated commerce workflows and financial
operations.

## Use cases

- **Automate Payment Operations**: Create payment links, process refunds, and
  list payment intents through conversational commands.

- **Streamline Invoicing**: Generate and finalize invoices, add line items, and
  track outstanding payments without leaving your development environment.

- **Access Business Insights**: Query account balances, list products and
  prices, and search across Stripe resources to make data-driven decisions.

## Prerequisites

- Create a [Stripe account](https://dashboard.stripe.com/register)
- Generate a [Restricted API key](https://dashboard.stripe.com/apikeys) from the
  Stripe Dashboard

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="stripe_agent",
            instruction="Help users manage their Stripe account",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@stripe/mcp",
                                "--tools=all",
                                # (Optional) Specify which tools to enable
                                # "--tools=customers.read,invoices.read,products.read",
                            ],
                            env={
                                "STRIPE_SECRET_KEY": STRIPE_SECRET_KEY,
                            }
                        ),
                        timeout=30,
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

        STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="stripe_agent",
            instruction="Help users manage their Stripe account",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://mcp.stripe.com",
                        headers={
                            "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "stripe_agent",
            instruction: "Help users manage their Stripe account",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "@stripe/mcp",
                            "--tools=all",
                            // (Optional) Specify which tools to enable
                            // "--tools=customers.read,invoices.read,products.read",
                        ],
                        env: {
                            STRIPE_SECRET_KEY: STRIPE_SECRET_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "stripe_agent",
            instruction: "Help users manage their Stripe account",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.stripe.com",
                    header: {
                        Authorization: `Bearer ${STRIPE_SECRET_KEY}`,
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! tip "Best practices"

    Enable human confirmation of tool actions and exercise caution when using
    the Stripe MCP server alongside other MCP servers to mitigate prompt
    injection risks.

## Available tools

Resource | Tool | API
-------- | ---- | ----
Account | `get_stripe_account_info` | Retrieve account
Balance | `retrieve_balance` | Retrieve balance
Coupon | `create_coupon` | Create coupon
Coupon | `list_coupons` | List coupons
Customer | `create_customer` | Create customer
Customer | `list_customers` | List customers
Dispute | `list_disputes` | List disputes
Dispute | `update_dispute` | Update dispute
Invoice | `create_invoice` | Create invoice
Invoice | `create_invoice_item` | Create invoice item
Invoice | `finalize_invoice` | Finalize invoice
Invoice | `list_invoices` | List invoices
Payment Link | `create_payment_link` | Create payment link
PaymentIntent | `list_payment_intents` | List PaymentIntents
Price | `create_price` | Create price
Price | `list_prices` | List prices
Product | `create_product` | Create product
Product | `list_products` | List products
Refund | `create_refund` | Create refund
Subscription | `cancel_subscription` | Cancel subscription
Subscription | `list_subscriptions` | List subscriptions
Subscription | `update_subscription` | Update subscription
Others | `search_stripe_resources` | Search Stripe resources
Others | `fetch_stripe_resources` | Fetch Stripe object
Others | `search_stripe_documentation` | Search Stripe knowledge

## Additional resources

- [Stripe MCP Server Documentation](https://docs.stripe.com/mcp)
- [Stripe MCP Server on GitHub](https://github.com/stripe/ai/tree/main/tools/modelcontextprotocol)
- [Build on Stripe with LLMs](https://docs.stripe.com/building-with-llms)
- [Add Stripe to your agentic workflows](https://docs.stripe.com/agents)
