import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "atlan_agent",
    instruction: "Help users search, discover, and manage enterprise data assets using Atlan",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    "https://mcp.atlan.com/mcp",
                ],
            },
        }),
    ],
});

export { rootAgent };