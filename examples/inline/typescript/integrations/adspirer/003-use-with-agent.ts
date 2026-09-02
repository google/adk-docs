import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "advertising_agent",
    instruction:
        "You are an advertising agent that helps users create, manage, " +
        "and optimize ad campaigns across Google Ads, Meta Ads, " +
        "LinkedIn Ads, and TikTok Ads.",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    "https://mcp.adspirer.com/mcp",
                ],
            },
        }),
    ],
});

export { rootAgent };