import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "zoominfo_agent",
    instruction: "Help users find companies, enrich contacts, and surface go-to-market insights using ZoomInfo",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    "https://mcp.zoominfo.com/mcp",
                ],
            },
        }),
    ],
});

export { rootAgent };