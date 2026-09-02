import { LlmAgent, MCPToolset } from "@google/adk";

const CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "cartesia_agent",
    instruction: "Help users generate speech and work with audio content",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: ["cartesia-mcp"],
                env: {
                    CARTESIA_API_KEY: CARTESIA_API_KEY,
                    // OUTPUT_DIRECTORY: "/path/to/output",  // Optional
                },
            },
        }),
    ],
});

export { rootAgent };