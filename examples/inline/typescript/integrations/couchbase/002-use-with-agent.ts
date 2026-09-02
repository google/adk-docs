import { LlmAgent, MCPToolset } from "@google/adk";

const CB_CONNECTION_STRING = "couchbase://localhost";
const CB_USERNAME = "Administrator";
const CB_PASSWORD = "password";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "couchbase_agent",
    instruction: "Help users explore and query Couchbase databases",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: ["couchbase-mcp-server"],
                env: {
                    CB_CONNECTION_STRING: CB_CONNECTION_STRING,
                    CB_USERNAME: CB_USERNAME,
                    CB_PASSWORD: CB_PASSWORD,
                    CB_MCP_READ_ONLY_MODE: "true", // Prevents write operations
                },
            },
        })
    ],
});

export { rootAgent };