import { LlmAgent, MCPToolset } from "@google/adk";

const POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "postman_agent",
    instruction: "Help users manage their Postman workspaces and collections",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "@postman/postman-mcp-server",
                    // "--full",  // Use all 100+ tools
                    // "--code",  // Use code generation tools
                    // "--region", "eu",  // Use EU region
                ],
                env: {
                    POSTMAN_API_KEY: POSTMAN_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };