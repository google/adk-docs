import { LlmAgent, MCPToolset } from "@google/adk";

const POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "postman_agent",
    instruction: "Help users manage their Postman workspaces and collections",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.postman.com/mcp",
            // (Optional) Use "/minimal" for essential tools only
            // (Optional) Use "/code" for code generation tools
            // (Optional) Use "https://mcp.eu.postman.com" for EU region
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${POSTMAN_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };