import { LlmAgent, MCPToolset } from "@google/adk";

const STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "stripe_agent",
    instruction: "Help users manage their Stripe account",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.stripe.com",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${STRIPE_SECRET_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };