import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "asana_agent",
    instruction: "Help users manage projects, tasks, and goals in Asana",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    "https://mcp.asana.com/sse",
                ],
            },
        }),
    ],
});

export { rootAgent };