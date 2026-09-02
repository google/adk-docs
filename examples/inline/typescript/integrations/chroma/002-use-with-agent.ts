import { LlmAgent, MCPToolset } from "@google/adk";

// For local storage, use:
const DATA_DIR = "/path/to/your/data/directory";

// For Chroma Cloud, use:
// const CHROMA_TENANT = "your-tenant-id";
// const CHROMA_DATABASE = "your-database-name";
// const CHROMA_API_KEY = "your-api-key";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "chroma_agent",
    instruction: "Help users store and retrieve information using semantic search",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: [
                    "chroma-mcp",
                    // For local storage, use:
                    "--client-type",
                    "persistent",
                    "--data-dir",
                    DATA_DIR,
                    // For Chroma Cloud, use:
                    // "--client-type",
                    // "cloud",
                    // "--tenant",
                    // CHROMA_TENANT,
                    // "--database",
                    // CHROMA_DATABASE,
                    // "--api-key",
                    // CHROMA_API_KEY,
                ],
            },
        }),
    ],
});

export { rootAgent };