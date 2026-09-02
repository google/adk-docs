import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "linear_agent",
    instruction: "Help users manage issues, projects, and cycles in Linear",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "mcp-remote", "https://mcp.linear.app/mcp"],
            },
        }),
    ],
});

export { rootAgent };