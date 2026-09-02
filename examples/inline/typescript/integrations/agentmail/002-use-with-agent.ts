import { LlmAgent, MCPToolset } from "@google/adk";

const AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "agentmail_agent",
    instruction: "Help users manage email inboxes and send messages",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "agentmail-mcp"],
                env: {
                    AGENTMAIL_API_KEY: AGENTMAIL_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };