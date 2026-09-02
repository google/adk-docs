import { LlmAgent, MCPToolset } from "@google/adk";

const PINECONE_API_KEY = "YOUR_PINECONE_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "pinecone_agent",
    instruction: "Help users manage and search their Pinecone vector indexes",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@pinecone-database/mcp"],
                env: {
                    PINECONE_API_KEY: PINECONE_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };