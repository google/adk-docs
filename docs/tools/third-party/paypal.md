# Paypal

The [Paypal MCP Server](https://github.com/paypal/paypal-mcp-server) connects
your ADK agent to the [PayPal](https://www.paypal.com/) ecosystem. This
integration gives your agent the ability to manage payments, invoices,
subscriptions, and disputes using natural language, enabling automated commerce
workflows and business insights.

## Use cases

- **Streamline Financial Operations**: Create orders, send invoices, and process
  refunds directly through chat without switching context. You can instruct your
  agent to "bill Client X" or "refund order Y" immediately.

- **Manage Subscriptions & Products**: Handle the full lifecycle of recurring
  billing by creating products, setting up subscription plans, and managing
  subscriber details using natural language.

- **Resolve Issues & Track Performance**: Summarize and accept dispute claims,
  track shipment statuses, and retrieve merchant insights to make data-driven
  decisions on the fly.

## Prerequisites

...

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"
    PAYPAL_ENVIRONMENT = "SANDBOX"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="paypal_agent",
        instruction="Help users manage their PayPal account",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@paypal/mcp",
                            "--tools=all",
                        ],
                        env={
                            "PAYPAL_ACCESS_TOKEN": PAYPAL_ACCESS_TOKEN,
                            "PAYPAL_ENVIRONMENT": PAYPAL_ENVIRONMENT,
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

    PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"
    PAYPAL_ENVIRONMENT = "https://mcp.sandbox.paypal.com/http"  # Use for sandbox
    # PAYPAL_ENVIRONMENT = "https://mcp.paypal.com/http"  # Use for production

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="paypal_agent",
        instruction="Help users manage their PayPal account",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url=PAYPAL_ENVIRONMENT,
                    headers={
                        "Authorization": f"Bearer {PAYPAL_ACCESS_TOKEN}",
                    },
                ),
            )
        ],
    )
    ```

## Available tools

### Catalog management

Tool | Description
---- | -----------
`create_product` | Create a new product in the PayPal catalog
`list_product` | List products from the PayPal catalog
`show_product_details` | Show details of a specific product from the PayPal catalog

### Dispute management

Tool | Description
---- | -----------
`list_disputes` | Retrieve a summary of all disputes with optional filtering
`get_dispute` | Retrieve detailed information about a specific dispute
`accept_dispute_claim` | Accept a dispute claim, resolving it in favor of the buyer

### Invoices

Tool | Description
---- | -----------
`create_invoice` | Create a new invoice in the PayPal system
`list_invoices` | List invoices
`get_invoice` | Retrieve details about a specific invoice
`send_invoice` | Send an existing invoice to the specified recipient
`send_invoice_reminder` | Send a reminder for an existing invoice
`cancel_sent_invoice` | Cancel a sent invoice
`generate_invoice_qr_code` | Generate a QR code for an invoice

### Payments

Tool | Description
---- | -----------
`create_order` | Create an order in the PayPal system based on the provided details
`create_refund` | Process a refund for a captured payment
`get_order` | Get details of a specific payment
`get_refund` | Get the details for a specific refund
`pay_order` | Capture payment for an authorized order

### Reporting and insights

Tool | Description
---- | -----------
`get_merchant_insights` | Retrieve business intelligence metrics and analytics for a merchant
`list_transaction` | List all transactions

### Shipment tracking

Tool | Description
---- | -----------
`create_shipment_tracking` | Create shipment tracking information for a PayPal transaction
`get_shipment_tracking` | Get shipment tracking information for a specific shipment
`update_shipment_tracking` | Update shipment tracking information for a specific shipment

### Subscription management

Tool | Description
---- | -----------
`cancel_subscription` | Cancel an active subscription
`create_subscription` | Create a new subscription
`create_subscription_plan` | Create a new subscription plan
`list_subscription_plans` | List subscription plans
`show_subscription_details` | Show details of a specific subscription
`show_subscription_plan_details` | Show details of a specific subscription plan
`update_subscription` | Update an existing subscription

### Remote MCP server tools

Tool | Description
---- | -----------
`search_product` | Find gift card products in the PayPal catalog
`create_cart` | Open a new shopping cart with specified items and shipping preferences
`checkout_cart` | Finalize a shopping cart to complete the purchase process

## Configuration

...

## Additional resources

- [Paypal MCP Server Documentation](https://docs.paypal.ai/developer/tools/ai/mcp-quickstart)
- [Paypal MCP Server Repository](https://github.com/paypal/paypal-mcp-server)
- [Paypal Agent Tools Reference](https://docs.paypal.ai/developer/tools/ai/agent-tools-ref)
