import { LlmAgent, MCPToolset } from "@google/adk";

const DEVELOPER_KNOWLEDGE_API_KEY = "YOUR_DEVELOPER_KNOWLEDGE_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "google_knowledge_agent",
    instruction: "Search Google developer documentation for implementation guidance.",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://developerknowledge.googleapis.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        "X-Goog-Api-Key": DEVELOPER_KNOWLEDGE_API_KEY,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };