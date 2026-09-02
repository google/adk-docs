import { LlmAgent, MCPToolset } from "@google/adk";

const QDRANT_URL = "http://localhost:6333"; // Or your Qdrant Cloud URL
const COLLECTION_NAME = "my_collection";
// const QDRANT_API_KEY = "YOUR_QDRANT_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "qdrant_agent",
    instruction: "Help users store and retrieve information using semantic search",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: ["mcp-server-qdrant"],
                env: {
                    QDRANT_URL: QDRANT_URL,
                    COLLECTION_NAME: COLLECTION_NAME,
                    // QDRANT_API_KEY: QDRANT_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };