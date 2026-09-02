import { LlmAgent, MCPToolset } from "@google/adk";

const SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "supermetrics_agent",
    instruction: "Help users query and analyze their marketing data from Supermetrics",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.supermetrics.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${SUPERMETRICS_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };