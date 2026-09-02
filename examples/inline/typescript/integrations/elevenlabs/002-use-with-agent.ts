import { LlmAgent, MCPToolset } from "@google/adk";

const ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "elevenlabs_agent",
    instruction: "Help users generate speech, clone voices, and process audio",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: ["elevenlabs-mcp"],
                env: {
                    ELEVENLABS_API_KEY: ELEVENLABS_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };