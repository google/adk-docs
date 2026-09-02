import { LlmAgent, MCPToolset } from "@google/adk";

const LINEAR_API_KEY = "YOUR_LINEAR_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "linear_agent",
    instruction: "Help users manage issues, projects, and cycles in Linear",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.linear.app/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${LINEAR_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };