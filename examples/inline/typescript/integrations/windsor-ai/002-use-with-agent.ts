import { LlmAgent, MCPToolset } from "@google/adk";

const WINDSOR_API_KEY = "YOUR_WINDSOR_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "windsor_agent",
    instruction: "Help users analyze their marketing and business data.",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.windsor.ai",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${WINDSOR_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };