import { LlmAgent, MCPToolset } from "@google/adk";

const ADSPIRER_ACCESS_TOKEN = "YOUR_ADSPIRER_ACCESS_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "advertising_agent",
    instruction:
        "You are an advertising agent that helps users create, manage, " +
        "and optimize ad campaigns across Google Ads, Meta Ads, " +
        "LinkedIn Ads, and TikTok Ads.",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.adspirer.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${ADSPIRER_ACCESS_TOKEN}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };