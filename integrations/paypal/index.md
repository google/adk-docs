# PayPal MCP tool for ADK

Supported in ADKPythonTypeScript

The [PayPal MCP Server](https://github.com/paypal/paypal-mcp-server) connects your ADK agent to the [PayPal](https://www.paypal.com/) ecosystem. This integration gives your agent the ability to manage payments, invoices, subscriptions, and disputes using natural language, enabling automated commerce workflows and business insights.

## Use cases

- **Streamline Financial Operations**: Create orders, send invoices, and process refunds directly through chat without switching context. You can instruct your agent to "bill Client X" or "refund order Y" immediately.
- **Manage Subscriptions & Products**: Handle the full lifecycle of recurring billing by creating products, setting up subscription plans, and managing subscriber details using natural language.
- **Resolve Issues & Track Performance**: Summarize and accept dispute claims, track shipment statuses, and retrieve merchant insights to make data-driven decisions on the fly.

## Prerequisites

- Create a [PayPal Developer account](https://developer.paypal.com/)
- Create an app and retrieve your credentials from the [PayPal Developer Dashboard](https://developer.paypal.com/)
- [Generate an access token](https://developer.paypal.com/reference/get-an-access-token/) from your credentials

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

PAYPAL_ENVIRONMENT = "SANDBOX"  # Options: "SANDBOX" or "PRODUCTION"
PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

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
                        # (Optional) Specify which tools to enable
                        # "--tools=subscriptionPlans.list,subscriptionPlans.show",
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

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

PAYPAL_MCP_ENDPOINT = "https://mcp.sandbox.paypal.com/sse"  # Production: https://mcp.paypal.com/sse
PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="paypal_agent",
    instruction="Help users manage their PayPal account",
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=PAYPAL_MCP_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {PAYPAL_ACCESS_TOKEN}",
                },
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const PAYPAL_ENVIRONMENT = "SANDBOX"; // Options: "SANDBOX" or "PRODUCTION"
const PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "paypal_agent",
    instruction: "Help users manage their PayPal account",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "@paypal/mcp",
                    "--tools=all",
                    // (Optional) Specify which tools to enable
                    // "--tools=subscriptionPlans.list,subscriptionPlans.show",
                ],
                env: {
                    PAYPAL_ACCESS_TOKEN: PAYPAL_ACCESS_TOKEN,
                    PAYPAL_ENVIRONMENT: PAYPAL_ENVIRONMENT,
                },
            },
        }),
    ],
});

export { rootAgent };
```

Note

**Token Expiration**: PayPal Access Tokens have a limited lifespan of 3-8 hours. If your agent stops working, ensure your token has not expired and generate a new one if necessary. You should implement token refresh logic to handle token expiration.

## Available tools

### Catalog management

| Tool                   | Description                                                |
| ---------------------- | ---------------------------------------------------------- |
| `create_product`       | Create a new product in the PayPal catalog                 |
| `list_products`        | List products from the PayPal catalog                      |
| `show_product_details` | Show details of a specific product from the PayPal catalog |
| `update_product`       | Update an existing product in the PayPal catalog           |

### Dispute management

| Tool                   | Description                                                |
| ---------------------- | ---------------------------------------------------------- |
| `list_disputes`        | Retrieve a summary of all disputes with optional filtering |
| `get_dispute`          | Retrieve detailed information about a specific dispute     |
| `accept_dispute_claim` | Accept a dispute claim, resolving it in favor of the buyer |

### Invoices

| Tool                       | Description                                         |
| -------------------------- | --------------------------------------------------- |
| `create_invoice`           | Create a new invoice in the PayPal system           |
| `list_invoices`            | List invoices                                       |
| `get_invoice`              | Retrieve details about a specific invoice           |
| `send_invoice`             | Send an existing invoice to the specified recipient |
| `send_invoice_reminder`    | Send a reminder for an existing invoice             |
| `cancel_sent_invoice`      | Cancel a sent invoice                               |
| `generate_invoice_qr_code` | Generate a QR code for an invoice                   |

### Payments

| Tool            | Description                                                        |
| --------------- | ------------------------------------------------------------------ |
| `create_order`  | Create an order in the PayPal system based on the provided details |
| `create_refund` | Process a refund for a captured payment                            |
| `get_order`     | Get details of a specific payment                                  |
| `get_refund`    | Get the details for a specific refund                              |
| `pay_order`     | Capture payment for an authorized order                            |

### Reporting and insights

| Tool                    | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| `get_merchant_insights` | Retrieve business intelligence metrics and analytics for a merchant |
| `list_transactions`     | List all transactions                                               |

### Shipment tracking

| Tool                       | Description                                                   |
| -------------------------- | ------------------------------------------------------------- |
| `create_shipment_tracking` | Create shipment tracking information for a PayPal transaction |
| `get_shipment_tracking`    | Get shipment tracking information for a specific shipment     |
| `update_shipment_tracking` | Update shipment tracking information for a specific shipment  |

### Subscription management

| Tool                             | Description                                  |
| -------------------------------- | -------------------------------------------- |
| `cancel_subscription`            | Cancel an active subscription                |
| `create_subscription`            | Create a new subscription                    |
| `create_subscription_plan`       | Create a new subscription plan               |
| `update_subscription`            | Update an existing subscription              |
| `list_subscription_plans`        | List subscription plans                      |
| `show_subscription_details`      | Show details of a specific subscription      |
| `show_subscription_plan_details` | Show details of a specific subscription plan |

## Configuration

You can control which tools are enabled using the `--tools` command-line argument. This is useful for limiting the scope of the agent's permissions.

You can enable all tools with `--tools=all` or specify a comma-separated list of specific tool identifiers.

**Note**: The configuration identifiers below use dot notation (e.g., `invoices.create`) which differs from the tool names exposed to the agent (e.g., `create_invoice`).

**Products**: `products.create`, `products.list`, `products.update`, `products.show`

**Disputes**: `disputes.list`, `disputes.get`, `disputes.create`

**Invoices**: `invoices.create`, `invoices.list`, `invoices.get`, `invoices.send`, `invoices.sendReminder`, `invoices.cancel`, `invoices.generateQRC`

**Orders & Payments**: `orders.create`, `orders.get`, `orders.capture`, `payments.createRefund`, `payments.getRefunds`

**Transactions**: `transactions.list`

**Shipment**: `shipment.create`, `shipment.get`

**Subscriptions**: `subscriptionPlans.create`, `subscriptionPlans.list`, `subscriptionPlans.show`, `subscriptions.create`, `subscriptions.show`, `subscriptions.cancel`

## Additional resources

- [PayPal MCP Server Documentation](https://docs.paypal.ai/developer/tools/ai/mcp-quickstart)
- [PayPal MCP Server Repository](https://github.com/paypal/paypal-mcp-server)
- [PayPal Agent Tools Reference](https://docs.paypal.ai/developer/tools/ai/agent-tools-ref)
