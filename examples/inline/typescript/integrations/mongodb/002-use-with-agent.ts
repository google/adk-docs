import { LlmAgent, MCPToolset } from "@google/adk";

// For database access, use a connection string:
const CONNECTION_STRING = "mongodb://localhost:27017/myDatabase";

// For Atlas management, use API credentials:
// const ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID";
// const ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "mongodb_agent",
    instruction: "Help users query and manage MongoDB databases",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mongodb-mcp-server",
                    "--readOnly", // Remove for write operations
                ],
                env: {
                    // For database access, use:
                    MDB_MCP_CONNECTION_STRING: CONNECTION_STRING,
                    // For Atlas management, use:
                    // MDB_MCP_API_CLIENT_ID: ATLAS_CLIENT_ID,
                    // MDB_MCP_API_CLIENT_SECRET: ATLAS_CLIENT_SECRET,
                },
            },
        }),
    ],
});

export { rootAgent };