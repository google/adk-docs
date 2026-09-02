import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "atlassian_agent",
    instruction: "Help users work with data in Atlassian products",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    "https://mcp.atlassian.com/v1/mcp",
                ],
            },
        }),
    ],
});

export { rootAgent };