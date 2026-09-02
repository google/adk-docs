import { LlmAgent, MCPToolset } from "@google/adk";

const STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
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