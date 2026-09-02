import { LlmAgent, MCPToolset } from "@google/adk";

const MARKIFACT_ACCESS_TOKEN = "YOUR_MARKIFACT_ACCESS_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "marketing_agent",
    instruction:
        "You are a performance marketing agent that helps users manage " +
        "ad campaigns, run analytics, sync e-commerce data, and " +
        "execute marketing workflows across Google Ads, Meta Ads, GA4, " +
        "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. " +
        "Always confirm with the user before any write operation.",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://api.markifact.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${MARKIFACT_ACCESS_TOKEN}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };