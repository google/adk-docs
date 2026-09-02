import { LlmAgent, MCPToolset } from "@google/adk";

const PAYPAL_ENVIRONMENT = "SANDBOX"; // Options: "SANDBOX" or "PRODUCTION"
const PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
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